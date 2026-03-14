import os
from dotenv import load_dotenv
import google.genai as genai
from PyPDF2 import PdfReader
import json
import re

# Cargar variables de entorno desde .env (si existe)
load_dotenv()

# Modelo por defecto (ajustable)
DEFAULT_MODEL = 'models/gemini-2.5-flash'

# Cliente cacheado (inicialización lazy)
_client = None


def get_client():
    """Devuelve un cliente genai inicializado. Lanza RuntimeError si falta la clave al intentar usarlo."""
    global _client
    if _client is not None:
        return _client

    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY no encontrada. Añade GEMINI_API_KEY en .env o en las variables de entorno.")

    _client = genai.Client(api_key=api_key)
    return _client


def _extract_text_from_genai_response(resp):
    # Manejar diferentes formas de respuesta que puede devolver la SDK
    # 1) resp.text (algunos wrappers)
    if resp is None:
        return ''
    if hasattr(resp, 'text') and resp.text:
        return resp.text
    # 2) resp.candidates -> coger content o display
    try:
        candidates = getattr(resp, 'candidates', None)
        if candidates and len(candidates) > 0:
            first = candidates[0]
            # varios campos posibles
            for attr in ('content', 'output', 'message', 'text'):
                if hasattr(first, attr) and getattr(first, attr):
                    val = getattr(first, attr)
                    # Si es un objeto complejo, intentar convertir a string o extraer partes
                    if hasattr(val, 'parts'):
                        return "".join([p.text for p in val.parts if hasattr(p, 'text')])
                    return str(val)
    except Exception:
        pass
    # 3) str fallback
    try:
        return str(resp)
    except Exception:
        return ''

def _clean_json_response(text):
    """Limpia el texto de respuesta para extraer JSON válido."""
    # Eliminar bloques de código markdown
    text = re.sub(r'^```json\s*', '', text, flags=re.MULTILINE)
    text = re.sub(r'^```\s*', '', text, flags=re.MULTILINE)
    text = re.sub(r'\s*```$', '', text, flags=re.MULTILINE)
    return text.strip()

def extract_text_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text() or ""
        text += page_text + "\n"
    return text


def generate_quiz_from_pdf(pdf_path):
    """Genera un quiz interactivo desde el PDF con esquema JSON estricto."""
    text = extract_text_from_pdf(pdf_path)
    if not text.strip():
        return "Error: No se pudo extraer texto del PDF. Asegúrate de que el PDF contenga texto legible."

    prompt = f"""
Basado en este texto, genera un quiz interactivo para estudiantes de 12-15 años, con 5 preguntas variadas.
Usa lenguaje simple y educativo. Evita el uso de emojis.

Debes devolver EXACTAMENTE un JSON válido con esta estructura:
{{
  "questions": [
    {{
      "id": 1,
      "type": "seleccion",  // "seleccion", "completacion", "emparejamiento", "desarrollo"
      "question": "Texto de la pregunta",
      "options": ["Opción A", "Opción B", "Opción C"],  // Para seleccion y completacion
      "correct": "Opción A",  // Para seleccion y completacion
      "pairs": {{"izquierda": ["A", "B"], "derecha": ["1", "2"]}},  // Solo para emparejamiento
      "matches": {{"A": "1", "B": "2"}}  // Solo para emparejamiento
    }},
    // Más preguntas...
  ]
}}

Tipos:
- "seleccion": Múltiple choice, options como array, correct como string.
- "completacion": Fill blank, options como array de posibles respuestas, correct como string.
- "emparejamiento": Matching, pairs con izquierda y derecha arrays, matches como dict.
- "desarrollo": Open-ended, options vacío, correct vacío (evaluado por IA).

Ejemplo completo:
{{
  "questions": [
    {{
      "id": 1,
      "type": "seleccion",
      "question": "¿Cuál es la capital de Francia?",
      "options": ["París", "Londres", "Madrid"],
      "correct": "París"
    }},
    {{
      "id": 2,
      "type": "completacion",
      "question": "La fotosíntesis ocurre en las ____.",
      "options": ["hojas", "raíces", "flores"],
      "correct": "hojas"
    }},
    {{
      "id": 3,
      "type": "emparejamiento",
      "question": "Empareja:",
      "pairs": {{"izquierda": ["Sol", "Agua"], "derecha": ["Energía", "Nutriente"]}},
      "matches": {{"Sol": "Energía", "Agua": "Nutriente"}}
    }},
    {{
      "id": 4,
      "type": "desarrollo",
      "question": "Explica qué es la gravedad.",
      "options": [],
      "correct": ""
    }}
  ]
}}

Texto: {text[:4000]}
"""
    client = get_client()
    resp = client.models.generate_content(model=DEFAULT_MODEL, contents=prompt)
    response_text = _extract_text_from_genai_response(resp)
    cleaned_text = _clean_json_response(response_text)

    try:
        data = json.loads(cleaned_text)
        if "questions" in data and isinstance(data["questions"], list):
            return data["questions"]
        else:
            return f"Error: JSON no tiene la estructura esperada: {response_text}"
    except json.JSONDecodeError:
        return f"Error al parsear JSON: {response_text}"


def evaluate_semantic_response(question, student_answer):
    """2. Evaluación semántica de respuestas de desarrollo."""
    prompt = f"Evalúa semánticamente la respuesta del estudiante a la pregunta. Otorga un puntaje del 0 al 10 y una breve retroalimentación alentadora.\nPregunta: {question}\nRespuesta del estudiante: {student_answer}"
    client = get_client()
    resp = client.models.generate_content(model=DEFAULT_MODEL, contents=prompt)
    return _extract_text_from_genai_response(resp)


def chat_with_sizu_tutor(message, history=None):
    """3. Tutor SIZU restrictivo a temas académicos."""
    
    history_text = ""
    if history:
        for msg in history:
            role = "Estudiante" if msg.get('sender') == 'user' else "Sizu"
            text = msg.get('text', '')
            history_text += f"{role}: {text}\n"

    prompt = f"""Eres SIZU, un tutor académico experto y amigable. Tu objetivo es explicar conceptos complejos de manera clara y completa para que un estudiante de secundaria no se quede con ninguna duda.
SOLO puedes responder preguntas sobre temas educativos (matemáticas, ciencias, lenguaje, historia, etc.).
Si el usuario pregunta algo fuera de tu ámbito, niégate amablemente y reorienta la conversación hacia temas de estudio.

Tus respuestas deben ser detalladas y bien estructuradas. Utiliza formato markdown (como **negritas** para términos clave y listas con guiones - para enumerar puntos) para que la información sea fácil de leer y visualmente agradable.
Evita el uso de emojis.

Historial de conversación:
{history_text}

Mensaje del estudiante: {message}"""
    client = get_client()
    resp = client.models.generate_content(model=DEFAULT_MODEL, contents=prompt)
    return _extract_text_from_genai_response(resp)
