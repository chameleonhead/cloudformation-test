#!/bin/bash
export DEPLOYMENT_BASE=/u02/ogg
export OGG_ETC_HOME=/u02/ogg/etc
export OGG_VAR_HOME=/u02/ogg/var
$DEPLOYMENT_BASE/ServiceManager/bin/startSM.sh
trap "$DEPLOYMENT_BASE/ServiceManager/bin/stopSM.sh; exit" SIGINT SIGTERM
tail -f $OGG_VAR_HOME/log/*.log
