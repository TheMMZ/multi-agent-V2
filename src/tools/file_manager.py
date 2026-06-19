import os
from langchain_core.tools import tool

@tool
def write_file_to_disk(file_relative_path: str, content: str) -> str:
    """
    Crée ou écrase un fichier sur le disque avec le contenu spécifié.
    Gère automatiquement la création des dossiers parents si nécessaires.

    Args:
        file_relative_path (str): Le chemin relatif du fichier (ex: 'backend/config.py').
        content (str): Le code complet ou le contenu textuel à écrire dans le fichier.

    Returns:
        str: Un message de succès ou d'erreur.
    """
    try:
        clean_path = os.path.normpath(file_relative_path)
        directory = os.path.dirname(clean_path)
        
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
            
        with open(clean_path, "w", encoding="utf-8") as file:
            file.write(content)
            
        return f"Succès : Le fichier '{clean_path}' a été créé/modifié avec succès."
    except Exception as e:
        return f"Erreur lors de l'écriture du fichier '{file_relative_path}' : {str(e)}"


@tool
def read_file_from_disk(file_relative_path: str) -> str:
    """
    Lit le contenu d'un fichier existant sur le disque. 
    Utile pour analyser le code actuel avant de faire des modifications ou des corrections.

    Args:
        file_relative_path (str): Le chemin relatif du fichier à lire (ex: 'backend/routes.py').

    Returns:
        str: Le contenu textuel complet du fichier ou un message d'erreur si le fichier n'existe pas.
    """
    try:
        clean_path = os.path.normpath(file_relative_path)
        
        if not os.path.exists(clean_path):
            return f"Erreur : Le fichier '{clean_path}' n'existe pas."
            
        with open(clean_path, "r", encoding="utf-8") as file:
            content = file.read()
            
        return content
    except Exception as e:
        return f"Erreur lors de la lecture du fichier '{file_relative_path}' : {str(e)}"