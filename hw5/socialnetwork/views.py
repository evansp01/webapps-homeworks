from django.shortcuts import render, redirect
from django.core.exceptions import ObjectDoesNotExist

# Decorator to use built-in authentication system
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404

# Used to create and manually log in a user
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.views.defaults import page_not_found
import datetime
import re
import mimetypes, urllib

# Django transaction system so we can use @transaction.atomic
from django.db import transaction

from socialnetwork.models import *
from socialnetwork.forms import *

CHARLIMIT = 160


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
    context['following'] = request.user.userprofile.follows.all()
    context['global_posts'] = len(Item.objects.all())
    context['user_posts'] = len(Item.objects.filter(user=request.user))
    context['viewing_posts'] = len(Item.objects.filter(user=viewing))
    return render(request, 'socialnetwork/profile_feed.html', context)


@login_required
def render_following(request):
    items = []
    #because who needs to know how to query the database properly
    following = request.user.userprofile.follows.all()
    for profile in following:
        items.extend(Item.objects.filter(user=profile.userkey))
    items.sort(key= lambda x : x.date)
    items.reverse()
    context = {}
    context['items'] = items
    context['following'] = following
    context['user'] = request.user
    context['global_posts'] = len(Item.objects.all())
    context['user_posts'] = len(Item.objects.filter(user=request.user))
    return render(request, 'socialnetwork/following_feed.html', context)


@login_required
def follow_or_unfollow(request, username):
    try:
        user = User.objects.get(username=username)
        if request.POST['action'] == 'follow':
            request.user.userprofile.follows.add(user.userprofile)
        if request.POST['action'] == 'unfollow':
            request.user.userprofile.follows.remove(user.userprofile)
    except ObjectDoesNotExist:
        pass
    return render_user(request, username)


@login_required
def following(request):
    return render_following(request)


@login_required
def profile(request, username):
    if request.POST and 'action' in request.POST:
        if request.POST['action'] == 'delete':
            return delete_item(request, username)
        return follow_or_unfollow(request, username)
    else:
        return render_user(request, username)


@login_required
def home(request):
    if request.POST:
        return add_item(request)
    else:
        return render_global(request, ItemForm())


@login_required
@transaction.atomic
def edit(request):
    context = {}
    if request.method == 'GET':
        context["form"] = ProfileForm(instance = request.user.userprofile)
        return render(request, 'socialnetwork/update_profile.html', context)
    form = ProfileForm(request.POST, request.FILES)
    if form.is_valid():
        request.user.userprofile.bio = form.cleaned_data['bio']
        request.user.userprofile.first = form.cleaned_data['first']
        request.user.userprofile.last = form.cleaned_data['last']
        request.user.userprofile.age = form.cleaned_data['age']
        #only update an existing image to no image if the clear image checkbox is checked
        if request.user.userprofile.image:
            if form.cleaned_data['imageupdate']:
                request.user.userprofile.image = form.cleaned_data['image']
        else:
            request.user.userprofile.image = form.cleaned_data['image']
        request.user.userprofile.save()
    context["form"] = form
    return render(request, 'socialnetwork/update_profile.html', context)

def get_image(request, username):
    try:
        viewing = User.objects.get(username=username)
        if not viewing.userprofile.image:
            raise Http404
        #saving the mime type is clearly overrated
        url = urllib.pathname2url(viewing.userprofile.image.name)
        content_type = mimetypes.guess_type(url)
        return HttpResponse(viewing.userprofile.image, content_type=content_type)
    except ObjectDoesNotExist:
        return page_not_found(request)

@login_required
@transaction.atomic
def add_item(request):
    form = ItemForm(request.POST)
    if form.is_valid():
        new_item = Item(text=form.cleaned_data['text'], user=request.user)
        new_item.save()
    return render_global(request, form)


@login_required
@transaction.atomic
def delete_item(request, username):
    if 'item_id' in request.POST:
        try:  # Deletes item if the logged-in user has an item matching the id
            item_id = request.POST['item_id']
            item_to_delete = Item.objects.get(id=item_id, user=request.user)
            item_to_delete.delete()
        except ObjectDoesNotExist:
            #this form was generated by me. If the item was already deleted
            #then we did what they wanted. If it did not exist, then they
            #mucked around with forms
            pass
    return render_user(request, username)


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
