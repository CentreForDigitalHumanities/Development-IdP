from oauth2_provider.oauth2_validators import OAuth2Validator


class OpenIDValidator(OAuth2Validator):
    oidc_claim_scope = {
        "sub":                   "openid",
        "name":                  "profile",
        "family_name":           "profile",
        "given_name":            "profile",
        "nickname":              "profile",
        "preferred_username":    "profile",
        "website":               "profile",
        "locale":                "profile",
        "email":                 "email",
        "email_verified":        "email",
    }

    def get_discovery_claims(self, request):
        claims = ["sub"]
        if self._get_additional_claims_is_request_agnostic():
            claims += list(self.get_claim_dict(request).keys())
        return claims

    def get_userinfo_claims(self, request):
        # TODO: make this configurable?

        claims = super().get_userinfo_claims(request)  # Type: dict

        data = {
            "name":               request.user.displayName,
            "family_name":        request.user.sn,
            "given_name":         request.user.givenName,
            "nickname":           request.user.username,
            "preferred_username": request.user.username
        }

        email = request.user.mail()
        if email:
            data["website"] = email[0]  # Don't ask
            data["email"] = email[0]
            data["email_verified"] = True
        else:
            data["website"] = ""
            data["email"] = ""
            data["email_verified"] = False

        data["locale"] = "NL"

        # Remove claims that are not requested
        for key in list(data.keys()):
            if self.oidc_claim_scope[key] not in request.scopes:
                del data[key]

        claims.update(data)

        return claims

