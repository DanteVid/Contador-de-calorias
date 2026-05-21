import os
import sys
from pathlib import Path
 
import cv2
import numpy as np
import requests
from rag.usda_rag import lookup_many
 
OLLAMA_URL  = "http://localhost:11434"
LLM = "gemma4:e2b"

def _build_prompt(count: dict[str, int], found: list[dict], missing: list[str]) -> str:
    """
    Found:  Los que tienen datos en la base
    Missing: Los que no tienen datos en la base.
    """

    context_lines = []
    for e in found:
        n = e["count"]
        kcal = e["kcal"]
        parts = []
        if e.get("protein"): parts.append(f"proteína {e['protein']} g")
        if e.get("carbs"): parts.append(f"carbohidratos {e['carbs']} g")
        if e.get("fat"): parts.append(f"grasa {e['fat']} g")
        macro_str = f" | {', '.join(parts)}" if parts else ""
        context_lines.append(
            f'- {n} × "{e["display"]}" → {kcal} kcal/100 g{macro_str}'
        )
 
    context_block = "\n".join(context_lines) if context_lines else "(ninguno)"
 
    missing_block = (
        "\n".join(f"- {m}" for m in missing) if missing else "(ninguno)"
    )

    lista = "\n".join([f"- {number} {food}" for food, number in count.items()])
 
    prompt = f"""Eres un nutricionista experto. Tienes los siguientes datos nutricionales de la base de datos USDA Legacy Food (valores por 100 gramos):
    === DATOS NUTRICIONALES USDA (por 100 g) ===
    {context_block}
    
    === INGREDIENTES SIN DATOS EN LA BASE (estima tú) ===
    {missing_block}
    
    Y los siguientes ingredientes detectados en la imagen (sin datos nutricionales, solo nombre y cantidad):
    === INGREDIENTES DETECTADOS EN LA IMAGEN ===
    {lista}

    INSTRUCCIONES:
    1. Para los ingredientes con datos USDA usa EXACTAMENTE los valores de kcal indicados — no los cambies.
    2. Para los ingredientes sin datos, estima las kcal por 100 g basándote en tu conocimiento.
    3. Traduce TODOS los nombres de ingredientes al español.
    4. Si hay más de 1 unidad del mismo ingrediente, indícalo con "N ×" (y cambia el nombre si es plural o singular al que corresponde en español).
    5. Responde ÚNICAMENTE en este formato, sin texto adicional, SIEMPRE con un emoji representativo junto a cada ingrediente:
    
    - [N ×] 🍗 Nombre en español: X kcal / 100 g 
    - [N ×] 🥦 Nombre en español: X kcal / 100 g 
    ...
    Por cada 100 g de este platillo te comes... Z kcal!

    Para calcular Z:
    1. Para cada ingrediente, calcula: (kcal / 100 g) × cantidad_gramos (Ejemplo: si hay 5 detectados, serían 500 g)
    2. Sea total_kcal la suma de todos esos valores 
    3. Sea total_gramos la suma de todos los gramos
    4. Z = (total_kcal / total_gramos) × 100

    Ejemplo: 200 g de pollo (165 kcal/100g) y 100 g de arroz (130 kcal/100g)
    → (165×200 + 130×100) / (200+100) × 100 = (33000+13000)/300 × 100 = 153.33 kcal/100g
    """
    
    return prompt
 
# Inferencia 
def run_inference(image: bytes | np.ndarray, model) -> str:
 
    if isinstance(image, bytes):
        nparr = np.frombuffer(image, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
 
    results = model.predict(source=image, conf=0.5)
    count: dict[str, int] = {}
    for r in results:
        for box in r.boxes:
            cls  = int(box.cls)
            name = model.names[cls]
            count[name] = count.get(name, 0) + 1
 
    print(f"Detected: {count}", flush=True)
 
    if not count:
        return "No se detectaron alimentos en la imagen."
 
    # Búsqueda semántica
    found, missing = lookup_many(count, distance_threshold=0.6)
 
    print(f"[RAG]  {len(found)}/{len(count)} alimentos encontrados en USDA", flush=True)
    for e in found:
        print(
            f"'{e['matched']}' -> '{e['display']}'"
            f"(distancia={e['distance']}, {e['kcal']} kcal/100g)",
            flush=True,
        )
    if missing:
        print(f"[RAG]  Sin coincidencia: {missing}", flush=True)
 
    prompt = _build_prompt(count, found, missing)
 
    # Se le manda al LLM
    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model":  LLM,
                "prompt": prompt,
                "stream": False,
            },
            timeout=120,
        )
        response.raise_for_status()
        resultado = response.json()["response"]
    except requests.RequestException as e:
        return f"Error: {e}"
 
    print(f"\n[LLM] Respuesta:\n{resultado}", flush=True)
    return resultado
 
