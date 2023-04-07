from django_silly_auth import SILLY_AUTH_SETTINGS as conf
import django_silly_auth

if django_silly_auth.VERBOSE:
    print("=== DSA IMPORT django_silly_auth.views.api_views")
    if conf["USE_DRF"]:
        print("=== DSA IMPORT django_silly_auth.views.api_views_if_drf")

if conf["USE_DRF"]:
    from django_silly_auth.views.api_views_if_drf import *
