#!/bin/bash

cd /rustdesk-api-server;
python manage.py runserver $HOST:21114;
