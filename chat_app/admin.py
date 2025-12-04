from django.contrib import admin
from .models import ContactList, Chat, EncryptedMessage

@admin.register(ContactList)
class ContactListAdmin(admin.ModelAdmin):
    list_display = ['user', 'contacts_count', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username']
    
    def contacts_count(self, obj):
        return obj.contacts.count()
    contacts_count.short_description = 'Количество контактов'

@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ['user1', 'user2', 'messages_count', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['user1__username', 'user2__username']
    
    def messages_count(self, obj):
        return obj.messages.count()
    messages_count.short_description = 'Количество сообщений'

@admin.register(EncryptedMessage)
class EncryptedMessageAdmin(admin.ModelAdmin):
    list_display = ['chat', 'sender', 'created_at', 'is_read']
    list_filter = ['is_read', 'created_at']
    search_fields = ['sender__username', 'chat__user1__username', 'chat__user2__username']
    
    # Запрещаем редактирование зашифрованных полей
    readonly_fields = ['encrypted_content', 'encrypted_metadata']