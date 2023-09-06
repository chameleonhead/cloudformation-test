#!/bin/bash
if [ ! -e /opt/oracle/ogg_deployments/Local ]; then
    /opt/oracle/product/19.1.0/oggcore_1/bin/oggca.sh -silent -responseFile /tmp/orainstall/oggca.rsp
fi;

export DEPLOYMENT_BASE=/opt/oracle/ogg_deployments/Local
export OGG_ETC_HOME=/opt/oracle/ogg_deployments/Local/ServiceManager/etc
export OGG_VAR_HOME=/opt/oracle/ogg_deployments/Local/ServiceManager/var
$DEPLOYMENT_BASE/ServiceManager/bin/startSM.sh
trap "$DEPLOYMENT_BASE/ServiceManager/bin/stopSM.sh; exit" SIGINT SIGTERM
tail -f $OGG_VAR_HOME/log/*.log
