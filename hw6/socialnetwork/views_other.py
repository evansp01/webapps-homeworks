from django.shortcuts import render, redirect
from django.core.exceptions import ObjectDoesNotExist
from django.template.loader import render_to_string
from django.middleware.csrf import get_token
import json


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
    items = Post.objects.all().order_by('-date')
    context = {}
    context['items'] = items
    context['user'] = request.user
    context['global_posts'] = len(Post.objects.all())
    context['user_posts'] = len(Post.objects.filter(user=request.user))
    context['form'] = form
    context['cform'] = CommentForm()
    return render(request, 'socialnetwork/home_feed.html', context)


@login_required
def render_following(request):
    items = []
    # because who needs to know how to query the database properly
    items = Post.objects.filter(
                 user__in=request.user.userprofile.follows.all(),             
                 ).order_by('-date')
    context = {}
    context['items'] = items
    context['following'] = request.user.userprofile.follows.all()
    context['user'] = request.user
    context['global_posts'] = len(Post.objects.all())
    context['user_posts'] = len(Post.objects.filter(user=request.user))
    context['cform'] = CommentForm()
    return render(request, 'socialnetwork/following_feed.html', context)


@login_required
def following(request):
    return render_following(request)


@login_required
def home(request):
    if request.POST:
        return add_item(request)
    else:
        return render_global(request, PostForm())

def home_feed(request):
    if request.GET:
        value = -1
        if 'last' in request.GET:
            value = int(request.GET['last'])
        items = Post.objects.all().order_by('-date')
        top = items[0].id
        index = 0
        for i, item in enumerate(items):
            print "id ", item.id, "value ", value
            if int(item.id) == int(value):
                index = i
                break
        items = items[0:index]
        csrf_token_value = get_token(request)
        feed = render_to_string("socialnetwork/item.html",{"items":items,
            "csrf_token": csrf_token_value, "cform":CommentForm()})
        response = {"html":feed,"last": top}
        jsond = json.dumps(response)
        return HttpResponse(jsond, content_type='application/json')


def comment(request, item_id):
    if request.POST:
        form = CommentForm(request.POST);
        if form.is_valid():
            comment = Comment(text = form.cleaned_data['text'],
                              user = request.user)
            comment.save()
            post = Post.objects.get(id=item_id)
            post.comments.add(comment)
            post.save()
            print "happy"
            return render(request, 'socialnetwork/comments.html', {"item":post})
        else:
            return page_not_found(request)

    return HttpResponse(
        "{}",
        content_type="application/json"
    )

@login_required
@transaction.atomic
def add_item(request):
    form = PostForm(request.POST)
    if form.is_valid():
        new_item = Post(text=form.cleaned_data['text'], user=request.user)
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
