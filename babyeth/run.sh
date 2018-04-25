#!/bin/bash

sleep 10
/usr/local/bin/geth attach http://public-node:8545/ --exec 'personal.newAccount("420blaze69everysingle1337day")' | tr -d '"' > /root/shared/babyeth.txt
sleep 10

cd /root/babyeth
/root/babyeth/publish.py

touch /root/babyeth/babyeth.log
echo "*/3 * * * * cd /root/babyeth && python3 /root/babyeth/babyeth.py >> /root/babyeth/babyeth.log 2>&1" > tmpcron
crontab tmpcron
service cron start

python3 /root/babyeth/babyeth.py >> /root/babyeth/babyeth.log 2>&1 &

# keep going forever
tail -f /root/babyeth/babyeth.log
