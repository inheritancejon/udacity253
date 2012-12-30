from django.conf.urls import patterns, include, url
from django.views.generic.simple import direct_to_template

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # / 
    # Generic view that links to all problem sets in the course
    url(r'^$', direct_to_template, {'template':'udacity_253.html'}, name='home'),
  
    # /problem_set_unit#_homework/
    # Include Udacity 253 solution apps urlconfs
    url(r'^1_appengine/', include('udacity253.apps.1_appengine.urls')),
    url(r'^2_rot13/', include('udacity253.apps.2_rot13.urls')),
    url(r'^2_usersignup/', include('udacity253.apps.2_usersignup.urls')),
    url(r'^3_basicblog/', include('udacity253.apps.3_basicblog.urls')),
    url(r'^4_cookiesusers/', include('udacity253.apps.4_cookiesusers.urls')),
    url(r'^5_jsonapiblog/', include('udacity253.apps.5_jsonapiblog.urls')),
    # Include the Django admin for easy maintanence 
    url(r'^admin/', include(admin.site.urls)),
)
