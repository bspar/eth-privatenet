#!/bin/bash

sleep 10
/usr/local/bin/geth attach http://public-node:8545/ --exec 'personal.newAccount("420blaze69everysingle1337day")' | tr -d '"' > /root/shared/guess.txt
sleep 10

cd /root/tricky
/root/tricky/publish.py

touch /root/tricky/oracle.log
echo "*/3 * * * * cd /root/tricky && /bin/oracle 420blaze69everysingle1337day >> /root/tricky/oracle.log 2>&1" > tmpcron
crontab tmpcron
service cron start

/bin/oracle 420blaze69everysingle1337day >> /root/tricky/oracle.log 2>&1 &
# keep going forever
tail -f /root/tricky/oracle.log
