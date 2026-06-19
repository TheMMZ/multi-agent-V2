from langchain_core.prompts import ChatPromptTemplate
from src.state.project_state import ProjectState
from src.core.config import get_slm_model

def concepteur_agent_node(state: ProjectState) -> dict:
  
    print("\n Agent Concepteur Analyse et modélisation de l'architecture...")
    
    llm = get_slm_model()
    
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", (
            "Vous êtes un Architecte Logiciel Senior. Votre rôle est de concevoir l'application demandée.\n"
            "Générez un rapport exhaustif en Markdown contenant strictement les sections suivantes :\n\n"
            
            "### 1. ANALYSE DES BESOINS\n"
            "- Analyse globale du besoin utilisateur.\n"
            "- Liste des fonctionnalités majeures.\n\n"
            
            "### 2. ARCHITECTURE TECHNIQUE & LOGICIELLE\n"
            
            "- Proposez l'architecture logicielle la plus adaptée au besoin de l'utilisateur.\n"
            "- Vous devez lister explicitement l'arborescence des fichiers cible (Backend et Frontend) "
            "  que l'équipe de développement devra créer.\n"
            "- Justifiez le choix de la structure (soit simple/ficher unique pour un petit script, "
            "  soit modulaire/multi-fichiers si l'application nécessite de la maintenance ou du routage complexe).\n"
            "- Frontend : Technologies recommandées (ex: HTML5/CSS3/JS natif).\n"
            "- Base de données : Proposez un modèle de stockage adapté (SQLite, JSON local, ou des dictionnaires en mémoire)."
            
            "### 3. DIAGRAMME DE FLUX (Mermaid)\n"
            "Générez un flux logique (graph TD) de l'application.\n\n"
            
            "### 4. DIAGRAMME DE CLASSE UML STRICT (Mermaid)\n"
            "Générez obligatoirement un diagramme de classe UML détaillé avec la syntaxe Mermaid `classDiagram`.\n"
            "Ce diagramme doit lister les entités, leurs attributs (+types) et méthodes pour guider l'Agent Développeur.\n"
            "Exemple de format attendu :\n"
            "```mermaid\n"
            "classDiagram\n"
            "    class Task {\n"
            "        +int id\n"
            "        +string title\n"
            "        +bool is_completed\n"
            "        +save()\n"
            "    }\n"
            "```"
        )),
        ("user", "Conçoit l'application suivante avec les diagrammes requis : {user_need}")
    ])
    
    chain = prompt_template | llm
    
    user_need = state.get("user_prompt")
    if not user_need:
        raise ValueError("Erreur : Aucun prompt utilisateur n'a été trouvé dans le State !")
        
    response = chain.invoke({"user_need": user_need})
    
    return {
        "functional_specs": response.content,
        "current_agent": "Concepteur"
    }