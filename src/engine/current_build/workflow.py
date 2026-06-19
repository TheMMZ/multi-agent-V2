from src.engine.current_build.graph_builder import build_my_graph

def run_agentic_workflow(user_prompt: str, functional_specs: str):
    graph = build_my_graph()
    
    initial_state = {
        "user_prompt": user_prompt,
        "functional_specs": functional_specs,
        "generated_code": {},
        "test_logs": [],
        "deployment_artifacts": {},
        "current_agent": "Initiateur"
    }
    
    final_state = initial_state
    for event in graph.stream(initial_state):
        for node_name, output in event.items():
            print(f"\n[Fin d'exécution du Node: '{node_name}']")
            if "current_agent" in output:
                print(f" Agent Actuel : {output['current_agent']}")
            print("--------------------------------------------------")
            final_state.update(output)
            
    print("\n======  WORKFLOW ENTIER TERMINÉ AVEC SUCCÈS ======")
    return final_state