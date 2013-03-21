from django.conf.urls import patterns, include, url
from django.views.generic.simple import direct_to_template

urlpatterns = patterns('udacity253.apps.2_usersignup.views',

    # View the problem solution 
    url(r'^$', 'index', name='usersignup_index'),
    url(r'^welcome/$', 'welcome', name='usersignup_welcome',),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
