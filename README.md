# Mara-Naboisho Lion Project  #

Mara-Naboisho Lion Project - GPS Collar data processor, Please see the [wiki](https://github.com/Y3PP3R/mnlp-tracking/wiki "wiki").

Developers are welcome to help thinking and coding!

Made public under the BSD-License, please see the LICENSE file for details.

## Contributors ##
- Ditte Lisbjerg (Project manager)
- Jasper Timmer (Developer)

## Configure the app ##
Add a file hidden_settings.py to mnlp/mnlp/. Add the following section to it:

    ADMINS = (
        ('Your Name', 'your@email.com'),
    )
    
    # Make this unique, and don't share it with anybody.
    SECRET_KEY = 'ASDLK@#$%SDdsfjlkrandomcharactersDAS:LKFJ'


Create dotCloud account and an application. Push this directory to dotCloud with dotcloud push. Create a dropbox application API key on the DropBox website, and set it in your dotcloud application in the following way:

    dotcloud env set DROPBOX_APP_KEY=key
    dotcloud env set DROPBOX_APP_SECRET=secret

You can login to http://yourapp-youruser.dotcloud.com/admin with the admin:password combination. There, link the dropbox account. Every whole hour, the application will now collect the KML/KMZ files from dropbox and process the positions. Check ./jobs/crontab for the command and frequency.

Do not forget to change the password of the admin account!