from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

from scobi_messenger.apps.accounts.models import User
from .models import Conversation


@login_required
def index(request):
    conversations = request.user.conversations.all()
    return render(request, 'chat/index.html', {
        'conversations': conversations
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

    conversation_qs = Conversation.objects.filter(users__in=[user, to_user])
    conversation = None

    if not conversation_qs.exists():
        conversation = Conversation.objects.create()
        conversation.users.add(user)
        conversation.users.add(to_user)
        conversation.save()
    else:
        conversation = conversation_qs[0]

    messages = conversation.messages.order_by('-created_at')[::-1]

    return render(request, 'chat/chat.html', {
        'to_user': to_user,
        'conversation': conversation,
        'messages': messages
    })
