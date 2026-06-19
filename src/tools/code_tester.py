import ast
import os
from langchain_core.tools import tool

@tool
def analyze_python_syntax(file_relative_path: str) -> str:
    """
    Analyse statiquement la syntaxe d'un fichier Python pour détecter les erreurs de syntaxe (SyntaxError).
    
    Args:
        file_relative_path (str): Le chemin du fichier Python à tester (ex: 'app.py').
        
    Returns:
        str: Un rapport indiquant si le fichier est valide ou s'il contient une erreur précise.
    """
    clean_path = os.path.normpath(file_relative_path)
    if not os.path.exists(clean_path):
        return f"Erreur : Le fichier '{clean_path}' n'existe pas."
        
    try:
        with open(clean_path, "r", encoding="utf-8") as file:
            source = file.read()
        
        # ast.parse compile le code en arbre de syntaxe abstraite. Si syntaxe invalide -> lève une exception.
        ast.parse(source, filename=clean_path)
        return f"Succès : Le fichier '{clean_path}' a une syntaxe Python 100% VALIDE."
        
    except SyntaxError as e:
        return f"CRITICAL SYNTAX ERROR dans '{clean_path}' à la ligne {e.lineno}, colonne {e.offset}: {e.msg}\nCode fautif : {e.text}"
    except Exception as e:
        return f"Erreur lors de l'analyse de '{clean_path}': {str(e)}"