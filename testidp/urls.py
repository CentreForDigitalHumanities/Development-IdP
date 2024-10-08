"""django_project_template URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path

from idp.views import ConnectDiscoveryInfoView

handler404 = 'main.error_views.error_404'
handler500 = 'main.error_views.error_500'
handler403 = 'main.error_views.error_403'
handler400 = 'main.error_views.error_400'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls')),
    path('saml/idp/', include('idp.urls')),
    re_path(
        r"^o/\.well-known/openid-configuration/?$",
        ConnectDiscoveryInfoView.as_view(),
        name="oidc-connect-discovery-info",
    ),
    path("o/", include("oauth2_provider.urls", namespace="oauth2_provider")),
    path('impersonate/', include('impersonate.urls')),
    path('cdhcore/', include('cdh.core.urls')),
    path('i18n/', include('django.conf.urls.i18n')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT, show_indexes=True)


admin.site.site_header = ''
admin.site.site_title = ''
admin.site.index_title = ''


if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),

    ] + urlpatterns
