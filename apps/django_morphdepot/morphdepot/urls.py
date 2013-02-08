from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$', 'views.directupload', name='directupload'),
)