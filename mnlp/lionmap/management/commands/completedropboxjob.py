import os
from dropbox import client, session
from django.core.management.base import NoArgsCommand, CommandError
from _kmz import KMZFile
from lionmap.models import DropboxAccount


class Command(NoArgsCommand):
    help = 'Processes all kml/kmz files in dropbox'
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

        meta_data = cl.metadata('/', list=True)
        entries = self.get_all_files(meta_data, cl)
        
        self.process_files(entries, cl)
        
    def get_all_files(self, meta_data, client):
        entries = [
            entry['path']
            for entry in meta_data['contents']
            if not entry['is_dir']
        ]
        dirs = [
            entry['path']
            for entry in meta_data['contents']
            if entry['is_dir']
        ]
        
        for folder in dirs:
            dir_meta = client.metadata(folder, list=True)
            entries += self.get_all_files(dir_meta, client)
                
        return entries

    def process_files(self, file_list, dropbox_client):
            for file in file_list:
                try:
                    print file
                    dbfile = dropbox_client.get_file(file).read()

                    kmx = KMZFile(dbfile)
                    if kmx.valid:
                        kmx.save_positions()
                except Exception, err:
                    print "Error with %s:" % file
                    print err
                    print "---"