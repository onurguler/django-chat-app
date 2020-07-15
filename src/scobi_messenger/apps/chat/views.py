from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core import serializers
from django.forms.models import model_to_dict
import channels.layers
from asgiref.sync import async_to_sync
from django.core.serializers.json import DjangoJSONEncoder
import json

from scobi_messenger.apps.accounts.models import User
from .models import Conversation, Message, Contact


@login_required
def index(request):
    # @TODO: send conversation list to template
    # conversations = request.user.contacts.conversations.all()
    return render(request, 'chat/index.html', {
        # 'conversations': conversations
    })


@login_required
def contacts(request):
    contacts = User.objects.all()
    return render(request, 'chat/contacts.html', {
        'contacts': contacts
    })


@login_required
def user_chat(request, username):
    """
    to_user ile olan conversationu al, eğer conversation yoksa yeni bir conversation oluştur

    @FIXME: Yeni bir conversation oluşturulduğunda ve hiç mesaj atılmadığında boş bir conversation olacak.
    Bu durumu engellemeye çalış.
    """
    user = request.user
    to_user = get_object_or_404(User, username=username)

    if user == to_user:
        # @TODO: return a error (kendine mesaj atamazsın)
        return redirect('chat:chat_index')

    contact_user_qs = Contact.objects.filter(user=user, friend=to_user)
    contact_to_user_qs = Contact.objects.filter(user=to_user, friend=user)

    contact_user = None
    contact_to_user = None

    if not contact_user_qs.exists():
        contact_user = Contact.objects.create(user=user, friend=to_user)
    else:
        contact_user = contact_user_qs[0]

    if not contact_to_user_qs.exists():
        contact_to_user = Contact.objects.create(user=to_user, friend=user)
    else:
        contact_to_user = contact_to_user_qs[0]

    conversation_qs = Conversation.objects.filter(
        participants__in=[contact_user, contact_to_user])
    conversation = None

    if not conversation_qs.exists():
        conversation = Conversation.objects.create()
        conversation.participants.add(contact_user)
        conversation.participants.add(contact_to_user)
        conversation.save()
    else:
        conversation = conversation_qs[0]

    messages = conversation.messages.order_by('-created_at')[::-1]

    return render(request, 'chat/chat.html', {
        'to_user': to_user,
        'conversation': conversation,
        'messages': messages
    })


@login_required
def send_user_chat_message(request, username):
    if not request.is_ajax():
        return JsonResponse({
            'success': False,
            'message': 'Server error.'
        }, status=500)

    to_user_qs = User.objects.filter(username=username)

    if not to_user_qs.exists():
        return JsonResponse({
            'success': False,
            'error': 'User does not exists.'
        }, status=404)

    user = request.user
    to_user = to_user_qs[0]

    contact_user = Contact.objects.get(user=user, friend=to_user)
    contact_to_user = Contact.objects.get(user=to_user, friend=user)

    conversation_qs = Conversation.objects.filter(
        participants__in=[contact_user, contact_to_user])

    if not conversation_qs.exists():
        return JsonResponse({
            'success': False,
            'error': 'Conversation does not exists'
        })

    conversation = conversation_qs[0]

    message_text = request.POST.get('text')

    message = Message.objects.create(
        sender=user, to_user=to_user, conversation=conversation, text=message_text)

    message_json = serializers.serialize('json', [message, ])
    message_json = json.loads(message_json)
    message_json = message_json[0]["fields"]
    message_json["sender"] = user.username
    message_json["to_user"] = to_user.username
    message_json = json.dumps(message_json)

    channel_layer = channels.layers.get_channel_layer()
    conversation_group_name = "chat_%s" % conversation.pk

    # Send message to room group
    async_to_sync(channel_layer.group_send)(
        conversation_group_name,
        {
            'type': 'chat_message',
            'message': message_json
        }
    )

    return JsonResponse({
        'success': True,
        'message': message_json
    })
