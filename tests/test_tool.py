from src.tools.file_manager import write_file_to_disk

print("--- Test direct de la fonction ---")
resultat = write_file_to_disk.invoke({
    "file_relative_path": "backend/test_config.py",
    "content": "DEBUG = True\nDATABASE_URI = 'sqlite:///test.db'"
})
print(resultat)

print("--- LES ARGUMENTS RECONNUS PAR LANGCHAIN ---")
print(write_file_to_disk.args)

print("\n--- LA DESCRIPTION ENVOYÉE AU LLM ---")
print(write_file_to_disk.description)