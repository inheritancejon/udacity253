from django.conf.urls import patterns, include, url

urlpatterns = patterns('udacity253.apps.7_final.views',
    
    # logout page
    url(r'^logout$', 'logout', name='final_logout'),
    # login page
    url(r'^login$', 'login', name='final_login'),
    # signup page
    url(r'^signup$', 'signup', name='final_signup'),
    # r^<page>$ what page are we viewing>
    url(r'^(?P<page>[a-zA-Z0-9_-]+)?$', 'wiki', name='final_wiki'),
    # redirect page for editing
    url(r'^_edit/(?P<page>[a-zA-Z0-9_-]+)?$', '_edit', name='final__edit'),
    # view history of edits for page
    url(r'^_history/(?P<page>[a-zA-Z0-9_-]+)?$', '_history', name='final__history'),

)

