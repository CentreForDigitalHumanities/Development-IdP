import saml2
from saml2.saml import NAMEID_FORMAT_TRANSIENT, NAMEID_FORMAT_PERSISTENT
from saml2.sigver import get_xmlsec_binary

from .settings import DEBUG, BASE_DIR
from .utils import discover

LOGIN_URL = '/login/'

BASE_URL = discover(
    "idp_base_url",
    default='http://localhost:7000/saml/idp'
)

SAML_IDP_SP_FIELD_DEFAULT_ATTRIBUTE_MAPPING = {
    "username": "uuShortID",
    "first_name": "givenName",
    "last_name": "uuPrefixedSn",
    "email": "mail",
}

SAML_IDP_CONFIG = {
    'debug': DEBUG,
    'xmlsec_binary': get_xmlsec_binary(['/opt/local/bin', '/usr/bin']),
    'entityid': '%s/metadata' % BASE_URL,
    'description': 'Second test IdP',

    'processor': 'testidp.saml_processor.SamlProcessor',

    "logging": {
        "version": 1,
        "formatters": {
            "simple": {
                "format": "[%(asctime)s] [%(levelname)s] [%(name)s.%(funcName)s] %(message)s",
            },
        },
        "handlers": {
            "stdout": {
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
                "level": "DEBUG",
                "formatter": "simple",
            },
        },
        "loggers": {
            "saml2": {
                "level": "DEBUG"
            },
        },
        "root": {
            "level": "DEBUG",
            "handlers": [
                "stdout",
            ],
        },
    },

    'service': {
        'idp': {
            'name': 'Django localhost IdP 2',
            'endpoints': {
                'single_sign_on_service': [
                    (f'{BASE_URL}/sso/post/',
                     saml2.BINDING_HTTP_POST),
                    (f'{BASE_URL}/sso/redirect/',
                     saml2.BINDING_HTTP_REDIRECT),
                ],
                "single_logout_service": [
                    (f"{BASE_URL}/slo/post/",
                     saml2.BINDING_HTTP_POST),
                    (f"{BASE_URL}/slo/redirect/",
                     saml2.BINDING_HTTP_REDIRECT)
                ],
            },
            'name_id_format': [NAMEID_FORMAT_TRANSIENT, NAMEID_FORMAT_PERSISTENT],
            'sign_response': True,
            'sign_assertion': True,
            'want_authn_requests_signed': False,
            'signing_algorithm': saml2.xmldsig.SIG_RSA_SHA256,
            'digest_algorithm':  saml2.xmldsig.DIGEST_SHA256,
        },
    },

    # Signing
    'key_file': str(BASE_DIR) + '/certificates/private.key',
    'cert_file': str(BASE_DIR) + '/certificates/public.cert',
    # Encryption
    'encryption_keypairs': [{
        'key_file': str(BASE_DIR) + '/certificates/private.key',
        'cert_file': str(BASE_DIR) + '/certificates/public.cert',
    }],
    'valid_for': 365 * 24,
    "organization": {
        "name": [
            ("Humanities IT", "en"),
        ],
    }
}
