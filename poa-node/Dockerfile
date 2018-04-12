# Build Geth in a stock Go builder container
FROM golang:1.9-alpine as builder

RUN apk add --no-cache make gcc musl-dev linux-headers git

#ADD ../go-ethereum /go-ethereum
RUN git clone https://github.com/ethereum/go-ethereum.git /go-ethereum && cd /go-ethereum && make geth

# Pull Geth into a second stage deploy alpine container
FROM alpine:latest

RUN apk add --no-cache ca-certificates
COPY --from=builder /go-ethereum/build/bin/geth /usr/local/bin/
# END TEMPLATE
# ============

ADD . /root/.ethereum/

CMD ["/root/.ethereum/run.sh"]
