import os, traceback
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv('GEMINI_API_KEY')
print('API_KEY present:', bool(api_key))
try:
    import google.generativeai as genai
    genai.configure(api_key=api_key)
    model = 'gemini-pro'
    prompt = 'Dime en una línea qué es la fotosíntesis.'
    print('Calling generate_content...')
    gemini_model = genai.GenerativeModel(model)
    resp = gemini_model.generate_content(prompt)
    print('RESP REPR:', repr(resp))
    print('RESP DIR:', dir(resp))
    # print attributes
    for attr in ['text','candidates','result','output']:
        if hasattr(resp, attr):
            print(f'ATTR {attr}:', getattr(resp, attr))
    # If candidates, inspect
    try:
        if hasattr(resp, 'candidates') and resp.candidates:
            print('CANDIDATE[0] dir:', dir(resp.candidates[0]))
            for a in ['content','text','output','message']:
                if hasattr(resp.candidates[0], a):
                    print(f'candidate.{a} =', getattr(resp.candidates[0], a))
    except Exception as e:
        print('While inspecting candidates:', e)
except Exception as e:
    print('Exception:', e)
    traceback.print_exc()
print('DONE')
