import os
from dropbox import client, session
from django.core.management.base import NoArgsCommand, CommandError
from _streaming_kml import KMZFile
from lionmap.models import DropboxAccount
import tempfile

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

        if dropbox_account.delta is None or dropbox_account.delta == '':
            delta = cl.delta()
            dropbox_account.delta = delta['cursor']
            dropbox_account.save()
        else:
            delta = cl.delta(dropbox_account.delta)
            dropbox_account.delta = delta['cursor']
            dropbox_account.save()
        entries = self.process_delta(delta, cl)
        self.process_files(entries, cl)
        
    def process_delta(self, delta, dropbox_client):
        entries = [
            name
            for name, metadata in delta['entries']
            if (not metadata is None)
            and (not metadata['is_dir'])
            and (
                name.endswith('.kml')
                or name.endswith('.kmz')
                )
        ]
        if delta['has_more']:
            try:
                entries += self.process_delta(dropbox_client.delta(), dropbox_client)
            except Exception, err:
                print "Error getting more data from Dropbox:"
                print err
                print "---"
                
        return entries

    def process_files(self, file_list, dropbox_client):
            for file in file_list:
                try:
                    print file
                    tfile = tempfile.NamedTemporaryFile(mode='wb', delete=False)

                    dropbox_reponse = dropbox_client.get_file(file)

                    while True:
                        data = dropbox_reponse.read(1024)
                        if not data:
                            break
                        tfile.write(data)

                    tfile.close()

                    kmx = KMZFile(tfile.name)
                    kmx.parse_positions()
                except Exception, err:
                    print "Error with %s:" % file
                    print err
                    print "---"
                finally:
                    try:
                        os.unlink(tfile.name)
                    except:
                        pass