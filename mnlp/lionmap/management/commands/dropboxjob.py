import os
from dropbox import client, session
from django.core.management.base import NoArgsCommand
from _kmz import KMZFile
from lionmap.models import DropboxAccount


class Command(NoArgsCommand):
    help = 'Processes all new kml/kmz files in dropbox'
    can_import_settings = True

    def handle_noargs(self, **options):

        # Get your app key and secret from the Dropbox developer website
        APP_KEY = os.environ['DROPBOX_APP_KEY'] if 'DROPBOX_APP_KEY' in os.environ else ''
        APP_SECRET = os.environ['DROPBOX_APP_SECRET'] if 'DROPBOX_APP_SECRET' in os.environ else ''

        dropbox_account = DropboxAccount.objects.get(pk=1)

        # ACCESS_TYPE should be 'dropbox' or 'app_folder' as configured for your app
        ACCESS_TYPE = 'app_folder'
        sess = session.DropboxSession(APP_KEY, APP_SECRET, ACCESS_TYPE)
        try:
            tokens = DropboxAccount.objects.get(pk=1)
            token_key = tokens.key
            token_secret = tokens.secret

            sess.set_token(token_key, token_secret)

            cl = client.DropboxClient(sess)
        except:
            print "Please link the application to the dropbox account first, using the Admin interface."
            return

        if dropbox_account.delta == '':
            delta = cl.delta()
            dropbox_account.delta = delta['cursor']
            dropbox_account.save()
        else:
            delta = cl.delta(dropbox_account.delta)
            dropbox_account.delta = delta['cursor']
            dropbox_account.save()
        self.process_deltas(delta, cl)

    def process_deltas(self, delta, dropbox_client):
        for i in range(0, len(delta['entries'])):
            try:
                if delta['entries'][i][1] is None:
                    continue

                fname = delta['entries'][i][0]

                if not (fname.endswith('.kml') or fname.endswith('.kmz')):
                    continue

                print fname

                dbfile = dropbox_client.get_file(delta['entries'][i][0]).read()

                kmx = KMZFile(dbfile)
                if kmx.valid:
                    kmx.save_positions()
            except Exception, err:
                print "error retrieving file %s\n%s" % (delta['entries'][i][0], err)
        if delta['has_more']:
            self.process_deltas(dropbox_client.delta(), dropbox_client)
