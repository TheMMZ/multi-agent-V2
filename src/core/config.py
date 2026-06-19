import os
from langchain_ollama import ChatOllama

def get_slm_model(model_name: str = "qwen2.5-coder") -> ChatOllama:
  
    ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    
    try:
        return ChatOllama(
            model=model_name,
            temperature=0.0,         
            base_url=ollama_base_url,
            num_predict=4096,        
            timeout=180              
        )
    except Exception as e:
        raise RuntimeError(f"Impossible de connecter ChatOllama sur {ollama_base_url}. Erreur: {str(e)}")