#!/bin/bash

DBDATA_CONTAINER=$(docker-compose ps | grep dbdata | awk '{print $1}')

if [[ $PWD/ = */scripts/ ]];
then
	cd ..
fi

echo "dbdata container: $DBDATA_CONTAINER"
docker run --volumes-from ${DBDATA_CONTAINER}\
	-v $(pwd)/data:/backup ubuntu \
	bash -c "mkdir -p /var/lib/postgresql/ && cd /var/lib/postgresql/ && tar xvf /backup/backup.tar data && mkdir -p /mb_media/ && cd / && tar xvf /backup/backup.tar mb_media"
