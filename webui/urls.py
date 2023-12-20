import django
if django.__version__.split('.')[0]>='4':
    from django.urls import re_path as url
else:
    from django.conf.urls import  url, include

from webui import views
 
urlpatterns = [
    
    url(r'^libopus.js', django.views.static.serve, {'document_root': 'static/web_client', 'path': 'libopus.js'}),
    url(r'^yuv.js', django.views.static.serve, {'document_root': 'static/web_client/js', 'path': 'yuv.js'}),
    url(r'^libopus.wasm', django.views.static.serve, {'document_root': 'static/web_client', 'path': 'libopus.wasm'}),
    url(r'^js/no_sleep.js', django.views.static.serve, {'document_root': 'static/web_client/js', 'path': 'no_sleep.js'}),
    url(r'^$',views.index),
    #url(r'^show$',views.show),

    url(r'^module/(?P<path>.*)$', django.views.static.serve, {'document_root': 'static/web_client/module'},name='web_client'),
    url(r'^js/(?P<path>.*)$', django.views.static.serve, {'document_root': 'static/web_client/js'},name='web_client'),
    url(r'^assets/(?P<path>.*)$', django.views.static.serve, {'document_root': 'static/web_client/assets'},name='web_client'),

    ]
