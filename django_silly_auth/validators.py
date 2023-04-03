from django.core.exceptions import ValidationError


def validate_email(email):
    # TODO: refactor with a more precise regex
    if "@" not in email:
        raise ValidationError(f"'{email}' is not a valid email address")


def validate_username(username):
    if "@" in username:
        raise ValidationError("Username must not contain '@'")