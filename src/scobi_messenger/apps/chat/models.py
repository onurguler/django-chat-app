from django.db import models

from scobi_messenger.apps.accounts.models import User


class Contact(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="contacts")
    friend = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return "%(user)s - %(friend)s" % {
            'user': self.user.username,
            'friend': self.friend.username
        }


class Conversation(models.Model):
    participants = models.ManyToManyField(
        Contact, blank=True, related_name="conversations")

    def __str__(self):
        return '{}'.format(self.pk)


class Message(models.Model):
    conversation = models.ForeignKey(
        Conversation, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name="outgoing_messages")
    to_user = models.ForeignKey(User, on_delete=models.CASCADE,
                                related_name="incoming_messages")
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "%(sender)s at %(conversation)s on %(created_at)s" % {
            'sender': self.sender.username,
            'conversation': self.conversation,
            'created_at': self.created_at
        }
