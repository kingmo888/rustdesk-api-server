# cython:language_level=3
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from api.models import RustDeskPeer, RustDesDevice, UserProfile, ShareLink
from django.forms.models import model_to_dict

from itertools import chain
from django.db.models.fields import DateTimeField, DateField, CharField, TextField
import datetime
from django.db.models import Model
import json
import time
import hashlib
import sys

salt = 'xiaomo'
EFFECTIVE_SECONDS = 7200

def getStrMd5(s):
    if not isinstance(s, (str,)):
        s = str(s)

    myHash = hashlib.md5()
    myHash.update(s.encode())

    return myHash.hexdigest()

def model_to_dict2(instance, fields=None, exclude=None, replace=None, default=None):
    """
    :params instance: 模型对象，不能是queryset数据集
    :params fields: 指定要展示的字段数据，('字段1','字段2')
    :params exclude: 指定排除掉的字段数据,('字段1','字段2')
    :params replace: 将字段名字修改成需要的名字，{'数据库字段名':'前端展示名'}
    :params default: 新增不存在的字段数据，{'字段':'数据'}
    """
    # 对传递进来的模型对象校验
    if not isinstance(instance, Model):
        raise Exception('model_to_dict接收的参数必须是模型对象')
    # 对替换数据库字段名字校验
    if replace and type(replace) == dict:
        for replace_field in replace.values():
            if hasattr(instance, replace_field):
                raise Exception(f'model_to_dict,要替换成{replace_field}字段已经存在了')
    # 对要新增的默认值进行校验
    if default and type(default) == dict:
        for default_key in default.keys():
            if hasattr(instance, default_key):
                raise Exception(f'model_to_dict,要新增默认值，但字段{default_key}已经存在了')
    opts = instance._meta
    data = {}
    for f in chain(opts.concrete_fields, opts.private_fields, opts.many_to_many):
        # 源码下：这块代码会将时间字段剔除掉，我加上一层判断，让其不再剔除时间字段
        if not getattr(f, 'editable', False):
            if type(f) == DateField or type(f) == DateTimeField:
                pass
            else:
                continue
        # 如果fields参数传递了，要进行判断
        if fields is not None and f.name not in fields:
            continue
        # 如果exclude 传递了，要进行判断
        if exclude and f.name in exclude:
            continue

        key = f.name
        # 获取字段对应的数据
        if type(f) == DateTimeField:
            # 字段类型是，DateTimeFiled 使用自己的方式操作
            value = getattr(instance, key)
            value = datetime.datetime.strftime(value, '%Y-%m-%d')
        elif type(f) == DateField:
            # 字段类型是，DateFiled 使用自己的方式操作
            value = getattr(instance, key)
            value = datetime.datetime.strftime(value, '%Y-%m-%d')
        elif type(f) == CharField or type(f) == TextField:
            # 字符串数据是否可以进行序列化，转成python结构数据
            value = getattr(instance, key)
            try:
                value = json.loads(value)
            except Exception as _:
                value = value
        else:#其他类型的字段
            # value = getattr(instance, key)
            key = f.name
            value = f.value_from_object(instance)
            # data[f.name] = f.value_from_object(instance)
        # 1、替换字段名字
        if replace and key in replace.keys():
            key = replace.get(key)
        data[key] = value
    #2、新增默认的字段数据
    if default:
        data.update(default)
    return data



def index(request):
    print('sdf',sys.argv)
    if request.user and request.user.username!='AnonymousUser':
        return HttpResponseRedirect('/api/work')
    return HttpResponseRedirect('/api/user_action?action=login')


def user_action(request):
    action = request.GET.get('action', '')
    if action == '':
        return
    if action == 'login':
        return user_login(request)
    if action == 'register':
        return user_register(request)
    if action == 'logout':
        return user_logout(request)

def user_login(request):
    if request.method == 'GET':
        return render(request, 'login.html')

    username = request.POST.get('account', '')
    password = request.POST.get('password', '')
    if not username or not password:
        return JsonResponse({'code':0, 'msg':'出了点问题。'})

    user = auth.authenticate(username=username,password=password)
    if user:
        auth.login(request, user)
        return JsonResponse({'code':1, 'url':'/api/work'})
    else:
        return JsonResponse({'code':0, 'msg':'帐号或密码错误！'})

def user_register(request):
    info = ''
    if request.method == 'GET':
        return render(request, 'reg.html')

    result = {
        'code':0,
        'msg':''
    }
    username = request.POST.get('user', '')
    password1 = request.POST.get('pwd', '')

    if len(username) <= 3:
        info = '用户名不得小于3位'
        result['msg'] = info
        return JsonResponse(result)

    if len(password1)<8 or len(password1)>20:
        info = '密码长度不符合要求, 应在8~20位。'
        result['msg'] = info
        return JsonResponse(result)

    user = UserProfile.objects.filter(Q(username=username)).first()
    if user:
        info = '用户名已存在。'
        result['msg'] = info
        return JsonResponse(result)
    user = UserProfile(
        username=username,
        password=make_password(password1),
        is_admin = True if UserProfile.objects.count()==0 else False,
        is_superuser = True if UserProfile.objects.count()==0 else False,
        is_active = True
    )
    user.save()
    result['msg'] = info
    result['code'] = 1
    return JsonResponse(result)

@login_required(login_url='/api/user_action?action=login')
def user_logout(request):
    info = ''
    auth.logout(request)
    return HttpResponseRedirect('/api/user_action?action=login')
        
def get_single_info(uid):
    peers = RustDeskPeer.objects.filter(Q(uid=uid))
    rids = [x.rid for x in peers]
    peers = {x.rid:model_to_dict(x) for x in peers}
    #print(peers)
    devices = RustDesDevice.objects.filter(rid__in=rids)
    devices = {x.rid:x for x in devices}

    for rid, device in devices.items():
        peers[rid]['create_time'] = device.create_time.strftime('%Y-%m-%d')
        peers[rid]['update_time'] = device.update_time.strftime('%Y-%m-%d')
        peers[rid]['version'] = device.version
        peers[rid]['memory'] = device.memory
        peers[rid]['cpu'] = device.cpu
        peers[rid]['os'] = device.os

    for rid in peers.keys():
        peers[rid]['has_rhash'] = '是' if len(peers[rid]['rhash'])>1 else '否'

    return [v for k,v in peers.items()]

def get_all_info():
    devices = RustDesDevice.objects.all()
    peers = RustDeskPeer.objects.all()
    devices = {x.rid:model_to_dict2(x) for x in devices}
    for peer in peers:
        user = UserProfile.objects.filter(Q(id=peer.uid)).first()
        device = devices.get(peer.rid, None)
        if device:
            devices[peer.rid]['rust_user'] = user.username
    return [v for k,v in devices.items()]

@login_required(login_url='/api/user_action?action=login')
def work(request):

    username = request.user
    u = UserProfile.objects.get(username=username)
    single_info = get_single_info(u.id)

    all_info = get_all_info()
    print(all_info)

    return render(request, 'show_work.html', {'single_info':single_info, 'all_info':all_info, 'u':u})


def check_sharelink_expired(sharelink):
    now = datetime.datetime.now()
    if sharelink.create_time > now:
        return False
    if (now - sharelink.create_time).seconds <15 * 60:
        return False
    else:
        sharelink.is_expired = True
        sharelink.save()
        return True


@login_required(login_url='/api/user_action?action=login')
def share(request):
    peers = RustDeskPeer.objects.filter(Q(uid=request.user.id))
    sharelinks = ShareLink.objects.filter(Q(uid=request.user.id) & Q(is_used=False) & Q(is_expired=False))


    # 省资源：处理已过期请求，不主动定时任务轮询请求，在任意地方请求时，检查是否过期，过期则保存。
    now = datetime.datetime.now()
    for sl in sharelinks:
        check_sharelink_expired(sl)
    sharelinks = ShareLink.objects.filter(Q(uid=request.user.id) & Q(is_used=False) & Q(is_expired=False))
    peers = [{'id':ix+1, 'name':f'{p.rid}|{p.alias}'} for ix, p in enumerate(peers)]
    sharelinks = [{'shash':s.shash, 'is_used':s.is_used, 'is_expired':s.is_expired, 'create_time':s.create_time, 'peers':s.peers} for ix, s in enumerate(sharelinks)]

    if request.method == 'GET':
        url = request.build_absolute_uri()
        if url.endswith('share'):
            return render(request, 'share.html', {'peers':peers, 'sharelinks':sharelinks})
        else:
            shash = url.split('/')[-1]
            sharelink = ShareLink.objects.filter(Q(shash=shash))
            msg = ''
            title = '成功'
            if not sharelink:
                title = '错误'
                msg = f'链接{url}:<br>分享链接不存在或已失效。'
            else:
                sharelink = sharelink[0]
                if str(request.user.id) == str(sharelink.uid):
                    title = '错误'
                    msg = f'链接{url}:<br><br>咱就说，你不能把链接分享给自己吧？！'
                else:
                    sharelink.is_used = True
                    sharelink.save()
                    peers = sharelink.peers
                    peers = peers.split(',')
                    # 自己的peers若重叠，需要跳过
                    peers_self_ids = [x.rid for x in RustDeskPeer.objects.filter(Q(uid=request.user.id))]
                    peers_share = RustDeskPeer.objects.filter(rid__in=peers)
                    peers_share_ids = [x.rid for x in peers_share]

                    for peer in peers_share:
                        if peer.rid in peers_self_ids:
                            continue
                        peer = RustDeskPeer.objects.get(rid=peer.rid)
                        peer.id = None
                        peer.uid = request.user.id
                        peer.save()
                        msg += f"{peer.rid},"

                    msg += '已被成功获取。'

            return render(request, 'msg.html', {'title':msg, 'msg':msg})
    else:
        data = request.POST.get('data', '[]')

        data = json.loads(data)
        if not data:
            return JsonResponse({'code':0, 'msg':'数据为空。'})
        rustdesk_ids = [x['title'].split('|')[0] for x in data]
        rustdesk_ids = ','.join(rustdesk_ids)
        sharelink = ShareLink(
            uid=request.user.id,
            shash = getStrMd5(str(time.time())+salt),
            peers=rustdesk_ids,
        )
        sharelink.save()

        return JsonResponse({'code':1, 'shash':sharelink.shash})

