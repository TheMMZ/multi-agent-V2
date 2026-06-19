from typing import TypedDict, Dict, List, Annotated
import operator

class ProjectState(TypedDict):
   
    user_prompt: str                          
    functional_specs: str                     
    
    generated_code: Annotated[Dict[str, str], operator.add] # {'index.html': '...', 'server.js': '...'}
    
    test_logs: List[str]                      # Rapport d'erreurs d' Agent Testeur
    deployment_artifacts: Dict[str, str]       # Dockerfile o scripts d' Agent Déployeur
    current_agent: str                        # (for tracking)