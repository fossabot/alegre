#!/bin/bash

dir=$(pwd)
cd $(dirname "${BASH_SOURCE[0]}")
cp Dockerfile ..
cd ..

# Build
docker build -t lapis/api_mlg .

# Run
secret=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 32 | head -n 1)
docker run -d -p 80:80 --name api_mlg -e SECRET_KEY_BASE=$secret lapis/api_mlg

echo
docker ps | grep 'api_mlg'
echo

echo '-----------------------------------------------------------'
echo 'Now go to your browser and access http://localhost/api'
echo '-----------------------------------------------------------'

rm Dockerfile
cd $dir