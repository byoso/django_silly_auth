import os

templates_dir = os.path.dirname(__file__)


def dsa_template_path(template_name):
    """Don't use it, django can deal with path by itself"""
    # return os.path.join(templates_dir, template_name)
    return template_name
