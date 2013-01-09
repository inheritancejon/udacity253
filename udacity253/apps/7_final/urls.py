from django.conf.urls import patterns, include, url

urlpatterns = patterns('udacity253.apps.7_final.views',
    
    #url(r'^$', 'index', name='7_final_index'),
    # r^<page>$ what page are we viewing
    url(r'^$', 'index', name='7_final_index'),
    url(r'^logout$', 'logout', name='7_final_logout'),
    url(r'^login$', 'login', name='7_final_login'),
    url(r'^signup$', 'signup', name='7_final_signup'),

    url(r'^(?P<page>[a-zA-Z0-9_-]+)?$', 'wiki', name='7_final_wiki'),
    # redirect page for editing
    url(r'^_edit/(?P<page>[a-zA-Z0-9_-]+)?$', '_edit', name='7_final__edit'),

    url(r'^_history/(?P<page>[a-zA-Z0-9_-]+)?$', '_history', name='7_final__history'),

)

