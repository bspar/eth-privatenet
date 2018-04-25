# Build Geth in a stock Go builder container
FROM golang:1.9-alpine as builder

RUN apk add --no-cache make gcc musl-dev linux-headers git

#ADD ../go-ethereum /go-ethereum
RUN git clone https://github.com/ethereum/go-ethereum.git /go-ethereum && cd /go-ethereum && make geth


# SSH
FROM ubuntu:16.04

RUN apt-get update && apt-get install -y openssh-server musl
RUN mkdir /var/run/sshd

# SSH login fix. Otherwise user is kicked off after login
RUN sed 's@session\s*required\s*pam_loginuid.so@session optional pam_loginuid.so@g' -i /etc/pam.d/sshd
RUN sed -i '/^#/!s/PermitRootLogin .*/PermitRootLogin yes/' /etc/ssh/sshd_config

ENV NOTVISIBLE "in users profile"
RUN echo "export VISIBLE=now" >> /etc/profile && echo root:l3tsgetreadytobl1zz | chpasswd

COPY authorized_keys /root/.ssh/authorized_keys

COPY --from=builder /go-ethereum/build/bin/geth /usr/local/bin/

CMD ["/usr/sbin/sshd", "-D"]
