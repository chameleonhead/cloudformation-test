# 接続できるまで待ち
sqlplus /nolog <<EOF
WHENEVER SQLERROR EXIT FAILURE
conn ggadmin@DST_ORCLPDB1/passw0rd
EOF
while [ $? -ne 0 ];
do
    sleep 60
    sqlplus /nolog <<EOF
WHENEVER SQLERROR EXIT FAILURE
conn ggadmin@DST_ORCLPDB1/passw0rd
EOF
done

# OGG のセットアップ（ターゲット）
cat <<EOF > $OGG_HOME/dirprm/repli1.prm
REPLICAT repli1
USERIDALIAS dst_pdb1
MAP ORCLPDB1.HR.*, TARGET ORCLPDB1.HR.*;
BATCHSQL
PURGEOLDEXTRACTS
DDLERROR DEFAULT DISCARD

EOF

ggsci << EOF
ADD CREDENTIALSTORE
ALTER CREDENTIALSTORE ADD USER ggadmin@DST_ORCLPDB1, PASSWORD passw0rd ALIAS dst_pdb1
DBLOGIN USERIDALIAS dst_pdb1
ADD CHECKPOINTTABLE ggadmin.ggs_checkpoint
ADD HEARTBEATTABLE
ADD REPLICAT repli1, INTEGRATED, EXTTRAIL rt
INFO ALL
EOF
