FROM python:3.11.7-slim-bullseye

RUN pip install pip -U
RUN pip config set global.index-url https://mirrors.cloud.tencent.com/pypi/simple
RUN pip config set install.trusted-host mirrors.cloud.tencent.com

WORKDIR /rustdesk-api-server
ADD . /rustdesk-api-server

VOLUME /rustdesk-api-server/db.sqlite3

ENV HOST 0.0.0.0
ENV TZ=Asia/Shanghai \
    DEBIAN_FRONTEND=noninteractive

EXPOSE 21114/tcp
EXPOSE 21114/udp

ENTRYPOINT ["python", "manage.py", "runserver $HOST:21114"]
