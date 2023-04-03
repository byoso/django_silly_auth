from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import get_user_model
from django.contrib.auth import login
from django.contrib.auth.hashers import check_password
from django.contrib.auth.decorators import login_required


from django_silly_auth.config import SILLY_AUTH_SETTINGS as conf
from django_silly_auth.forms import NewPasswordForm, NewEmailConfirmForm

User = get_user_model()


def reset_password(request, token):
    user = User.verify_jwt_token(token)
    if not user:
        return HttpResponse('error: invalid token')
    if request.method == 'POST':
        form = NewPasswordForm(request.POST)
        if form.is_valid():
            user.set_password(form.cleaned_data['password'])
            user.is_active = True
            user.save()
            return render(request, conf["RESET_PASSWORD_DONE_TEMPLATE"], {'link': conf["SITE_URL"]})
        else:
            return render(request, conf["RESET_PASSWORD_TEMPLATE"], {'form': form})

    if user:
        if not user.confirmed:
            user.confirmed = True
            user.save()
        # login(request, user)
        context = {
            "user": user,
            "site_name": conf["SITE_NAME"],
            "form": NewPasswordForm(),
            "base_template": conf["BASE_TEMPLATE"],
        }
        return render(request, conf["RESET_PASSWORD_TEMPLATE"], context)


@login_required
def password_reset_done(request):
    context = {
        "site_name": conf["SITE_NAME"],
        "link": conf["SITE_URL"],
        "base_template": conf["BASE_TEMPLATE"],
    }
    return render(request, conf["RESET_PASSWORD_DONE_TEMPLATE"], context)


def confirm_new_email(request, token):
    """Recieves the token given by email and confirms the user's account"""
    if request.method == 'POST':
        user = User.verify_jwt_token(token)
        if user and user.new_email:
            form = NewEmailConfirmForm(request.POST)
            if form.is_valid():
                match = check_password(form.cleaned_data['password'], user.password)
                if match:
                    user.email = user.new_email
                    user.new_email = None
                    user.save()
                    context = {
                        "user": user,
                        "site_name": conf["SITE_NAME"],
                        "link": conf["SITE_URL"]
                    }
                    return render(request, conf["NEW_EMAIL_CONFIRMED_DONE_TEMPLATE"], context)
                form.add_error('password', 'Invalid password')
            context = {
                "form": form,
                "user": user,
                "site_name": conf["SITE_NAME"],
            }
            return render(request, conf["NEW_EMAIL_CONFIRM_TEMPLATE"], context)

    else:
        user = User.verify_jwt_token(token)
        if user and user.new_email:
            form = NewEmailConfirmForm()
            context = {
                "form": form,
                "user": user,
                "site_name": conf["SITE_NAME"],
            }
            return render(request, conf["NEW_EMAIL_CONFIRM_TEMPLATE"], context)
    if conf["SITE_URL"]:
        return redirect(conf["SITE_URL"])
    return HttpResponse('error: invalid token or no email change ongoing')


def email_change_done(request):
    context = {

    }
    return render(request, conf["NEW_EMAIL_DONE_TEMPLATE"], context)