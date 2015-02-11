from django.shortcuts import render, redirect
from django.core.exceptions import ObjectDoesNotExist

# Decorator to use built-in authentication system
from django.contrib.auth.decorators import login_required

# Used to create and manually log in a user
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.views.defaults import page_not_found
import datetime
import re

# Django transaction system so we can use @transaction.atomic
from django.db import transaction

from socialnetwork.models import *

CHARLIMIT = 160

@login_required
def render_global(request):
    items = Item.objects.all().order_by('-date')
    context = {}
    context['items'] = items
    context['user'] = request.user
    context['global_posts'] = len(Item.objects.all())
    context['user_posts'] = len(Item.objects.filter(user = request.user))
    return render(request,'socialnetwork/index.html',context)

@login_required
def render_user(request, username):
    try:
        viewing = User.objects.get(username=username)
    except ObjectDoesNotExist:
        return page_not_found(request)
    items = Item.objects.filter(user=viewing).order_by('-date')
    context = {}
    context['items'] = items
    context['user'] = request.user
    context['viewing'] = viewing
    context['global_posts'] = len(Item.objects.all())
    context['user_posts'] = len(Item.objects.filter(user = request.user))
    context['viewing_posts'] = len(Item.objects.filter(user = viewing))
    return render(request,'socialnetwork/profile.html',context)


@login_required
def user_profile(request, username):
    if request.POST:
        return delete_item(request, username)
    else:
        return render_user(request, username)

@login_required
def home(request):        
    if request.POST:
        return add_item(request)
    else:
        return render_global(request)


@login_required
@transaction.atomic
def add_item(request):
    errors = []

    # Creates a new item if it is present as a parameter in the request
    if not 'item' in request.POST or not request.POST['item']:
        errors.append('You must enter an item to add.')
    else:
        if len(request.POST['item']) > CHARLIMIT:
            errors.append('Item cannot be longer than {} characters' % CHARLIMIT)
        else:
            new_item = Item(text=request.POST['item'], user=request.user,
                            date=datetime.datetime.now())
            new_item.save()
    return render_global(request)


@login_required
@transaction.atomic
def delete_item(request, username):
    errors = []
    if not 'item_id' in request.POST:
        errors.append("You must specify the item to delete")
    else:
        try: # Deletes item if the logged-in user has an item matching the id
            item_id = request.POST['item_id']
            item_to_delete = Item.objects.get(id=item_id, user=request.user)
            item_to_delete.delete()
        except ObjectDoesNotExist:
            errors.append('You have not posted this item')

    return render_user(request, username)


def validate_registration(request, context):
    errors = []
    context['errors'] = errors
    # Checks the validity of the form data
    if not 'username' in request.POST or not request.POST['username']:
        errors.append('Username is required.')
    else:
        # Save the username in the request context to re-fill the username
        # field in case the form has errrors
        valid_usernames = re.compile("^[a-zA-Z0-9_\-\.]*$")
        if not valid_usernames.match(request.POST['username']):
            errors.append('Usernames can contain letters (a-z), '+
                'numbers (0-9), dashes (-), underscores (_) and periods (.)')
        else:
            context['username'] = request.POST['username']
    if not 'first' in request.POST or not request.POST['first']:
        errors.append('First name is required.')
    else:
        # Save the first in the request context to re-fill the first
        # field in case the form has errrors
        context['first'] = request.POST['first']
    if not 'last' in request.POST or not request.POST['last']:
        errors.append('Last name is required.')
    else:
        # Save the last in the request context to re-fill the last
        # field in case the form has errrors
        context['last'] = request.POST['last']

    if not 'password1' in request.POST or not request.POST['password1']:
        errors.append('Password is required.')
    if not 'password2' in request.POST or not request.POST['password2']:
        errors.append('Confirm password is required.')

    if 'password1' in request.POST and 'password2' in request.POST \
            and request.POST['password1'] and request.POST['password2'] \
            and request.POST['password1'] != request.POST['password2']:
        errors.append('Passwords did not match.')
    return errors


@transaction.atomic
def register(request):
    context = {}

    # Just display the registration form if this is a GET request
    if request.method == 'GET':
        return render(request, 'socialnetwork/register.html', context)

    # Ensure that the information given in the form was valid
    errors = validate_registration(request, context)
    
    # Check that the username is not already taken
    if len(User.objects.filter(username=request.POST['username'])) > 0:
        errors.append('Username is already taken.')

    if errors:
        return render(request, 'socialnetwork/register.html', context)

    # Creates the new user from the valid form data
    new_user = User.objects.create_user(username=request.POST['username'],
                                        password=request.POST['password1'])
    new_user.first_name = request.POST['first']
    new_user.last_name  = request.POST['last']
    new_user.save()

    # Logs in the new user and redirects to his/her todo list
    new_user = authenticate(username=request.POST['username'],
                            password=request.POST['password1'])
    login(request, new_user)
    return redirect('/')
