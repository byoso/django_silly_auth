from django.contrib.auth import get_user_model
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.exceptions import (
    ValidationError,
    PermissionDenied,
    NotFound,
    AuthenticationFailed
    )

from django_silly_auth.serializers import (
    GetAllUsersSerializer,
    CreateUserSerializer,
    PasswordsSerializer,
    EmailSerializer,
    )
from django_silly_auth.config import SILLY_AUTH_SETTINGS as conf
from django_silly_auth.utils import (
    send_password_reset_email,
    send_confirm_email
)
from django_silly_auth.utils import warning


print("=== IMPORT django_silly_auth.api_view_if_drf")

User = get_user_model()


@api_view(['GET'])
@permission_classes([AllowAny])
def confirm_email(request, token):
    """Recieves the token given by email and confirms the user's account"""
    user = User.verify_jwt_token(token)
    if user:
        user.is_confirmed = True
        user.save()
        return Response({'success': _('account confirmed')})
    msg = "Invalid Token"
    raise ValidationError(msg, code='authorization')


@api_view(['POST'])
@permission_classes([AllowAny])
def resend_email_confirmation(request):
    """Reends an email to the user to confirm his account"""
    credential = request.data.get('credential')
    if not credential:
        raise ValidationError(_("no credential provided"), code='authorization')
    if "@" in credential:
        user = User.objects.filter(email=credential).first()
    else:
        user = User.objects.filter(username=credential).first()
    if user:
        if user.is_confirmed:
            return Response({'error': _('account already confirmed')})
        send_confirm_email(request, user)
        return Response({'success': _('email sent for password reset')})
    msg = "Invalid credential"
    raise ValidationError(msg, code='authorization')


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def logout_api_view(request):
    """Destroys the auth token"""
    request.user.auth_token.delete()
    return Response({'success': _('logged out, token destroyed')})


@api_view(['POST'])
@permission_classes([AllowAny])
def request_password_reset(request):
    """Sends an email to the user with a link to reset their password"""
    credential = request.data.get('credential')
    if not credential:
        raise ValidationError(_("no credential provided"), code='authorization')
    if "@" in credential:
        user = User.objects.filter(email=credential).first()
    else:
        user = User.objects.filter(username=credential).first()
    if user:
        send_password_reset_email(request, user)
        return Response({'success': _('email sent for password reset')})
    msg = "Invalid credential"
    raise ValidationError(msg, code='authorization')


@api_view(['GET'])
@permission_classes([AllowAny])
def reset_password(request, token):
    """Recieves the token given by email and confirms the user's account"""
    user = User.verify_jwt_token(token)
    if user:
        if not user.is_confirmed:
            user.is_confirmed = True
            user.save()
        if conf["PASSWORD_RESET_REDIRECT"]:
            return redirect(conf["PASSWORD_RESET_REDIRECT"])
        return Response({'success': _(f'{user.name} identifyed, password changed')})
    msg = _("Invalid Token")
    raise ValidationError(msg, code='authorization')


class UserView(APIView):
    permission_classes = []

    def get(self, request, format=None):
        """GET all users, only for testing purposes"""
        if conf["GET_ALL_USERS"]:
            warning(
                "WARNING: SILLY_AUTH[\"GET_ALL_USERS\"] "
                "== True, set it to False in production."
            )
            users = User.objects.all()
            serializer = GetAllUsersSerializer(users, many=True)
            return Response({'users': serializer.data})
        else:
            msg = _("Request not allowed")
            raise PermissionDenied(msg, code='authorization')

    def post(self, request, format=None):
        """Create a new user"""
        serializer = CreateUserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.set_password(request.data['password'])
            user.save()
            serializer = GetAllUsersSerializer(user)
            msg = {
                "user": serializer.data,
            }

            if conf["EMAIL_SEND_ACCOUNT_CONFIRM_LINK"]:
                msg["message"] = _("Account created, check your inbox to activate it")
                send_confirm_email(request, user)

            return Response(msg)
        else:
            msg = serializer.errors
            raise ValidationError(msg, code='authorization')


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    """Changes the user's password"""
    serializer = PasswordsSerializer(data=request.data)
    if serializer.is_valid():
        user = request.user
        password = request.data.get('password')
        user.set_password(password)
        user.save()
        return Response({'success': _('password changed')})
    msg = serializer.errors
    raise ValidationError(msg, code='authorization')


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_email_request(request):
    user = request.user
    serializer = EmailSerializer(data=request.data)
    if serializer.is_valid():
        new_email = request.data.get('email')
        user.new_email = new_email
        user.save()
        send_confirm_email(request, user, new_email=True)

        return Response({'success': _('New email saved, check your inbox to activate it')})
    msg = serializer.errors
    raise ValidationError(msg, code='authorization')
