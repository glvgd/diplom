from django.db import models
from django.contrib.auth.models import User

class HollandQuestion(models.Model):
    TYPE_CHOICES = [
        ('R', 'Реалистичный'),
        ('I', 'Интеллектуальный'),
        ('A', 'Артистичный'),
        ('S', 'Социальный'),
        ('E', 'Предприимчивый'),
        ('C', 'Конвенциональный'),
    ]
    text = models.CharField(max_length=500)
    order = models.IntegerField(unique=True)
    personality_type = models.CharField(max_length=1, choices=TYPE_CHOICES)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"Вопрос {self.order}: {self.text[:50]}"

class HollandTestResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='holland_results')
    date_taken = models.DateTimeField(auto_now_add=True)
    realistic_score = models.IntegerField(default=0)
    investigative_score = models.IntegerField(default=0)
    artistic_score = models.IntegerField(default=0)
    social_score = models.IntegerField(default=0)
    enterprising_score = models.IntegerField(default=0)
    conventional_score = models.IntegerField(default=0)
    primary_type = models.CharField(max_length=1, blank=True, choices=HollandQuestion.TYPE_CHOICES)
    secondary_type = models.CharField(max_length=1, blank=True, choices=HollandQuestion.TYPE_CHOICES)

    def calculate_primary_types(self):
        scores = {
            'R': self.realistic_score,
            'I': self.investigative_score,
            'A': self.artistic_score,
            'S': self.social_score,
            'E': self.enterprising_score,
            'C': self.conventional_score,
        }
        sorted_types = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        self.primary_type = sorted_types[0][0]
        self.secondary_type = sorted_types[1][0]

    def get_primary_type_name(self):
        return dict(HollandQuestion.TYPE_CHOICES).get(self.primary_type, '')

    def get_secondary_type_name(self):
        return dict(HollandQuestion.TYPE_CHOICES).get(self.secondary_type, '')

    def get_recommended_professions(self):
        professions = {
            'R': ['Инженер', 'Строитель', 'Механик', 'Программист', 'Электрик'],
            'I': ['Ученый', 'Исследователь', 'Аналитик', 'Врач', 'Химик'],
            'A': ['Дизайнер', 'Художник', 'Музыкант', 'Архитектор', 'Писатель'],
            'S': ['Учитель', 'Психолог', 'Врач', 'Социальный работник', 'HR-специалист'],
            'E': ['Менеджер', 'Предприниматель', 'Юрист', 'Маркетолог', 'Продавец'],
            'C': ['Бухгалтер', 'Администратор', 'Библиотекарь', 'Оператор', 'Секретарь'],
        }
        return {
            'primary': professions.get(self.primary_type, [])[:5],
            'secondary': professions.get(self.secondary_type, [])[:3]
        }

    class Meta:
        ordering = ['-date_taken']