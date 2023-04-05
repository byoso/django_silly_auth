from django_silly_auth.config import SILLY_AUTH_SETTINGS as conf


print("=== IMPORT django_silly_auth.views.api_views")

if conf["USE_DRF"]:
    from django_silly_auth.views.api_views_if_drf import *
    print("=== * FROM django_silly_auth.api_views_if_drf")
