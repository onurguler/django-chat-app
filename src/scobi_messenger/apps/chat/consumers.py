import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

from scobi_messenger.apps.accounts.models import User
from .models import Conversation, Contact


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        """
        Eğer requesti yapan user parametre olarak gelen conversation içerisinde varsa,
        ve parametre olarak gelen to_user o conversationun içerisinde varsa bağlantıyı
        kabul et. Değilse reddet.

        @TODO: Conversationda ikiden fazla user olma durumunda incele. 
               yani grup mesajlarında bir sorun olabilir
        """
        self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']
        self.conversation_group_name = 'chat_%s' % self.conversation_id
        self.user = self.scope['user']
        self.to_user_username = self.scope['url_route']['kwargs']['username']

        if not self.user.is_authenticated:
            self.close()
            return

        if self.user.username == self.to_user_username:
            self.close()
            return

        try:
            to_user = User.objects.get(username=self.to_user_username)
            conversation = Conversation.objects.get(pk=self.conversation_id)
            conversation_users = conversation.participants.all()

            contact_user = Contact.objects.get(user=self.user, friend=to_user)
            contact_to_user = Contact.objects.get(
                user=to_user, friend=self.user)

            if not contact_user in conversation_users:
                self.close()
                return
            if not contact_to_user in conversation_users:
                self.close()
                return

            # Join room group
            async_to_sync(self.channel_layer.group_add)(
                self.conversation_group_name,
                self.channel_name
            )

            self.accept()
        except:
            self.close()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.conversation_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.conversation_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    # Receive message from room group
    def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'message': message
        }))
