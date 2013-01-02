from django.conf.urls import patterns, include, url
from django.contrib.gis import admin
from django.conf import settings
import os

debugpatterns = patterns('',
    url(r'^heatmaps/(?P<path>.*)$', 'django.views.static.serve', {'document_root': os.path.join(settings.STATIC_ROOT, 'heatmaps')}),
)