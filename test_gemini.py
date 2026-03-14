import os
from dotenv import load_dotenv
import google.genai as genai

# Cargar variables de entorno
load_dotenv()

# Configurar API Key
api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    print("Error: GEMINI_API_KEY no encontrada en .env o en las variables de entorno")
    exit(1)

client = genai.Client(api_key=api_key)

# Probar la conexión
try:
    response = client.models.generate_content(model='gemini-2.0-flash-exp', contents="Hola, ¿puedes confirmar que la API de Gemini está funcionando?")
    print("Respuesta de Gemini:")
    print(response.text)
    print("\nLa API de Gemini está conectada correctamente.")
except Exception as e:
    print(f"Error al conectar con Gemini API: {str(e)}")
