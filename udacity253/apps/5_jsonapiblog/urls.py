from django.conf.urls import patterns, include, url

urlpatterns = patterns('udacity253.apps.5_jsonapiblog.views',
    
    # View the blog home, check for ".json" added to end of URI, optional 
    url(r'^(?P<json_api>\.json)?$', 'index', name='jsonapiblog_index'),
    # newpost/ views the newpost template to create posts
    url(r'^newpost$', 'newpost', name='jsonapiblog_newpost'),
    # r^<pk><json_api>$ views an individual blog post by primary key, check for
    # ".json" added to end of URI, optional
    url(r'^(?P<pk>\d+)(?P<json_api>\.json)?$', 'post', name='jsonapiblog_post'),
    # signup page
    url(r'^signup$', 'signup', name='jsonapiblog_signup'),
    # login page
    url(r'^login$', 'login', name='jsonapiblog_login'),
    # logout url
    url(r'^logout$', 'logout', name='jsonapiblog_logout'),
    # welcome message
    url(r'^welcome$', 'welcome', name='jsonapiblog_welcome',),

)

