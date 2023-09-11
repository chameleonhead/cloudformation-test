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
ggsci << EOF
ADD CREDENTIALSTORE
ALTER CREDENTIALSTORE ADD USER ggadmin@DST_ORCLPDB1, PASSWORD passw0rd ALIAS dst_pdb1
EOF

cat <<EOF > $OGG_HOME/dirprm/repli2.prm
REPLICAT repli2
USERIDALIAS dst_pdb1
MAP ORCLPDB1.HR.*, TARGET ORCLPDB1.HRCA.*;
EOF

ggsci << EOF
DBLOGIN USERIDALIAS dst_pdb1
ADD REPLICAT repli2, INTEGRATED, EXTTRAIL rt
ADD SCHEMATRANDATA ggadmin
INFO ALL
EOF
