# cython:language_level=3
from django.db import models
from django.contrib import admin
from django.utils.translation import gettext as _
from django.db.models import Q
from django.db.models.query import QuerySet


class RustDeskToken(models.Model):
    ''' Token
    '''
    username = models.CharField(verbose_name=_('用户名'), max_length=20)
    rid = models.CharField(verbose_name=_('RustDesk ID'), max_length=16)
    uid = models.CharField(verbose_name=_('用户ID'), max_length=16)
    uuid = models.CharField(verbose_name=_('uuid'), max_length=60)
    access_token = models.CharField(verbose_name=_('access_token'), max_length=60, blank=True)
    create_time = models.DateTimeField(verbose_name=_('登录时间'), auto_now_add=True)
    # expire_time = models.DateTimeField(verbose_name='过期时间')

    class Meta:
        ordering = ('-username',)
        verbose_name = "Token"
        verbose_name_plural = _("Token列表")


class RustDeskTokenAdmin(admin.ModelAdmin):
    list_display = ('username', 'uid')
    search_fields = ('username', 'uid')
    list_filter = ('create_time', )  # 过滤器


class RustDeskTag(models.Model):
    ''' Tags
    '''
    uid = models.CharField(verbose_name=_('所属用户ID'), max_length=16)
    tag_name = models.CharField(verbose_name=_('标签名称'), max_length=60)
    tag_color = models.CharField(verbose_name=_('标签颜色'), max_length=60, blank=True)

    class Meta:
        ordering = ('-uid',)
        verbose_name = "Tags"
        verbose_name_plural = _("Tags列表")


class RustDeskTagAdmin(admin.ModelAdmin):
    list_display = ('tag_name', 'uid', 'tag_color')
    search_fields = ('tag_name', 'uid')
    list_filter = ('uid', )


class RustDeskPeer(models.Model):
    ''' Pees
    '''
    uid = models.CharField(verbose_name=_('用户ID'), max_length=16)
    rid = models.CharField(verbose_name=_('客户端ID'), max_length=60)
    username = models.CharField(verbose_name=_('系统用户名'), max_length=20)
    hostname = models.CharField(verbose_name=_('操作系统名'), max_length=30)
    alias = models.CharField(verbose_name=_('别名'), max_length=30)
    platform = models.CharField(verbose_name=_('平台'), max_length=30)
    tags = models.CharField(verbose_name=_('标签'), max_length=30)
    rhash = models.CharField(verbose_name=_('设备链接密码'), max_length=60)

    class Meta:
        ordering = ('-username',)
        verbose_name = "Peers"
        verbose_name_plural = _("Peers列表")

    @classmethod
    def get_peers_by_uid(cls, uid: str) -> QuerySet:
        ''' 
        Get all peers owned by a user.

        Args:
            uid (required): str, uid

        Returns:
            QuerySet: A queryset of peers owned by the user.
        '''
        return cls.objects.filter(uid=uid)


class RustDeskPeerAdmin(admin.ModelAdmin):
    list_display = ('rid', 'uid', 'username', 'hostname', 'platform', 'alias', 'tags')
    search_fields = ('deviceid', 'alias')
    list_filter = ('rid', 'uid', )


class RustDesDevice(models.Model):
    rid = models.CharField(verbose_name=_('客户端ID'), max_length=60, blank=True)
    cpu = models.CharField(verbose_name='CPU', max_length=100)
    hostname = models.CharField(verbose_name=_('主机名'), max_length=100)
    memory = models.CharField(verbose_name=_('内存'), max_length=100)
    os = models.CharField(verbose_name=_('操作系统'), max_length=100)
    uuid = models.CharField(verbose_name='uuid', max_length=100)
    username = models.CharField(verbose_name=_('系统用户名'), max_length=100, blank=True)
    version = models.CharField(verbose_name=_('客户端版本'), max_length=100)
    create_time = models.DateTimeField(verbose_name=_('设备注册时间'), auto_now_add=True)
    update_time = models.DateTimeField(verbose_name=('设备更新时间'), auto_now=True, blank=True)
    owner = models.CharField(verbose_name=_('所属用户'), max_length=100, blank=True)

    class Meta:
        ordering = ('-rid',)
        verbose_name = _("设备")
        verbose_name_plural = _("设备列表")

    @classmethod
    def update_device(cls, rid: str, uuid: str, cpu: str = None,
                      hostname: str = None, memory: str = None, os: str = None,
                      username: str = None, version: str = None, owner: str = None
                      ) -> 'RustDesDevice':
        ''' 
        Update or create a device and update its information if provided.

        Args:
            rid (required): str, rid
            uuid (required): str, uuid
            cpu (optional): str, default None
            hostname (optional): str, default None
            memory (optional): str, default None
            os (optional): str, default None
            username (optional): str, default None
            version (optional): str, default None
            owner (optional): str, default None

        Returns:
            RustDesDevice: The created or updated device object.
        '''
        # Use get_or_create to either get an existing device or create a new one
        device, created = cls.objects.get_or_create(rid=rid, uuid=uuid)
        # Collect all non-None fields that need to be updated
        update_fields = {}

        if cpu is not None:
            update_fields['cpu'] = cpu
        if hostname is not None:
            update_fields['hostname'] = hostname
        if memory is not None:
            update_fields['memory'] = memory
        if os is not None:
            update_fields['os'] = os
        if username is not None:
            update_fields['username'] = username
        if version is not None:
            update_fields['version'] = version
        if owner is not None:  # assuming you want to update owner even when it is None
            update_fields['owner'] = owner
        # Update only the provided fields
        if update_fields:
            for field, value in update_fields.items():
                setattr(device, field, value)
            device.save(update_fields=update_fields.keys())
        return device

    @classmethod
    def get_devices_by_owner(cls, owner: str) -> QuerySet:
        ''' 
        Get all devices owned by a user.

        Args:
            owner (required): str, owner

        Returns:
            QuerySet: A queryset of devices owned by the user.
        '''
        return cls.objects.filter(owner=owner)


class RustDesDeviceAdmin(admin.ModelAdmin):
    list_display = ('rid', 'hostname', 'memory', 'uuid', 'version', 'create_time', 'update_time')
    search_fields = ('hostname', 'memory')
    list_filter = ('rid', )


class ConnLog(models.Model):
    id = models.IntegerField(verbose_name='ID', primary_key=True)
    action = models.CharField(verbose_name='Action', max_length=20, null=True)
    conn_id = models.CharField(verbose_name='Connection ID', max_length=10, null=True)
    from_ip = models.CharField(verbose_name='From IP', max_length=30, null=True)
    from_id = models.CharField(verbose_name='From ID', max_length=20, null=True)
    rid = models.CharField(verbose_name='To ID', max_length=20, null=True)
    conn_start = models.DateTimeField(verbose_name='Connected', null=True)
    conn_end = models.DateTimeField(verbose_name='Disconnected', null=True)
    session_id = models.CharField(verbose_name='Session ID', max_length=60, null=True)
    uuid = models.CharField(verbose_name='uuid', max_length=60, null=True)


class ConnLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'action', 'conn_id', 'from_ip', 'from_id', 'rid', 'conn_start', 'conn_end', 'session_id', 'uuid')
    search_fields = ('from_ip', 'rid')
    list_filter = ('id', 'from_ip', 'from_id', 'rid', 'conn_start', 'conn_end')


class FileLog(models.Model):
    id = models.IntegerField(verbose_name='ID', primary_key=True)
    file = models.CharField(verbose_name='Path', max_length=500)
    remote_id = models.CharField(verbose_name='Remote ID', max_length=20, default='0')
    user_id = models.CharField(verbose_name='User ID', max_length=20, default='0')
    user_ip = models.CharField(verbose_name='User IP', max_length=20, default='0')
    filesize = models.CharField(verbose_name='Filesize', max_length=500, default='')
    direction = models.IntegerField(verbose_name='Direction', default=0)
    logged_at = models.DateTimeField(verbose_name='Logged At', null=True)


class FileLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'file', 'remote_id', 'user_id', 'user_ip', 'filesize', 'direction', 'logged_at')
    search_fields = ('file', 'remote_id', 'user_id', 'user_ip')
    list_filter = ('id', 'file', 'remote_id', 'user_id', 'user_ip', 'filesize', 'direction', 'logged_at')


class ShareLink(models.Model):
    ''' 分享链接
    '''
    uid = models.CharField(verbose_name=_('用户ID'), max_length=16)
    shash = models.CharField(verbose_name=_('链接Key'), max_length=60)
    peers = models.CharField(verbose_name=_('机器ID列表'), max_length=20)
    is_used = models.BooleanField(verbose_name=_('是否使用'), default=False)
    is_expired = models.BooleanField(verbose_name=_('是否过期'), default=False)
    create_time = models.DateTimeField(verbose_name=_('生成时间'), auto_now_add=True)

    class Meta:
        ordering = ('-create_time',)
        verbose_name = _("分享链接")
        verbose_name_plural = _("链接列表")


class ShareLinkAdmin(admin.ModelAdmin):
    list_display = ('shash', 'uid', 'peers', 'is_used', 'is_expired', 'create_time')
    search_fields = ('peers', )
    list_filter = ('is_used', 'uid', 'is_expired')
