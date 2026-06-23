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
        ("user", "Voici les spécifications sur l'application : \n\n{specs}\n\nRetours du Testeur (le cas échéant) : \n{test_logs}")
    ])
    
    specs = state.get("functional_specs")
    test_logs = state.get("test_logs", [])
    test_logs_str = "\n".join(test_logs) if test_logs else "Aucun retour de test pour le moment."
    
    if not specs:
        raise ValueError("Erreur : Aucune spécification technique trouvée dans le State !")
    
    chain = prompt_template | llm_with_tools
    response = chain.invoke({"specs": specs, "test_logs": test_logs_str})
    
    code_summary = {}
    
    import json
    
    # Extraction des tool_calls
    tool_calls = response.tool_calls
    
    # Fallback pour Qwen/Ollama
    if not tool_calls and response.content:
        content_str = response.content.strip()
        
        # Clean markdown
        if "```json" in content_str:
            content_str = content_str.split("```json")[1].split("```")[0].strip()
        elif "```" in content_str:
            content_str = content_str.split("```")[1].split("```")[0].strip()
            
        # Fix qwen2.5-coder bug with trailing braces (e.g. }}} instead of }})
        if content_str.endswith("}}}"):
            content_str = content_str[:-1]
            
        try:
            import re
            # Extract JSON array or object using regex to ignore trailing garbage
            match_array = re.search(r'\[\s*\{.*\}\s*\]', content_str, re.DOTALL)
            match_obj = re.search(r'\{.*\}', content_str, re.DOTALL)
            
            if match_array:
                data_list = json.loads(match_array.group(0))
                for data in data_list:
                    if "name" in data and "arguments" in data:
                        tool_calls.append({"name": data["name"], "args": data["arguments"], "id": "call_fallback"})
            elif match_obj:
                # Sometimes there are multiple JSON objects separated by newlines
                # but if regex matches one big block, we try parsing it
                try:
                    data = json.loads(match_obj.group(0))
                    if "name" in data and "arguments" in data:
                        tool_calls.append({"name": data["name"], "args": data["arguments"], "id": "call_fallback"})
                except json.JSONDecodeError:
                    # Fallback to line by line regex matching
                    for line in content_str.split('\n'):
                        m = re.search(r'\{.*\}', line)
                        if m:
                            data = json.loads(m.group(0))
                            if "name" in data and "arguments" in data:
                                tool_calls.append({"name": data["name"], "args": data["arguments"], "id": "call_fallback"})
        except Exception as e:
            print(f"[Debug] Fallback parse failed: {e}")
            print(f"[Debug] Raw content was: {content_str}")

    # 2. Exécution dynamique de n'importe quelle tool appelée par le LLM
    if tool_calls:
        print(f"\n[Développeur] L'Agent a déclenché {len(tool_calls)} action(s).")
        for tool_call in tool_calls:
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