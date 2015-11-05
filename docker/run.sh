#!/bin/bash

dir=$(pwd)
cd $(dirname "${BASH_SOURCE[0]}")
cd ..

# Build
docker build -t nlp/mlg .

# Run
secret=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 32 | head -n 1)
docker run -d -p 80:80 --name api_mlg nlp/mlg

echo
docker ps | grep mlg
echo

echo '-----------------------------------------------------------'
echo 'Now go to your browser and access http://<hostname>/api'
echo '-----------------------------------------------------------'

cd $dir
