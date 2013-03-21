from django.conf.urls import patterns, include, url
from django.views.generic.simple import direct_to_template

urlpatterns = patterns('udacity253.apps.4_cookiesusers.views',

    # View the problem solution 
    # url(r'^$', 'index'),
    # Udacity wasn't happy with signup/$, had to be signup$
    url(r'^$', 'signup', name='cookiesusers_signup'),
    url(r'^signup$', 'signup', name='cookiesusers_signup'),
    url(r'^login$', 'login', name='cookiesusers_login'),
    url(r'^logout$', 'logout', name='cookiesusers_logout'),
    url(r'^welcome/$', 'welcome', name='cookiesusers_welcome',),

)
