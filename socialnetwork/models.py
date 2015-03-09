from django.db import models
import os

# User class for built-in authentication module
from django.contrib.auth.models import User

class Post(models.Model):
    text = models.CharField(max_length=140)
    user = models.ForeignKey(User)
    date = models.DateTimeField(auto_now_add=True)
    def __unicode__(self):
        return self.text

class Comment(models.Model):
    text = models.CharField(max_length=140)
    user = models.ForeignKey(User)
    date = models.DateTimeField(auto_now_add=True)
    post = models.ManyToManyField(Post, related_name='comments', symmetrical=False)
    def __unicode__(self):
        return self.text


class UserProfile(models.Model):
    userkey = models.OneToOneField(User)
    age = models.PositiveIntegerField(null=True)
    bio = models.CharField(max_length=430, blank=True)
    image = models.ImageField(upload_to="pictures", blank=True)
    follows = models.ManyToManyField('self', related_name='followers', symmetrical=False)


