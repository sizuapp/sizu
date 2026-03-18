import os
from dotenv import load_dotenv
import google.generativeai as genai

# Cargar variables de entorno
load_dotenv()

# Configurar API Key
api_key = os.getenv('GEMINI_API_KEY')
genai.configure(api_key=api_key)

# Probar la conexión
try:
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content("Hola, ¿puedes confirmar que la API de Gemini está funcionando?")
    print("Respuesta de Gemini:")
    print(response.text)
    print("\nLa API de Gemini está conectada correctamente.")
except Exception as e:
    print(f"Error al conectar con Gemini API: {str(e)}")
