from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.db import transaction
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.exceptions import (
    ValidationError,
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
    send_confirm_email,
    delete_unconfirmed
)


if conf["VERBOSE"]:
    print("=== DSA IMPORT django_silly_auth.views.api_view_if_drf")

User = get_user_model()


@transaction.atomic
@api_view(['POST'])
@permission_classes([AllowAny])
def resend_email_confirmation(request):
    """Resends an email to the user to confirm his account"""
    credential = request.data.get('credential')
    if not credential:
        msg = _("no credential provided")
        raise ValidationError({"error": msg}, code='authorization')
    if "@" in credential:
        user = User.objects.filter(email=credential).first()
    else:
        user = User.objects.filter(username=credential).first()
    if user:
        if user.is_confirmed:
            msg = _("Your account is already confirmed.")
            raise ValidationError({"error": msg}, code='authorization')
            # return Response({'error': _('account already confirmed')})
        send_confirm_email(request, user)
        return Response({'success': _('Email sent for password reset')})
    msg = "Invalid credential"
    raise ValidationError({"error": msg}, code='authorization')


@transaction.atomic
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def logout_api_view(request):
    """Destroys the auth token"""
    print("=== DSA LOGOUT API VIEW")
    request.user.auth_token.delete()
    return Response({'success': _('Logged out.')})


@transaction.atomic
@api_view(['POST'])
@permission_classes([AllowAny])
def request_password_reset(request):
    """Sends an email to the user with a link to reset their password"""
    credential = request.data.get('credential')
    if not credential:
        msg = _("No credentials were provided")
        raise ValidationError({"error": msg}, code='authorization')
    if "@" in credential:
        user = User.objects.filter(email=credential).first()
    else:
        user = User.objects.filter(username=credential).first()
    if user:
        send_password_reset_email(request, user)
        return Response({'success': _("Email sent for password reset")})
    msg = _("Invalid credential")
    raise ValidationError({"error": msg}, code='authorization')


class UserView(APIView):
    permission_classes = []

    @transaction.atomic
    def post(self, request, format=None):
        """Create a new user"""
        serializer = CreateUserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.set_password(request.data['password'])
            user.save()
            delete_unconfirmed(user)
            message = _(
                    f"Please check your inbox at '{user.email}' "
                    "to confirm your account. "
            )
            if conf["DELETE_UNCONFIRMED_TIME"] != 0:
                message += (
                    _("If you do not confirm your account within the next "),
                    _(f"{conf['DELETE_UNCONFIRMED_TIME']} hours, "),
                    _("it will be deleted.")
                )
            serializer = GetAllUsersSerializer(user)
            msg = {
                "user": serializer.data,
            }

            send_confirm_email(request, user)

            return Response(msg)
        else:
            msg = serializer.errors
            raise ValidationError({"error": msg}, code='authorization')


@transaction.atomic
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
        return Response({'success': _('Password successfully changed.')})
    msg = serializer.errors
    raise ValidationError({"error": msg}, code='authorization')


@transaction.atomic
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

        return Response(
            {'success': _(f"New email saved, check your inbox at '{new_email}' to activate it.")})
    msg = serializer.errors
    raise ValidationError({"error": msg}, code='authorization')
