FROM ubuntu:16.04

RUN apt update \
    && apt install -y python-pip python3-pip \
        build-essential libjansson-dev libcurl4-openssl-dev \
        cron musl software-properties-common gdb

ADD . /root

RUN pip3 install -r /root/requirements.txt
WORKDIR /root

CMD ["/root/run.sh"]
