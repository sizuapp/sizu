import os
from dotenv import load_dotenv

try:
    from google import genai
except ImportError:
    genai = None

# Cargar variables de entorno
load_dotenv()

if not genai:
    print('No está instalado google-genai; installalo con pip install google-genai')
    raise SystemExit(1)

# Configurar API Key
api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    print('No se encontró GEMINI_API_KEY en .env')
    raise SystemExit(1)

client = genai.Client()

try:
    model_name = os.getenv('GEMINI_MODEL', 'gemini-2.5')
    response = client.responses.create(
        model=model_name,
        input=[
            {
                'role': 'user',
                'content': [
                    {'type': 'text', 'text': 'Hola, ¿puedes confirmar que la API de Gemini está funcionando?'}
                ]
            }
        ],
        max_output_tokens=150,
    )
    output = response.output[0]['content'][0].get('text', '') if response.output else ''
    print('Respuesta de Gemini:')
    print(output)
    print('\nLa API de Gemini está conectada correctamente.')
except Exception as e:
    print(f'Error al conectar con Gemini API: {str(e)}')
