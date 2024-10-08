
from django.contrib.auth import views as auth_views
from django.urls import path

from .views import HomeView, OpenIDApplicationCreateView, OpenIDApplicationDeleteView, \
    OpenIDApplicationEditView, \
    SamlMetadataView, \
    SamlSPCreateView, \
    SamlSPDeleteView, SamlSPEditView, UserCreateView, UserEditView

app_name = 'main'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('saml-metadata/<int:sp>/', SamlMetadataView.as_view(),
         name='saml-metadata'),
    path('saml-sp/new/', SamlSPCreateView.as_view(),
         name='sp-create'),
    path('saml-sp/<int:pk>/delete/', SamlSPDeleteView.as_view(),
         name='sp-delete'),
    path('saml-sp/<int:pk>/', SamlSPEditView.as_view(),
         name='sp-edit'),
    path('oidc-app/new/', OpenIDApplicationCreateView.as_view(),
         name='oidc-app-create'),
    path('oidc-app/<int:pk>/delete/', OpenIDApplicationDeleteView.as_view(),
         name='oidc-app-delete'),
    path('oidc-app/<int:pk>/', OpenIDApplicationEditView.as_view(),
         name='oidc-app-edit'),
    path('user/new/', UserCreateView.as_view(),
         name='user-create'),
    path('user/<int:pk>/', UserEditView.as_view(),
         name='user-edit'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]
