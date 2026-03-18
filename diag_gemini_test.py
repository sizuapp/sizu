import os
from dotenv import load_dotenv

print('STEP 1: start script')

load_dotenv()
api_key = os.getenv('GEMINI_API_KEY')
print('STEP 2: GEMINI_API_KEY present:', bool(api_key))

try:
    import google.generativeai as genai
    print('STEP 3: imported google.generativeai, version attribute:', getattr(genai, '__version__', 'unknown'))
except Exception as e:
    print('STEP 3: import google.genai failed:', repr(e))

try:
    genai.configure(api_key=api_key)
    print('STEP 4: genai configured')
except Exception as e:
    print('STEP 4: client creation failed:', repr(e))

try:
    print('STEP 5: calling model.generate_content...')
    model = genai.GenerativeModel('gemini-pro')
    resp = model.generate_content('Ping desde diag test. ¿Responde?')
    print('STEP 6: response received. type:', type(resp))
    # Try to print textual response
    if hasattr(resp, 'text'):
        print('RESPONSE TEXT:', resp.text)
    else:
        print('RESPONSE RAW:', resp)
except Exception as e:
    print('STEP 5/6: API call failed:', repr(e))

print('STEP 7: end script')
