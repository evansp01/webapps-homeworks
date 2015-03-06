from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
# Decorator to use built-in authentication system
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404

# Used to create and manually log in a user
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.views.defaults import page_not_found
import mimetypes
import urllib
import os

# Django transaction system so we can use @transaction.atomic
from django.db import transaction

from socialnetwork.models import *
from socialnetwork.forms import *


@login_required
def profile(request, username):
    if request.POST:
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
    viewing = get_object_or_404(User, username=username)
    if not viewing.userprofile.image:
        image_location = 'pictures/default/default.jpg'
        full_path = os.path.join(settings.MEDIA_ROOT, 'default.jpg')
        #print full_path
        with open(full_path, "rb") as f:
            return HttpResponse(f.read(), content_type="image/jpeg")
        #return HttpResponse(image, content_type=content_type)
    
    # saving the mime type is clearly overrated
    image_location = viewing.userprofile.image
    url = urllib.pathname2url(image_location.name)
    content_type = mimetypes.guess_type(url)
    return HttpResponse(viewing.userprofile.image, content_type=content_type)



@login_required
def follow_or_unfollow(request, username):
    try:
        user = User.objects.get(username=username)
        form = FollowForm(request.POST)
        if form.is_valid():
            action = form.cleaned_data['action']
            if action == 'follow':
                request.user.userprofile.follows.add(user.userprofile)
            if action == 'unfollow':
                request.user.userprofile.follows.remove(user.userprofile)
    except ObjectDoesNotExist:
        pass
    return render_user(request, username)

@login_required
@transaction.atomic
def update_image(request, form):
    new_image = form.cleaned_data['image'] or form.cleaned_data['imageupdate']
    if new_image:
        if request.user.userprofile.image:
            try:
                file_name = os.path.join(settings.MEDIA_ROOT, request.user.userprofile.image.name)
                os.remove(file_name)
            except OSError:
                pass
        request.user.userprofile.image = form.cleaned_data['image']


@login_required
@transaction.atomic
def edit(request):
    context = {}
    if request.method == 'GET':
        current_form = ProfileForm(
            instance=request.user.userprofile, 
            initial={'first':request.user.first_name, 'last':request.user.last_name}
        )
        context["form"] = current_form
        return render(request, 'socialnetwork/update_profile.html', context)
    form = ProfileForm(request.POST, request.FILES)
    if form.is_valid():
        request.user.userprofile.bio = form.cleaned_data['bio']
        request.user.first_name = form.cleaned_data['first']
        request.user.last_name = form.cleaned_data['last']
        request.user.userprofile.age = form.cleaned_data['age']
        # only update an existing image to no image if the clear image checkbox
        # is checked
        update_image(request, form)
        request.user.userprofile.save()
        request.user.save()
    context["form"] = form
    return render(request, 'socialnetwork/update_profile.html', context)
