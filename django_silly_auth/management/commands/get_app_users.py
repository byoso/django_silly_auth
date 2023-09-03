import os
import shutil
from pathlib import Path

from django.core.management.base import BaseCommand


DSAP_DIR = Path(__file__).resolve().parent.parent.parent


class Command(BaseCommand):
    """Django command to get the application _users installed in the project"""

    def handle(self, *args, **options):

        from_directory = os.path.join(DSAP_DIR, "plop/_users")
        shutil.copytree(
            from_directory, os.path.join(os.getcwd(), '_users'))

        print(
            "_user application added, \n"
            "do not forget to "
            "- add _users to INSTALLED_APPS \n"
            "- AUTH_USER_MODEL = '_users.User' \n"
            "- makemigrations and migrate \n"
            )
