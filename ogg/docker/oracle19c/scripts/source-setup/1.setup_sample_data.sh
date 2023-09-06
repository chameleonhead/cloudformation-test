#!/usr/bin/env bash
ORIGPATH=$(dirname "$0")
unzip -o $ORIGPATH/db-sample-schemas-main.zip -d $ORIGPATH
cd $ORIGPATH/db-sample-schemas-main/human_resources
sqlplus / as sysdba @$ORIGPATH/setup_sample_data.dat << EOF



EOF
