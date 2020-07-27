#!/bin/bash
DBUSERNAME="odoo"
DBHOST="mdgtest.ctwxzwpgho6b.ap-southeast-1.rds.amazonaws.com"
DBPORT="5432"
DBNAME="mdg_uat"
DBPASSWORD="jack123$"

#psql -h ${DBHOST} -p ${DBPORT}  -u ${DBUSERNAME} -d ${DBNAME} "select * from res_users" > "target_update.log"
psql -h mdgtest.ctwxzwpgho6b.ap-southeast-1.rds.amazonaws.com -p 5432 -U odoo -d mdg_uat -c "select * from insert_daily_customer_target(10);"  > /root/scripts/target_update.log
#DBSCRIPT = "`psql -h  ${DBHOST} -u ${DBUSERNAME} -d ${DBNAME} "select * from res_users" > customer.csv"`"
#echo ${DBSCRIPT}
echo customer_target_run `date` >  /root/scripts/target_update.log
