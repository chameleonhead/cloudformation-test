#!/bin/bash
docker-compose down -v
docker-compose -f docker-compose-ca.yml down -v
items=(
    "docker/ogg19c-ca/data/source-ogg"
    "docker/ogg19c-ca/data/target-ogg"
    "docker/ogg19c-ma/data/source-deployments"
    "docker/ogg19c-ma/data/target-deployments"
    "docker/oracle19c/data/source-oradata"
    "docker/oracle19c/data/target-oradata"
)
for item in "${items[@]}" ; do
    if [ -e $item ]; then
        rm -rf $item
    fi
    mkdir -p $item
    chown 543321:54321 $item
    chmod 775 $item
done
