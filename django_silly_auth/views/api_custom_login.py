
from django.db import transaction
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model


from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.serializers import ValidationError
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

from django_silly_auth.serializers import (
    LoginSerializer,
    CredentialJWTokenSerializer
    )
import django_silly_auth

if django_silly_auth.VERBOSE:
    print("=== DSA IMPORT django_silly_auth.views.api_custom_login")

User = get_user_model()


class LoginWithAuthToken(ObtainAuthToken):

    def post(self, request, *args, **kwargs):
        """Login view modified to use email or username as credential"""
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        credential = serializer.validated_data['credential']
        if "@" in credential:
            user = User.objects.filter(email=credential).first()
        else:
            user = User.objects.filter(username=credential).first()
        password = serializer.validated_data['password']
        match = False
        if user:
            match = user.check_password(password)
        if match:
            if not user.is_confirmed and not user.is_superuser:
                msg = _('Account not confirmed. Please check your email for a confirmation link.')
                raise ValidationError(msg, code='authorization')
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key})
        msg = _('Unable to log in with the provided credentials.')
        raise ValidationError(msg, code='authorization')


class LoginWithJWTToken(APIView):
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        serializer = CredentialJWTokenSerializer(data=request.data)
        msg = list()
        if serializer.is_valid():
            jwt_token = serializer.validated_data['jwt_token']
            user = User.verify_jwt_token(jwt_token)
            if not user.is_confirmed:
                user.is_confirmed = True
                user.new_email = None
                user.save()
                msg += [_("Your account has been confirmed, please change your password if necessary.")]
            if user.new_email:
                user.email = user.new_email
                user.new_email = None
                user.save()
                msg += [_("Your new email has been activated")]
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key, 'message': msg})
        raise ValidationError(serializer.errors, code='authorization')
