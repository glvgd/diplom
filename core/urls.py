from django.urls import path
from . import views

app_name = 'core'  

urlpatterns = [
    path('', views.dashboard, name='home'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('testing/', views.testing, name='testing'),  # существующие тесты/задания
    path('api/tasks/<int:subject_id>/', views.get_tasks, name='get_tasks'),
    path('api/check/', views.check_answer, name='check_answer'),
    path('api/chat/', views.chat_api, name='chat_api'),
    path('professions/', views.professions, name='professions'),
    path('profession/<int:profession_id>/', views.profession_detail, name='profession_detail'),
    path('profile/', views.profile, name='profile'),
    path('chat/', views.chat, name='chat'),
]