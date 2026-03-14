import os
from dotenv import load_dotenv

print('STEP 1: start script')

load_dotenv()
api_key = os.getenv('GEMINI_API_KEY')
print('STEP 2: GEMINI_API_KEY=', api_key)

try:
    import google.genai as genai
    print('STEP 3: imported google.genai, version attribute:', getattr(genai, '__version__', 'unknown'))
except Exception as e:
    print('STEP 3: import google.genai failed:', repr(e))

try:
    client = genai.Client(api_key=api_key)
    print('STEP 4: client created')
except Exception as e:
    print('STEP 4: client creation failed:', repr(e))

try:
    print('STEP 5: calling models.generate_content...')
    resp = client.models.generate_content(model='gemini-2.0-flash-exp', contents='Ping desde diag test. ¿Responde?')
    print('STEP 6: response received. type:', type(resp))
    # Try to print textual response
    if hasattr(resp, 'text'):
        print('RESPONSE TEXT:', resp.text)
    else:
        print('RESPONSE RAW:', resp)
except Exception as e:
    print('STEP 5/6: API call failed:', repr(e))

print('STEP 7: end script')

