import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import ChatMessage
from .utils import get_bot_response

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        
        # Проверяем авторизацию
        if self.user.is_authenticated:
            await self.accept()
            
            # Отправляем приветственное сообщение
            await self.send(text_data=json.dumps({
                'type': 'message',
                'username': 'AI Ассистент',
                'message': 'Привет! Я AI-ассистент. Задавай вопросы о профессиях, подготовке к ЕГЭ или поступлении в вузы!',
                'is_bot': True
            }))
            
            # Отправляем историю чата
            messages = await self.get_chat_history()
            for msg in messages:
                await self.send(text_data=json.dumps({
                    'type': 'message',
                    'username': msg['username'],
                    'message': msg['message'],
                    'is_bot': msg['is_bot']
                }))
        else:
            await self.close()
    
    async def disconnect(self, close_code):
        pass
    
    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            message = text_data_json['message']
            
            # Сохраняем сообщение пользователя
            await self.save_message(message, is_bot=False)
            
            # Отправляем сообщение пользователя обратно
            await self.send(text_data=json.dumps({
                'type': 'message',
                'username': self.user.username,
                'message': message,
                'is_bot': False
            }))
            
            # Получаем ответ от бота
            bot_response = await self.get_bot_response(message)
            
            # Сохраняем ответ бота
            await self.save_message(bot_response, is_bot=True)
            
            # Отправляем ответ бота
            await self.send(text_data=json.dumps({
                'type': 'message',
                'username': 'AI Ассистент',
                'message': bot_response,
                'is_bot': True
            }))
            
        except Exception as e:
            print(f"Error in receive: {e}")
    
    @database_sync_to_async
    def save_message(self, message, is_bot=False):
        ChatMessage.objects.create(
            user=self.user,
            message=message,
            is_bot=is_bot
        )
    
    @database_sync_to_async
    def get_chat_history(self):
        messages = ChatMessage.objects.filter(user=self.user)[:50]
        return [{
            'username': 'Вы' if not msg.is_bot else 'AI Ассистент',
            'message': msg.message,
            'is_bot': msg.is_bot,
        } for msg in messages]
    
    @database_sync_to_async
    def get_bot_response(self, message):
        return get_bot_response(message, self.user)