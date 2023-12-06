## Rustdesk Api接口介绍
<p align="center">
    <img src ="https://img.shields.io/badge/version-1.0.0-blueviolet.svg"/>
    <img src ="https://img.shields.io/badge/platform-windows|linux-green.svg"/>
    <img src ="https://img.shields.io/badge/python-3.7|3.8|3.9|3.10|3.11-blue.svg" />
    <img src ="https://img.shields.io/badge/Django-3.2+|4.x-yelow.svg" />
</p>

### 缘起
看了市面上各类RustDesk WEB API版本，或多或少的存在一些问题，比如说，需要通过url注册、新版客户端某些接口不支持、无法方便的修改密码等不足，因此博采众长，撸一个自己喜欢的版本来用。在此要感谢论坛及github的各位朋友写的接口，省去了我抓包找接口的时间。
![主页面](/images/front_main.png)

### 功能特点
 - 支持前台网页自主注册和登录。
   - 注册页与登录页：
  
  <img src="images/front_reg.png" width="45%" />
  <img src="images/front_login.png" width="45%" />
  
 - 支持前台展示设备信息，分为管理员版、用户版。
 - 支持自定义别名（备注）。
 - 支持后台管理。
 - 支持彩色标签。
 
 <img src="images/rust_books.png" width="45%" />
 
 - 支持设备在线统计。
 - 支持设备密码保存。
 - 利用心跳接口自动管理token并保活。
 - 支持分享设备给其他用户（本功能暂未实现）。
 
 后台主页：
<img src="images/admin_main.png" width="60%" />

### 管理员设置
当数据库中不存在账户时，第一个注册的账户直接获取超级管理员权限，之后注册账户为普通账户。

### 其他说明
设备信息
经测试，客户端会在非绿色版模式下，安装为服务的模式中，定时发送设备信息到api接口，
所以如果想要设备信息，需要安装rustdesk客户端并启动服务。

### 连接速度慢
新版本Key模式链接速度慢，可以在服务端启动服务时，不要带参数的-k，此时，客户端也不能配置key



### 获取方法

#### 开箱即用版

  Window独立打包版，无需安装环境，直接运行`启动.bat`即可。请前往release下载。仅支持windows
  独立版截图：![window独立绿色版](/images/windows_run.png)



#### 代码版本

将代码克隆到本地后，请先安装依赖：
`pip install -r requirements.txt`

确保依赖安装正确后，执行：
`python manage.py runserver 0.0.0.0:21114`  端口号请自行修改。

此时即可使用`http://本机IP:端口`的形式来访问啦。

支持Django3及Django4+
注意，如果cengtos配置时，Django4会因为系统的sqlite3版本过低而出问题，请修改依赖库中的文件，路径： 
`xxxx/Lib/site-packages/django/db/backends/sqlite3/base.py` (这是例子，根据情况自行查找包所在地址)


修改内容:
```
# from sqlite3 import dbapi2 as Database   #(注释掉这行)
from pysqlite3 import dbapi2 as Database # 启用pysqlite3
```

#### Docker方式



### 计划开发

1、分享设备给其他已注册用户

    说明：类似网盘url分享，url激活后可以获得某个或某组或某个标签下的设备
    备注：其实web api作为中间件，可做的不多，更多功能还是需要修改客户端来实现，就不太值当了。
