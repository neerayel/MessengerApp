import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.chat_id = self.scope['url_route']['kwargs']['chat_id']
        self.chat_group_name = f'chat_{self.chat_id}'
        self.user = self.scope['user']
        
        # Проверка аутентификации
        if self.user.is_anonymous:
            await self.close()
            return
        
        # Проверка доступа к чату
        if not await self.check_chat_access():
            await self.close()
            return
        
        # Присоединение к группе чата
        await self.channel_layer.group_add(
            self.chat_group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        # Выход из группы чата
        if hasattr(self, 'chat_group_name'):
            await self.channel_layer.group_discard(
                self.chat_group_name,
                self.channel_name
            )
    
    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            message = text_data_json.get('message', '')
            
            if not message:
                return
            
            # Сохранение сообщения в БД
            message_id = await self.save_message(message)
            
            # Отправка сообщения в группу чата
            await self.channel_layer.group_send(
                self.chat_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'sender': self.user.username,
                    'message_id': message_id,
                }
            )
        except json.JSONDecodeError:
            pass
    
    async def chat_message(self, event):
        # Отправка сообщения WebSocket клиенту
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender': event['sender'],
            'message_id': event['message_id'],
            'type': 'chat_message'
        }))
    
    @database_sync_to_async
    def check_chat_access(self):
        from .models import Chat  # Ленивый импорт внутри функции
        User = get_user_model()
        
        try:
            chat = Chat.objects.get(id=self.chat_id)
            return self.user == chat.user1 or self.user == chat.user2
        except Chat.DoesNotExist:
            return False
    
    @database_sync_to_async
    def save_message(self, content):
        from .models import Chat, EncryptedMessage  # Ленивый импорт
        
        chat = Chat.objects.get(id=self.chat_id)
        message = EncryptedMessage.objects.create(
            chat=chat,
            sender=self.user
        )
        message.set_content(content)
        message.save()
        
        # Обновляем время изменения чата
        chat.save()
        
        return message.id