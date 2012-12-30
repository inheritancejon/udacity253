from django.conf.urls import patterns, include, url
from django.views.generic.simple import direct_to_template

urlpatterns = patterns('udacity253.apps.2_rot13.views',

    # View the problem solution 
    url(r'^$', 'index', name='rot13_index'),

)
