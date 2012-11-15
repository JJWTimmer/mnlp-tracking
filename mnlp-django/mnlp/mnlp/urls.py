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
	
    url(r'^$', 'lionmap.views.hello_view', name='hello_page'),
    url(r'^kml/$', 'lionmap.views.kml'),
)
