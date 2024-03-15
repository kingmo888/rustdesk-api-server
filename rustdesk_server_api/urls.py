"""rustdesk_server_api URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
import django
from django.contrib import admin
from django.urls import path

from api.views import index
if django.__version__.split('.')[0]>='4':
    from django.urls import re_path as url
    from django.conf.urls import  include
else:
    from django.conf.urls import  url, include
from django.views import static ##新增
from django.conf import settings


urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
    path('admin/', admin.site.urls),
    url(r'^$', index),
    url(r'^api/', include('api.urls')),
    url(r'^webui/', include('webui.urls')),
    url(r'^static/(?P<path>.*)$', static.serve, {'document_root': settings.STATIC_ROOT}, name='static'),
    url(r'^canvaskit@0.33.0/(?P<path>.*)$', static.serve, {'document_root': 'static/web_client/canvaskit@0.33.0'},name='web_client'),

]

from django.conf.urls import static as sc
if not settings.DEBUG:
    urlpatterns += sc.static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)