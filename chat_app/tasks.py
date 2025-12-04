from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import EncryptedMessage
import logging

logger = logging.getLogger(__name__)

@shared_task
def clean_old_chats():
    try:
        # Вычисляем дату 1 день назад
        one_day_ago = timezone.now() - timedelta(days=1)
        
        # Находим и удаляем старые сообщения
        old_messages = EncryptedMessage.objects.filter(
            created_at__lt=one_day_ago
        )
        
        count = old_messages.count()
        old_messages.delete()
        
        logger.info(f"Удалено {count} старых сообщений")
        return f"Удалено {count} старых сообщений"
        
    except Exception as e:
        logger.error(f"Ошибка при очистке чатов: {str(e)}")
        return f"Ошибка: {str(e)}"