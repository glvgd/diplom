import re
from .models import Profession, Subject, UserProgress

class LocalChatBot:
    def __init__(self):
        # Вместо моментальной загрузки объявляем переменные со значением None.
        # Это защищает контейнер от падения при первом запуске, когда таблиц еще нет.
        self._professions = None
        self._subjects = None
    
    @property
    def professions(self):
        # Загружаем профессии из БД только тогда, когда к ним происходит первое реальное обращение
        if self._professions is None:
            self._professions = list(Profession.objects.all())
        return self._professions

    @property
    def subjects(self):
        # Загружаем предметы из БД по требованию
        if self._subjects is None:
            self._subjects = list(Subject.objects.all())
        return self._subjects
    
    def load_knowledge_base(self):
        """Метод оставлен пустым для сохранения совместимости, если он вызывается в других файлах"""
        pass
    
    def get_response(self, message, user=None):
        """Главный метод для получения ответа"""
        message_lower = message.lower()
        
        # Приветствие
        if any(word in message_lower for word in ['привет', 'здравствуй', 'добрый день', 'здравствуйте']):
            return self.get_greeting()
        
        # Помощь
        if any(word in message_lower for word in ['помощь', 'help', 'что ты умеешь', 'команды']):
            return self.get_help()
        
        # Список профессий
        if any(word in message_lower for word in ['список профессий', 'какие профессии', 'все профессии']):
            return self.get_professions_list()
        
        # Поиск профессии
        if any(word in message_lower for word in ['профессия', 'расскажи о профессии', 'что такое']) and len(message_lower) > 10:
            return self.search_profession(message_lower)
        
        # Зарплаты
        if 'зарплат' in message_lower or 'сколько зарабатывает' in message_lower:
            return self.get_salary_info(message_lower)
        
        # ЕГЭ/ОГЭ
        if any(word in message_lower for word in ['егэ', 'огэ', 'экзамен', 'предметы']):
            return self.get_exam_info()
        
        # Вузы
        if any(word in message_lower for word in ['вуз', 'университет', 'куда поступить', 'институт']):
            return self.get_university_info(message_lower)
        
        # Статистика пользователя
        if any(word in message_lower for word in ['мой прогресс', 'моя статистика', 'сколько решил']):
            if user:
                return self.get_user_stats(user)
            return self.get_help()
        
        # Востребованность
        if 'востребован' in message_lower:
            return self.get_demand_info()
        
        # Спасибо
        if 'спасиб' in message_lower:
            return "🙏 Пожалуйста! Рад помочь! Обращайся если будут ещё вопросы!"
        
        # Ответ по умолчанию
        return self.get_default_response()
    
    def get_greeting(self):
        return """👋 Привет! Я AI-ассистент ProfGuide!

Я помогаю школьникам выбрать будущую профессию и подготовиться к ЕГЭ.

📝 Напиши 'помощь' чтобы узнать, что я умею!"""
    
    def get_help(self):
        return """🆘 Я могу помочь тебе:

📚 **Профессии**
• Список всех профессий
• Рассказать о конкретной профессии
• Узнать зарплаты специалистов
• Показать востребованность

📖 **Образование**
• Какие предметы ЕГЭ нужны
• Вузы России по направлениям

📊 **Статистика**
• Твой прогресс в решении заданий

**Примеры запросов:**
• "Список профессий"
• "Расскажи о программисте"
• "Сколько зарабатывает инженер"
• "Какие вузы у IT"
• "Мой прогресс"

Что тебя интересует? 😊"""
    
    def get_professions_list(self):
        if not self.professions:
            return "😔 Профессии пока не добавлены в базу данных."
        
        result = "💼 **Список профессий на платформе:**\n\n"
        for i, prof in enumerate(self.professions[:10], 1):
            result += f"{i}. **{prof.name}** — {prof.description[:50]}...\n"
        
        if len(self.professions) > 10:
            result += f"\n📚 И ещё {len(self.professions) - 10} профессий. Напиши название интересующей!"
        
        return result
    
    def search_profession(self, query):
        for prof in self.professions:
            if prof.name.lower() in query:
                demand_stars = '⭐' * prof.demand_level + '☆' * (5 - prof.demand_level)
                return f"""**{prof.name}** 📋

📖 {prof.description}

💰 **Зарплата:** {prof.salary_min:,} - {prof.salary_max:,} ₽
📈 **Востребованность:** {demand_stars}
🏛️ **Вузы:** {prof.universities[:100]}...

Подробнее на странице профессии!"""
        
        return "🤔 Не нашёл такую профессию. Напиши 'список профессий' чтобы посмотреть все доступные."
    
    def get_salary_info(self, query):
        for prof in self.professions:
            if prof.name.lower() in query:
                return f"💰 **{prof.name}** зарабатывает от {prof.salary_min:,} до {prof.salary_max:,} рублей в месяц в России."
        
        highest = max(self.professions, key=lambda x: x.salary_max) if self.professions else None
        if highest:
            return f"💵 Самая высокооплачиваемая профессия: **{highest.name}** — до {highest.salary_max:,} ₽\n\nЧтобы узнать зарплату конкретной профессии, напиши её название!"
        
        return self.get_help()
    
    def get_exam_info(self):
        if not self.subjects:
            return "😔 Предметы пока не добавлены."
        
        result = "📚 **Доступные предметы для подготовки:**\n\n"
        for subj in self.subjects:
            result += f"• {subj.name} ({subj.get_exam_type_display()}) — {subj.icon}\n"
        
        result += "\n✅ Перейди в раздел 'Тестирование' чтобы начать решать задания!"
        return result
    
    def get_university_info(self, query):
        for prof in self.professions:
            if prof.name.lower() in query and prof.universities:
                unis = prof.universities.split(',')[:3]
                return f"🏛️ Чтобы стать **{prof.name}**, рекомендуют поступать в:\n\n" + "\n".join([f"• {u.strip()}" for u in unis]) + "\n\n🎓 Это ведущие вузы России!"
        
        return "🎓 **Топ вузов России:**\n• МГУ им. Ломоносова\n• СПбГУ\n• НИУ ВШЭ\n• МФТИ\n• МГТУ им. Баумана\n\nЧтобы узнать вузы по конкретной профессии, напиши её название!"
    
    def get_user_stats(self, user):
        solved = UserProgress.objects.filter(user=user).count()
        correct = UserProgress.objects.filter(user=user, is_correct=True).count()
        
        if solved == 0:
            return "📊 Ты ещё не решил ни одного задания. Начни в разделе 'Тестирование'!"
        
        accuracy = int(correct / solved * 100)
        
        from .utils import recommend_professions
        recommendations = recommend_professions(user, limit=3)
        
        result = f"""📊 **Твоя статистика:**

✅ Решено заданий: {solved}
🎯 Правильных ответов: {correct}
📈 Точность: {accuracy}%

"""
        if recommendations:
            result += "🎯 **Рекомендованные профессии:**\n"
            for prof in recommendations:
                result += f"• {prof.name}\n"
            result += "\n👉 Перейди в раздел 'Профессии' для подробностей!"
        
        return result
    
    def get_demand_info(self):
        if not self.professions:
            return "😔 Нет данных о профессиях."
        
        top_demand = sorted(self.professions, key=lambda x: x.demand_level, reverse=True)[:5]
        result = "📈 **Самые востребованные профессии:**\n\n"
        for prof in top_demand:
            stars = '⭐' * prof.demand_level
            result += f"• **{prof.name}** {stars}\n"
        
        return result
    
    def get_default_response(self):
        return """🤔 Я не совсем понял вопрос.

📝 Напиши **'помощь'** чтобы увидеть список команд, которые я понимаю.

Или задай вопрос о профессиях, ЕГЭ или вузах!"""