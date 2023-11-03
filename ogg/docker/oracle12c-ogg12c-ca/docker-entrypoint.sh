netca -silent -responseFile /home/oracle/install/netca.rsp
dbca -silent -createDatabase -responseFile /home/oracle/install/dbca.rsp ||
 cat /opt/oracle/cfgtoollogs/dbca/"$ORACLE_SID"/"$ORACLE_SID".log ||
 cat /opt/oracle/cfgtoollogs/dbca/"$ORACLE_SID".log

#!/bin/bash
if [ ! -e $OGG_HOME/mgr ]; then
    # Oracle GoldenGate Client Architecture のインストール
    unzip /home/oracle/install/123010_fbo_ggs_Linux_x64_shiphome.zip -d /home/oracle/install
    /home/oracle/install/fbo_ggs_Linux_x64_shiphome/Disk1/runInstaller -silent -waitForCompletion -ignoreSysPrereqs -responseFile /home/oracle/install/oggcore.rsp
    rm -rf /home/oracle/install/fbo_ggs_Linux_x64_shiphome

    echo "CREATE SUBDIRS" | $OGG_HOME/ggsci
    cat << EOF > $OGG_HOME/dirprm/mgr.prm
PORT 7809
AUTOSTART ER *
AUTORESTART ER *, RETRIES 3, WAITMINUTES 5
EOF

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

cd $OGG_HOME
trap "echo STOP MANAGER! | ggsci; exit" SIGINT SIGTERM
echo START MANAGER | $OGG_HOME/ggsci
tail -f $OGG_HOME/*.log
