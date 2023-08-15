from django.contrib.auth.models import AbstractUser
from django.db.models import CharField, EmailField
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    email = EmailField(_('email address'), unique=True)
    first_name = CharField(_('first name'), max_length=150)
    last_name = CharField(_('last name'), max_length=150)

    REQUIRED_FIELDS = ['first_name', 'last_name', 'username']
    USERNAME_FIELD = 'email'
