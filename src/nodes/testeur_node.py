
from langchain_core.prompts import ChatPromptTemplate
from src.state.project_state import ProjectState
from src.core.config import get_slm_model
from src.tools.code_tester import analyze_python_syntax
from src.tools.file_manager import read_file_from_disk  

def testeur_agent_node(state: ProjectState) -> dict:
    print("\n[Agent Testeur] Inspection complète et QA (Backend & Frontend)...")
    
    llm = get_slm_model()
    generated_files = state.get("generated_code", {})
    
    if not generated_files:
        return {
            "test_logs": ["STATUT_APPROUVÉ : Aucun fichier généré à tester."],
            "current_agent": "Testeur"
        }
    

    python_files = [f for f in generated_files.keys() if f.endswith('.py')]
    syntax_reports = []
    
    for f in python_files:
        report = analyze_python_syntax.invoke({"file_relative_path": f})
        syntax_reports.append(f"Syntaxe [{f}] : {report}")
  
    full_code_context = []
    for file_path in generated_files.keys():
        # Lire le vrai contenu écrit sur le disque
        content = read_file_from_disk.invoke({"file_relative_path": file_path})
        full_code_context.append(f"=== FICHIER : {file_path} ===\n{content}\n")
    

    prompt_template = ChatPromptTemplate.from_messages([
        ("system", (
            "Vous êtes un Ingénieur QA (Quality Assurance) Senior d'élite.\n"
            "Votre mission est de fournir un RAPPORT DE QUALITÉ complet (Backend + Frontend).\n\n"
            
            "REQUIS DE TEST À VÉRIFIER :\n"
            "1. Erreurs de Syntaxe : Analysez les rapports machines fournis.\n"
            "2. Simulation de Cas d'Utilisation : Simulez mentalement les requêtes Fetch du JS vers l'API Flask. "
            "Est-ce que la route `/api/todos` renvoie le bon format ? Est-ce que le DOM est bien mis à jour ?\n"
            "3. Intégration UI/Frontend : Vérifiez si le fichier HTML intègre bien Bootstrap/Tailwind, et si les IDs des boutons correspondent au script JS.\n"
            "4. Gestion des Erreurs : Est-ce qu'il y a des try/except côté Python et des `.catch()` côté JS ?\n\n"
            
            "FORMAT DU RAPPORT DE RETOUR :\n"
            "###  RAPPORT DE QUALITÉ DU CODE\n"
            "- **Analyse Backend** : [Statut et remarques]\n"
            "- **Analyse Frontend & UI** : [Validation de la synchro HTML/JS]\n"
            "- **Simulation de Bugs / edge cases** : [Ce qui pourrait planter si l'input est vide, etc.]\n\n"
            
            "CRITÈRE DE VERDICT INTERNE :\n"
            "- Si le code est propre, fonctionnel, robuste et sans bug -> Ajoutez la mention exacte : STATUT_APPROUVÉ\n"
            "- Si vous détectez un bug, un manque de robustesse, ou une incohérence UI/API -> Proposez des corrections claires et ajoutez la mention exacte : STATUT_REJETÉ"
        )),
        ("user", (
            "Voici les rapports de syntaxe machine :\n{syntax}\n\n"
            "Voici le code source complet de l'application :\n{code_source}"
        ))
    ])
    
    # Exécution du pipeline
    chain = prompt_template | llm
    response = chain.invoke({
        "syntax": "\n".join(syntax_reports),
        "code_source": "\n".join(full_code_context)
    })
    
    verdict = response.content
    print(f"\n[Verdict Final du Testeur QA] :\n{verdict}")
    
    return {
        "test_logs": [verdict],
        "current_agent": "Testeur"
    }