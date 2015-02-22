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
def profile(request, username):
    if request.POST and 'action' in request.POST:
        return follow_or_unfollow(request, username)
    else:
        return render_user(request, username)


@login_required
def render_user(request, username):
    try:
        viewing = User.objects.get(username=username)
    except ObjectDoesNotExist:
        return page_not_found(request)
    items = Post.objects.filter(user=viewing).order_by('-date')
    context = {}
    context['items'] = items
    context['user'] = request.user
    context['viewing'] = viewing
    context['following'] = request.user.userprofile.follows.all()
    context['global_posts'] = len(Post.objects.all())
    context['user_posts'] = len(Post.objects.filter(user=request.user))
    context['viewing_posts'] = len(Post.objects.filter(user=viewing))
    context['cform'] = CommentForm()
    return render(request, 'socialnetwork/profile_feed.html', context)


def get_image(request, username):
    try:
        viewing = User.objects.get(username=username)
        if not viewing.userprofile.image:
            raise Http404
        # saving the mime type is clearly overrated
        url = urllib.pathname2url(viewing.userprofile.image.name)
        content_type = mimetypes.guess_type(url)
        return HttpResponse(viewing.userprofile.image, content_type=content_type)
    except ObjectDoesNotExist:
        return page_not_found(request)


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
@transaction.atomic
def edit(request):
    context = {}
    if request.method == 'GET':
        context["form"] = ProfileForm(instance=request.user.userprofile)
        return render(request, 'socialnetwork/update_profile.html', context)
    form = ProfileForm(request.POST, request.FILES)
    if form.is_valid():
        request.user.userprofile.bio = form.cleaned_data['bio']
        request.user.userprofile.first = form.cleaned_data['first']
        request.user.userprofile.last = form.cleaned_data['last']
        request.user.userprofile.age = form.cleaned_data['age']
        # only update an existing image to no image if the clear image checkbox
        # is checked
        if not form.cleaned_data['image']:
            if form.cleaned_data['imageupdate']:
                request.user.userprofile.image = form.cleaned_data['image']
        else:
            request.user.userprofile.image = form.cleaned_data['image']
        request.user.userprofile.save()
    context["form"] = form
    return render(request, 'socialnetwork/update_profile.html', context)
