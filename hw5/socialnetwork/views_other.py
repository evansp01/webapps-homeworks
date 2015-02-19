from django.shortcuts import render, redirect
from django.core.exceptions import ObjectDoesNotExist

# Decorator to use built-in authentication system
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404

# Used to create and manually log in a user
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.views.defaults import page_not_found
import mimetypes
import urllib

# Django transaction system so we can use @transaction.atomic
from django.db import transaction

from socialnetwork.models import *
from socialnetwork.forms import *


@login_required
def render_global(request, form):
    items = Item.objects.all().order_by('-date')
    context = {}
    context['items'] = items
    context['user'] = request.user
    context['global_posts'] = len(Item.objects.all())
    context['user_posts'] = len(Item.objects.filter(user=request.user))
    context['form'] = form
    return render(request, 'socialnetwork/home_feed.html', context)


@login_required
def render_following(request):
    items = []
    # because who needs to know how to query the database properly
    following = request.user.userprofile.follows.all()
    for profile in following:
        items.extend(Item.objects.filter(user=profile.userkey))
    items.sort(key=lambda x: x.date)
    items.reverse()
    context = {}
    context['items'] = items
    context['following'] = following
    context['user'] = request.user
    context['global_posts'] = len(Item.objects.all())
    context['user_posts'] = len(Item.objects.filter(user=request.user))
    return render(request, 'socialnetwork/following_feed.html', context)


@login_required
def following(request):
    return render_following(request)


@login_required
def home(request):
    if request.POST:
        return add_item(request)
    else:
        return render_global(request, ItemForm())


@login_required
@transaction.atomic
def add_item(request):
    form = ItemForm(request.POST)
    if form.is_valid():
        new_item = Item(text=form.cleaned_data['text'], user=request.user)
        new_item.save()
    return render_global(request, form)


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
    else:
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        new_user = User.objects.create_user(
            username=username, password=password)
        UserProfile.objects.create(
            userkey=new_user,
            first=form.cleaned_data['first_name'],
            last=form.cleaned_data['last_name'],
            bio='',
        )
        new_user = authenticate(username=username, password=password)
        login(request, new_user)
        return redirect('/')
