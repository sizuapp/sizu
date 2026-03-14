import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('GEMINI_API_KEY')
print('GEMINI_API_KEY present:', bool(api_key))

try:
    import google.genai as genai
    client = genai.Client(api_key=api_key)
    print('Imported google.genai, client created')
except Exception as e:
    print('Import or client creation failed:', repr(e))
    raise

# Try several possible list methods
try:
    print('Trying client.list_models()...')
    models = client.list_models()
    print('client.list_models() =>', type(models))
    for m in models:
        print('MODEL:', getattr(m, 'name', m))
except Exception as e:
    print('client.list_models() failed:', repr(e))

try:
    print('Trying client.models.list()...')
    models = client.models.list()
    print('client.models.list() =>', type(models))
    for m in models:
        print('MODEL:', getattr(m, 'name', m))
except Exception as e:
    print('client.models.list() failed:', repr(e))

try:
    print('Trying client.models.list_models()...')
    models = client.models.list_models()
    print('client.models.list_models() =>', type(models))
    for m in models:
        print('MODEL:', getattr(m, 'name', m))
except Exception as e:
    print('client.models.list_models() failed:', repr(e))

print('Done')

