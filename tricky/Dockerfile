# Build Geth in a stock Go builder container
FROM golang:1.9-alpine as builder

RUN apk add --no-cache make gcc musl-dev linux-headers git

#ADD ../go-ethereum /go-ethereum
RUN git clone https://github.com/ethereum/go-ethereum.git /go-ethereum && cd /go-ethereum && make geth



FROM ubuntu:16.04

RUN apt update \
    && apt install -y python-pip python3-pip \
        build-essential libjansson-dev libcurl4-openssl-dev \
        cron musl software-properties-common gdb

RUN add-apt-repository ppa:ethereum/ethereum && apt update && apt install -y solc

ADD . /root/tricky

RUN pip3 install -r /root/tricky/requirements.txt

RUN gcc /root/tricky/oracle.c -lcurl -ljansson -fno-stack-protector -D_FORTIFY_SOURCE=0 -O1 -o /bin/oracle

COPY --from=builder /go-ethereum/build/bin/geth /usr/local/bin/

CMD ["/root/tricky/run.sh"]
