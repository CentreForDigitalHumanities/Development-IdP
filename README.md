# Django Identity Provider

A quick and dirty IdP for local development with applications using Federated Authentication.

Internally it's follows SurfConext attribute/claim naming, but has built-in 
profiles to act like the UU IdP.

NOTE: Currently only SAML is implemented, with OpenID possibly being added in 
the future.

## Instructions

1. Setup a virtualenv and activate it
2. Install dependencies ``pip install -r requirements.txt``
3. Load initial data ``python manage.py loaddata main/fixtures/initial.json``
4. Verify that ``BASE_URL`` in ``testidp/saml_settings.py`` is set to the correct host for your usage
   * By default this is ``localhost:7000``, which is probably fine?
5. Run the IDP ``python manage.py runserver <port>``
   * If you kept using the default, this is  ``python manage.py runserver 7000``
6. You're done!

You can use the generic admin account (username/pass: admin/admin). 

## Adding SAML Providers

1. Make sure your app has SAML already setup and is using 
   ``http(s)://localhost:7000/saml/idp/metadata`` as it's IdP
   * Replacing ``localhost:7000`` with the actual IP of the IdP
2. Click 'New' next to Service Provider in the app
3. Provide at least your SP's ``entity_id`` and ``metadata`` (by URL import or 
   manually)
4. Choose your starting attribute map* 
5. Done!
6. Optionally: review your new SP by editting. You might want to add missing 
   attributes to the attribute map

### Note on attribute maps

In SAML, (well, PySAML), the term attribute map is often used and often not even
referring to the same thing. This can be confusing, so to clear up:

In the context _of this app_ you'll only have to worry about SP attribute maps,
which both maps the internal attribute name to the name sent to the SP and 
restricts what attribute names are sent. 

For example, internally the Solis-ID is named ``uid``, but the UU IdP calls this
attribute ``uushortid``. Thus, we need to _map_ ``uuid`` to ``uushortid``. 

Thus, you'll get this attribute map:
```json
{
    "uid": "uushortid",
}
```

However, with this map the IdP will only supply the SP the solis-id of the 
logged in user. Thus, a more common attribute map would be:

```json
{
    "uid": "uushortid",
    "mail": "mail",
    "givenName": "givenName",
    "sn": "uuprefixedsn",
}
```
