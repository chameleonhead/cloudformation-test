#!/bin/bash
docker-compose -f docker-compose.yml down -v
docker-compose -f docker-compose-19ca.yml down -v
docker-compose -f docker-compose-19ma.yml down -v
docker-compose -f docker-compose-21ma.yml down -v

items=(
    "docker/ogg19c-ca/data"
    "docker/ogg19c-ma/data"
    "docker/ogg21c-ma/data"
    "docker/oracle19c/data"
)
for item in "${items[@]}" ; do
    if [ -e $item ]; then
        rm -rf $item
    fi
    mkdir -p $item
    chown 1000:1000 $item
    chmod 775 $item
done

items=(
    "docker/ogg19c-ca/data/source"
    "docker/ogg19c-ca/data/source-19ca"
    "docker/ogg19c-ca/data/target-19ca"
    "docker/ogg19c-ma/data/source-19ma"
    "docker/ogg19c-ma/data/target-19ma"
    "docker/ogg21c-ma/data/source-21ma"
    "docker/ogg21c-ma/data/target"
    "docker/ogg21c-ma/data/target-21ma"
)
for item in "${items[@]}" ; do
    if [ -e $item ]; then
        rm -rf $item
    fi
    mkdir -p $item
    chown 54321:54321 $item
    chmod 775 $item
done

items=(
    "docker/oracle19c/data/source"
    "docker/oracle19c/data/source-19ca"
    "docker/oracle19c/data/source-19ma"
    "docker/oracle19c/data/source-21ma"
)
for item in "${items[@]}" ; do
    if [ -e docker/oracle19c/images/ee-image.zip ]; then
        unzip docker/oracle19c/images/ee-image.zip -d $item
        chown -R 54321:54322 $item
    else
        if [ -e $item ]; then
            rm -rf $item
        fi
        mkdir -p $item
        chown 54321:54322 $item
        chmod 775 $item
    fi
done


items=(
    "docker/oracle19c/data/target"
    "docker/oracle19c/data/target-19ca"
    "docker/oracle19c/data/target-19ma"
    "docker/oracle19c/data/target-21ma"
)
for item in "${items[@]}" ; do
    if [ -e docker/oracle19c/images/se2-image.zip ]; then
        unzip docker/oracle19c/images/se2-image.zip -d $item
        chown -R 54321:54322 $item
    else
        if [ -e $item ]; then
            rm -rf $item
        fi
        mkdir -p $item
        chown 54321:54322 $item
        chmod 775 $item
    fi
done