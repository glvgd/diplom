from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from .models import Subject, Task, Profession, ProfessionRequirement, UserProgress, UserProfile, ChatMessage

class SubjectAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'exam_type', 'icon', 'color', 'tasks_count']
    list_filter = ['exam_type']
    search_fields = ['name']
    list_editable = ['icon', 'color']
    list_per_page = 20
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'exam_type', 'icon', 'color')
        }),
    )
    
    def tasks_count(self, obj):
        return obj.task_set.count()
    tasks_count.short_description = 'Кол-во заданий'

class TaskAdmin(admin.ModelAdmin):
    list_display = ['id', 'subject', 'text_preview', 'correct_answer', 'exam_year', 'points']
    list_filter = ['subject', 'exam_year']
    search_fields = ['text', 'correct_answer']
    list_editable = ['points']
    list_per_page = 20
    
    fieldsets = (
        ('Задание', {
            'fields': ('subject', 'text', 'correct_answer', 'explanation')
        }),
        ('Дополнительно', {
            'fields': ('exam_year', 'points')
        }),
    )
    
    def text_preview(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    text_preview.short_description = 'Текст задания'

class ProfessionRequirementInline(admin.TabularInline):
    model = ProfessionRequirement
    extra = 1
    autocomplete_fields = ['subject']
    fields = ['subject', 'importance']

class ProfessionAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'salary_range', 'demand_level_display', 'requirements_count']
    list_filter = ['demand_level']
    search_fields = ['name', 'description']
    list_per_page = 20
    inlines = [ProfessionRequirementInline]
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'description', 'requirements')
        }),
        ('Зарплата', {
            'fields': ('salary_min', 'salary_max')
        }),
        ('Востребованность', {
            'fields': ('demand_level',)
        }),
        ('Мультимедиа', {
            'fields': ('image_url', 'video_url'),
            'classes': ('collapse',)
        }),
        ('Образование', {
            'fields': ('universities',),
        }),
    )
    
    def salary_range(self, obj):
        return f"{obj.salary_min:,} - {obj.salary_max:,} ₽".replace(',', ' ')
    salary_range.short_description = 'Зарплата'
    
    def demand_level_display(self, obj):
        stars = '⭐' * obj.demand_level + '☆' * (5 - obj.demand_level)
        return format_html('<span style="font-size:16px">{}</span>', stars)
    demand_level_display.short_description = 'Востребованность'
    
    def requirements_count(self, obj):
        return obj.professionrequirement_set.count()
    requirements_count.short_description = 'Требований'

class UserProgressAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'task_info', 'is_correct_icon', 'solved_at']
    list_filter = ['is_correct', 'solved_at', 'task__subject']
    search_fields = ['user__username', 'task__text']
    readonly_fields = ['solved_at']
    date_hierarchy = 'solved_at'
    list_per_page = 20
    
    def task_info(self, obj):
        return f"{obj.task.subject.name}: {obj.task.text[:30]}..."
    task_info.short_description = 'Задание'
    
    def is_correct_icon(self, obj):
        return '✅' if obj.is_correct else '❌'
    is_correct_icon.short_description = 'Результат'
    is_correct_icon.admin_order_field = 'is_correct'

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Профиль'
    fields = ['grade', 'school', 'avatar', 'telegram']

class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active', 'date_joined', 'solved_count']
    list_filter = ['is_staff', 'is_superuser', 'is_active', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    list_per_page = 20
    inlines = [UserProfileInline]
    
    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительная информация', {
            'fields': ()
        }),
    )
    
    def solved_count(self, obj):
        return obj.userprogress_set.count()
    solved_count.short_description = 'Решено заданий'

class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'message_preview', 'is_bot', 'created_at']
    list_filter = ['is_bot', 'created_at']
    search_fields = ['user__username', 'message']
    readonly_fields = ['created_at']
    list_per_page = 20
    
    def message_preview(self, obj):
        return obj.message[:50] + '...' if len(obj.message) > 50 else obj.message
    message_preview.short_description = 'Сообщение'

# Регистрируем все модели в админке
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
admin.site.register(Subject, SubjectAdmin)
admin.site.register(Task, TaskAdmin)
admin.site.register(Profession, ProfessionAdmin)
admin.site.register(UserProgress, UserProgressAdmin)
admin.site.register(ChatMessage, ChatMessageAdmin)