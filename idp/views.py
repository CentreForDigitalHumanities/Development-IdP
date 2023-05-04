import logging
from django.contrib.auth import get_user_model, logout
from django.http import HttpRequest, HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt

from djangosaml2idp.error_views import error_cbv
from djangosaml2idp.idp import IDP
from djangosaml2idp.utils import repr_saml, verify_request_signature
from djangosaml2idp.views import IdPHandlerViewMixin, store_params_in_session

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
