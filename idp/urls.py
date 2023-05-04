from django.urls import path

from djangosaml2idp import views as dsidp_views
from . import views

app_name = 'djangosaml2idp'

urlpatterns = [
    path('sso/init/', dsidp_views.SSOInitView.as_view(),
         name="saml_idp_init"),
    path('sso/<str:binding>/', dsidp_views.sso_entry, name="saml_login_binding"),
    path('login/process/', dsidp_views.LoginProcessView.as_view(), name='saml_login_process'),
    path('login/process_multi_factor/', dsidp_views.get_multifactor, name='saml_multi_factor'),
    path('slo/<str:binding>/', views.LogoutProcessView.as_view(), name="saml_logout_binding"),
    path('metadata/', dsidp_views.metadata, name='saml2_idp_metadata'),
]
