
from django.utils.translation import gettext

from django.utils.functional import lazy
from django.utils.translation import gettext_lazy
from django.conf import settings



# in django.utils.translation:
# gettext_lazy = lazy(gettext, str)


if settings.USE_I18N:
    gettext_lazy = gettext_lazy
else:
    def gettext_lazy(string):
        """The users may want to use DSA with or without i18n. this is a helper function to make it work both ways.
        Use this gettext_lazy function instead of the original django's gettext_lazy in the code:
        from django_silly_auth.translation import gettext_lazy as _
        """
        return string
