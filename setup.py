#! /usr/bin/env python3
# coding: utf-8

"""
REMINDER:
1- build
./setup.py sdist bdist_wheel
2- basic verifications
twine check dist/*
2.5- Deploy on testpypi (optionnal, site here : https://test.pypi.org/):
twine upload --repository testpypi dist/*
3- upload to PyPi
twine upload dist/*
"""

from django_silly_auth import __version__
import pathlib
from setuptools import setup


# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="django-silly-auth",
    version=f"{__version__}",
    description=(
        "Authentication package for Django and DRF"
        ),
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/byoso/django_silly_auth",
    author="Vincent Fabre",
    author_email="peigne.plume@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
    ],
    packages=[
        "django_silly_auth",
        "django_silly_auth.templates",
        "django_silly_auth.templates.silly_auth",
        "django_silly_auth.templates.silly_auth._try",
        "django_silly_auth.templates.silly_auth.classic",
        "django_silly_auth.templates.silly_auth.emails",
        "django_silly_auth.templates.silly_auth.silly",
        "django_silly_auth.views",
        "django_silly_auth.locale",
        "django_silly_auth.locale.fr",
        "django_silly_auth.locale.fr.LC_MESSAGES",
        "django_silly_auth.locale.en",
        "django_silly_auth.locale.en.LC_MESSAGES",
        "django_silly_auth.tests",
        ],
    # include_package_data=True,
    package_data={'': ['*.txt', '*.html', '*.po', '*.mo', '*.pot']},
    python_requires='>=3.7',
    install_requires=[
        "pyjwt >= 2.6.0",
    ],
    keywords='django auth drf jwt',
    # entry_points={
    #     "console_scripts": [
    #         "django_silly_auth=main.cmd:cmd",
    #     ]
    # },
    setup_requires=['wheel'],
)
