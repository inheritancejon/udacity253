from django.conf.urls import patterns, include, url
from django.views.generic.simple import direct_to_template

urlpatterns = patterns('udacity253.apps.1_appengine.views',

    # View the problem solution 
    url(r'^$', 'index', name='appengine_index'),
    
)

