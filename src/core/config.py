import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama

load_dotenv()

def get_slm_model():
    selected_model = os.getenv("SELECTED_MODEL", "gemini")
    
    if selected_model == "ollama":
        ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        try:
            return ChatOllama(
                model="qwen2.5-coder:7b",
                temperature=0.0,         
                base_url=ollama_base_url,
                num_predict=4096,        
                timeout=180              
            )
        except Exception as e:
            raise RuntimeError(f"Impossible de connecter ChatOllama sur {ollama_base_url}. Erreur: {str(e)}")
            
    else:
        # Default to Gemini
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("Erreur : GOOGLE_API_KEY introuvable dans le fichier .env")
            
        try:
            return ChatGoogleGenerativeAI(
                model="gemini-2.5-flash",
                temperature=0.0,
                max_output_tokens=8192,
                google_api_key=api_key
            )
        except Exception as e:
            raise RuntimeError(f"Impossible d'initialiser Gemini. Erreur: {str(e)}")