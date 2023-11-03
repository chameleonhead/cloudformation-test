# 接続できるまで待ち
sqlplus /nolog <<EOF
WHENEVER SQLERROR EXIT FAILURE
conn ggadmin@SRC_ORCL/passw0rd
EOF
while [ $? -ne 0 ];
do
    sleep 60
    sqlplus /nolog <<EOF
WHENEVER SQLERROR EXIT FAILURE
conn ggadmin@SRC_ORCL/passw0rd
EOF
done

cat <<EOF > $OGG_HOME/GLOBALS
GGSCHEMA ggadmin
EOF

# OGG のセットアップ（ソース）
ggsci << EOF
ADD CREDENTIALSTORE
ALTER CREDENTIALSTORE ADD USER ggadmin@SRC_ORCL, PASSWORD passw0rd ALIAS src_orcl
DBLOGIN USERIDALIAS src_orcl
ADD CHECKPOINTTABLE ggadmin.ggs_checkpoint
ADD SCHEMATRANDATA HR
ADD HEARTBEATTABLE
EOF

cat <<EOF > $OGG_HOME/dirprm/capture1.prm
EXTRACT capture1
USERIDALIAS src_orcl
EXTTRAIL lt
DDL
TABLE HR.*;
EOF

ggsci << EOF
DBLOGIN USERIDALIAS src_orcl
REGISTER EXTRACT capture1 DATABASE
ADD EXTRACT capture1, INTEGRATED TRANLOG, BEGIN NOW
ADD EXTTRAIL lt, EXTRACT capture1, megabytes 500
EOF

cat <<EOF > $OGG_HOME/dirprm/pump1.prm
EXTRACT pump1
RMTHOST $TARGET_OGG_HOST, PORT $TARGET_OGG_PORT
RMTTRAIL rt
PASSTHRU
TABLE HR.*;
EOF

ggsci << EOF
DBLOGIN USERIDALIAS src_orcl
ADD EXTRACT pump1, EXTTRAILSOURCE lt, BEGIN NOW
ADD RMTTRAIL rt, EXTRACT pump1
INFO ALL
EOF
