from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.template.loader import render_to_string
from django.middleware.csrf import get_token
import json
from django.core.urlresolvers import reverse


# Decorator to use built-in authentication system
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404

# Used to create and manually log in a user
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.views.defaults import page_not_found
import mimetypes
import urllib
from django.contrib.auth.tokens import default_token_generator

# Django transaction system so we can use @transaction.atomic
from django.db import transaction
from django.core.mail import send_mail

from socialnetwork.models import *
from socialnetwork.forms import *

@transaction.atomic
def register(request):
    context = {}
    # Just display the registration form if this is a GET request
    if request.method == 'GET':
        context['form'] = RegisterForm()
        return render(request, 'socialnetwork/register.html', context)
    form = RegisterForm(request.POST)
    if not form.is_valid():
        context['form'] = form
        return render(request, 'socialnetwork/register.html', context)
    #everything is okay, register
    username = form.cleaned_data['username']
    password = form.cleaned_data['password']
    new_user = User.objects.create_user(
        username=username, 
        password=password,
        first_name=form.cleaned_data['first_name'],
        last_name=form.cleaned_data['last_name'],
        email=form.cleaned_data['email'],
    )
    new_user.is_active = False
    new_user.save()

    UserProfile.objects.create(
        userkey=new_user,
        bio='',
    )
    return send_email(new_user, request)


html_body = \
"""
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
        <title>Example document</title>
    </head>
    <body>

    <p>Dear %s,</p>

    <p>Congratulations! Your application to The Social Network has been accepted.
    Please click <a href="%s">here</a> to verify your email address.</p>

    <p>If that didn't work, copy and paste the folowing line into your address bar:</p>

    <p>%s</p>

    <p>If this request was not made by you, it is probably the end of the world,
    and we encourage you to panic!</p>

    <p>Warm Regards,</p>

    <p>The Team</p>

    </body>
</html>
"""


text_body = \
"""
Dear %s

Congratulations! Your application to The Social Network has been accepted.
Please copy and paste the folowing line into your address bar:

%s

If this request was not made by you, it is probably the end of the world,
and we encourage you to panic!

Warm Regards,

The Team
"""

def send_email(new_user, request):
    token = default_token_generator.make_token(new_user)

    url = request.get_host() + reverse('socialnetwork.views.confirm', args=(new_user.username, token))
    email_html = html_body % (new_user.username, url, url)
    email_text = text_body % (new_user.username, url)

    send_mail(subject="Verify your email address",
              html_message=email_html,
              message= email_text,
              from_email="yolo@cmu.edu",
              recipient_list=[new_user.email])
    context = {}
    context['confirm'] = new_user.email
    return render(request, 'socialnetwork/confirm_sent.html', context)


@transaction.atomic
def confirm(request, username, token):
    user = get_object_or_404(User, username=username)

    # Send 404 error if token is invalid
    if not default_token_generator.check_token(user, token):
        raise Http404

    # Otherwise token was valid, activate the user.
    user.is_active = True
    user.save()
    context = {}
    context['user'] = user
    return render(request, 'socialnetwork/account_confirmed.html', context)


