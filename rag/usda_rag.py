"""
RAG module — USDA Foundation Foods + ChromaDB + Ollama embeddings.
 
Flujo:
  1. build_index()  →  lee el JSON USDA, genera embeddings con Ollama
                       y los persiste en ChromaDB (correr una sola vez).
  2. lookup_many()  →  recibe el dict de YOLO {nombre: cantidad},
                       hace búsqueda semántica en ChromaDB y devuelve
                       los datos nutricionales reales por 100 g.
"""
 
import json
import os
from pathlib import Path
from typing import Optional
 
import chromadb
from chromadb.utils.embedding_functions import OllamaEmbeddingFunction
 

OLLAMA_URL    = "http://localhost:11434"
EMBED_MODEL   = "nomic-embed-text"
CHROMA_PATH   = str(Path(__file__).parent.parent / "dataset" / "chroma_db")
COLLECTION    = "usda_foods"
 
_collection = None
 
 
def _get_embedding_function():
    return OllamaEmbeddingFunction(url=OLLAMA_URL, model_name=EMBED_MODEL)
 
 
def _get_collection():
    global _collection
    if _collection is not None:
        return _collection
 
    ef     = _get_embedding_function()
    client = chromadb.PersistentClient(path=CHROMA_PATH)
 
    # si ya existe la colección la reutiliza
    _collection = client.get_or_create_collection(
        name=COLLECTION,
        embedding_function=ef,
        metadata={"hnsw:space": "cosine"},
    )
    return _collection
 
 
#  Construir indice 
def build_index(usda_json_path: str | Path) -> int:
    """
    Lee el JSON USDA, genera embeddings con Ollama y los guarda en ChromaDB.
    Solo necesita correrse una vez. Si la colección ya tiene datos, no hace nada.
 
    Retorna el número de alimentos en la colección.
    """
    collection = _get_collection()
 
    if collection.count() > 0:
        print(f"[RAG] Índice ya existe con {collection.count()} alimentos. "
              "Usa rebuild_index() para regenerar.")
        return collection.count()
 
    return _populate_index(usda_json_path, collection)
 
 
def rebuild_index(usda_json_path: str | Path) -> int:
    """Borra y reconstruye la colección desde cero."""
    ef     = _get_embedding_function()
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    try:
        client.delete_collection(COLLECTION)
    except Exception:
        pass
 
    global _collection
    _collection = client.create_collection(
        name=COLLECTION,
        embedding_function=ef,
        metadata={"hnsw:space": "cosine"},
    )
    return _populate_index(usda_json_path, _collection)
 
 
def _populate_index(usda_json_path: str | Path, collection) -> int:
    """Parsea el JSON USDA y carga los alimentos en ChromaDB."""
    print(f"[RAG] Cargando USDA JSON desde {usda_json_path} …")
    with open(usda_json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
 
    records = []
    for food in data.get("SRLegacyFoods", []):
        if not isinstance(food, dict):
            continue
        desc = food.get("description", "")
        if not desc:
            continue
 
        kcal = protein = carbs = fat = None
        for n in food.get("foodNutrients", []):
            if not isinstance(n, dict):
                continue
            nutrient = n.get("nutrient")
            if not isinstance(nutrient, dict):
                continue
            name = nutrient.get("name", "")
            unit = nutrient.get("unitName", "")
            amt  = n.get("amount")
 
            if name == "Energy" and unit == "kcal":
                kcal = amt
            elif name == "Protein" and unit == "g":
                protein = amt
            elif "Carbohydrate" in name and "difference" in name and unit == "g":
                carbs = amt
            elif name == "Total lipid (fat)" and unit == "g":
                fat = amt
 
        if kcal is not None:
            records.append({
                "id":       str(food.get("fdcId", len(records))),
                "document": desc,                          # texto que se vectoriza
                "metadata": {
                    "kcal":    round(kcal,    1),
                    "protein": round(protein, 2) if protein is not None else 0.0,
                    "carbs":   round(carbs,   2) if carbs   is not None else 0.0,
                    "fat":     round(fat,     2) if fat     is not None else 0.0,
                },
            })
 
    print(f"[RAG] {len(records)} alimentos encontrados. Generando embeddings …")
 
    # Añadir en lotes para no saturar Ollama
    batch_size = 20
    for i in range(0, len(records), batch_size):
        batch = records[i : i + batch_size]
        collection.add(
            ids       = [r["id"]       for r in batch],
            documents = [r["document"] for r in batch],
            metadatas = [r["metadata"] for r in batch],
        )
        print(f"[RAG]   Lote {i // batch_size + 1}/{-(-len(records) // batch_size)} añadido")
 
    print(f"[RAG] Índice construido: {collection.count()} alimentos en ChromaDB.")
    return collection.count()
 
 
# Consulta
def lookup(food_name: str, n_results: int = 1) -> Optional[dict]:
    """
    Busca el alimento más parecido semánticamente a food_name.
 
    Retorna:
        {
            "display":  str,    # descripción original
            "matched":  str,    
            "distance": float,  # distancia coseno 
            "kcal":     float,  # por 100 g
            "protein":  float,
            "carbs":    float,
            "fat":      float,
        }
    """
    collection = _get_collection()
    if collection.count() == 0:
        return None
 
    results = collection.query(
        query_texts=[food_name],
        n_results=min(n_results, collection.count()),
        include=["documents", "metadatas", "distances"],
    )
 
    doc      = results["documents"][0][0]
    meta     = results["metadatas"][0][0]
    distance = results["distances"][0][0]
 
    return {
        "display":  doc,
        "matched":  food_name,
        "distance": round(distance, 4),
        "kcal":     meta["kcal"],
        "protein":  meta.get("protein"),
        "carbs":    meta.get("carbs"),
        "fat":      meta.get("fat"),
    }
 
 
def lookup_many(
    food_counts: dict[str, int],
    distance_threshold: float = 0.6,
) -> tuple[list[dict], list[str]]:
    """
    Busca múltiples alimentos a la vez.
 
    food_counts: {nombre_detectado: cantidad}  (salida de YOLO)
    distance_threshold: distancia coseno máxima aceptable (0=idéntico, 1=opuesto).
    Valores > threshold se consideran sin coincidencia.
 
    Retorna:
        found   – lista de dicts con datos USDA + campo "count"
        missing – nombres sin coincidencia aceptable
    """
    found   = []
    missing = []
 
    for name, count in food_counts.items():
        entry = lookup(name)
        if entry is None:
            missing.append(name)
            continue
 
        if entry["distance"] > distance_threshold:
            missing.append(name)
        else:
            entry["count"] = count
            found.append(entry)
 
    return found, missing
