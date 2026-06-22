from typing import TypedDict, Dict, List, Annotated
import operator

def merge_dicts(a: Dict[str, str], b: Dict[str, str]) -> Dict[str, str]:
    res = a.copy() if a else {}
    if b: res.update(b)
    return res

class ProjectState(TypedDict):
   
    user_prompt: str                          
    functional_specs: str                     
    
    generated_code: Annotated[Dict[str, str], merge_dicts] # {'index.html': '...', 'server.js': '...'}
    
    test_logs: List[str]                      # Rapport d'erreurs d' Agent Testeur
    deployment_artifacts: Dict[str, str]       # Dockerfile o scripts d' Agent Déployeur
    current_agent: str                        # (for tracking)