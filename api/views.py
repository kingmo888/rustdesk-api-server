from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib.auth.hashers import make_password
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from django.forms.models import model_to_dict

from itertools import chain
from django.db.models.fields import DateTimeField, DateField, CharField, TextField

from django.db.models import Model

from django.http import JsonResponse
import json
import time
import datetime
import hashlib
from api.models import RustDeskToken, UserProfile, RustDeskTag, RustDeskPeer, RustDesDevice

import copy

from .views_front import *
from .views_api import *
from .front_locale import *
