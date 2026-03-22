import os
from dotenv import load_dotenv
import google.generativeai as genai
from PyPDF2 import PdfReader
import json
import re

# Cargar variables de entorno desde .env (si existe)
load_dotenv()

# Configurar la API key al inicio para todo el módulo
api_key = os.getenv('GEMINI_API_KEY')
genai.configure(api_key=api_key)

# Modelo por defecto (ajustable)
DEFAULT_MODEL = 'models/gemini-2.5-flash'

def _extract_text_from_genai_response(resp):
    # El manejo de la respuesta puede simplificarse con el nuevo SDK
    try:
        return resp.text
    except Exception as e:
        print(f"Error extrayendo texto de la respuesta: {e}")
        # Como fallback, intentar acceder a partes si 'text' falla
        try:
            return "".join([part.text for part in resp.parts])
        except Exception:
            return f"Error: Respuesta no procesable: {resp}"


def _clean_json_response(text):
    """Limpia el texto de respuesta para extraer JSON válido."""
    text = re.sub(r'^```json\s*', '', text, flags=re.MULTILINE)
    text = re.sub(r'^```\s*', '', text, flags=re.MULTILINE)
    text = re.sub(r'\s*```$', '', text, flags=re.MULTILINE)
    return text.strip()

def extract_text_from_pdf(pdf_file):
    """Extrae texto de un archivo PDF de manera segura."""
    try:
        # Asegurar que el puntero del archivo esté al inicio
        if hasattr(pdf_file, 'seek'):
            pdf_file.seek(0)
        
        reader = PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text() or ""
            text += page_text + "\n"
        return text
    except Exception as e:
        print(f"Error leyendo PDF: {e}")
        return ""


def generate_quiz_from_pdf(pdf_file):
    """Genera un quiz interactivo desde el PDF con esquema JSON estricto."""
    text = extract_text_from_pdf(pdf_file)
    if not text.strip():
        return "Error: No se pudo extraer texto. El PDF podría ser una imagen o estar dañado."

    prompt = f"""
Basado en este texto, genera un quiz interactivo para estudiantes de 12-15 años, con 5 preguntas variadas.
Usa lenguaje simple y educativo. Evita el uso de emojis.

Debes devolver EXACTAMENTE un JSON válido con esta estructura:
{{
  "questions": [
    {{
      "id": 1,
      "type": "seleccion",
      "question": "Texto de la pregunta",
      "options": ["Opción A", "Opción B", "Opción C"],
      "correct": "Opción A"
    }}
  ]
}}

Texto: {text[:4000]}
"""
    try:
        model = genai.GenerativeModel(DEFAULT_MODEL)
        resp = model.generate_content(prompt)
        response_text = _extract_text_from_genai_response(resp)
        cleaned_text = _clean_json_response(response_text)
        data = json.loads(cleaned_text)
        if "questions" in data and isinstance(data["questions"], list):
            return data["questions"]
        else:
            return f"Error: JSON no tiene la estructura esperada: {response_text}"
    except json.JSONDecodeError:
        return f"Error al parsear JSON de la respuesta: {response_text}"
    except Exception as e:
        return f"Error inesperado al generar quiz: {e}"


def evaluate_semantic_response(question, student_answer):
    """2. Evaluación semántica de respuestas de desarrollo."""
    prompt = f"Evalúa semánticamente la respuesta del estudiante a la pregunta. Otorga un puntaje del 0 al 10 y una breve retroalimentación alentadora.\nPregunta: {question}\nRespuesta del estudiante: {student_answer}"
    try:
        model = genai.GenerativeModel(DEFAULT_MODEL)
        resp = model.generate_content(prompt)
        return _extract_text_from_genai_response(resp)
    except Exception as e:
        return f"Error inesperado al evaluar: {e}"


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
    try:
        model = genai.GenerativeModel(DEFAULT_MODEL)
        resp = model.generate_content(prompt)
        return _extract_text_from_genai_response(resp)
    except Exception as e:
        return f"Error inesperado en el tutor: {e}"

if __name__ == "__main__":
    # Listar modelos disponibles (Adaptado para usar el cliente existente google.genai)
    print("Modelos disponibles:")
    for model in genai.list_models():  # Changed to genai.list_models() for correct listing
        print(model.name)
# Logic removed to restore initial state
