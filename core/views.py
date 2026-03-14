from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .forms import CustomUserCreationForm
from .services import chat_with_sizu_tutor, generate_quiz_from_pdf, evaluate_semantic_response
import os
from django.conf import settings
from pathlib import Path

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
    quiz = None
    results = None
    error_message = None

    if request.method == 'POST':
        if request.FILES.get('pdf_file'):
            pdf_file = request.FILES['pdf_file']
            # Guardar el archivo temporalmente
            temp_path = Path(settings.MEDIA_ROOT) / pdf_file.name
            os.makedirs(str(temp_path.parent), exist_ok=True)
            with open(str(temp_path), 'wb') as f:
                for chunk in pdf_file.chunks():
                    f.write(chunk)

            # Generar el quiz
            try:
                quiz_data = generate_quiz_from_pdf(str(temp_path))
                if isinstance(quiz_data, list):
                    quiz = quiz_data
                    request.session['current_quiz'] = quiz
                else:
                    error_message = quiz_data  # Mensaje de error devuelto por el servicio
                # Limpiar el archivo temporal
                os.remove(str(temp_path))
            except Exception as e:
                error_message = f"Error al generar el quiz: {str(e)}"

            # Ganar puntos (solo si no hubo error, opcional, pero lo dejo como estaba)
            if not error_message:
                request.user.sizu_points += 50
                request.user.save()

        elif 'submit_answers' in request.POST:
            # Evaluar respuestas
            quiz = request.session.get('current_quiz')
            if quiz:
                results = []
                total_score = 0
                for q in quiz:
                    qid = q['id']
                    user_answer = request.POST.get(f'answer_{qid}')
                    if q['type'] == 'seleccion':
                        correct = user_answer == q['correct']
                        score = 20 if correct else 0
                        total_score += score
                        results.append({
                            'question': q['question'],
                            'user_answer': user_answer,
                            'correct_answer': q['correct'],
                            'correct': correct,
                            'score': score
                        })
                    elif q['type'] == 'completacion':
                        correct = user_answer.lower().strip() == q['correct'].lower().strip()
                        score = 20 if correct else 0
                        total_score += score
                        results.append({
                            'question': q['question'],
                            'user_answer': user_answer,
                            'correct_answer': q['correct'],
                            'correct': correct,
                            'score': score
                        })
                    elif q['type'] == 'emparejamiento':
                        # Build user_matching dict from POST
                        user_matching = {}
                        for left in q['pairs']['izquierda']:
                            match_value = request.POST.get(f'matching_{qid}_{left}')
                            if match_value:
                                user_matching[left] = match_value
                        correct = user_matching == q['matches']
                        score = 20 if correct else 0
                        total_score += score
                        results.append({
                            'question': q['question'],
                            'user_answer': user_matching,
                            'correct_answer': q['matches'],
                            'correct': correct,
                            'score': score
                        })
                    elif q['type'] == 'desarrollo':
                        # Use AI to evaluate
                        evaluation = evaluate_semantic_response(q['question'], user_answer)
                        # Parse score from evaluation, assume format "Puntaje: X/10 ..."
                        try:
                            score_line = evaluation.split('Puntaje:')[1].split('/')[0].strip()
                            score = int(score_line) * 2  # 0-20
                        except:
                            score = 10  # Default
                        total_score += score
                        results.append({
                            'question': q['question'],
                            'user_answer': user_answer,
                            'evaluation': evaluation,
                            'score': score
                        })
                # Add total score
                results.append({'total_score': total_score})
                request.session['quiz_results'] = results
                # Award points
                request.user.sizu_points += total_score
                request.user.save()

    # Obtener quiz de la sesión si existe
    if 'current_quiz' in request.session and not quiz and not error_message:
        quiz = request.session['current_quiz']

    # Obtener resultados si existen
    if 'quiz_results' in request.session:
        results = request.session['quiz_results']

    # Obtener historial de chat de la sesión
    chat_history = request.session.get('chat_history', [])

    return render(request, 'core/dashboard.html', {'quiz': quiz, 'results': results, 'error': error_message, 'chat_history': chat_history})

@login_required
def tutor_chat_api(request):
    if request.method == 'POST':
        user_message = request.POST.get('message', '')
        if user_message:
            try:
                # Recuperar historial
                history = request.session.get('chat_history', [])
                
                bot_reply = chat_with_sizu_tutor(user_message, history)
                
                # Actualizar historial y guardar en sesión (máximo 20 mensajes)
                history.append({'sender': 'user', 'text': user_message})
                history.append({'sender': 'bot', 'text': bot_reply})
                request.session['chat_history'] = history[-20:]
                
                return JsonResponse({'reply': bot_reply})
            except Exception as e:
                return JsonResponse({'reply': f"Error en el tutor: {str(e)}"}, status=500)
    return JsonResponse({'error': 'Método no permitido'}, status=400)

@login_required
def evaluate_development(request):
    """Endpoint para evaluar respuestas de desarrollo."""
    if request.method == 'POST':
        question = request.POST.get('question')
        answer = request.POST.get('answer')
        if question and answer:
            evaluation = evaluate_semantic_response(question, answer)
            return JsonResponse({'evaluation': evaluation})
    return JsonResponse({'error': 'Datos inválidos'}, status=400)