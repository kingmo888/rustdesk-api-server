
from django.http import JsonResponse
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.conf import settings as _settings

@login_required(login_url='/api/user_action?action=login')
def index(request):
    if _settings.ID_SERVER == '127.0.0.1':
        html = "网站未配置ID_SERVER选项, 无法使用web client!<br>" + '<a href="..">返回</a>'
        return HttpResponse(html)
    return render(request, 'webui.html')
