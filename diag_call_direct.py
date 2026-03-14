import traceback

print('DIAG START')
try:
    from core import services
    print('Imported core.services')
    print('API_KEY present in module:', hasattr(services, 'API_KEY'))
    print('DEFAULT_MODEL:', getattr(services, 'DEFAULT_MODEL', None))
except Exception as e:
    print('Import core.services failed:', e)
    traceback.print_exc()
    raise

try:
    print('\nCalling chat_with_sizu_tutor...')
    res = services.chat_with_sizu_tutor('¿Qué es la fotosíntesis?')
    print('chat result repr:', repr(res))
    print('chat result type:', type(res))
except Exception as e:
    print('chat_with_sizu_tutor failed:', e)
    traceback.print_exc()

try:
    print('\nCalling evaluate_semantic_response...')
    res2 = services.evaluate_semantic_response('Explica la gravedad en 2 líneas', 'La gravedad es una fuerza que atrae objetos con masa.')
    print('evaluate result repr:', repr(res2))
    print('evaluate result type:', type(res2))
except Exception as e:
    print('evaluate_semantic_response failed:', e)
    traceback.print_exc()

print('DIAG END')

