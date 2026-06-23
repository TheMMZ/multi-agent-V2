# src/tools/execution_env.py

import subprocess
import time
import urllib.request
from langchain_core.tools import tool

@tool
def deploy_local_and_verify(file_relative_path: str = "app.py", port: int = 5000) -> str:
    """
    Lance l'application Flask en arrière-plan localement et vérifie son accessibilité.
    Retourne le lien d'accès et le statut de disponibilité.
    """
    url = f"http://127.0.0.1:{port}"
    try:
        print(f"[Tool Déploiement] Lancement de {file_relative_path} sur le port {port}...")
        
        # Lancer Flask en arrière-plan (Background process)
        process = subprocess.Popen(
            ["python", file_relative_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # S'accorder un petit temps (3 secondes) pour que le serveur Flask démarre
        time.sleep(3)
        
        # Vérifier l'accessibilité via une requête HTTP simple
        print(f"[Tool Deploiement] Tentative de connexion a {url}...")
        response = urllib.request.urlopen(url, timeout=5)
        
        if response.status == 200:
            return (
                f" DÉPLOIEMENT RÉUSSI LOCALEMENT !\n"
                f" Lien de l'application : {url}\n"
                f"Statut : Accessible et fonctionnelle (HTTP 200)."
            )
        else:
            return f"⚠️ Serveur lancé mais statut HTTP inattendu : {response.status}"
            
    except Exception as e:
        return f"Échec du déploiement ou de la vérification d'accessibilité : {str(e)}"