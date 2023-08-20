from django.contrib.auth.models import AbstractUser

from django_silly_auth.mixins import SillyAuthUserMixin


class User(SillyAuthUserMixin, AbstractUser):
    pass
