#!/bin/bash

cd $(dirname $0)
set -e
set -a

if [[ -z "${VERSION}" ]]; then
    echo "VERSION variable is unset"
    exit 1
fi

if [[ -z "$1" ]]; then
    echo "Missing first argument"
    exit 1
fi

if [[ -z "${VENDORS}" ]]; then
    VENDORS=$(ls -1 vendors/ | sed s/.conf//)
fi

set -a
for VENDOR in ${VENDORS}; do
    echo "Deploying for ${VENDOR}"
    source vendors/${VENDOR}.conf
    ./deploy.sh $1 output/raspberrypi64/images/chameleonos-${THINGOS_PREFIX}-raspberrypi64-${VERSION}.img.xz
done
