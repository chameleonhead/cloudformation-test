#!/bin/bash
if [ ! -e /opt/oracle/ogg_deployments/ServiceManager ]; then
    sed -i "s/11000/$PORT_BASE/" /tmp/orainstall/oggca.rsp
    sed -i "s/11001/$(expr ${PORT_BASE} + 1)/" /tmp/orainstall/oggca.rsp
    sed -i "s/11002/$(expr ${PORT_BASE} + 2)/" /tmp/orainstall/oggca.rsp
    sed -i "s/11003/$(expr ${PORT_BASE} + 3)/" /tmp/orainstall/oggca.rsp
    sed -i "s/11004/$(expr ${PORT_BASE} + 4)/" /tmp/orainstall/oggca.rsp
    sed -i "s/11005/$(expr ${PORT_BASE} + 5)/" /tmp/orainstall/oggca.rsp
    $OGG_HOME/bin/oggca.sh -silent -responseFile /tmp/orainstall/oggca.rsp

    if [ ! -e /opt/oracle/ogg_deployments/Local/etc ]; then
        rm -rf /opt/oracle/ogg_deployments/Local
        # if Local deployment does not exist, run ServiceManager and then create
        # first creation only fails on docker
        cp /tmp/orainstall/oggca.rsp /tmp/orainstall/oggca_Local.rsp
        sed -i "s/CREATE_NEW_SERVICEMANAGER=true/CREATE_NEW_SERVICEMANAGER=false/" /tmp/orainstall/oggca_Local.rsp
        $OGG_HOME/bin/oggca.sh -silent -responseFile /tmp/orainstall/oggca_Local.rsp
    fi;

    SCRIPTS_ROOT="/opt/oracle/scripts/setup"
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

export OGG_DEPLOYMENT_HOME=/opt/oracle/ogg_deployments/ServiceManager
export OGG_ETC_HOME=$OGG_DEPLOYMENT_HOME/etc
export OGG_VAR_HOME=$OGG_DEPLOYMENT_HOME/var
trap "$OGG_DEPLOYMENT_HOME/bin/stopSM.sh; exit" SIGINT SIGTERM
$OGG_DEPLOYMENT_HOME/bin/startSM.sh
tail -F "${OGG_DEPLOYMENT_HOME}"/var/log/ServiceManager.log
