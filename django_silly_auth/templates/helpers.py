import os

templates_dir = os.path.dirname(__file__)


def dsa_template_path(template_name):
    return os.path.join(templates_dir, template_name)