
from django.http import JsonResponse
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.conf import settings as _settings

@login_required(login_url='/api/user_action?action=login')
def index(request):
    if _settings.ID_SERVER == '':
        _settings.ID_SERVER = request.get_host().split(":")[0]
    return render(request, 'webui.html')
