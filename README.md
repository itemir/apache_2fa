# Apache Two-Factor (2FA) Authentication with Google Authenticator

<img src='https://raw.githubusercontent.com/itemir/apache_2fa/master/2fa_demo.gif' align='left' width='400' height='276' hspace='5' vspace='5'>

[Two-factor authentication](https://en.wikipedia.org/wiki/Multi-factor_authentication) also known as 2FA, adds an extra step to a basic authentication procedure. Without 2FA, a user only enters username and password. In this case, the password is the single factor of authentication. With 2FA an additional authentication mechanism is used, that is preferably performed out-of-band.

[Google Authenticator](https://en.wikipedia.org/wiki/Google_Authenticator) is an application that implements two-factor authentication services using the Time-based One-time Password Algorithm (TOTP).

Apache provides a basic authentication mechanism with mod_auth_digest. For more secure applications, it is often required to have an additional layer of authentication. This repository provides necessary code and instructions to add two-factor authentication to basic Apache authentication. This method is transparent to underlying applications so it can be used for any Apache served web site whether it is static, dynamic (PHP, Django, Flask etc.) or pre-packaged (Wiki, CRM, CMS etc.).

Instructions
---

Clone the repository and install dependencies:

    $ git clone https://github.com/itemir/apache_2fa
    $ cd apache_2fa
    $ sudo pip install onetimepass

Create a directory for storing states:

    $ mkdir state

Adjust permissions to allow access only to Apache (replace www-data with the user id of Apache process as needed):

    $ sudo chown www-data:www-data state
    $ sudo chown www-data:www-data tokens.json
    $ sudo chmod 750 state
    $ sudo chmod 640 tokens.json

Enable mod_rewrite, mod_auth_digest and mod_cgid if not already enabled (you will need to restart Apache):

    $ sudo a2enmod rewrite
    $ sudo a2enmod auth_digest
    $ sudo a2enmod cgid
    $ sudo service apache2 restart

Add the following configuration to Apache configuration under appropriate VirtualHost:

    RewriteEngine On

    RewriteCond %{REQUEST_URI} !^/auth/
    RewriteCond %{HTTP_COOKIE} !^.*2FA_Auth=([a-zA-Z0-9]+)
    RewriteRule ^(.*)$ /auth/auth?$1?%{QUERY_STRING} [L,R=302]

    RewriteCond %{REQUEST_URI} !^/auth/
    RewriteCond %{HTTP_COOKIE} ^.*2FA_Auth=([a-zA-Z0-9]+)
    RewriteCond <path to apache_2fa>/state/%1 !-f
    RewriteRule ^(.*)$ /auth/auth?$1?%{QUERY_STRING} [L,R=302]

    ScriptAlias /auth/ <path to_apache 2fa (note the trailing slash)>/

    <Directory <path to apache_2fa>>
        AuthType Digest
        AuthName "yourdomain.com"
        AuthDigestDomain /
        AuthDigestProvider file
        AuthUserFile <path to apache_2fa>/apache_credentials
        Require valid-user
    </Directory>

    <Directory <path to protected directory>>
        AuthType Digest
        AuthName "yourdomain.com"
        AuthDigestDomain /
        AuthDigestProvider file
        AuthUserFile <path to apache_2fa>/apache_credentials
        Require valid-user
    </Directory>

Replace *path to apache_2fa* with the full path of cloned repository, *path to protected directory* with the actual path of the site you are trying to protect. If you change *yourdomain.com* make sure to make corresponding changes in *apache_credentials* file. Pay special attention to trailing slashes where present. You may be able to combine two Directory configurations into one depending on your directory structure, just make sure both paths are covered by the same auhentication mechanism.

Test the configuration and reload Apache if no errors. If there are errors, verify steps above and make sure if you have all necessary modules enabled.

    $ sudo apachectl configtest
    $ sudo service apache2 reload

If all went well, you can now test the application. Go to a protected web page. You should be prompted to enter a username and password. Use **test_user** / **test_password**. You should now be prompted for an Authentication Token. If **test_user** authentication fails, change the password with the following command:

    $ htdigest apache_credentials yourdomain.com test_user

In order to obtain Authentication Token, download Google Authenticator for [iOS](https://itunes.apple.com/us/app/google-authenticator/id388497605?mt=8) or [Android](https://play.google.com/store/apps/details?id=com.google.android.apps.authenticator2&hl=en) and create a profile by using **ND4LKCSFMUQISO6CBZQATLDP** secret key (there are many other applications that provide the same capability with additional features, you can basically use any application that supports TOTP). Once you define a profile, Google Authenticator will create a token that you can use in this form.

If the test is successful, edit *apache_credentials* and *tokens.json* files and remove **test_user**.

Maintenance
---
You can create new users by using *htdigest* tool:

    $ htdigest apache_credentials yourdomain.com <new_user>

For creating secret keys for Google Authenticator, refer to [this article](https://nerdyness2012.wordpress.com/tag/oathtool/). You need to save generated secret keys (base32) in *tokens.json* file.

For every successful authentication session, a new file will be created under */state* directory. This file is relevant until the cookie expires (default value is 6 hours for expiration). You will eventually want to clean stale entried in this directory. *state_clean* utility that is included the repository can be used to delete state files that are older than 24 hours. You can call it from a cron job daily:

    0 * * * * <path to apache_2fa>/clean_state
