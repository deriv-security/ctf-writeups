#!/bin/bash

echo "$FLAG" > "./flag_$(head -c16 /dev/urandom | base64 | tr -dc 'a-zA-Z0-9' | head -c16).txt"
unset FLAG
./ynetd -p 8083 /home/ctf/app