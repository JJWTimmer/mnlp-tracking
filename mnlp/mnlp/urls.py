from django.conf.urls import patterns, include, url
from django.contrib.gis import admin

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
                       # Examples:
                       # url(r'^$', 'mnlp.views.home', name='home'),
                       # url(r'^mnlp/', include('mnlp.foo.urls')),

                       # Uncomment the admin/doc line below to enable admin documentation:
                       # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

                       # Uncomment the next line to enable the admin:
                       url(r'^admin/', include(admin.site.urls)),

                       url(r'^$', 'lionmap.views.show_map'),
                       url(r'^lions/$', 'lionmap.views.lions'),
                       url(r'^liondata/$', 'lionmap.views.lion_data'),
                       url(r'^heatmapdata/$', 'lionmap.views.heatmap_data'),
                       url(r'^lastdata/$', 'lionmap.views.last_positions'),
                       url(r'^json/lion/(?P<lion>\d+)/$', 'lionmap.views.positions_to_json'),
                       url(r'^full/$', 'lionmap.views.fullscreen'),
)

try:
    from local_urls import *

    urlpatterns += debugpatterns
except ImportError:
    pass
