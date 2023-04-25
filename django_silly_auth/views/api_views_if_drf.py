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
    UserInfosSerializer,
    GetAllUsersSerializer,
    CreateUserSerializer,
    PasswordsSerializer,
    EmailSerializer,
    UsernameSerializer,
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
def email_confirm_email_resend(request):
    """Resends an email to the user to confirm his account"""
    credential = request.data.get('credential')
    if not credential:
        error = _("no credential provided")
        raise ValidationError({"detail": [error]}, code='authorization')
    if "@" in credential:
        user = User.objects.filter(email=credential).first()
    else:
        user = User.objects.filter(username=credential).first()
    if user:
        if user.is_confirmed:
            error = _("Your account is already confirmed.")
            raise ValidationError({"detail": [error]}, code='authorization')
        send_confirm_email(request, user)
        return Response({'success': _('Email sent for password reset')})
    error = "Invalid credential"
    raise ValidationError({"detail": [error]}, code='authorization')


@transaction.atomic
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def token_logout(request):
    """Destroys the auth token"""
    request.user.auth_token.delete()
    return Response({'success': _('Logged out.')})


@transaction.atomic
@api_view(['POST'])
@permission_classes([AllowAny])
def password_request_reset(request):
    """Sends an email to the user with a link to reset their password"""
    credential = request.data.get('credential')
    if not credential:
        error = _("No credentials were provided")
        raise ValidationError({"detail": [error]}, code='authorization')
    if "@" in credential:
        user = User.objects.filter(email=credential).first()
    else:
        user = User.objects.filter(username=credential).first()
    if user:
        send_password_reset_email(request, user)
        return Response({'success': _("Email sent for password reset")})
    error = _("Invalid credential")
    raise ValidationError({"detail": [error]}, code='authorization')


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
            message1 = _(
                "Please check your inbox at '%(email)s' to confirm your account. "
                ) % {'email': user.email}
            if conf["DELETE_UNCONFIRMED_TIME"] != 0:
                message2 = _(
                    "If you do not confirm your account within the next "
                    "%(hours)s hours, it will be deleted."
                    ) % {'hours': conf['DELETE_UNCONFIRMED_TIME']}

                message = "%(message1)s %(message2)s" % {
                    'message1': message1,
                    'message2': message2,
                }
            serializer = UserInfosSerializer(user)
            msg = {
                "user": serializer.data,
                "message": message,
            }

            send_confirm_email(request, user)

            return Response(msg)
        else:
            error = serializer.errors
            raise ValidationError(error, code='authorization')


@api_view(['GET'])
def get_users_all(request):
    """!! FOR DEV ONLY !! Get all users"""
    users = User.objects.all()
    serializer = GetAllUsersSerializer(users, many=True)
    return Response(serializer.data)


@transaction.atomic
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def password_change(request):
    """Changes the user's password"""
    serializer = PasswordsSerializer(data=request.data)
    if serializer.is_valid():
        user = request.user
        password = request.data.get('password')
        user.set_password(password)
        user.save()
        return Response({'success': _('Password successfully changed.')})
    error = serializer.errors
    raise ValidationError(error, code='authorization')


@transaction.atomic
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def email_request_change(request):
    user = request.user
    serializer = EmailSerializer(data=request.data)
    if serializer.is_valid():
        new_email = request.data.get('email')
        user.new_email = new_email
        user.save()
        send_confirm_email(request, user, new_email=True)

        return Response(
            {'success': _(
                "New email saved, check your inbox at '%(new_email)s' "
                "to activate it."
            ) % {'new_email': new_email}}
        )
    error = serializer.errors
    raise ValidationError(error, code='authorization')


@transaction.atomic
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def username_change(request):
    """Changes the user's username"""
    serializer = UsernameSerializer(data=request.data)
    if serializer.is_valid():
        user = request.user
        username = request.data.get('username')
        user.username = username
        user.save()
        return Response({'success': _('Username successfully changed.')})
    error = serializer.errors
    raise ValidationError(error, code='authorization')


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def users_my_infos(request):
    """Returns the user's infos"""
    serializer = UserInfosSerializer(request.user)
    return Response(serializer.data)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def users_delete_me(request):
    """Deletes the user's account"""
    request.user.auth_token.delete()
    request.user.delete()
    return Response({'success': _('Account successfully deleted.')})
