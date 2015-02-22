from django.conf.urls import patterns, include, url

urlpatterns = patterns('socialnetwork.views',
    url(r'^$', 'home'),
    # Route for built-in authentication with our own custom login page
    url(r'^register$', 'register'),
    url(r'^following$', 'following'),
    url(r'^profile/(?P<username>[a-zA-Z0-9_\-\.]*)$','profile'),
    url(r'^profile/(?P<username>[a-zA-Z0-9_\-\.]*)/image$','get_image'),
    url(r'^comment/(?P<item_id>\d*)$', 'comment'),
    url(r'^editprofile$','edit'),
    url(r'^feed/home$','home_feed'),
)

urlpatterns += patterns('',
    url(r'^login$', 'django.contrib.auth.views.login', {'template_name':'socialnetwork/login.html'}),
    # Route to logout a user and send them back to the login page
    url(r'^logout$', 'django.contrib.auth.views.logout_then_login'),
    )

