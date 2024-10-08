import logging
from urllib.parse import urlparse

from django.contrib.auth import get_user_model, logout
from django.http import HttpRequest, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt

from djangosaml2idp.error_views import error_cbv
from djangosaml2idp.idp import IDP
from djangosaml2idp.utils import repr_saml, verify_request_signature
from djangosaml2idp.views import IdPHandlerViewMixin, store_params_in_session
from oauth2_provider.models import AbstractGrant, Application
from oauth2_provider.settings import oauth2_settings
from oauth2_provider.views.mixins import OIDCOnlyMixin

logger = logging.getLogger(__name__)

User = get_user_model()


@method_decorator([never_cache, csrf_exempt], name='dispatch')
class LogoutProcessView(IdPHandlerViewMixin, View):
    """ View which processes the actual SAML Single Logout request

    Custom version because djangosaml2idp's LoginProcessView cannot handle
    signed logout requests
    """
    __service_name = 'Single LogOut'

    def post(self, request: HttpRequest, *args, **kwargs):
        return self.get(request, *args, **kwargs)

    def get(self, request: HttpRequest, *args, **kwargs):
        logger.info("--- {} Service ---".format(self.__service_name))
        # do not assign a variable that overwrite request object, if it will fail the return with HttpResponseBadRequest trows naturally
        store_params_in_session(request)
        binding = request.session['Binding']
        relay_state = request.session['RelayState']
        logger.debug(
            "--- {} requested [\n{}] to IDP ---".format(self.__service_name,
                                                        binding))

        idp_server = IDP.load()

        # adapted from pysaml2 examples/idp2/idp_uwsgi.py
        try:
            req_info = idp_server.parse_logout_request(
                request.session['SAMLRequest'], binding)
        except Exception as excp:
            expc_msg = "{} Bad request: {}".format(self.__service_name, excp)
            logger.error(expc_msg)
            return error_cbv.handle_error(request, exception=expc_msg,
                                          status_code=400)

        logger.debug(
            "{} - local identifier: {} from {}".format(self.__service_name,
                                                       req_info.message.name_id.text,
                                                       req_info.message.name_id.sp_name_qualifier))
        logger.debug(
            "--- {} SAML request [\n{}] ---".format(self.__service_name,
                                                    repr_saml(req_info.xmlstr,
                                                              b64=False)))

        try:
            verify_request_signature(req_info)
        except ValueError as excp:
            return error_cbv.handle_error(request, exception=excp,
                                          status_code=400)

        logger.debug('--- Verified SAML request signature ---')

        resp = idp_server.create_logout_response(req_info.message, [binding])

        # Refetch destination e.a. as `create_logout_response` returns a str
        # when creating a signed response
        binding, destination = idp_server.pick_binding(
            "single_logout_service", [binding], "spsso", req_info
        )

        try:
            # hinfo returns request or response, it depends by request arg
            hinfo = idp_server.apply_binding(binding, resp.__str__(),
                                             destination,
                                             relay_state,
                                             response=True)
        except Exception as excp:
            logger.error("ServiceError: %s", excp)
            return error_cbv.handle_error(request, exception=excp, status=400)

        logger.debug("--- {} Response [\n{}] ---".format(
            self.__service_name,
            repr_saml(resp.__str__().encode())
        ))
        logger.debug("--- binding: {} destination:{} relay_state:{} "
                     "---".format(binding, destination, relay_state))

        # logout user from IDP
        logout(request)

        if hinfo['method'] == 'GET':
            return HttpResponseRedirect(hinfo['headers'][0][1])
        else:
            html_response = self.create_html_response(
                request,
                binding=binding,
                authn_resp=resp.__str__(),
                destination=destination,
                relay_state=relay_state)
        return self.render_response(request, html_response, None)


class ConnectDiscoveryInfoView(OIDCOnlyMixin, View):
    """
    View used to show oidc provider configuration information per
    `OpenID Provider Metadata <https://openid.net/specs/openid-connect-discovery-1_0.html#ProviderMetadata>`_

    Modified to support UU weirdness
    """

    def get(self, request, *args, **kwargs):
        issuer_url = oauth2_settings.OIDC_ISS_ENDPOINT

        if not issuer_url:
            issuer_url = oauth2_settings.oidc_issuer(request)
            authorization_endpoint = request.build_absolute_uri(reverse("oauth2_provider:authorize"))
            token_endpoint = request.build_absolute_uri(reverse("oauth2_provider:token"))
            userinfo_endpoint = oauth2_settings.OIDC_USERINFO_ENDPOINT or request.build_absolute_uri(
                reverse("oauth2_provider:user-info")
            )
            introspection_endpoint =  request.build_absolute_uri(reverse('oauth2_provider:introspect'))
            jwks_uri = request.build_absolute_uri(reverse("oauth2_provider:jwks-info"))
            if oauth2_settings.OIDC_RP_INITIATED_LOGOUT_ENABLED:
                end_session_endpoint = request.build_absolute_uri(
                    reverse("oauth2_provider:rp-initiated-logout")
                )
        else:
            parsed_url = urlparse(oauth2_settings.OIDC_ISS_ENDPOINT)
            host = parsed_url.scheme + "://" + parsed_url.netloc
            authorization_endpoint = "{}{}".format(host, reverse("oauth2_provider:authorize"))
            token_endpoint = "{}{}".format(host, reverse("oauth2_provider:token"))
            userinfo_endpoint = oauth2_settings.OIDC_USERINFO_ENDPOINT or "{}{}".format(
                host, reverse("oauth2_provider:user-info")
            )
            introspection_endpoint = "{}{}".format(host, reverse('oauth2_provider:introspect'))

            jwks_uri = "{}{}".format(host, reverse("oauth2_provider:jwks-info"))
            if oauth2_settings.OIDC_RP_INITIATED_LOGOUT_ENABLED:
                end_session_endpoint = "{}{}".format(host, reverse("oauth2_provider:rp-initiated-logout"))

        signing_algorithms = [Application.HS256_ALGORITHM]
        if oauth2_settings.OIDC_RSA_PRIVATE_KEY:
            signing_algorithms = [Application.RS256_ALGORITHM, Application.HS256_ALGORITHM]

        # Weird UU behavior, only openid scope is advertised but other scopes are supported
        scopes_supported = ["openid"]
        # More weird UU behavior, no claims are advertised but claims are supported
        oidc_claims = []


        data = {
            "issuer": issuer_url,
            "authorization_endpoint": authorization_endpoint,
            "token_endpoint": token_endpoint,
            "userinfo_endpoint": userinfo_endpoint,
            "introspection_endpoint": introspection_endpoint,
            "jwks_uri": jwks_uri,
            "scopes_supported": scopes_supported,
            "response_types_supported": oauth2_settings.OIDC_RESPONSE_TYPES_SUPPORTED,
            "subject_types_supported": oauth2_settings.OIDC_SUBJECT_TYPES_SUPPORTED,
            "id_token_signing_alg_values_supported": signing_algorithms,
            "token_endpoint_auth_methods_supported": (
                oauth2_settings.OIDC_TOKEN_ENDPOINT_AUTH_METHODS_SUPPORTED
            ),
            "code_challenge_methods_supported": [key for key, _ in AbstractGrant.CODE_CHALLENGE_METHODS],
            "claims_supported": oidc_claims,
        }
        if oauth2_settings.OIDC_RP_INITIATED_LOGOUT_ENABLED:
            data["end_session_endpoint"] = end_session_endpoint
        response = JsonResponse(data)
        response["Access-Control-Allow-Origin"] = "*"
        return response
