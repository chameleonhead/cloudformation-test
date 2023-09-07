#!/bin/bash
SCRIPTS_ROOT=/opt/oracle/scripts/setup
TEMP_PATH=/tmp/oraclescripts
mkdir -p $TEMP_PATH
unzip -o $SCRIPTS_ROOT/db-sample-schemas-main.zip -d $TEMP_PATH
cp $SCRIPTS_ROOT/setup_sample_data.dat $TEMP_PATH/setup_sample_data.dat
cd $TEMP_PATH/db-sample-schemas-main/human_resources
sqlplus / as sysdba @$TEMP_PATH/setup_sample_data.dat << EOF



EOF
