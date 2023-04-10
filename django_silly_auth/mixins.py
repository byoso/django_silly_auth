import jwt
import time
import uuid
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.core.validators import (
    MinLengthValidator,
    MaxLengthValidator,
)

from django_silly_auth.config import SILLY_AUTH_SETTINGS as conf

if conf["VERBOSE"]:
    print("=== DSA IMPORT django_silly_auth.mixins")


class SillyAuthUserMixin(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    username = models.CharField(
        _("username"),
        max_length=150,
        unique=True,
        help_text=_(
            _("Required. 150 characters or fewer. Letters, digits and ./+/-/_ only."),
        ),
        validators=[
            MinLengthValidator(5),
            MaxLengthValidator(150)
        ],
        error_messages={
            "unique": _("A user with that username already exists."),
            "max_length": _("Username must be less than 150 characters."),
            "invalid": _("Username must contain only letters, digits and ./+/-/_ characters."),
        },
    )
    email = models.EmailField(_("email address"), unique=True)

    new_email = models.EmailField(blank=True, null=True, unique=False)
    is_confirmed = models.BooleanField(default=False)

    class Meta:
        abstract = True

    def get_jwt_token(self, expires_in=conf["EMAIL_VALID_TIME"]):

        token = jwt.encode(
            {'id': str(self.id), 'exp': time.time()+expires_in},
            settings.SECRET_KEY, algorithm='HS256'
        )
        return token

    @staticmethod
    def verify_jwt_token(token):
        try:
            pk = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=['HS256'])['id']
        except Exception as e:
            print("Token error:", e)
            return None
        return get_object_or_404(get_user_model(), id=pk)

    def clean(self):
        if "@" in self.username:
            raise ValidationError(
                {'username': _("A username cannot include the symbol '@'.")})
        super().clean()

    def save(self, *args, **kwargs):
        # self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"<User (DSA): {self.username}>"
