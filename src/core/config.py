import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

def get_slm_model(model_name: str = "gemini-2.5-flash") -> ChatGoogleGenerativeAI:
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("Erreur : GOOGLE_API_KEY introuvable dans le fichier .env")
        
    try:
        return ChatGoogleGenerativeAI(
            model=model_name,
            temperature=0.0,
            max_output_tokens=8192,
            google_api_key=api_key
        )
    except Exception as e:
        raise RuntimeError(f"Impossible d'initialiser Gemini. Erreur: {str(e)}")