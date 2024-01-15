# rustdesk-api-server

<p align="center">
    <i>A Python implementation of Rustdesk API with WebUI management support</i>
    <br/>
    <img src ="https://img.shields.io/badge/Version-1.4.2-blueviolet.svg"/>
    <img src ="https://img.shields.io/badge/Python-3.7|3.8|3.9|3.10|3.11-blue.svg" />
    <img src ="https://img.shields.io/badge/Django-3.2+|4.x-yelow.svg" />
    <br/>
    <img src ="https://img.shields.io/badge/Platform-Windows|Linux-green.svg"/>
    <img src ="https://img.shields.io/badge/Docker-arm|arm64|amd64-blue.svg" />
</p>

## Background

After reviewing various versions of RustDesk WEB APIs available in the market, I found that there are some shortcomings, such as the need for URL registration, lack of support for certain interfaces in the new client version, and the inability to easily change passwords. Therefore, I decided to combine the strengths of different versions and create my own version that I like. I want to express my gratitude to the friends on the forum and GitHub who wrote the interfaces, saving me time in capturing and finding interfaces.

![Main Page](images/front_main.png)

## Features

- Supports self-registration and login on the front-end web page.
  - Registration and login pages:
  ![Front Registration](images/front_reg.png)
  ![Front Login](images/front_login.png)

- Displays device information on the front-end, with separate versions for administrators and users.
- Supports custom aliases (remarks).
- Supports backend management.
- Supports colored labels.
![Rust Books](images/rust_books.png)

- Supports device online statistics.
- Supports saving device passwords.
- Automatically manages tokens and keeps them alive using the heartbeat interface.
- Supports sharing devices with other users.
![Rust Share](images/share.png)
- Supports web control panel (currently only supports non-SSL mode, see usage issues below).
![Rust Share](images/webui.png)

Admin homepage:
![Admin Main](images/admin_main.png)

## Installation

### Method 1: Out-of-the-box

Only supports Windows. Download the release, no need to install the environment, just run `启动.bat` directly. Screenshots:

![Run directly on Windows](/images/windows_run.png)

### Method 2: Run the Code

```bash
# Clone the code locally
git clone https://github.com/kingmo888/rustdesk-api-server.git
# Enter the directory
cd rustdesk-api-server
# Install dependencies
pip install -r requirements.txt
# After ensuring that the dependencies are installed correctly, execute:
# Modify the port number as needed; it is recommended to keep 21114 as the default port for Rustdesk API
python manage.py runserver 0.0.0.0:21114
```

Now you can access it using the format `http://localhost:port`.

**Note**: If configuring on CentOS, Django 4 may have issues due to the system's low version of sqlite3. Please modify the file in the dependency library. Path: `xxxx/Lib/site-packages/django/db/backends/sqlite3/base.py` (find the package location according to your situation), and modify the content:
```python
# from sqlite3 import dbapi2 as Database   #(Comment out this line)
from pysqlite3 import dbapi2 as Database # Enable pysqlite3
```

### Method 3: Docker Run

#### Docker Method 1: Build it yourself
```bash
git clone https://github.com/kingmo888/rustdesk-api-server.git
cd rustdesk-api-server
docker compose --compatibility up --build -d
```
Thanks to the enthusiastic netizen @ferocknew for providing this.

#### Docker Method 2: Pre-built Run

docker run command:

```bash
docker run -d \
  --name rustdesk-api-server \
  -p 21114:21114 \
  -e CSRF_TRUSTED_ORIGINS=http://yourdomain.com:21114 \ # Cross-origin trusted source, optional
  -e ID_SERVER=yourdomain.com \ # ID server used by the Web control panel
  -v /yourpath/db:/rustdesk-api-server/db \ # Modify /yourpath/db to the directory where you want to mount the database on your host
  -v /etc/timezone:/etc/timezone:ro \
  -v /etc/localtime:/etc/localtime:ro \
  --network bridge \
  --restart unless-stopped \
  ghcr.io/kingmo888/rustdesk-api-server:latest
```

docker-compose method:

```yaml
version: "3.8"
services:
  rustdesk-api-server:
    container_name: rustdesk-api-server
    image: ghcr.io/kingmo888/rustdesk-api-server:latest
    environment:
      - CSRF_TRUSTED_ORIGINS=http://yourdomain.com:21114 # Cross-origin trusted source, optional
      - ID_SERVER=yourdomain.com # ID server used by the Web control panel
    volumes:
      - /yourpath/db:/rustdesk-api-server/db # Modify /yourpath/db to the directory where you want to mount the database on your host
      - /etc/timezone:/etc/timezone:ro
      - /etc/localtime:/etc/localtime:ro
    network_mode: bridge
    ports:
      - "21114:21114"
    restart: unless-stopped
```

## Environment Variables

| Variable Name | Reference Value | Remarks |
| ---- | ------- | ----------- |
| `HOST` | Default `0.0.0.0` | IP to bind the service |
| `TZ` | Default `Asia/Shanghai`, optional | Timezone |
| `SECRET_KEY` | Optional, custom random string | Program encryption key |
| `CSRF_TRUSTED_ORIGINS` | Optional, verification closed by default;<br> If needed, fill in your access address `http://yourdomain.com:21114` <br>**If you want to disable verification, please delete this variable instead of leaving it blank** | Cross-origin trusted source |
| `ID_SERVER` | Optional, default is the same host as the API server.<br> Can be customized, such as `yourdomain.com` | ID server used by the Web control panel |
| `DEBUG` | Optional, default `False` | Debug mode |

## Usage Issues

- Administrator Setup

  When there is no account in the database, the first registered account will directly obtain super administrator privileges, and subsequent registered accounts will be ordinary accounts.

- Device Information

  After testing, the client will periodically send device information to the API interface in the service mode installed in non-green mode. Therefore, if you want device information, you need to install the rustdesk client and start the service.

- Slow Connection Speed

  In the new Key mode, the connection speed is slow. When starting the service on the server, do not use the -k without parameters. In this case, the client cannot configure the key either.

- Web Control Panel Configuration

  - Set the ID_SERVER environment variable, or modify the ID_SERVER configuration

 item in the rustdesk_server_api/settings.py file, and fill in the IP or domain name of the ID server.

- Web Control Panel Keeps Spinning

  - Check if the ID server is filled in correctly.

  - The Web control panel currently only supports non-SSL mode. If the webui is accessed via https, please remove the 's', otherwise ws will not connect and keep spinning. For example: https://domain.com/webui, change it to http://domain.com/webui

- CSRF verification fails when logging in or logging out of backend operations: The CSRF verification failed. The request was aborted.

  This type of operation is most likely a combination of Docker configuration + Nginx reverse proxy + SSL. Pay attention to modifying CSRF_TRUSTED_ORIGINS. If it is SSL, it should start with https, otherwise it should be http.

## Development Plans

- [x] Share devices with other registered users (v1.3+)

  > Explanation: Similar to sharing URLs of cloud disks, activating the URL will allow access to devices under a certain group or certain label.
  > Note: As a middleware, the web API can't do much, and more features still need to be implemented by modifying the client, which is not very cost-effective.

- [x] Integration of Web client form (v1.4+)

  > Integrated the web client of a master. Already integrated. [Source](https://www.52pojie.cn/thread-1708319-1-1.html)

## Other Related Tools

- [CMD script to change client ID](https://github.com/abdullah-erturk/RustDesk-ID-Changer)

- [rustdesk](https://github.com/rustdesk/rustdesk)

- [rustdesk-server](https://github.com/rustdesk/rustdesk-server)