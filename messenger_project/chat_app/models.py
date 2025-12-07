from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError
from .encryption import encrypt_message, decrypt_message
import json

class ContactList(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='contact_list')
    contacts = models.ManyToManyField(User, related_name='added_by', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Контакты пользователя {self.user.username}"

    def add_contact(self, contact_user):
        if contact_user != self.user and contact_user not in self.contacts.all():
            self.contacts.add(contact_user)
            return True
        return False

    def remove_contact(self, contact_user):
        if contact_user in self.contacts.all():
            self.contacts.remove(contact_user)
            return True
        return False

class Chat(models.Model):
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chats_as_user1')
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chats_as_user2')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user1', 'user2']
        ordering = ['-updated_at']

    def __str__(self):
        return f"Чат между {self.user1.username} и {self.user2.username}"

    def clean(self):
        if self.user1 == self.user2:
            raise ValidationError("Пользователь не может создать чат с самим собой")
        if self.user1.id > self.user2.id:
            self.user1, self.user2 = self.user2, self.user1

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def get_other_user(self, current_user):
        if current_user == self.user1:
            return self.user2
        return self.user1

class EncryptedMessage(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    encrypted_content = models.TextField()  # Зашифрованный текст
    encrypted_metadata = models.TextField()  # Зашифрованные метаданные
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Сообщение от {self.sender.username} в {self.chat}"

    def set_content(self, content, metadata=None):
        if metadata is None:
            metadata = {}
        
        # Шифруем текст сообщения
        self.encrypted_content = encrypt_message(content)
        
        # Шифруем метаданные
        metadata_str = json.dumps(metadata)
        self.encrypted_metadata = encrypt_message(metadata_str)

    def get_content(self):
        try:
            return decrypt_message(self.encrypted_content)
        except:
            return "[Не удалось расшифровать сообщение]"

    def get_metadata(self):
        try:
            metadata_str = decrypt_message(self.encrypted_metadata)
            return json.loads(metadata_str)
        except:
            return {}