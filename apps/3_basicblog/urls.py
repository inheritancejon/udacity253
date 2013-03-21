from django.conf.urls import patterns, include, url

urlpatterns = patterns('udacity253.apps.3_basicblog.views',
    # View the problem solution 
    url(r'^$', 'index', name='basicblog_index'),
    # newpost/ views the newpost template to create posts
    url(r'^newpost$', 'newpost', name='basicblog_newpost'),
    # r^(\d+)/$ views an individual blog post by primary key
    url(r'^(?P<pk>\d+)$', 'post', name='basicblog_post')
)

