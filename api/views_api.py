# cython:language_level=3
from django.http import JsonResponse
import json
import time
import datetime
# import hashlib
import math
from django.contrib import auth
# from django.forms.models import model_to_dict
from api.models import RustDeskToken, UserProfile, RustDeskTag, RustDeskPeer, RustDesDevice, ConnLog, FileLog
from django.db.models import Q
import copy
from .views_front import *
from django.utils.translation import gettext as _
from django.conf import settings


def _get_uid_by_username(username: str | int) -> int:
    """
    Get user ID by username.
    args:
        username: The username to be queried.
    """
    try:
        uid = int(username)
        if not UserProfile.check_if_user_exists_by_uid(uid):
            uid = None
    except:
        uid = UserProfile.get_uid_by_username(username=username)
    return uid


def update_device_owner(rid: str, uuid: str, owner: str = None, add: bool = False, *args, **kwargs) -> RustDesDevice:
    """
    Update device owner.

    Args:
        rid: The device ID to be updated.
        uuid: The device UUID to be updated.
        owner: The owner to be set. If add is False, owner will be set to None.
        add: If True, add owner; if False, remove owner by setting it to None.
    """
    if rid == '' and uuid == '':
        return None
    # If add is False, set owner to None, indicating the owner will be removed
    if not add:
        owner = ""
    # Retrieve the device using both 'rid' and 'uuid' for filtering
    device = RustDesDevice.update_device(rid=rid, uuid=uuid, owner=owner)
    return device


def _tag_list_to_str(tag_list: list[str]) -> str:
    """
    Convert a list of tags to a string.
    """
    tag_list = [x for x in tag_list if x != '']
    return ",".join(tag_list)


def _tag_str_to_list(tag_str: str) -> list[str]:
    """
    Convert a string of tags to a list.
    """
    tag_list = tag_str.split(',')
    return [x for x in tag_list if x != '']


def update_self_tag(username: str) -> RustDeskTag:
    """
    Update self tag.
    """
    uid = _get_uid_by_username(username=username)
    if not uid:
        return None
    tag, created = RustDeskTag.objects.get_or_create(uid=uid, tag_name=settings.SELF_TAG_NAME)
    tag.tag_color = settings.SELF_TAG_COLOR
    tag.save()
    return tag


def update_self_devices_to_peers(username: str) -> None:
    """
    Update self devices to peers.
    """
    self_tag = update_self_tag(username=username)
    if self_tag is None:
        return None
    username = UserProfile.get_username_by_uid(uid=self_tag.uid)
    devices = RustDesDevice.get_devices_by_owner(owner=username)
    for device in devices:
        device: RustDesDevice = device
        peer, created = RustDeskPeer.objects.get_or_create(uid=self_tag.uid, rid=device.rid)
        peer.username = device.username
        peer.hostname = device.hostname
        peer.platform = device.os
        tags = _tag_str_to_list(peer.tags)
        if self_tag.tag_name not in tags:
            tags.append(self_tag.tag_name)
        peer.tags = _tag_list_to_str(tags)
        peer.save()


def delete_self_devices_from_peers(username: str) -> None:
    """
    When a user logs out, delete the devices from peers.
    """
    uid = _get_uid_by_username(username=username)
    if not uid:
        return None
    peers = RustDeskPeer.get_peers_by_uid(uid=uid)
    for peer in peers:
        peer: RustDeskPeer = peer
        tags = _tag_str_to_list(peer.tags)
        if settings.SELF_TAG_NAME in tags:
            if len(tags) == 1:
                peer.delete()
            else:
                tags.remove(settings.SELF_TAG_NAME)
                peer.tags = _tag_list_to_str(tags)
                peer.rhash = ""
                peer.save()


def login(request):
    result = {}
    if request.method == 'GET':
        result['error'] = _('请求方式错误！请使用POST方式。')
        return JsonResponse(result)
    data = json.loads(request.body.decode())
    username = data.get('username', '')
    password = data.get('password', '')
    rid = data.get('id', '')
    uuid = data.get('uuid', '')
    autoLogin = data.get('autoLogin', True)
    rtype = data.get('type', '')
    deviceInfo = data.get('deviceInfo', '')
    user = auth.authenticate(username=username, password=password)
    if not user:
        result['error'] = _('帐号或密码错误！请重试，多次重试后将被锁定IP！')
        return JsonResponse(result)
    user.rid = rid
    user.uuid = uuid
    user.autoLogin = autoLogin
    user.rtype = rtype
    user.deviceInfo = json.dumps(deviceInfo)
    user.save()
    update_device_owner(rid=rid, uuid=uuid, owner=username, add=True)
    update_self_tag(username=username)
    token = RustDeskToken.objects.filter(Q(uid=user.id) & Q(username=user.username) & Q(rid=user.rid)).first()

    # 检查是否过期
    if token:
        now_t = datetime.datetime.now()
        nums = (now_t - token.create_time).seconds if now_t > token.create_time else 0
        if nums >= EFFECTIVE_SECONDS:
            token.delete()
            token = None

    if not token:
        # 获取并保存token
        token = RustDeskToken(
            username=user.username,
            uid=user.id,
            uuid=user.uuid,
            rid=user.rid,
            access_token=getStrMd5(str(time.time()) + salt)
        )
        token.save()

    result['access_token'] = token.access_token
    result['type'] = 'access_token'
    result['user'] = {'name': user.username}
    return JsonResponse(result)


def logout(request):
    if request.method == 'GET':
        result = {'error': _('请求方式错误！')}
        return JsonResponse(result)

    data = json.loads(request.body.decode())
    rid = data.get('id', '')
    uuid = data.get('uuid', '')
    user = UserProfile.objects.filter(Q(rid=rid) & Q(uuid=uuid)).first()
    if not user:
        result = {'error': _('异常请求！')}
        return JsonResponse(result)
    token = RustDeskToken.objects.filter(Q(uid=user.id) & Q(rid=user.rid)).first()
    if token:
        token.delete()

    result = {'code': 1}
    update_device_owner(rid=rid, uuid=uuid, owner=None, add=False)
    delete_self_devices_from_peers(username=user.username)
    return JsonResponse(result)


def currentUser(request):
    result = {}
    if request.method == 'GET':
        result['error'] = _('错误的提交方式！')
        return JsonResponse(result)
    # postdata = json.loads(request.body)
    # rid = postdata.get('id', '')
    # uuid = postdata.get('uuid', '')

    access_token = request.META.get('HTTP_AUTHORIZATION', '')
    access_token = access_token.split('Bearer ')[-1]
    token = RustDeskToken.objects.filter(Q(access_token=access_token)).first()
    user = None
    if token:
        user = UserProfile.objects.filter(Q(id=token.uid)).first()

    if user:
        if token:
            result['access_token'] = token.access_token
        result['type'] = 'access_token'
        result['name'] = user.username
    return JsonResponse(result)


def ab(request):
    '''
    '''
    access_token = request.META.get('HTTP_AUTHORIZATION', '')
    access_token = access_token.split('Bearer ')[-1]
    token = RustDeskToken.objects.filter(Q(access_token=access_token)).first()
    if not token:
        result = {'error': _('拉取列表错误！')}
        return JsonResponse(result)
    if request.method == 'GET':
        update_self_devices_to_peers(username=token.uid)
        result = {}
        uid = token.uid
        tags = RustDeskTag.objects.filter(Q(uid=uid))
        tag_names = []
        tag_colors = {}
        if tags:
            tag_names = [str(x.tag_name) for x in tags]
            tag_colors = {str(x.tag_name): int(x.tag_color) for x in tags if x.tag_color != ''}

        peers_result = []
        peers = RustDeskPeer.objects.filter(Q(uid=uid))
        if peers:
            for peer in peers:
                tags = _tag_str_to_list(peer.tags)
                tmp = {
                    'id': peer.rid,
                    'username': peer.username,
                    'hostname': peer.hostname,
                    'alias': peer.alias,
                    'platform': peer.platform,
                    'tags': tags,
                    'hash': peer.rhash,
                }
                peers_result.append(tmp)

        result['updated_at'] = datetime.datetime.now()
        result['data'] = {
            'tags': tag_names,
            'peers': peers_result,
            'tag_colors': json.dumps(tag_colors)
        }
        result['data'] = json.dumps(result['data'])
        return JsonResponse(result)
    else:
        postdata = json.loads(request.body.decode())
        data = postdata.get('data', '')
        data = {} if data == '' else json.loads(data)
        tagnames = data.get('tags', [])
        tag_colors = data.get('tag_colors', '')
        tag_colors = {} if tag_colors == '' else json.loads(tag_colors)
        peers = data.get('peers', [])

        if tagnames:
            # 删除旧的tag
            RustDeskTag.objects.filter(uid=token.uid).delete()
            # 增加新的
            newlist = []
            for name in tagnames:
                tag = RustDeskTag(
                    uid=token.uid,
                    tag_name=name,
                    tag_color=tag_colors.get(name, '')
                )
                newlist.append(tag)
            RustDeskTag.objects.bulk_create(newlist)
        if peers:
            RustDeskPeer.objects.filter(uid=token.uid).delete()
            newlist = []
            for one in peers:
                tags = one['tags']
                if settings.SELF_TAG_NAME in tags:
                    tags.remove(settings.SELF_TAG_NAME)
                tags_str = _tag_list_to_str(tags)
                peer = RustDeskPeer(
                    uid=token.uid,
                    rid=one['id'],
                    username=one['username'],
                    hostname=one['hostname'],
                    alias=one['alias'],
                    platform=one['platform'],
                    tags=tags_str,
                    rhash=one['hash'],
                )
                newlist.append(peer)
            RustDeskPeer.objects.bulk_create(newlist)
            # update self devices to peers after updating the address book
            update_self_devices_to_peers(username=token.uid)

    result = {
        'code': 102,
        'data': _('更新地址簿有误')
    }
    return JsonResponse(result)


def ab_get(request):
    # 兼容 x86-sciter 版客户端，此版客户端通过访问 "POST /api/ab/get" 来获取地址簿
    request.method = 'GET'
    return ab(request)


def sysinfo(request) -> JsonResponse:
    # 客户端注册服务后，才会发送设备信息
    result = {}
    if request.method == 'GET':
        result['error'] = _('错误的提交方式！')
        return JsonResponse(result)

    postdata: dict[str, str] = json.loads(request.body)
    device = RustDesDevice.objects.filter(Q(rid=postdata['id']) & Q(uuid=postdata['uuid'])).first()
    if not device:
        device = RustDesDevice(
            rid=postdata['id'],
            cpu=postdata['cpu'],
            hostname=postdata['hostname'],
            memory=postdata['memory'],
            os=postdata['os'],
            username=postdata.get('username', '-'),
            uuid=postdata['uuid'],
            version=postdata['version'],
        )
        device.save()
    else:
        postdata2 = copy.copy(postdata)
        postdata2['rid'] = postdata2['id']
        postdata2.pop('id')
        RustDesDevice.objects.filter(Q(rid=postdata['id']) & Q(uuid=postdata['uuid'])).update(**postdata2)
    result['data'] = 'ok'
    return JsonResponse(result)


def heartbeat(request):
    postdata = json.loads(request.body)
    device = RustDesDevice.objects.filter(Q(rid=postdata['id']) & Q(uuid=postdata['uuid'])).first()
    if device:
        device.save()
    # token保活
    create_time = datetime.datetime.now() + datetime.timedelta(seconds=EFFECTIVE_SECONDS)
    RustDeskToken.objects.filter(Q(rid=postdata['id']) & Q(uuid=postdata['uuid'])).update(create_time=create_time)
    result = {}
    result['data'] = _('在线')
    return JsonResponse(result)


def audit(request):
    postdata = json.loads(request.body)
    # print(postdata)
    audit_type = postdata['action'] if 'action' in postdata else ''
    if audit_type == 'new':
        new_conn_log = ConnLog(
            action=postdata['action'] if 'action' in postdata else '',
            conn_id=postdata['conn_id'] if 'conn_id' in postdata else 0,
            from_ip=postdata['ip'] if 'ip' in postdata else '',
            from_id='',
            rid=postdata['id'] if 'id' in postdata else '',
            conn_start=datetime.datetime.now(),
            session_id=postdata['session_id'] if 'session_id' in postdata else 0,
            uuid=postdata['uuid'] if 'uuid' in postdata else '',
        )
        new_conn_log.save()
    elif audit_type == "close":
        ConnLog.objects.filter(Q(conn_id=postdata['conn_id'])).update(conn_end=datetime.datetime.now())
    elif 'is_file' in postdata:
        # print(postdata)
        files = json.loads(postdata['info'])['files']
        filesize = convert_filesize(int(files[0][1]))
        new_file_log = FileLog(
            file=postdata['path'],
            user_id=postdata['peer_id'],
            user_ip=json.loads(postdata['info'])['ip'],
            remote_id=postdata['id'],
            filesize=filesize,
            direction=postdata['type'],
            logged_at=datetime.datetime.now(),
        )
        new_file_log.save()
    else:
        try:
            peer = postdata['peer']
            ConnLog.objects.filter(Q(conn_id=postdata['conn_id'])).update(session_id=postdata['session_id'])
            ConnLog.objects.filter(Q(conn_id=postdata['conn_id'])).update(from_id=peer[0])
        except Exception as e:
            print(postdata, e)

    result = {
        'code': 1,
        'data': 'ok'
    }
    return JsonResponse(result)


def convert_filesize(size_bytes):
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return "%s %s" % (s, size_name[i])


def users(request):
    result = {
        'code': 1,
        'data': _('好的')
    }
    return JsonResponse(result)


def peers(request):
    result = {
        'code': 1,
        'data': 'ok'
    }
    return JsonResponse(result)
