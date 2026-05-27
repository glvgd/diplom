from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import HollandQuestion, HollandTestResult
from .forms import HollandTestForm

@login_required
def holland_test_start(request):
    previous_results = HollandTestResult.objects.filter(user=request.user)
    context = {
        'previous_results': previous_results,
        'questions_count': HollandQuestion.objects.count(),
    }
    return render(request, 'start.html', context)  # ← start.html

@login_required
def holland_test_take(request):
    questions = HollandQuestion.objects.all().order_by('order')
    
    if request.method == 'POST':
        form = HollandTestForm(questions, request.POST)
        if form.is_valid():
            scores = {'R': 0, 'I': 0, 'A': 0, 'S': 0, 'E': 0, 'C': 0}
            
            for question in questions:
                answer = int(form.cleaned_data[f'question_{question.id}'])
                scores[question.personality_type] += answer
            
            result = HollandTestResult(
                user=request.user,
                realistic_score=scores['R'],
                investigative_score=scores['I'],
                artistic_score=scores['A'],
                social_score=scores['S'],
                enterprising_score=scores['E'],
                conventional_score=scores['C']
            )
            result.save()
            result.calculate_primary_types()
            result.save()
            
            messages.success(request, '🎉 Тест успешно пройден!')
            return redirect('holland_test:result', result_id=result.id)
    else:
        form = HollandTestForm(questions)
    
    context = {
        'form': form,
        'total_questions': questions.count(),
    }
    return render(request, 'take.html', context)  # ← take.html

@login_required
def holland_test_result(request, result_id):
    result = get_object_or_404(HollandTestResult, id=result_id, user=request.user)
    
    chart_data = {
        'labels': ['Реалистичный', 'Интеллектуальный', 'Артистичный', 
                   'Социальный', 'Предприимчивый', 'Конвенциональный'],
        'scores': [
            result.realistic_score,
            result.investigative_score,
            result.artistic_score,
            result.social_score,
            result.enterprising_score,
            result.conventional_score
        ],
    }
    
    context = {
        'result': result,
        'chart_data': chart_data,
        'recommended_professions': result.get_recommended_professions(),
    }
    return render(request, 'result.html', context)  # ← result.html

@login_required
def holland_test_history(request):
    results = HollandTestResult.objects.filter(user=request.user)
    return render(request, 'history.html', {'results': results})  # ← history.html