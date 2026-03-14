import os, traceback
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv('GEMINI_API_KEY')
print('API_KEY present:', bool(api_key))
try:
    import google.genai as genai
    client = genai.Client(api_key=api_key)
    model = 'models/gemini-2.5-flash'
    prompt = 'Dime en una línea qué es la fotosíntesis.'
    print('Calling generate_content...')
    resp = client.models.generate_content(model=model, contents=prompt)
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

