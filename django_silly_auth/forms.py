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


User = get_user_model()


class NewPasswordForm(forms.Form):

    password = forms.CharField(
        max_length=64, widget=forms.PasswordInput,
        validators=[validate_password]
    )
    password2 = forms.CharField(
        label="Confirm password",
        max_length=64, widget=forms.PasswordInput,
        validators=[validate_password]
    )

    def clean_password2(self):
        password = self.cleaned_data['password']
        password2 = self.cleaned_data['password2']
        if password != password2:
            raise ValidationError("Passwords don't match, do it again")
        return password2


class NewEmailConfirmForm(forms.Form):

    password = forms.CharField(
        max_length=64, widget=forms.PasswordInput,
        validators=[validate_password]
    )

#################### FULL CLASSIC FORMS ####################

class LoginForm(forms.Form):
    credential = forms.CharField(
        label=_("Username or email"),
        max_length=64,
        widget=forms.TextInput({'placeholder': _('username or email')})
    )
    password = forms.CharField(
        label=_("Password"),
        max_length=64, widget=forms.PasswordInput,
        validators=[validate_password]
    )

    def clean_login(self):
        credential = self.cleaned_data['credential']
        if "@" in credential:
            user = User.objects.filter(email=credential)
        else:
            user = User.objects.filter(username=credential)
        if not user or not user[0].is_confirmed:
            raise ValidationError(_(f"user '{credential}' unknown or unconfirmed"))
        return credential


class SignUpForm(forms.Form):
    username = forms.CharField(
        label=_("Username"),
        validators=[MinLengthValidator(4), MaxLengthValidator(64)],
        max_length=64,
    )
    email = forms.EmailField(
        label=_("Email"),
        validators=[EmailValidator()])

    password = forms.CharField(
        label=_("Password"),
        max_length=64, widget=forms.PasswordInput,
        validators=[validate_password]
    )
    password2 = forms.CharField(
        label="Confirm password",
        max_length=64, widget=forms.PasswordInput,
        validators=[validate_password]
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
            raise ValidationError(_("'@' not allowed in a username"))
        else:
            user = User.objects.filter(username=username)
            if user:
                raise ValidationError(_(f"'{username}' already used by someone"))
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        user = User.objects.filter(email=email)
        if user:
            raise ValidationError(_(f"'{email}' already used."))
        return email


class CredentialForm(forms.Form):
    credential = forms.CharField(
        label=_("Email or username"),
        validators=[])

    def clean_credential(self):
        credential = self.cleaned_data['credential']
        if "@" in credential:
            user = User.objects.filter(email=credential)
        else:
            user = User.objects.filter(username=credential)
        if not user:
            raise ValidationError(_(f"'{credential}' unknown or unconfirmed"))
        return credential


class ResetPasswordForm(forms.Form):
    password = forms.CharField(
        label=_("Password"),
        max_length=64, widget=forms.PasswordInput,
        validators=[validate_password]
    )
    password2 = forms.CharField(
        label=_("Confirm password"),
        max_length=64, widget=forms.PasswordInput,
        validators=[validate_password]
    )

    def clean_password(self):
        password = self.cleaned_data['password']
        return password

    def clean_password2(self):
        password = self.cleaned_data['password']
        password2 = self.cleaned_data['password2']
        if password != password2:
            raise ValidationError(_("different than password"))
        return password2


class ChangeUsernameForm(forms.Form):
    username = forms.CharField(
        validators=[MinLengthValidator(4), MaxLengthValidator(64)],
        max_length=64,
    )

    def clean_username(self):
        username = self.cleaned_data['username']
        if "@" in username:
            raise ValidationError(_("'@' not allowed in a username"))
        else:
            user = User.objects.filter(username=username)
            if user:
                raise ValidationError(_(f"'{username}' is already used by someone"))
        return username


class ChangeEmailForm(forms.Form):
    email = forms.EmailField(
        label=_("New e-mail address"),
        validators=[EmailValidator()]
        )

    def clean_email(self):
        email = self.cleaned_data['email']
        user = User.objects.filter(email=email)
        if user:
            raise ValidationError(_(f"'{email}' already used by someone"))
        return email
