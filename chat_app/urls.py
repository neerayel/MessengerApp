from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('accounts/logout/', views.logout_view, name='logout'),

    path('contacts/', views.contacts_view, name='contacts'),
    path('contacts/remove/<int:user_id>/', views.remove_contact, name='remove_contact'),
    path('chat/<int:chat_id>/', views.chat_view, name='chat'),
    path('chat/<int:chat_id>/send/', views.send_message, name='send_message'),
    path('chat/<int:chat_id>/get-new/', views.get_new_messages, name='get_new_messages'),
]
