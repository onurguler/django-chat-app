from django.urls import path

from . import views


app_name = 'chat'

urlpatterns = [
    path('', views.index, name='chat_index'),
    path('contacts/', views.contacts, name='contacts'),
    path('user/<str:username>', views.user_chat, name='user_chat'),
]
