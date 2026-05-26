from django.db import models
from django.contrib.auth.models import User

class Subject(models.Model):
    EXAM_TYPES = [
        ('OGE', 'ОГЭ'),
        ('EGE', 'ЕГЭ'),
    ]
    name = models.CharField(max_length=50, verbose_name='Название')
    exam_type = models.CharField(max_length=3, choices=EXAM_TYPES, verbose_name='Тип экзамена')
    icon = models.CharField(max_length=50, default='📚', verbose_name='Иконка')
    color = models.CharField(max_length=20, default='#667eea', verbose_name='Цвет')
    
    def __str__(self):
        return f"{self.name} ({self.get_exam_type_display()})"
    
    class Meta:
        verbose_name = 'Предмет'
        verbose_name_plural = 'Предметы'

class Task(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, verbose_name='Предмет')
    text = models.TextField(verbose_name='Текст задания')
    correct_answer = models.CharField(max_length=20, verbose_name='Правильный ответ')
    explanation = models.TextField(verbose_name='Объяснение', blank=True)
    exam_year = models.IntegerField(default=2026, verbose_name='Год экзамена')
    points = models.IntegerField(default=1, verbose_name='Баллы')
    
    def __str__(self):
        return f"{self.subject.name} - Задание {self.id}"
    
    class Meta:
        verbose_name = 'Задание'
        verbose_name_plural = 'Задания'

class Profession(models.Model):
    DEMAND_LEVELS = [
        (1, 'Низкий спрос'),
        (2, 'Ниже среднего'),
        (3, 'Средний спрос'),
        (4, 'Выше среднего'),
        (5, 'Высокий спрос'),
    ]
    
    name = models.CharField(max_length=100, verbose_name='Название профессии')
    description = models.TextField(verbose_name='Описание')
    requirements = models.TextField(verbose_name='Требования', blank=True)
    salary_min = models.IntegerField(verbose_name='Мин. зарплата')
    salary_max = models.IntegerField(verbose_name='Макс. зарплата')
    demand_level = models.IntegerField(choices=DEMAND_LEVELS, default=3, verbose_name='Востребованность')
    required_subjects = models.ManyToManyField(Subject, through='ProfessionRequirement', verbose_name='Требуемые предметы')
    image_url = models.URLField(blank=True, verbose_name='Изображение')
    video_url = models.URLField(blank=True, verbose_name='Видео профессии')
    universities = models.TextField(verbose_name='Вузы', blank=True, help_text='Список вузов через запятую')
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Профессия'
        verbose_name_plural = 'Профессии'

class ProfessionRequirement(models.Model):
    profession = models.ForeignKey(Profession, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    importance = models.FloatField(default=1.0, verbose_name='Важность (0-2)')
    
    class Meta:
        unique_together = ['profession', 'subject']

class UserProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    task = models.ForeignKey(Task, on_delete=models.CASCADE, verbose_name='Задание')
    is_correct = models.BooleanField(default=False, verbose_name='Правильно')
    solved_at = models.DateTimeField(auto_now_add=True, verbose_name='Время решения')
    
    class Meta:
        unique_together = ['user', 'task']
        verbose_name = 'Прогресс пользователя'
        verbose_name_plural = 'Прогресс пользователей'

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    grade = models.IntegerField(choices=[(i, f'{i} класс') for i in range(9, 12)], default=10, verbose_name='Класс')
    school = models.CharField(max_length=200, blank=True, verbose_name='Школа')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name='Аватар')
    telegram = models.CharField(max_length=100, blank=True, verbose_name='Telegram')
    
    def __str__(self):
        return f"{self.user.username} - {self.grade} класс"
    
    class Meta:
        verbose_name = 'Профиль пользователя'
        verbose_name_plural = 'Профили пользователей'

class ChatMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    message = models.TextField(verbose_name='Сообщение')
    is_bot = models.BooleanField(default=False, verbose_name='От бота')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Время создания')
    
    class Meta:
        verbose_name = 'Сообщение чата'
        verbose_name_plural = 'Сообщения чата'
        ordering = ['created_at']