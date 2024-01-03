# -*- coding: utf-8 -*-
"""
Created on Thu Nov 19 15:51:21 2020

@author: lenovo
"""

import platform
import logging
from .models_user import UserProfile
logger = logging.getLogger(__name__)

from django.conf import settings as _settings

def settings(request):
    """
    TEMPLATE_CONTEXT_PROCESSORS
    """
    context = { 'settings': _settings }
    try:
        username = request.user
        u = UserProfile.objects.get(username=username)  
        context['test'] = '这是一个测试变量'
        context['u'] = u
        #context['user'] = u
        context['username'] = username
        context['is_admin'] = u.is_admin
        context['is_active'] = u.is_active
        context['domain'] = _settings.ID_SERVER
        context['is_windows'] = True if platform.system() == 'Windows' else False
        

        logger.info("set system status variable")
    except Exception as e:
        logger.error("settings:{}".format( e))
    return context