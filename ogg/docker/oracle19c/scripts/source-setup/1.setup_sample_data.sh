#!/bin/bash
SCRIPTS_ROOT=/opt/oracle/scripts/setup
unzip -o $SCRIPTS_ROOT/db-sample-schemas-main.zip -d $SCRIPTS_ROOT
cd $SCRIPTS_ROOT/db-sample-schemas-main/human_resources
sqlplus / as sysdba @$SCRIPTS_ROOT/setup_sample_data.dat << EOF



EOF
