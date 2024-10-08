# Django Identity Provider

A quick and dirty IdP for local development with applications using Federated Authentication.

Internally it's follows SurfConext attribute/claim naming, but has built-in
profiles to act like the UU IdP.

NOTE: Currently only SAML is implemented, with OpenID possibly being added in
the future.

## Instructions

### Running with Docker

TODO: write this. TL;DR: ``docker-compose up`` and `./docker_initial_setup.sh` the first time.

### Running locally

1. Setup a virtualenv and activate it
2. Install dependencies ``pip install -r requirements.txt``
4. Run migrations ``python manage.py migrate``
5. Load initial data ``python manage.py loaddata main/fixtures/initial.json``
6. (Optional) Load admin user ``python manage.py loaddata main/fixtures/admin-user.json``
   * This will create an admin user with username/pass: admin/admin. Will override any existing user with pk 1
   * Otherwise, create an admin user using ``python manage.py createsuperuser``
7. (Optional) Load test users ``python manage.py loaddata main/fixtures/surfconext-test-users.json``
   * These test users are identical to the test users in SurfConext's test environment.
   * These accounts will override any existing user using a PK between 2 and 40.
8. Verify that ``BASE_URL`` in ``testidp/saml_settings.py`` is set to the correct host for your usage
   * By default this is ``localhost:7000``, which is probably fine?
9. Run the IDP ``python manage.py runserver <port>``
   * If you kept using the default, this is  ``python manage.py runserver 7000``
10. You're done!

## Adding SAML Service Providers

1. Make sure your app has SAML already setup and is using
   ``http(s)://localhost:7000/saml/idp/metadata`` as it's IdP
   * Replacing ``localhost:7000`` with the actual IP of the IdP
2. Click 'New' next to Service Provider in the app
3. Provide at least your SP's ``entity_id`` and ``metadata`` (preferably by URL import)
4. Choose your starting attribute map*
5. Done!
6. Optionally: review your new SP by editting. You might want to add missing
   attributes to the attribute map

### Note on attribute maps

In SAML, (well, PySAML), the term attribute map is often used and often not even
referring to the same thing. This can be confusing, so to clear up:

In the context _of this app_ you'll only have to worry about SP attribute maps,
which both maps the attribute name (as stored in the dev-IdP's database) to the
name sent to the SP and restricts what attribute names are sent. (Any attribute
not in the dict will not be sent back to the SP.)

For example, internally the Solis-ID is named ``username``, but the UU IdP calls
this attribute ``uuShortId``. Thus, we need to _map_ ``username`` to
``uuShortId``.

Thus, you'll get this attribute map:
```json
{
    "username": "uuShortId"
}
```

However, with this map the IdP will only supply the SP the solis-id of the
logged-in user. Thus, a more common attribute map would be:

```json
{
    "username": "uuShortId",
    "mail": "mail",
    "givenName": "givenName",
    "sn": "uuPrefixedSn"
}
```

The app provides a couple preset attribute maps, which can be chosen when
registering an SP in the app. These maps can also be consulted in the file
`main/attribute_map_presets.py`.

## Known Issues
### xmlsec1 bug for Mac users
If you are working on an Apple device, you might run into problems with reading
the certificates for some obscure mac reasons. The currently functioning
workaround (as per 10-1-2024) is reverting your `xmlsec1` package to version
`1.2.37`. You can do that with the following code ([source](https://github.com/xmlsec/python-xmlsec/issues/254#issuecomment-1726249435>`)):

```shell
brew uninstall libxmlsec1
export DESIRED_SHA="7f35e6ede954326a10949891af2dba47bbe1fc17"
wget -O /tmp/libxmlsec1.rb "https://raw.githubusercontent.com/Homebrew/homebrew-core/${DESIRED_SHA}/Formula/libxmlsec1.rb"
brew install --formula /tmp/libxmlsec1.rb
```
