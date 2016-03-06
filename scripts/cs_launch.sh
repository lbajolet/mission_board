#!/bin/bash

if [[ $PWD/ = */scripts/ ]];
then
	cd ..
fi

echo "Building containers..."
docker-compose build
# docker-compose up mb_db

echo "Setuping base data and data containers..."
docker-compose run mb bash /opt/mb/scripts/setup.sh

echo "Launching competition..."
docker-compose up
