#!/bin/bash

sudo rm -rf shared
sudo docker stop $(sudo docker ps -aq) # stops *all* containers
# sudo docker system prune -a

docker-compose up
