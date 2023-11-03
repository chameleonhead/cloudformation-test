#!/bin/bash
cat << EOF > $ORACLE_HOME/network/admin/tnsnames.ora
SRC_ORCL=(DESCRIPTION =
    (ADDRESS = (PROTOCOL = TCP)(HOST = localhost)(PORT = 1521))
    (CONNECT_DATA =
      (SERVER = DEDICATED)
      (SERVICE_NAME = ORCL)
    )
  )
EOF