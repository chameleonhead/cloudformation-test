# 接続できるまで待ち
export PATH=${OGG_HOME}/bin:${OGG_HOME}/lib/instantclient:$PATH
export LD_LIBRARY_PATH=${OGG_HOME}/lib/instantclient:${OGG_HOME}/lib
export TNS_ADMIN=/opt/oracle/network/admin

sqlplus /nolog <<EOF >/dev/null
WHENEVER SQLERROR EXIT FAILURE
conn ggadmin@DST_ORCLPDB1/passw0rd
EOF
while [ $? -ne 0 ];
do
    sleep 60
    sqlplus /nolog <<EOF >/dev/null
WHENEVER SQLERROR EXIT FAILURE
conn ggadmin@DST_ORCLPDB1/passw0rd
EOF
done

# OGG のセットアップ（ターゲット）
export OGG_DEPLOYMENT_HOME=/opt/oracle/ogg_deployments/Local
export OGG_ETC_HOME=$OGG_DEPLOYMENT_HOME/etc
export OGG_VAR_HOME=$OGG_DEPLOYMENT_HOME/var

cat <<EOF > $OGG_ETC_HOME/conf/ogg/REPLI1.prm
REPLICAT repli1
USERIDALIAS dst_pdb1
MAP ORCLPDB1.HR.*, TARGET ORCLPDB1.HR.*;
EOF

adminclient << EOF
CONNECT http://localhost:$PORT_BASE AS oggadmin, PASSWORD P@ssw0rd
ALTER CREDENTIALSTORE ADD USER ggadmin@DST_ORCLPDB1, PASSWORD passw0rd ALIAS dst_pdb1
DBLOGIN USERIDALIAS dst_pdb1
ADD CHECKPOINTTABLE ggadmin.ggs_checkpoint
ADD HEARTBEATTABLE
ADD REPLICAT repli1, INTEGRATED, EXTTRAIL rt, CHECKPOINTTABLE ggadmin.ggs_checkpoint
START REPLICAT repli1
INFO ALL
EOF
