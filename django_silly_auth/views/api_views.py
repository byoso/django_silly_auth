from django_silly_auth.config import SILLY_AUTH_SETTINGS as conf

if conf["VERBOSE"]:
    print("=== DSA IMPORT django_silly_auth.views.api_views")
    if conf["USE_DRF"]:
        print("=== DSA IMPORT django_silly_auth.views.api_views_if_drf")

if conf["USE_DRF"]:
    from django_silly_auth.views.api_views_if_drf import *
    from django_silly_auth.views.api_custom_login import (
        LoginWithAuthToken,
        LoginWithJWTToken,
    )
