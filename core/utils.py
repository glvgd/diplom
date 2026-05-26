from django.db.models import Count, Q
from .models import UserProgress, Profession, ProfessionRequirement

def get_bot_response(message, user):
    """Простой AI-ответ для чата"""
    message_lower = message.lower()
    
    # Получаем статистику пользователя
    solved_count = UserProgress.objects.filter(user=user).count()
    correct_count = UserProgress.objects.filter(user=user, is_correct=True).count()
    
    if 'привет' in message_lower or 'здравствуй' in message_lower:
        return "👋 Привет! Я AI-ассистент ProfGuide. Я помогаю школьникам выбрать будущую профессию. Спроси меня о чём угодно!"
    
    elif 'професси' in message_lower or 'работа' in message_lower:
        if solved_count > 0:
            return f"📊 Ты уже решил(а) {solved_count} заданий! Твоя точность {int(correct_count/solved_count*100)}%. Перейди на вкладку 'Профессии', чтобы увидеть персональные рекомендации!"
        return "💼 Чтобы получить рекомендации профессий, перейди на вкладку 'Профессии' или реши несколько заданий в разделе 'Тестирование'!"
    
    elif 'егэ' in message_lower or 'огэ' in message_lower:
        return "📚 В разделе 'Тестирование' ты найдёшь реальные задания ЕГЭ и ОГЭ 2026 года с подробными объяснениями. Решай и повышай свой уровень!"
    
    elif 'вуз' in message_lower or 'университет' in message_lower or 'поступить' in message_lower:
        return "🏛️ В разделе 'Профессии' выбери любую профессию и увидишь список ведущих вузов России, где можно получить эту специальность!"
    
    elif 'сколько' in message_lower and 'заданий' in message_lower:
        return f"📝 Ты решил(а) {solved_count} заданий! Из них правильно: {correct_count}. Отличный прогресс! Продолжай в том же духе! 🎯"
    
    elif 'спасибо' in message_lower:
        return "🙏 Пожалуйста! Рад помочь! Если будут ещё вопросы - обращайся!"
    
    elif 'помощ' in message_lower:
        return "🆘 Я могу:\n• Рассказать о профессиях\n• Подсказать где готовиться к ЕГЭ\n• Посоветовать вузы\n• Показать твою статистику\n\nЧто тебя интересует?"
    
    else:
        return f"❓ Я не совсем понял вопрос. Но я могу помочь тебе с:\n• Выбором профессии\n• Подготовкой к ЕГЭ/ОГЭ\n• Поступлением в вузы\n\nСпроси меня конкретнее! Например: 'Какие профессии востребованы?' или 'Как подготовиться к ЕГЭ по математике?'"

def recommend_professions(user, limit=3):
    """Рекомендация профессий на основе результатов пользователя"""
    results = UserProgress.objects.filter(user=user, is_correct=True)
    
    if not results.exists():
        return Profession.objects.all()[:limit]
    
    # Считаем успехи по предметам
    subject_scores = {}
    for result in results:
        subject_id = result.task.subject.id
        subject_scores[subject_id] = subject_scores.get(subject_id, 0) + 1
    
    # Нормализуем
    max_score = max(subject_scores.values()) if subject_scores else 1
    for subject_id in subject_scores:
        subject_scores[subject_id] /= max_score
    
    # Оцениваем профессии
    profession_scores = []
    for profession in Profession.objects.all():
        total_importance = 0
        weighted_score = 0
        
        requirements = ProfessionRequirement.objects.filter(profession=profession)
        for req in requirements:
            score = subject_scores.get(req.subject.id, 0)
            importance = req.importance
            total_importance += importance
            weighted_score += importance * score
        
        if total_importance > 0:
            final_score = weighted_score / total_importance
            profession_scores.append((profession, final_score))
        else:
            profession_scores.append((profession, 0))
    
    profession_scores.sort(key=lambda x: x[1], reverse=True)
    return [p for p, _ in profession_scores[:limit]]