﻿-- Function: financial_report_yearly_balance_sheet_report_analytic(integer, integer, integer, text, integer, integer)

-- DROP FUNCTION financial_report_yearly_balance_sheet_report_analytic(integer, integer, integer, text, integer, integer);

CREATE OR REPLACE FUNCTION financial_report_yearly_balance_sheet_report_analytic(report_id integer, start_fiscal_year integer, end_fiscal_year integer, state_cond text, analytic_id integer, branch integer)
  RETURNS numeric AS
$BODY$
  DECLARE
    balance numeric;
    account_ids int[];
    analytic_account_ids int[];
    temp_account_id int[];
    r account_account_financial_report%rowtype;
    sql text :=   'select
                    COALESCE(sum((aml.debit - aml.credit)),0)
                  from account_move_line aml,
                    account_period period,
                    account_fiscalyear fiscalyear,
                    account_move
                  WHERE
                    aml.period_id = period.id AND
                    aml.move_id = account_move.id AND
                    period.fiscalyear_id = fiscalyear.id';

  BEGIN
		    IF analytic_id >0  and analytic_id is not null THEN
				select array_agg(id) into analytic_account_ids from account_analytic_tree  where analytic_id  = ANY(PATH);
		    Else
				select array_agg(id) into analytic_account_ids from analytic_report_tree;
		    END IF; 
                      
                     -- select account_id from account_account_financial_report where report_line_id=report_id
                    FOR r IN select *  from account_account_financial_report where report_line_id=$1
                    LOOP
			select array_cat(account_ids,array_agg(id)) into account_ids from account_tree where r.account_id = ANY(PATH);
                    END LOOP;
                    --there is not account and return null for that
		     IF account_ids IS NULL THEN
			return null;
		     END IF;
                    IF account_ids IS NOT NULL THEN
                        sql := sql || ' AND aml.account_id in ('|| array_to_string(account_ids, ',') ||')';
	            END IF;
	            IF analytic_account_ids IS NULL THEN
				sql := sql || ' AND aml.analytic_account_id is not null';
		    END IF;
		    IF analytic_account_ids IS NOT NULL THEN
				sql := sql || ' AND aml.analytic_account_id in ('|| array_to_string(analytic_account_ids, ',') ||')';
		    END IF;
		     

     --IF  start_fiscal_year >0 and end_fiscal_year > 0 and start_fiscal_year is not null and end_fiscal_year is not null THEN
      sql := sql || ' AND fiscalyear.id >= $2 AND fiscalyear.id <= $3 ';
    --END IF;

    IF $4 = 'posted' THEN
       sql := sql || ' AND account_move.state = $4';
    END IF;
    RAISE NOTICE ' SQL (%)', sql;
    IF branch >0  and branch is not null THEN
      sql := sql || ' AND aml.branch_id = $5 ';
    END IF;
    
    EXECUTE sql into balance USING analytic_account_ids,start_fiscal_year,end_fiscal_year,state_cond,branch;
    IF balance < 0 THEN
    balance = balance * -1;
    END IF;

   return balance;
  END;
  $BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION financial_report_yearly_balance_sheet_report_analytic(integer, integer, integer, text, integer, integer)
  OWNER TO odoo;
