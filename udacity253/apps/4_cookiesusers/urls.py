from django.conf.urls import patterns, include, url
from django.views.generic.simple import direct_to_template

urlpatterns = patterns('udacity253.apps.4_cookiesusers.views',
                       
    # signup page
    url(r'^signup$', 'signup', name='cookiesusers_signup'),
    # login page
    url(r'^login$', 'login', name='cookiesusers_login'),
    # lgout url
    url(r'^logout$', 'logout', name='cookiesusers_logout'),
    # welcome message
    url(r'^welcome/$', 'welcome', name='cookiesusers_welcome',),

)
