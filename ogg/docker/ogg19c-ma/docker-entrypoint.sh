#!/bin/bash
if [ ! -e /opt/oracle/ogg_deployments/Local ]; then
    sed -i "s/11000/$PORT_BASE/" /tmp/orainstall/oggca.rsp
    sed -i "s/11001/$(expr ${PORT_BASE} + 1)/" /tmp/orainstall/oggca.rsp
    sed -i "s/11002/$(expr ${PORT_BASE} + 2)/" /tmp/orainstall/oggca.rsp
    sed -i "s/11003/$(expr ${PORT_BASE} + 3)/" /tmp/orainstall/oggca.rsp
    sed -i "s/11004/$(expr ${PORT_BASE} + 4)/" /tmp/orainstall/oggca.rsp
    sed -i "s/11005/$(expr ${PORT_BASE} + 5)/" /tmp/orainstall/oggca.rsp
    /opt/oracle/product/19.1.0/oggcore_1/bin/oggca.sh -silent -responseFile /tmp/orainstall/oggca.rsp

    SCRIPT_ROOT="/opt/oracle/scripts/setup"
    # Execute custom provided files (only if directory exists and has files in it)
    if [ -d "$SCRIPTS_ROOT" ] && [ -n "$(ls -A "$SCRIPTS_ROOT")" ]; then

        echo "";
        echo "Executing user defined scripts"

        for f in "$SCRIPTS_ROOT"/*; do
            case "$f" in
                *.sh)     echo "$0: running $f"; . "$f" ;;
                *)        echo "$0: ignoring $f" ;;
            esac
            echo "";
        done
        
        echo "DONE: Executing user defined scripts"
        echo "";

    fi;

fi;

export DEPLOYMENT_BASE=/opt/oracle/ogg_deployments/ServiceManager
export OGG_ETC_HOME=$DEPLOYMENT_BASE/etc
export OGG_VAR_HOME=$DEPLOYMENT_BASE/var
trap "$DEPLOYMENT_BASE/bin/stopSM.sh; exit" SIGINT SIGTERM
$DEPLOYMENT_BASE/bin/startSM.sh
tail -f $OGG_VAR_HOME/log/*.log
