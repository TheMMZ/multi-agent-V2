
from langchain_core.prompts import ChatPromptTemplate
from src.state.project_state import ProjectState
from src.core.config import get_slm_model
from src.tools.execution_env import deploy_local_and_verify
from src.tools.file_manager import write_file_to_disk

def deployeur_agent_node(state: ProjectState) -> dict:
    print("\n[Agent Déployeur] Simulation et Réalisation du déploiement local...")
    
    llm = get_slm_model()
    
    # 1. Bind les tools (générer requirements + deploy_local)
    llm_with_tools = llm.bind_tools([write_file_to_disk, deploy_local_and_verify])
    
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", (
            "Vous êtes un Ingénieur DevOps Senior.\n"
            "Votre objectif est de réaliser le déploiement local de l'application.\n\n"
            "CONSIGNES OBLIGATOIRES :\n"
            "1. Appelez 'write_file_to_disk' pour vous assurer que le fichier 'requirements.txt' est bien écrit.\n"
            "2. Appelez impérativement l'outil 'deploy_local_and_verify' pour lancer réellement l'application 'app.py' et tester son accessibilité.\n"
            "3. Dans votre rapport final, vous devez obligatoirement fournir le lien généré par l'outil."
        )),
        ("user", "Voici le code validé. Lancez le déploiement et vérifiez l'accès.")
    ])
    
    chain = prompt_template | llm_with_tools
    response = chain.invoke({"user_prompt": state.get("user_prompt", "")})
    
    deployment_summary = {}
    
    import json
    
    # Extraction des tool_calls
    tool_calls = response.tool_calls
    
    # Fallback pour Qwen/Ollama si les outils sont retournés dans le content au lieu de tool_calls
    if not tool_calls and response.content:
        content_str = response.content.strip()
        # Qwen renvoie souvent plusieurs objets JSON par ligne ou dans un format texte
        try:
            # On essaie de séparer par des retours à la ligne si plusieurs JSON
            lines = content_str.split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith('{') and line.endswith('}'):
                    data = json.loads(line)
                    if "name" in data and "arguments" in data:
                        tool_calls.append({
                            "name": data["name"],
                            "args": data["arguments"],
                            "id": "call_fallback"
                        })
        except Exception as e:
            print(f"[Debug] Fallback parse failed: {e}")
    
    if tool_calls:
        for tool_call in tool_calls:
            # Exécuter l'outil d'écriture (requirements.txt, etc.)
            if tool_call["name"] == "write_file_to_disk":
                write_file_to_disk.invoke(tool_call["args"])
            
            # Exécuter l'outil de déploiement réel
            if tool_call["name"] == "deploy_local_and_verify":
                print("[Execution] Lancement du deploiment local et ping de l'URL...")
                result_verification = deploy_local_and_verify.invoke(tool_call["args"])
                print(f"\n[Resultat Deploiement] :\n{result_verification}")
                deployment_summary["deployment_report"] = result_verification
    else:
        print("[Warning] Aucun outil n'a été appelé par l'agent.")
                
    return {
        "deployment_artifacts": deployment_summary,
        "current_agent": "Déployeur"
    }