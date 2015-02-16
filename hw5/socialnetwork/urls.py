from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^$', 'socialnetwork.views.home'),
    # Route for built-in authentication with our own custom login page
    url(r'^login$', 'django.contrib.auth.views.login', {'template_name':'socialnetwork/login.html'}),
    # Route to logout a user and send them back to the login page
    url(r'^logout$', 'django.contrib.auth.views.logout_then_login'),
    url(r'^register$', 'socialnetwork.views.register'),
    url(r'^following$', 'socialnetwork.views.following'),
    url(r'^profile/(?P<username>[a-zA-Z0-9_\-\.]*)$','socialnetwork.views.profile'),
)

