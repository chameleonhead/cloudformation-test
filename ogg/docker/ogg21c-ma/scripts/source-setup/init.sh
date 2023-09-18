export PATH=${OGG_HOME}/bin:${OGG_HOME}/lib/instantclient:$PATH
export LD_LIBRARY_PATH=${OGG_HOME}/lib/instantclient:${OGG_HOME}/lib
export TNS_ADMIN=/opt/oracle/network/admin

# 接続できるまで待ち
sqlplus /nolog <<EOF
WHENEVER SQLERROR EXIT FAILURE
conn c##ggadmin@SRC_ORCLCDB/passw0rd
EOF
while [ $? -ne 0 ];
do
    sleep 60
    sqlplus /nolog <<EOF
WHENEVER SQLERROR EXIT FAILURE
conn c##ggadmin@SRC_ORCLCDB/passw0rd
EOF
done

# OGG のセットアップ（ソース）
export OGG_DEPLOYMENT_HOME=/opt/oracle/ogg_deployments/Local
export OGG_ETC_HOME=$OGG_DEPLOYMENT_HOME/etc
export OGG_VAR_HOME=$OGG_DEPLOYMENT_HOME/var

adminclient << EOF
CONNECT http://localhost:$PORT_BASE AS oggadmin, PASSWORD P@ssw0rd
ALTER CREDENTIALSTORE ADD USER c##ggadmin@SRC_ORCLCDB, PASSWORD passw0rd ALIAS src_cdb
ALTER CREDENTIALSTORE ADD USER ggadmin@SRC_ORCLPDB1, PASSWORD passw0rd ALIAS src_pdb1
DBLOGIN USERIDALIAS src_pdb1
ADD CHECKPOINTTABLE ORCLPDB1.ggadmin.ggs_checkpoint
ADD SCHEMATRANDATA ORCLPDB1.HR
ADD HEARTBEATTABLE
EOF

cat <<EOF > $OGG_ETC_HOME/conf/ogg/CAPTURE1.prm
EXTRACT capture1
USERIDALIAS src_cdb
EXTTRAIL lt
DDL
TABLE ORCLPDB1.HR.*;
EOF

adminclient << EOF
CONNECT http://localhost:$PORT_BASE AS oggadmin, PASSWORD P@ssw0rd
DBLOGIN USERIDALIAS src_cdb
REGISTER EXTRACT capture1 DATABASE CONTAINER (ORCLPDB1)
ADD EXTRACT capture1, INTEGRATED TRANLOG, BEGIN NOW
ADD EXTTRAIL lt, EXTRACT capture1, megabytes 500
START EXTRACT capture1
ADD DISTPATH path1 SOURCE trail://localhost:$(expr ${PORT_BASE} + 1)/services/v2/sources?trail=lt TARGET ogg://$TARGET_OGG_HOST:$TARGET_OGG_PORT/services/v2/targets?trail=rt TARGETTYPE MANAGER
START DISTPATH path1
INFO ALL
EOF
