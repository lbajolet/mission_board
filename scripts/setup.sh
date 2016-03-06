#!/bin/bash

echo "Preparing to setup databases..."
sleep 20

echo $PWD
if [[ $PWD/ = */scripts/ ]];
then
	cd ..
fi

echo 	$PWD
if [[ $PWD = / ]];
then
	cd /opt/mb/
fi

cd src/mission_board
python manage.py resettestdata

chmod -R 777 /mb_media
chown -R www-data: /mb_media
