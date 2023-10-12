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

cat <<EOF > $OGG_HOME/GLOBALS
GGSCHEMA ggadmin
EOF

# OGG のセットアップ（ソース）
ggsci << EOF
ADD CREDENTIALSTORE
ALTER CREDENTIALSTORE ADD USER c##ggadmin@SRC_ORCLCDB, PASSWORD passw0rd ALIAS src_cdb
ALTER CREDENTIALSTORE ADD USER ggadmin@SRC_ORCLPDB1, PASSWORD passw0rd ALIAS src_pdb1
DBLOGIN USERIDALIAS src_pdb1
ADD CHECKPOINTTABLE ORCLPDB1.ggadmin.ggs_checkpoint
ADD SCHEMATRANDATA ORCLPDB1.HR
ADD HEARTBEATTABLE
EOF

cat <<EOF > $OGG_HOME/dirprm/capture1.prm
EXTRACT capture1
USERIDALIAS src_cdb
EXTTRAIL lt
DDL
TABLE ORCLPDB1.HR.*;
EOF

ggsci << EOF
DBLOGIN USERIDALIAS src_cdb
REGISTER EXTRACT capture1 DATABASE CONTAINER (ORCLPDB1)
ADD EXTRACT capture1, INTEGRATED TRANLOG, BEGIN NOW
ADD EXTTRAIL lt, EXTRACT capture1, megabytes 500
EOF

cat <<EOF > $OGG_HOME/dirprm/pump1.prm
EXTRACT pump1
RMTHOST $TARGET_OGG_HOST, PORT $TARGET_OGG_PORT
RMTTRAIL rt
PASSTHRU
TABLE ORCLPDB1.HR.*;
EOF

ggsci << EOF
DBLOGIN USERIDALIAS src_cdb
ADD EXTRACT pump1, EXTTRAILSOURCE lt, BEGIN NOW
ADD RMTTRAIL rt, EXTRACT pump1
INFO ALL
EOF
