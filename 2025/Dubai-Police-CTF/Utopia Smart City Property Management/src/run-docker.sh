#!/bin/bash

docker-compose -p challenge up --build --wait --force-recreate  --renew-anon-volumes --remove-orphans
