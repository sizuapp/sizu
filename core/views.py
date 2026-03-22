from django.shortcuts import render, redirect
import json
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.messages import get_messages
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
    """Vista principal que maneja la carga del PDF y muestra el quiz."""
    quiz_data = request.session.get('quiz_data')
    error = None

    if request.method == 'POST' and 'pdf_file' in request.FILES:
        form = UploadPDFForm(request.POST, request.FILES)
        if form.is_valid():
            # Generar quiz desde el servicio
            try:
                quiz_data = generate_quiz_from_pdf(request.FILES['pdf_file'])
                request.session['quiz_data'] = quiz_data
            except Exception as e:
                messages.error(request, f"Error generando el quiz: {e}")
        else:
            messages.error(request, "Por favor, selecciona un archivo PDF válido.")
    else:
        form = UploadPDFForm()

    storage = get_messages(request)
    for msg in storage:
        error = msg.message
        break

    return render(request, 'core/dashboard.html', {
        'form': form,
        'quiz': quiz_data,
        'user': request.user,
        'chat_history': [], # Inicializar historial vacío para JS
        'error': error,
    })

@login_required
def submit_quiz(request):
    """Procesa las respuestas del quiz."""
    if request.method == 'POST':
        questions = request.session.get('quiz_data', [])
        results = []
        total_score_increment = 0
        
        for q in questions:
            qid = str(q['id'])
            user_answer = request.POST.get(f"answer_{qid}")
            correct_answer = q.get('correct')
            is_correct = user_answer == correct_answer
            
            points = 10 if is_correct else 0
            total_score_increment += points
            
            results.append({
                'question': q['question'],
                'user_answer': user_answer,
                'correct_answer': correct_answer,
                'correct': is_correct,
                'score': points
            })
        
        # Guardar puntos
        request.user.sizu_points += total_score_increment
        request.user.save()
        
        # Añadir resumen final
        results.append({'total_score': total_score_increment})
        
        # Limpiar quiz de sesión pero mostrar resultados
        if 'quiz_data' in request.session:
            del request.session['quiz_data']
            
        return render(request, 'core/dashboard.html', {
            'results': results,
            'form': UploadPDFForm(),
            'chat_history': []
        })
    return redirect('dashboard')

@login_required
def chat_api(request):
    """API para el chat asíncrono."""
    if request.method == 'POST':
        message = request.POST.get('message')
        if message:
            reply = chat_with_sizu_tutor(message)
            return JsonResponse({'reply': reply})
    return JsonResponse({'error': 'Invalid request'}, status=400)