"""
CORRER UNA SOLA VEZ PARA GENERAR LOS EMBEDDINGS DE LA BASE DE DATOS 
 
Genera los embeddings de la base de datos de USDA con Ollama y los persiste en ChromaDB.
 
Antes de ejecutar instale nomic embed si no lo ha hecho para poder generar los embeddings:
    ollama pull nomic-embed-text
 
Y ejecute así:
    python scripts/build_usda_index.py
"""
import os
import sys
from pathlib import Path
 
# Agrega el directorio raíz al path para poder importar rag/
sys.path.insert(0, str(Path(__file__).parent.parent))
 
from rag.usda_rag import build_index, rebuild_index
 
USDA_JSON = Path(__file__).parent.parent / "dataset" / "FoodData_Central_sr_legacy_food_json_2018-04.json"
 
if __name__ == "__main__":
    if not USDA_JSON.exists():
        print(f"[ERROR] No se encontró el JSON USDA en: {USDA_JSON}")
        print("Coloque el archivo en dataset/ o defina la variable USDA_JSON.")
        sys.exit(1)
 
    # Para forzar a reconstruir el indice si ya existe
    force = "--rebuild" in sys.argv
    if force:
        print("[INFO] Modo --rebuild: borrando colección existente …")
        total = rebuild_index(USDA_JSON)
    else:
        total = build_index(USDA_JSON)
 
    print(f"\n {total} alimentos indexados en ChromaDB.")
    print("Ya puede arrancar la app con: uvicorn app.main:app --reload")
