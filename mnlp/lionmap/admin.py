from django.contrib.gis import admin as GeoAdmin
from django.contrib import admin
from models import Lion, Collar, Position, Pride, Tracking, DropboxAccount
from singleton_models.admin import SingletonModelAdmin
from dropbox import client, rest, session
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from django.db import transaction
from functools import update_wrapper
import os
from django.template.response import TemplateResponse
from django.http import HttpResponseRedirect
from django.db.models import F

csrf_protect_m = method_decorator(csrf_protect)

class LionListFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = 'lion'

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'lion'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        lions = Lion.objects.all()
        lionlist = [(str(lion.id), lion.name) for lion in lions]
        return lionlist

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        if self.value():
            print self.value()
            return queryset.filter(
                collar__lion__id=self.value(),
                timestamp__gte=F('collar__tracking__start'),
                timestamp__lte=F('collar__tracking__end')
            )


class DropboxAdmin(SingletonModelAdmin):

    def get_link_url(self):
        return reverse('admin:%s_%s_link' % info, current_app=self.admin_site.name)

    def get_urls(self):
        from django.conf.urls.defaults import patterns, url

        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)
            return update_wrapper(wrapper, view)

        info = self.model._meta.app_label, self.model._meta.module_name

        urlpatterns = patterns('',
            url(r'^history/$',
                wrap(self.history_view),
                {'object_id': '1'},
                name='%s_%s_history' % info),
            url(r'^link/$',
                wrap(self.link_view),
                {},
                name='%s_%s_link' % info),
            url(r'^$',
                wrap(self.change_view),
                {'object_id': '1'},
                name='%s_%s_change' % info),
        )
        return urlpatterns

    @csrf_protect_m
    @transaction.commit_on_success
    def link_view(self, request):
        # Get your app key and secret from the Dropbox developer website
        APP_KEY = os.environ['DROPBOX_APP_KEY'] if 'DROPBOX_APP_KEY' in os.environ else ''
        APP_SECRET = os.environ['DROPBOX_APP_SECRET'] if 'DROPBOX_APP_SECRET' in os.environ else ''

        # ACCESS_TYPE should be 'dropbox' or 'app_folder' as configured for your app
        ACCESS_TYPE = 'app_folder'
        sess = session.DropboxSession(APP_KEY, APP_SECRET, ACCESS_TYPE)

        if 'apply' in request.POST:
            access_token = None
            try:
                rq_token = request.session['dropbox_request_token']
                # This will fail if the user didn't visit the above URL and hit 'Allow'
                access_token = sess.obtain_access_token(rq_token)
            except Exception, err:
                self.message_user(request, "There was an error linking, did you visit the URL and clicked Accept?\n%s." % err)
                return HttpResponseRedirect(request.get_full_path())

            cl = client.DropboxClient(sess)

            dropbox_user = cl.account_info()['display_name']

            try:
                dropbox = DropboxAccount.objects.get(pk=1)
                dropbox.name=dropbox_user
                dropbox.key=access_token.key
                dropbox.secret=access_token.secret
                dropbox.delta=''
                dropbox.save()
            except Exception, err:
                self.message_user(request, "There was an error saving:\n%s." % err)
                return HttpResponseRedirect(request.get_full_path())

            self.message_user(request, "Successfully linked to Dropbox account %s." % dropbox_user)
            return HttpResponseRedirect('/admin')
        else:
            request_token = sess.obtain_request_token()
            request.session['dropbox_request_token'] = request_token
            url = sess.build_authorize_url(request_token)

            dropbox = DropboxAccount.objects.get(pk=1)

        return TemplateResponse(request, 'admin/link_account.html', {
            'DROPBOX_URL': url, 'CURRENT_DROPBOX_USER': dropbox.name}, current_app=self.admin_site.name)
    link_view.short_description = "Link Dropbox account"

class PositionAdmin(GeoAdmin.OSMGeoAdmin):
    list_filter = ('collar',LionListFilter)
    ordering = ('-timestamp',)

class TrackingAdmin(admin.ModelAdmin):
    list_filter = ('lion',)
    ordering = ('-start',)

admin.site.register(Lion)
admin.site.register(Collar)
admin.site.register(Pride)
admin.site.register(Tracking, TrackingAdmin)
admin.site.register(Position, PositionAdmin)
admin.site.register(DropboxAccount, DropboxAdmin)
