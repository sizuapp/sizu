from django.shortcuts import render, redirect
import json
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .forms import CustomUserCreationForm, UploadPDFForm
from .services import generate_quiz_from_pdf, chat_with_sizu_tutor

def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

@login_required
def dashboard(request):
    """Muestra el dashboard y el formulario para generar nuevos quices."""
    if request.method == 'POST':
        form = UploadPDFForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                # 1. Llamamos al servicio de IA con el archivo en memoria
                questions = generate_quiz_from_pdf(request.FILES['pdf_file'])
                
                # 2. Si obtenemos preguntas válidas, las guardamos en la sesión
                if isinstance(questions, list):
                    request.session['quiz_data'] = questions
                    # Usamos 'quiz' en lugar de 'questions' para coincidir con dashboard.html
                    return render(request, 'core/dashboard.html', {'form': form, 'quiz': questions, 'chat_history': []})
                else:
                    # Si questions es un string, es un mensaje de error del servicio
                    error_msg = questions if isinstance(questions, str) else "Error generando el quiz."
                    messages.error(request, error_msg)
            except Exception as e:
                print(f"Error inesperado en dashboard: {e}")
                messages.error(request, "Hubo un problema de conexión o el archivo es muy pesado. Intenta de nuevo.")
    else:
        form = UploadPDFForm()
    
    # Pasamos chat_history vacío para evitar errores en Alpine.js
    return render(request, 'core/dashboard.html', {'form': form, 'chat_history': []})

@login_required
def submit_quiz(request):
    """Procesa las respuestas del quiz, calcula el puntaje y actualiza al usuario."""
    if request.method == 'POST':
        # Recuperamos las preguntas originales de la sesión
        questions = request.session.get('quiz_data', [])
        score_increment = 0
        results = []
        
        for q in questions:
            question_id = str(q.get('id'))
            # El name del input en HTML es "answer_ID" según tu dashboard.html
            user_answer = request.POST.get(f'answer_{question_id}')
            correct_answer = q.get('correct')
            
            is_correct = user_answer == correct_answer
            
            if user_answer == correct_answer:
                score_increment += 10 # 10 puntos por respuesta correcta

            results.append({
                'question': q.get('question'),
                'user_answer': user_answer,
                'correct_answer': correct_answer,
                'correct': is_correct,
                'score': 10 if is_correct else 0
            })

        # Agregar resumen final a los resultados
        results.append({'total_score': score_increment})

        # Actualizamos los puntos del usuario en la Base de Datos
        request.user.sizu_points += score_increment
        request.user.save()
        
        messages.success(request, f"¡Quiz completado! Has ganado {score_increment} puntos.")

        # Limpiamos la sesión y volvemos al dashboard
        if 'quiz_data' in request.session:
            del request.session['quiz_data']
            
        # Renderizamos dashboard con los resultados y el historial de chat vacío
        return render(request, 'core/dashboard.html', {
            'form': UploadPDFForm(),
            'results': results,
            'chat_history': []
        })
    
    return redirect('dashboard')

@login_required
def chat_api(request):
    """API para manejar el chat con el tutor SIZU."""
    if request.method == 'POST':
        message = request.POST.get('message')
        if not message:
            return JsonResponse({'error': 'Mensaje vacío'}, status=400)
        
        # Llamamos al servicio de IA
        reply = chat_with_sizu_tutor(message)
        return JsonResponse({'reply': reply})
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)