from .settings import BASE_DIR

PRIVATE_KEY = str(BASE_DIR) + '/certificates/private.key'

with open(PRIVATE_KEY) as f:
    OIDC_RSA_PRIVATE_KEY = f.read()


OAUTH2_PROVIDER = {
    "OAUTH2_VALIDATOR_CLASS": "testidp.openid_validator.OpenIDValidator",
    "OIDC_ENABLED": True,
    "OIDC_RSA_PRIVATE_KEY": OIDC_RSA_PRIVATE_KEY,
    "OIDC_RP_INITIATED_LOGOUT_ENABLED": True,
    "OIDC_RP_INITIATED_LOGOUT_ALWAYS_PROMPT": True,
    "PKCE_REQUIRED": False,
    "SCOPES": {
        "openid": "OpenID Connect scope",
        "profile": "Profile scope",
        "email":   "email",
    },
    "OIDC_RESPONSE_TYPES_SUPPORTED": [
        "token",
        "id_token",
        "code",
        "token id_token",
        "code token",
        "code id_token token",
        "code id_token",
    ]
}
