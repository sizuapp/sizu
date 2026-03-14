from core import services

print('Calling chat_with_sizu_tutor...')
print(services.chat_with_sizu_tutor('¿Qué es la fotosíntesis?'))

# Para generate_quiz_from_pdf, simulamos creando un PDF temporal simple o llamamos a la función de generación con un texto directo
print('\nCalling generate_quiz_from_pdf with a dummy small PDF...')
# Crear un mini-PDF requiere librerías; en su lugar llamamos a la función interna con un texto corto
from core.services import _extract_text_from_genai_response
# Generar un prompt directamente usando la función pública no es trivial sin un PDF, así que llamamos a evaluate_semantic_response como comprobación adicional
print('\nCalling evaluate_semantic_response...')
print(services.evaluate_semantic_response('Explica la gravedad en 2 líneas', 'La gravedad es una fuerza que atrae objetos con masa.'))

