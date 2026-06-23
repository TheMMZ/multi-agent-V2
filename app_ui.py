import streamlit as st
import uuid
from langgraph.checkpoint.memory import MemorySaver
import sys
import os

# Ensure src is accessible
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.engine.current_build.graph_builder import build_my_graph

st.set_page_config(page_title="Multi-Agent Builder", page_icon="🤖", layout="wide")

st.title("🤖 Générateur d'Applications Multi-Agent")
st.markdown("Interface Chatbot interactive avec **Human-in-the-Loop** (Validation QA).")

with st.sidebar:
    st.header("⚙️ Paramètres")
    selected_model_ui = st.selectbox("Modèle d'IA :", ["gemini", "ollama"], index=0)
    selected_mode_ui = st.selectbox("Niveau d'accès :", ["Limited (Human-in-the-loop)", "Full Access (No human interact)"], index=0)
    
    if st.button("🔄 Réinitialiser le Graphe"):
        if "memory" in st.session_state:
            del st.session_state["memory"]
        st.rerun()

# Synchronisation de la variable d'environnement pour config.py
os.environ["SELECTED_MODEL"] = selected_model_ui

# Initialisation de la mémoire et du graphe dans la session utilisateur
if "memory" not in st.session_state:
    st.session_state.memory = MemorySaver()
    st.session_state.graph = build_my_graph(checkpointer=st.session_state.memory, mode=selected_mode_ui)
    st.session_state.thread_id = str(uuid.uuid4())
    st.session_state.chat_history = []
    st.session_state.current_mode = selected_mode_ui

# Recompilation si le mode change
if st.session_state.get("current_mode") != selected_mode_ui:
    st.session_state.graph = build_my_graph(checkpointer=st.session_state.memory, mode=selected_mode_ui)
    st.session_state.current_mode = selected_mode_ui

config = {"configurable": {"thread_id": st.session_state.thread_id}}
graph = st.session_state.graph

# Afficher l'historique du chat
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Récupérer l'état actuel du graphe
state = graph.get_state(config)

if not state.next:
    # --- PHASE 1 : NOUVELLE REQUÊTE ---
    # Le graphe est inactif (soit il n'a jamais démarré, soit il est à la fin)
    user_prompt = st.chat_input("Décrivez l'application que vous souhaitez créer...")
    
    if user_prompt:
        # Afficher la requête utilisateur
        st.session_state.chat_history.append({"role": "user", "content": user_prompt})
        with st.chat_message("user"):
            st.markdown(user_prompt)
            
        with st.spinner("Exécution des Agents (Concepteur ➔ Développeur ➔ Testeur)..."):
            initial_state = {"user_prompt": user_prompt, "test_logs": []}
            # stream(None) ne marchera pas pour initialiser, on passe l'état initial
            for event in graph.stream(initial_state, config=config):
                for node_name, node_state in event.items():
                    msg = f"✅ **Agent {node_name.capitalize()}** a terminé sa tâche."
                    
                    if node_name == "deployeur":
                        artifacts = node_state.get("deployment_artifacts", {})
                        report = artifacts.get("deployment_report", "")
                        if report:
                            msg += f"\n\n🌐 **Rapport de Déploiement :**\n```text\n{report}\n```"
                            
                    st.session_state.chat_history.append({"role": "assistant", "content": msg})
                    with st.chat_message("assistant"):
                        st.markdown(msg)
            
            # Recharger la page pour afficher l'interruption
            st.rerun()

else:
    # --- PHASE 2 : HUMAN-IN-THE-LOOP ---
    # Le graphe est en pause (interruption)
    next_node = state.next[0]
    current_values = state.values
    test_logs = current_values.get("test_logs", [])
    last_test_log = test_logs[-1] if test_logs else "Aucun rapport."
    
    # Affichage du rapport du Testeur
    st.warning("⏸️ Le workflow est en pause. L'Agent Testeur a fourni son rapport.")
    with st.expander("📄 Voir le rapport du Testeur", expanded=True):
        st.markdown(last_test_log)
    
    st.divider()
    
    # Choix de l'utilisateur
    if next_node == "developpeur":
        st.info("🔄 Le code a été **REJETÉ** par le Testeur. Il va être renvoyé au Développeur pour correction.")
        
        # L'utilisateur peut ajouter des instructions pour la correction
        user_feedback = st.chat_input("Ajoutez des instructions humaines pour le Développeur (Optionnel)...")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🚀 Continuer sans ajouter d'instructions", use_container_width=True):
                user_feedback = "Aucune instruction humaine additionnelle."
                
        if user_feedback:
            # On ajoute le feedback utilisateur à la fin du rapport du testeur
            new_log = last_test_log + f"\n\n--- INSTRUCTIONS HUMAINES ADDITIONNELLES ---\n{user_feedback}"
            current_values["test_logs"][-1] = new_log
            
            # Mise à jour de l'état "comme si" c'était le testeur qui l'avait écrit
            graph.update_state(config, {"test_logs": current_values["test_logs"]}, as_node="testeur")
            
            st.session_state.chat_history.append({"role": "user", "content": f"📝 Instructions envoyées au Développeur : {user_feedback}"})
            
            with st.spinner("Reprise de l'exécution (Développeur ➔ Testeur)..."):
                for event in graph.stream(None, config=config):
                    for node_name, node_state in event.items():
                        msg = f"✅ **Agent {node_name.capitalize()}** a terminé sa tâche."
                        st.session_state.chat_history.append({"role": "assistant", "content": msg})
                        with st.chat_message("assistant"):
                            st.markdown(msg)
            st.rerun()

    elif next_node == "deployeur":
        st.success("✅ Le code a été **APPROUVÉ** par le Testeur ! Prêt pour le déploiement.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🚀 Approuver et Lancer le Déploiement", use_container_width=True, type="primary"):
                st.session_state.chat_history.append({"role": "user", "content": "Approbation humaine : Déploiement autorisé."})
                with st.spinner("Exécution de l'Agent Déployeur..."):
                    for event in graph.stream(None, config=config):
                        for node_name, node_state in event.items():
                            if node_name == "deployeur":
                                artifacts = node_state.get("deployment_artifacts", {})
                                report = artifacts.get("deployment_report", "Déploiement terminé.")
                                msg = f"🌐 **Déploiement Terminé !**\n\n```text\n{report}\n```"
                                st.session_state.chat_history.append({"role": "assistant", "content": msg})
                                with st.chat_message("assistant"):
                                    st.markdown(msg)
                st.rerun()
                
        with col2:
            # L'utilisateur force le rejet
            reject_reason = st.text_input("Forcer des modifications (Renvoyer au Développeur):", placeholder="Ex: Change la couleur de fond en bleu...")
            if st.button("🔄 Refuser et Renvoyer", use_container_width=True):
                if reject_reason:
                    # On force le statut à REJETÉ pour que route_after_test l'envoie au developpeur
                    new_log = last_test_log + f"\n\nSTATUT_REJETÉ\n--- INSTRUCTIONS HUMAINES ADDITIONNELLES ---\n{reject_reason}"
                    current_values["test_logs"][-1] = new_log
                    
                    # Mise à jour de l'état
                    graph.update_state(config, {"test_logs": current_values["test_logs"]}, as_node="testeur")
                    
                    st.session_state.chat_history.append({"role": "user", "content": f"❌ Refus humain. Nouvelles instructions : {reject_reason}"})
                    
                    with st.spinner("Reprise de l'exécution (Développeur ➔ Testeur)..."):
                        for event in graph.stream(None, config=config):
                            for node_name, node_state in event.items():
                                msg = f"✅ **Agent {node_name.capitalize()}** a terminé sa tâche."
                                st.session_state.chat_history.append({"role": "assistant", "content": msg})
                                with st.chat_message("assistant"):
                                    st.markdown(msg)
                    st.rerun()
                else:
                    st.error("Veuillez saisir une raison pour renvoyer le code au développeur.")
