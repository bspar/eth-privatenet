#!/bin/bash

sudo rm -rf shared
docker-compose down
# sudo docker stop $(sudo docker ps -aq) # stops *all* containers
# sudo docker system prune -a

docker-compose build 
docker-compose up
