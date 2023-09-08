#!/bin/bash
if [ ! -e $OGG_HOME ]; then
    # Oracle GoldenGate Client Architecture のインストール
    /tmp/orainstall/fbo_ggs_Linux_x64_shiphome/Disk1/runInstaller -silent -waitForCompletion -ignoreSysPrereqs -responseFile /tmp/orainstall/oggcore.rsp
    ggsci << EOF
CREATE SUBDIRS
EOF
    cat <<EOF > $OGG_HOME/dirprm/mgr.prm
PORT 7809
DYNAMICPORTLIST 7810-7820, 7830
AUTOSTART ER t*
AUTORESTART ER t*, RETRIES 4, WAITMINUTES 4
STARTUPVALIDATIONDELAY 5
USERIDALIAS mgr1
PURGEOLDEXTRACTS /ogg/dirdat/tt*, USECHECKPOINTS, MINKEEPHOURS 2
EOF
fi;

ggsci << EOF
START MANAGER
EOF