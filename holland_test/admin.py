from django.contrib import admin
from .models import HollandQuestion, HollandTestResult

@admin.register(HollandQuestion)
class HollandQuestionAdmin(admin.ModelAdmin):
    list_display = ['order', 'text', 'personality_type']
    list_filter = ['personality_type']
    search_fields = ['text']

@admin.register(HollandTestResult)
class HollandTestResultAdmin(admin.ModelAdmin):
    list_display = ['user', 'date_taken', 'primary_type', 'secondary_type']
    readonly_fields = ['date_taken']