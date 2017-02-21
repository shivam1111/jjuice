"""jjuice URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import include
from django.shortcuts import render
admin.autodiscover()


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^', include('catalog.urls',namespace="catalog")),
    url(r'^misc/', include('misc.urls',namespace="misc")),
    url(r'^cart/', include('cart.urls',namespace="cart")),
    url(r'^accounts/', include('odoo_auth.urls',namespace="odoo_auth")),
    url(r'^accounts/', include('django.contrib.auth.urls',namespace="auth")),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

def handler404(request):
    response = render(request,'404.html', locals())
    response.status_code = 404
    return response

def handler500(request):
    response = render(request,'500.html', locals())
    response.status_code = 500
    return response