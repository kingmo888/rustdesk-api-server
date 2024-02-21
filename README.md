# rustdesk-api-server

## 如果项目有帮到你，给个star不过分吧？

[The English explanation is available by clicking here.](https://github.com/kingmo888/rustdesk-api-server/blob/master/README_EN.md)

<p align="center">
    <i>一个 python 实现的 Rustdesk API 接口，支持 WebUI 管理</i>
    <br/>
    <img src ="https://img.shields.io/badge/Version-1.4.5-blueviolet.svg"/>
    <img src ="https://img.shields.io/badge/Python-3.7|3.8|3.9|3.10|3.11-blue.svg" />
    <img src ="https://img.shields.io/badge/Django-3.2+|4.x-yelow.svg" />
    <br/>
    <img src ="https://img.shields.io/badge/Platform-Windows|Linux-green.svg"/>
    <img src ="https://img.shields.io/badge/Docker-arm|arm64|amd64-blue.svg" />
</p>

![主页面](images/front_main.png)

## 功能特点

- 支持前台网页自主注册和登录。
  - 注册页与登录页：
  ![Front Registration](images/front_reg.png)
  ![Front Login](images/front_login.png)

- 支持前台展示设备信息，分为管理员版、用户版。
- 支持自定义别名（备注）。
- 支持后台管理。
- 支持彩色标签。
![Rust Books](images/rust_books.png)

- 支持设备在线统计。
- 支持设备密码保存。
- 利用心跳接口自动管理token并保活。
- 支持分享设备给其他用户。
![Rust Share](images/share.png)
- 支持web控制端（目前仅支持非SSL模式，见下面使用问题说明）
![Rust Share](images/webui.png)

后台主页：
![Admin Main](images/admin_main.png)

## 安装

### 方法1：开箱即用

仅支持Windows，请前往 release 下载，无需安装环境，直接运行`启动.bat`即可。 截图：

![window直接运行版](/images/windows_run.png)


### 方法2：代码运行

```bash
# 将代码克隆到本地
git clone https://github.com/kingmo888/rustdesk-api-server.git
# 进入目录
cd rustdesk-api-server
# 安装依赖
pip install -r requirements.txt
# 确保依赖安装正确后，执行：
# 端口号请自行修改，建议保留21114为Rustdesk API默认端口
python manage.py runserver 0.0.0.0:21114
```

此时即可使用 `http://本机IP:端口` 的形式来访问。

**注意**：如果 CentOS 配置时，Django4 会因为系统的 sqlite3 版本过低而出问题，请修改依赖库中的文件。路径：`xxxx/Lib/site-packages/django/db/backends/sqlite3/base.py` （根据情况自行查找包所在地址），修改内容:
```python
# from sqlite3 import dbapi2 as Database   #(注释掉这行)
from pysqlite3 import dbapi2 as Database # 启用pysqlite3
```

### 方法3：Docker 运行

#### Docker方法1：自行构建
```bash
git clone https://github.com/kingmo888/rustdesk-api-server.git
cd rustdesk-api-server
docker compose --compatibility up --build -d
```
感谢热心网友 @ferocknew 提供。

#### Docker方法2：预构建运行

docker run 命令：

```bash
docker run -d \
  --name rustdesk-api-server \
  -p 21114:21114 \
  -e CSRF_TRUSTED_ORIGINS=http://yourdomain.com:21114 \ #防跨域信任来源，可选
  -e ID_SERVER=yourdomain.com \ #Web控制端使用的ID服务器
  -v /yourpath/db:/rustdesk-api-server/db \ #修改/yourpath/db为你宿主机数据库挂载目录
  -v /etc/timezone:/etc/timezone:ro \
  -v /etc/localtime:/etc/localtime:ro \
  --network bridge \
  --restart unless-stopped \
  ghcr.io/kingmo888/rustdesk-api-server:latest
```

docker-compose 方式：

```yaml
version: "3.8"
services:
  rustdesk-api-server:
    container_name: rustdesk-api-server
    image: ghcr.io/kingmo888/rustdesk-api-server:latest
    environment:
      - CSRF_TRUSTED_ORIGINS=http://yourdomain.com:21114 #防跨域信任来源，可选
      - ID_SERVER=yourdomain.com #Web控制端使用的ID服务器
    volumes:
      - /yourpath/db:/rustdesk-api-server/db #修改/yourpath/db为你宿主机数据库挂载目录
      - /etc/timezone:/etc/timezone:ro
      - /etc/localtime:/etc/localtime:ro
    network_mode: bridge
    ports:
      - "21114:21114"
    restart: unless-stopped
```

## 环境变量

| 变量名 | 参考值 | 备注 |
| ---- | ------- | ----------- |
| `HOST` | 默认 `0.0.0.0` | 绑定服务的IP |
| `TZ` | 默认 `Asia/Shanghai`，可选 | 时区 |
| `SECRET_KEY` | 可选，自定义一串随机字符 | 程序加密秘钥 |
| `CSRF_TRUSTED_ORIGINS` | 可选，默认关闭验证；<br>如需开启填写你的访问地址 `http://yourdomain.com:21114` <br>**如需关闭验证请删除此变量，而不是留空** | 防跨域信任来源 |
| `ID_SERVER` | 可选，默认为和API服务器同主机。<br>可自定义如 `yourdomain.com` | Web控制端使用的ID服务器 |
| `DEBUG` | 可选，默认 `False` | 调试模式 |

## 使用问题

- 管理员设置

  当数据库中不存在账户时，第一个注册的账户直接获取超级管理员权限，之后注册账户为普通账户。

- 设备信息

  经测试，客户端会在非绿色版模式下，安装为服务的模式中，定时发送设备信息到api接口，所以如果想要设备信息，需要安装rustdesk客户端并启动服务。

- 连接速度慢

  新版本Key模式链接速度慢，可以在服务端启动服务时，不要带参数的-k，此时，客户端也不能配置key。

- Web控制端配置

  - 设置ID_SERVER环境变量，或修改rustdesk_server_api/settings.py文件中ID_SERVER配置项，将ID服务器/中继服务器IP或域名填上。

- Web控制端一直转圈

  - 检查ID服务器填写是否正确

  - Web控制端目前仅支持非SSL模式，若webui为https访问，请将s去掉，否则ws连不上一直转圈。如：https://domain.com/webui，改为http://domain.com/webui

- 后台操作登录或登出时：CSRF验证失败. 请求被中断.

  这种操作大概率是docker配置+nginx反代+SSL的组合，要注意修改CSRF_TRUSTED_ORIGINS，如果是ssl那就是https开头，否则就是http。

## 开发计划

- [x] 分享设备给其他已注册用户（v1.3+）

  > 说明：类似网盘url分享，url激活后可以获得某个或某组或某个标签下的设备
  > 备注：其实web api作为中间件，可做的不多，更多功能还是需要修改客户端来实现，就不太值当了。

- [x] 集成Web客户端形式（v1.4+）

  > 将大神的web客户端集成进来，已集成。 [来源](https://www.52pojie.cn/thread-1708319-1-1.html)
  
- [ ] 对过期（不在线）设备的过滤，用以区分在线&离线设备

  > 通过配置方式，对过期超过指定时间的设备清理或过滤。

- [ ] 首屏拆分为用户列表页与管理员列表页并增加分页。

- [ ] 支持信息导出到为xlsx文件。


## 其他相关工具

- [可以修改客户端ID的CMD脚本](https://github.com/abdullah-erturk/RustDesk-ID-Changer)

- [rustdesk](https://github.com/rustdesk/rustdesk)

- [rustdesk-server](https://github.com/rustdesk/rustdesk-server)

## Stargazers over time
[![Stargazers over time](https://starchart.cc/kingmo888/rustdesk-api-server.svg?variant=adaptive)](https://starchart.cc/kingmo888/rustdesk-api-server)
