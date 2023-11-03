#!/bin/bash
export ORACLE_SID=ORCL
if [ ! -e /opt/oracle/oradata ]; then
    # Oracle Database Client 12c の配置
    # linuxx64_12201_database.zip を展開すると database/runInstaller が現れる
    su oracle - << EOT
unzip -q /home/oracle/install/linuxx64_12201_database.zip -d /home/oracle/install && \
/home/oracle/install/database/runInstaller -silent -waitForCompletion -ignoreSysPrereqs -responseFile /home/oracle/install/db_install.rsp || true && \
rm -rf /home/oracle/install/database
EOT
    /home/oracle/oraInventory/orainstRoot.sh && /opt/oracle/product/12c/dbhome_1/root.sh
    # Oracle Database の作成
    su oracle - << EOT
netca -silent -responseFile /home/oracle/install/netca.rsp
dbca -silent -createDatabase -responseFile /home/oracle/install/dbca.rsp || cat /opt/oracle/cfgtoollogs/dbca/"$ORACLE_SID"/"$ORACLE_SID".log || cat /opt/oracle/cfgtoollogs/dbca/"$ORACLE_SID".log
EOT

    # Oracle GoldenGate Client Architecture のインストール
    # 123010_fbo_ggs_Linux_x64_shiphome.zip を展開すると fbo_ggs_Linux_x64_shiphome/Disk1/runInstaller が現れる
    su oracle - << EOT
unzip -q /home/oracle/install/123010_fbo_ggs_Linux_x64_shiphome.zip -d /home/oracle/install
/home/oracle/install/fbo_ggs_Linux_x64_shiphome/Disk1/runInstaller -silent -waitForCompletion -ignoreSysPrereqs -responseFile /home/oracle/install/oggcore.rsp
rm -rf /home/oracle/install/fbo_ggs_Linux_x64_shiphome
EOT
    su oracle - << EOT
echo "CREATE SUBDIRS" | $OGG_HOME/ggsci
cat << EOF > $OGG_HOME/dirprm/mgr.prm
PORT 7809
AUTOSTART ER *
AUTORESTART ER *, RETRIES 3, WAITMINUTES 5
EOF
EOT

    SCRIPTS_ROOT="/opt/oracle/scripts/setup"
    su oracle - << EOT
# Execute custom provided files (only if directory exists and has files in it)
if [ -d "$SCRIPTS_ROOT" ] && [ -n "$(ls -A "$SCRIPTS_ROOT")" ]; then

    echo "";
    echo "Executing user defined scripts"

    for f in "$SCRIPTS_ROOT"/*; do
        case "$f" in
            *.sh)     echo "$0: running $f"; . "$f" ;;
            *.sql)    echo "$0: running $f"; echo "exit" | "$ORACLE_HOME"/bin/sqlplus -s "/ as sysdba" @"$f"; echo ;;
            *)        echo "$0: ignoring $f" ;;
        esac
        echo "";
    done
    
    echo "DONE: Executing user defined scripts"
    echo "";

fi;
EOT

fi;

su oracle - <<EOT
cd $OGG_HOME
trap "echo STOP MANAGER! | ggsci; exit" SIGINT SIGTERM
echo START MANAGER | $OGG_HOME/ggsci
tail -f $OGG_HOME/*.log
EOT