from rest_framework import parsers, renderers
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.compat import coreapi, coreschema
from rest_framework.response import Response
from rest_framework.schemas import ManualSchema
from rest_framework.schemas import coreapi as coreapi_schema
from rest_framework.views import APIView

from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.serializers import ValidationError
from django.utils.translation import gettext_lazy as _


class LoginWithAuthToken(ObtainAuthToken):

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        # custom part here:########################
        if not user.confirmed and not user.is_superuser:
            msg = _('Account not confirmed. Please check your email for a confirmation link.')
            raise ValidationError(msg, code='authorization')
        # end of customization ####################
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key})


login_with_auth_token = LoginWithAuthToken.as_view()