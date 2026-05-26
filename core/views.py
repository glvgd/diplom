from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from .models import Subject, Task, Profession, UserProgress, UserProfile, ProfessionRequirement, ChatMessage
from .utils import recommend_professions
from .chat_bot import LocalChatBot
import json

chat_bot = LocalChatBot()

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user:
            login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'login.html', {'error': 'Неверное имя пользователя или пароль'})
    
    return render(request, 'login.html')

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        grade = request.POST.get('grade', 10)
        
        if User.objects.filter(username=username).exists():
            return render(request, 'register.html', {'error': 'Пользователь уже существует'})
        
        user = User.objects.create_user(username=username, email=email, password=password)
        UserProfile.objects.create(user=user, grade=grade)
        
        login(request, user)
        return redirect('dashboard')
    
    return render(request, 'register.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard(request):
    total_solved = UserProgress.objects.filter(user=request.user).count()
    correct_solved = UserProgress.objects.filter(user=request.user, is_correct=True).count()
    accuracy = round(correct_solved / total_solved * 100, 1) if total_solved > 0 else 0
    
    subject_stats = []
    for subject in Subject.objects.all():
        solved = UserProgress.objects.filter(user=request.user, task__subject=subject).count()
        correct = UserProgress.objects.filter(user=request.user, task__subject=subject, is_correct=True).count()
        if solved > 0:
            subject_stats.append({
                'name': subject.name,
                'icon': subject.icon,
                'color': subject.color,
                'solved': solved,
                'correct': correct,
                'accuracy': round(correct / solved * 100, 1)
            })
    
    recommendations = recommend_professions(request.user)
    
    context = {
        'total_solved': total_solved,
        'accuracy': accuracy,
        'subject_stats': subject_stats,
        'recommendations': recommendations,
    }
    return render(request, 'dashboard.html', context)

@login_required
def testing(request):
    subjects = Subject.objects.all()
    return render(request, 'testing.html', {'subjects': subjects})

@login_required
def get_tasks(request, subject_id):
    solved_tasks = UserProgress.objects.filter(user=request.user).values_list('task_id', flat=True)
    tasks = Task.objects.filter(subject_id=subject_id).exclude(id__in=solved_tasks)[:10]
    
    tasks_data = [{
        'id': task.id,
        'text': task.text,
    } for task in tasks]
    
    return JsonResponse({'tasks': tasks_data})

@csrf_exempt
@login_required
@require_http_methods(["POST"])
def check_answer(request):
    data = json.loads(request.body)
    task_id = data.get('task_id')
    answer = data.get('answer', '').strip()
    
    task = get_object_or_404(Task, id=task_id)
    is_correct = answer.lower() == task.correct_answer.lower()
    
    UserProgress.objects.create(
        user=request.user,
        task=task,
        is_correct=is_correct
    )
    
    return JsonResponse({
        'correct': is_correct,
        'explanation': task.explanation if not is_correct else '',
        'correct_answer': task.correct_answer if not is_correct else ''
    })

@login_required
def professions(request):
    professions_list = Profession.objects.all()
    return render(request, 'professions.html', {'professions': professions_list})

@login_required
def profession_detail(request, profession_id):
    profession = get_object_or_404(Profession, id=profession_id)
    requirements = ProfessionRequirement.objects.filter(profession=profession).select_related('subject')
    universities = profession.universities.split(',') if profession.universities else []
    
    return render(request, 'profession_detail.html', {
        'profession': profession,
        'requirements': requirements,
        'universities': universities
    })

@login_required
def profile(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    history = UserProgress.objects.filter(user=request.user).select_related('task', 'task__subject').order_by('-solved_at')[:50]
    
    if request.method == 'POST':
        profile.school = request.POST.get('school', '')
        profile.grade = request.POST.get('grade', 10)
        profile.telegram = request.POST.get('telegram', '')
        profile.save()
        return redirect('profile')
    
    return render(request, 'profile.html', {
        'profile': profile,
        'history': history
    })

@login_required
def chat(request):
    return render(request, 'chat.html')

@csrf_exempt
@login_required
def chat_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            message = data.get('message', '')
            response = chat_bot.get_response(message, request.user)
            return JsonResponse({'response': response})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Method not allowed'}, status=405)