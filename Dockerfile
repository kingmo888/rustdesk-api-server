FROM python:3.10.3-slim-bullseye 

WORKDIR /rustdesk-api-server
ADD . /rustdesk-api-server

RUN pip install pip -U -i https://mirrors.cloud.tencent.com/pypi/simple
RUN pip config set global.index-url https://mirrors.cloud.tencent.com/pypi/simple
RUN pip config set install.trusted-host mirrors.cloud.tencent.com
RUN pip install -r requirements.txt

VOLUME /rustdesk-api-server/db.sqlite3

ENV HOST 0.0.0.0
ENV TZ=Asia/Shanghai \
    DEBIAN_FRONTEND=noninteractive

EXPOSE 21114/tcp
EXPOSE 21114/udp

RUN cd /rustdesk-api-server

ENTRYPOINT ["bash", "run.sh"]
