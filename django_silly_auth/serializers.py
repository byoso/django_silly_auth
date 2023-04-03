from django.contrib.auth import get_user_model
from django.core import exceptions
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

User = get_user_model()


class GetAllUsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email')


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
            username_errors += ["A username must not contain '@'", ]

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
            password_errors += ["Passwords don't match", ]

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
            email_errors += ["Email already in use", ]

        if email_errors:
            errors['email'] = email_errors
            raise serializers.ValidationError(errors)
        return data