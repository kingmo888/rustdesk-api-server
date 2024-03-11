# 默认数据库(sqlite3)转Mysql数据库保姆级教程

### 本教程尽量保持源码安装与docker安装的通用性。

1、源码安装（如果采用源码安装的跳过1、2步骤）
```
# 将代码克隆到本地
git clone https://github.com/kingmo888/rustdesk-api-server.git
# 进入目录
cd rustdesk-api-server
# 安装依赖
pip install -r requirements.txt
```

2、覆盖数据库

全新安装时数据库为默认数据库，请将你正在使用的数据库覆盖到`/db/db.sqlite3`

3、 从sqlite数据库备份数据

执行命令：`python manage.py dumpdata > data.json`，将数据导出到根目录下的`data.json`中。

4、修改数据库配置

假设新建的mysql空数据库的信息如下：

| 信息 | 值 |
| ------- | ------- |
| 数据库服务器IP | 192.168.1.33 |
| 数据库名 | rustdesk_api |
| 数据库用户名 | myuser |
| 数据库密码 | 123456 |
| 数据库端口 | 3099 |


在文件`rustdesk_server_api/settings.py`中依次修改如下配置：

- (1) `DATABASE_TYPE = os.environ.get("DATABASE_TYPE", 'SQLITE')`改为`DATABASE_TYPE = os.environ.get("DATABASE_TYPE", 'MYSQL')`
- (2) `MYSQL_HOST = os.environ.get("MYSQL_HOST", '127.0.0.1')`改为`MYSQL_HOST = os.environ.get("MYSQL_HOST", '192.168.1.33')`
- (3) `MYSQL_DBNAME = os.environ.get("MYSQL_DBNAME", '-')`改为`MYSQL_DBNAME = os.environ.get("MYSQL_DBNAME", 'rustdesk_api')`
- (4) `MYSQL_USER = os.environ.get("MYSQL_USER", '-')`改为`MYSQL_USER = os.environ.get("MYSQL_USER", 'myuser')`
- (5) `MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", '-')`改为`MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", '123456')`
- (6) `MYSQL_PORT = os.environ.get("MYSQL_PORT", '3306')`改为`MYSQL_PORT = os.environ.get("MYSQL_PORT", '3099')`

5、使用命令在mysql中创建表

`python manage.py makemigrations`

`python manage.py migrate`

通过mysql数据库管理工具查看数据库表：`django_content_type`, `auth_permission`，如果存在数据，需要将这两个标清空，否则导入备份数据时会出错（提示重复导入数据）。

6、将备份数据导入mysql

执行`python manage.py loaddata data.json`

在加载数据的过程中，最有可能的报错是提示导出的数据文件data.json中编码不是utf-8，需要把data.json文件转为utf-8格式，然后在加载数据到mysql中。

还有可能会提示其他原数据有问题导致的报错，根据报错提示查看原数据的问题。修改之后再次从sqlite3导出数据，然后导入数据。


7、docker使用

如果mysql数据库已经配置好，则只需要将环境变量中mysql的部分按要求修改，重启即可。
如果未配置mysql数据库，则将`步骤6`中已经配置好的mysql数据库导出，并在你需要的指定位置新建并还原，然后将环境变量中mysql的部分按要求修改，重启即可。