from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import (
    EmailValidator,
    MinLengthValidator,
    MaxLengthValidator
    )
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import get_user_model
from django_silly_auth.config import SILLY_AUTH_SETTINGS as conf

if conf["VERBOSE"]:
    print("=== DSA IMPORT django_silly_auth.forms")

User = get_user_model()


class LoginForm(forms.Form):
    credential = forms.CharField(
        label=_("Username or email"),
        max_length=64,
        widget=forms.TextInput({
            'placeholder': _('Username or email'),
        })
    )
    password = forms.CharField(
        label=_("Password"),
        max_length=64,
        widget=forms.PasswordInput(
            {'placeholder': _('Password')}
        ),
        validators=[validate_password]
    )

    def clean_login(self):
        credential = self.cleaned_data['credential']
        if "@" in credential:
            user = User.objects.filter(email=credential)
        else:
            user = User.objects.filter(username=credential)
        if not user or not user[0].is_confirmed:
            raise ValidationError(_(
                "User '%(credential)s' unknown or unconfirmed"
                ) % {"credential": credential}
                )
        return credential


class SignUpForm(forms.Form):
    username = forms.CharField(
        label=_("Username"),
        validators=[MinLengthValidator(4), MaxLengthValidator(64)],
        max_length=64,
        widget=forms.TextInput({
            'placeholder': _('Username'),
        })
    )
    email = forms.EmailField(
        label=_("Email"),
        validators=[EmailValidator()],
        widget=forms.EmailInput({
            'placeholder': _('Email'),
        }),
        )

    password = forms.CharField(
        label=_("Password"),
        max_length=64,
        validators=[validate_password],
        widget=forms.PasswordInput({
            'placeholder': _('Password'),
        }),
    )
    password2 = forms.CharField(
        label=_("Confirm password"),
        max_length=64,
        validators=[validate_password],
        widget=forms.PasswordInput({
            'placeholder': _('Password'),
        }),
    )

    def clean_password2(self):
        password = self.cleaned_data['password']
        password2 = self.cleaned_data['password2']
        if password != password2:
            raise ValidationError(_("different than password"))
        return password2

    def clean_username(self):
        username = self.cleaned_data['username']
        if "@" in username:
            raise ValidationError(_("A username cannot include the symbol '@'."))
        else:
            user = User.objects.filter(username=username)
            if user:
                raise ValidationError(_(
                    "'%(username)s' is already taken by someone else."
                    ) % {"username": username}
                    )
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        user = User.objects.filter(email=email)
        if user:
            raise ValidationError(_(
                "'%(email)s' is already taken by someone else."
                ) % {"email": email}
                )
        return email


class CredentialForm(forms.Form):
    credential = forms.CharField(
        label=_("Username or email"),
        validators=[],
        widget=forms.TextInput({
            'placeholder': _('Username or email'),
        }),
        )

    def clean_credential(self):
        credential = self.cleaned_data['credential']
        if "@" in credential:
            user = User.objects.filter(email=credential)
        else:
            user = User.objects.filter(username=credential)
        if not user:
            raise ValidationError(_(
                "'%(credential)s' unknown or unconfirmed"
                ) % {"credential": credential}
                )
        return credential


class ResetPasswordForm(forms.Form):
    password = forms.CharField(
        label=_("Password"),
        max_length=64,
        widget=forms.PasswordInput({
            'placeholder': _('Password'),
        }),
        validators=[validate_password]
    )
    password2 = forms.CharField(
        label=_("Confirm password"),
        max_length=64,
        widget=forms.PasswordInput({
            'placeholder': _('Password'),
        }),
        validators=[validate_password]
    )

    def clean_password(self):
        password = self.cleaned_data['password']
        return password

    def clean_password2(self):
        password = self.cleaned_data['password']
        password2 = self.cleaned_data['password2']
        if password != password2:
            raise ValidationError(_("The passwords you entered do not match."))
        return password2


class ChangeUsernameForm(forms.Form):
    username = forms.CharField(
        label=_("New username"),
        validators=[MinLengthValidator(4), MaxLengthValidator(64)],
        max_length=64,
        widget=forms.TextInput({
            'placeholder': _('Username'),
        })
    )

    def clean_username(self):
        username = self.cleaned_data['username']
        if "@" in username:
            raise ValidationError(_("A username cannot include the symbol '@'."))
        else:
            user = User.objects.filter(username=username)
            if user:
                raise ValidationError(_(
                    "'%(username)s' is already taken by someone else."
                    ) % {"username": username}
                    )
        return username


class ChangeEmailForm(forms.Form):
    email = forms.EmailField(
        label=_("New email address"),
        validators=[EmailValidator()],
        widget=forms.EmailInput({
            'placeholder': _('Email'),
        }),
        )

    def clean_email(self):
        email = self.cleaned_data['email']
        user = User.objects.filter(email=email)
        if user:
            raise ValidationError(_(
                "'%(email)s' already taken by someone else."
                ) % {"email": email}
                )
        return email
