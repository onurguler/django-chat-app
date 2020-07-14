from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    email = models.EmailField(unique=True, null=False, blank=False)
    username = models.CharField(
        unique=True, null=False, blank=False, max_length=35,
        help_text='Required. %(username_max_length)d characters or fewer. Letters, digits and _ only.' % {
            'username_max_length': 35},)

    def __str__(self):
        return "%(username)s - %(email)s" % {
            'username': self.username,
            'email': self.email
        }
