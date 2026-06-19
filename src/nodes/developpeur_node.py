from langchain_core.prompts import ChatPromptTemplate
from src.state.project_state import ProjectState
from src.core.config import get_slm_model
from src.tools.file_manager import write_file_to_disk, read_file_from_disk

def developpeur_agent_node(state: ProjectState) -> dict:
    print("\n[Agent Développeur] Analyse des specs et gestion des fichiers...")
    
    llm = get_slm_model()
    
    # 1. Bind dial les deux outils
    tools_map = {
        "write_file_to_disk": write_file_to_disk,
        "read_file_from_disk": read_file_from_disk
    }
    llm_with_tools = llm.bind_tools(list(tools_map.values()))
    
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", (
            "Vous êtes un Développeur Full-Stack Senior avec 10 ans d'expérience. Vous fuyez le code générique d'IA.\n"
            "Votre objectif est de générer ou modifier une application Flask + Vanilla JS modulaire et propre.\n\n"
            
            "DIRECTIVES DE STYLE (HUMAIN) :\n"
            "- Écrivez du code robuste : incluez des blocs try/except, des validations d'inputs et des codes HTTP appropriés.\n"
            "- Pas de raccourcis : Ne mettez JAMAIS de commentaires du type '# [Reste du code ici...]'. Écrivez tout.\n"
            "- Stratégie de modification : Si vous devez corriger un bug, utilisez d'abord 'read_file_from_disk' pour lire "
            "le fichier concerné, puis appliquez vos corrections avec 'write_file_to_disk'.\n\n"
            
            "Pour la création initiale, appelez 'write_file_to_disk' pour :\n"
            "1. 'backend/config.py' | 2. 'backend/models.py' | 3. 'backend/routes.py' | 4. 'app.py' \n"
            "5. 'templates/index.html' | 6. 'static/style.css' | 7. 'static/app.js'"
        )),
        ("user", "Voici les spécifications ou retours sur l'application : \n\n{specs}")
    ])
    
    specs = state.get("functional_specs")
    if not specs:
        raise ValueError("Erreur : Aucune spécification technique trouvée dans le State !")
    
    chain = prompt_template | llm_with_tools
    response = chain.invoke({"specs": specs})
    
    code_summary = {}
    
    # 2. Exécution dynamique de n'importe quelle tool appelée par le LLM
    if response.tool_calls:
        print(f"\n[Développeur] L'Agent a déclenché {len(response.tool_calls)} action(s).")
        for tool_call in response.tool_calls:
            tool_name = tool_call["name"]
            args = tool_call["args"]
            
            if tool_name in tools_map:
                print(f"Exécution de l'outil [{tool_name}]...")
                try:
                    # Invocation dynamique via le dictionnaire tools_map
                    result_msg = tools_map[tool_name].invoke(args)
                    print(f"    -> {result_msg}")
                    
                    # Remplir le summary selon l'action
                    file_path = args.get("file_relative_path", "unknown")
                    code_summary[file_path] = f"Action [{tool_name}] exécutée"
                except Exception as e:
                    print(f"Erreur avec l'outil {tool_name}: {str(e)}")
                    code_summary[args.get("file_relative_path", "unknown")] = f"Erreur: {str(e)}"
    else:
        print("Warning : Le modèle n'a pas déclenché d'outils.")
        
    return {
        "generated_code": code_summary,
        "current_agent": "Developpeur"
    }