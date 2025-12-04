from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Q
from .forms import CustomUserCreationForm, CustomAuthenticationForm, ContactAddForm, MessageForm
from .models import ContactList, Chat, EncryptedMessage
from django.utils import timezone
from datetime import timedelta
import json

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'registration/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
    else:
        form = CustomAuthenticationForm()
    
    return render(request, 'registration/login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def home(request):
    user = request.user
    
    # Получаем все чаты пользователя
    chats = Chat.objects.filter(
        Q(user1=user) | Q(user2=user)
    ).order_by('-updated_at')
    
    # Добавляем информацию о последнем сообщении
    for chat in chats:
        last_message = chat.messages.last()
        chat.last_message = last_message.get_content() if last_message else "Нет сообщений"
        chat.other_user = chat.get_other_user(user)
        chat.unread_count = chat.messages.filter(is_read=False).exclude(sender=user).count()
    
    context = {
        'chats': chats,
    }
    return render(request, 'chat_app/index.html', context)

@login_required
def contacts_view(request):
    user = request.user
    contact_list, created = ContactList.objects.get_or_create(user=user)
    
    if request.method == 'POST':
        form = ContactAddForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            try:
                contact_user = User.objects.get(username=username)
                if contact_list.add_contact(contact_user):
                    try:
                        # Создаем чат с новым контактом
                        Chat.objects.get_or_create(
                            user1=user,
                            user2=contact_user
                        )
                    finally:
                        return redirect('contacts')
            except User.DoesNotExist:
                form.add_error('username', 'Пользователь не найден')
    else:
        form = ContactAddForm()
    
    context = {
        'contact_list': contact_list,
        'contacts': contact_list.contacts.all(),
        'form': form,
    }
    return render(request, 'chat_app/contacts.html', context)

@login_required
def remove_contact(request, user_id):
    user = request.user
    contact_list = get_object_or_404(ContactList, user=user)
    contact_user = get_object_or_404(User, id=user_id)
    
    contact_list.remove_contact(contact_user)
    return redirect('contacts')

@login_required
def chat_view(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id)
    
    # Проверяем, что пользователь имеет доступ к чату
    if request.user not in [chat.user1, chat.user2]:
        return redirect('home')
    
    other_user = chat.get_other_user(request.user)
    
    # Помечаем сообщения как прочитанные
    chat.messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)
    
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            content = form.cleaned_data['content']
            message = EncryptedMessage.objects.create(
                chat=chat,
                sender=request.user
            )
            message.set_content(content)
            message.save()
            
            # Обновляем время изменения чата
            chat.save()
            
            return redirect('chat', chat_id=chat_id)
    else:
        form = MessageForm()
    
    # Получаем сообщения
    messages = chat.messages.all().order_by('created_at')
    
    context = {
        'chat': chat,
        'other_user': other_user,
        'messages': messages,
        'form': form,
    }
    return render(request, 'chat_app/chat.html', context)

@login_required
@require_POST
def send_message(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id)
    
    if request.user not in [chat.user1, chat.user2]:
        return JsonResponse({'error': 'Доступ запрещен'}, status=403)
    
    data = json.loads(request.body)
    content = data.get('content', '').strip()
    
    if not content:
        return JsonResponse({'error': 'Сообщение не может быть пустым'}, status=400)
    
    message = EncryptedMessage.objects.create(
        chat=chat,
        sender=request.user
    )
    message.set_content(content)
    message.save()
    
    # Обновляем время изменения чата
    chat.save()
    
    return JsonResponse({
        'success': True,
        'message_id': message.id,
        'content': content,
        'sender': request.user.username,
        'created_at': message.created_at.strftime('%H:%M'),
    })

@login_required
def get_new_messages(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id)
    
    if request.user not in [chat.user1, chat.user2]:
        return JsonResponse({'error': 'Доступ запрещен'}, status=403)
    
    last_message_id = request.GET.get('last_message_id', 0)
    
    new_messages = chat.messages.filter(
        id__gt=last_message_id
    ).exclude(sender=request.user)
    
    messages_data = []
    for message in new_messages:
        messages_data.append({
            'id': message.id,
            'content': message.get_content(),
            'sender': message.sender.username,
            'created_at': message.created_at.strftime('%H:%M'),
            'is_read': message.is_read,
        })
        
        # Помечаем как прочитанное
        if not message.is_read:
            message.is_read = True
            message.save()
    
    return JsonResponse({
        'messages': messages_data,
        'has_new': len(messages_data) > 0
    })