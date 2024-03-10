#!/bin/bash

cd /rustdesk-api-server;

if [ ! -e "./db/db.sqlite3" ]; then
    cp "./db_bak/db.sqlite3" "./db/db.sqlite3"
    echo "首次运行，初始化数据库"
fi

python manage.py makemigrations
python manage.py migrate
python manage.py runserver $HOST:21114;
