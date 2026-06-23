from langgraph.graph import StateGraph, END
from src.state.project_state import ProjectState

from src.nodes.concepteur_node import concepteur_agent_node
from src.nodes.developpeur_node import developpeur_agent_node
from src.nodes.testeur_node import testeur_agent_node
from src.nodes.deployeur_node import deployeur_agent_node

def route_after_test(state: ProjectState) -> str:
    logs = state.get("test_logs", [])
    last_feedback = logs[-1] if logs else ""
    
    if "STATUT_REJETÉ" in last_feedback:
        print("\n[Router] Code rejeté par le Testeur! Retour au Développeur.")
        return "developpeur"
    else:
        print("\n[Router] Code approuvé ! Passage à l'étape Déploiement.")
        return "deployeur"  

def build_my_graph(checkpointer=None, mode="Limited"):
    
    workflow = StateGraph(ProjectState)
    
    workflow.add_node("concepteur", concepteur_agent_node)
    workflow.add_node("developpeur", developpeur_agent_node)
    workflow.add_node("testeur", testeur_agent_node)
    workflow.add_node("deployeur", deployeur_agent_node)
    
    workflow.set_entry_point("concepteur")
    
    workflow.add_edge("concepteur", "developpeur") 
    workflow.add_edge("developpeur", "testeur")     
    
    workflow.add_conditional_edges(
        "testeur",           
        route_after_test,    
        {
            "developpeur": "developpeur",  
            "deployeur": "deployeur"      
        }
    )
    
    workflow.add_edge("deployeur", END)
    
    if mode == "Limited (Human-in-the-loop)":
        return workflow.compile(checkpointer=checkpointer, interrupt_after=["testeur"])
    else:
        return workflow.compile(checkpointer=checkpointer)