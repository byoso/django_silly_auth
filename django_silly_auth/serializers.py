from django.contrib.auth import get_user_model
from django.core import exceptions
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers
from django_silly_auth.config import SILLY_AUTH_SETTINGS as conf

if conf["VERBOSE"]:
    print("=== DSA IMPORT django_silly_auth.serializers")

User = get_user_model()


class UserInfosSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = [*conf["USER_INFOS_EXCLUDE"]]


class GetAllUsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class CreateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')

    def validate(self, data):
        username = data.get('username')
        # email = data.get('email')
        password = data.get('password')
        username_errors = list()
        email_errors = list()
        password_errors = list()

        errors = dict()
        try:
            validate_password(
                password=password,
                user=None,
                password_validators=None)
        except exceptions.ValidationError as e:
            password_errors += list(e.messages)

        if "@" in username:
            username_errors += [_("A username cannot include the symbol '@'."), ]

        if username_errors:
            errors["username"] = username_errors
        if password_errors:
            errors["password"] = password_errors
        if email_errors:
            errors["email"] = email_errors

        if errors:
            raise serializers.ValidationError(errors)
        return data


class PasswordsSerializer(serializers.Serializer):
    password = serializers.CharField(
        write_only=True
    )
    password2 = serializers.CharField(
        write_only=True
    )

    def validate(self, data):
        password = data.get('password')
        password2 = data.get('password2')
        errors = dict()
        password_errors = list()

        if password != password2:
            password_errors += [_("The passwords you entered do not match."), ]

        try:
            validate_password(
                password=password,
                user=None,
                password_validators=None)

        except exceptions.ValidationError as e:
            password_errors += list(e.messages)

        if password_errors:
            errors['password'] = password_errors
            raise serializers.ValidationError(errors)
        return data


class EmailSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate(self, data):
        email = data.get('email')
        errors = dict()
        email_errors = list()

        if User.objects.filter(email=email).exists():
            email_errors += [_("This email is already associated with an existing account."), ]

        if email_errors:
            errors['email'] = email_errors
            raise serializers.ValidationError(errors)
        return data


class LoginSerializer(serializers.Serializer):
    credential = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        credential = data.get('credential')
        password = data.get('password')
        errors = dict()
        credential_errors = list()
        password_errors = list()

        if "@" in credential:
            if not User.objects.filter(email=credential).exists():
                credential_errors += [_("Email not found"), ]
        else:
            if not User.objects.filter(username=credential).exists():
                credential_errors += [_("User not found"), ]

        if credential_errors:
            errors['credential'] = credential_errors
        if password_errors:
            errors['password'] = password_errors

        if errors:
            raise serializers.ValidationError(errors)
        return data


class CredentialJWTokenSerializer(serializers.Serializer):
    credential = serializers.CharField()
    jwt_token = serializers.CharField()

    def validate(self, data):
        credential = data.get('credential')
        jwt_token = data.get('jwt_token')
        errors = dict()
        credential_errors = list()
        jwt_errors = list()
        user = None
        if "@" in credential:
            if not User.objects.filter(email=credential).exists():
                credential_errors += [_("Email not found"), ]
            else:
                user = User.objects.filter(email=credential).first()
        else:
            if not User.objects.filter(username=credential).exists():
                credential_errors += [_("User not found"), ]
            else:
                user = User.objects.filter(username=credential).first()
        if credential_errors:
            errors['credential'] = credential_errors

        jwt_user = User.verify_jwt_token(jwt_token)
        if (user is not None and jwt_user is not None) and user != jwt_user:
            jwt_errors += [_("The given token does not match the user")]
        if User.verify_jwt_token(jwt_token) is None:
            jwt_errors += [_("jwt token invalid or expired")]
        if jwt_errors:
            errors['jwt_token'] = jwt_errors
        if errors:
            raise serializers.ValidationError(errors)
        return data


class UsernameSerializer(serializers.Serializer):
    username = serializers.CharField()

    def validate(self, data):
        username = data.get('username')
        errors = dict()
        username_errors = list()

        if User.objects.filter(username=username).exists():
            username_errors += [_("This username is already associated with an existing account."), ]

        if "@" in username:
            username_errors += [_("A username cannot include the symbol '@'."), ]

        if username_errors:
            errors['username'] = username_errors
            raise serializers.ValidationError(errors)
        return data
