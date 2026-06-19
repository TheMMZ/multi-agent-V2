import os
import sys

 
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.nodes.concepteur_node import concepteur_agent_node

def run_unit_test():
    print("[Test Unitaire] Début du Test de l'Agent Concepteur...")
    
    mock_state = {
        "user_prompt": "Une application web de gestion de stock avec Flask et Base de données locale.",
        "functional_specs": "",
        "generated_code": {},
        "test_logs": [],
        "deployment_artifacts": {},
        "current_agent": ""
    }
    
    try:
        # Exécuter la Node
        result = concepteur_agent_node(mock_state)
        
        print("\n✅ Test exécuté avec succès !")
        print("================ LIVRABLE DE L'AGENT CONCEPTEUR ================")
        print(result["functional_specs"])
        print("================================================================")
        
    except Exception as e:
        print(f"\n Le test a échoué ! Erreur : {str(e)}")

if __name__ == "__main__":
    run_unit_test()