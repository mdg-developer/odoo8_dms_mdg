#!/bin/bash
DBUSERNAME="odoo"
DBHOST= "mdgtest.ctwxzwpgho6b.ap-southeast-1.rds.amazonaws.com"
DBPORT="5432"
DBNAME="mdg_uat"
DBPASSWORD="jack123$"

psql -h ${DBHOST} -U ${DBUSERNAME} -d ${DBNAME} "select * from res_users" > customer.csv
echo customer_target_run `date`
