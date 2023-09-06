#!/bin/bash
ORIGPATH=$(pwd)
unzip -o ./db-sample-schemas-main.zip -d $ORIGPATH
cd $ORIGPATH/db-sample-schemas-main/human_resources
sqlplus / as sysdba @$ORIGPATH/setup_sample_data.dat << EOF



EOF
