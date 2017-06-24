-- Function: trail_balance_amount(integer, integer, date, date, integer, integer, text, text)

-- DROP FUNCTION trail_balance_amount(integer, integer, date, date, integer, integer, text, text);

CREATE OR REPLACE FUNCTION trail_balance_amount(account_id integer, fiscal_year integer, start_date date, end_date date, start_period_id integer, end_period_id integer, state_cond text, credit_debit_balance text)
  RETURNS numeric AS
$BODY$
 DECLARE
    check_id boolean;
    amount numeric;
    acc_id numeric;
    sql_cond text := 'credit';
    sql text :=   'from account_move_line aml,
                    account_period period,
                    account_fiscalyear fiscalyear,
                    account_move
                  WHERE
                    aml.period_id = period.id AND
                    aml.move_id = account_move.id AND
                    period.fiscalyear_id = fiscalyear.id';            

  BEGIN

		IF credit_debit_balance = 'C' THEN
			sql_cond := 'SELECT COALESCE(sum(aml.credit),0.00) ';
		END IF;

		IF credit_debit_balance = 'D' THEN
			sql_cond := 'SELECT COALESCE(sum(aml.debit),0.00)';
		END IF;
		acc_id =$1;
		IF credit_debit_balance = 'B' THEN
			--IF (select acc_id in (select id,* from account_tree where path[1:2] = '{1,3}' or path[1:2] = '{1,4}' or path[1:2] = '{1,5}')) THEN
			IF (select acc_id in (select aa.id from account_account aa , account_account_type  acc_type where aa.user_type = acc_type.id and acc_type.report_type in ('income','liability'))) THEN
			    sql_cond := 'SELECT COALESCE(sum((aml.debit - aml.credit)*-1),0.00)';
			    RAISE NOTICE ' True';
			ELSE 
			  sql_cond := 'SELECT COALESCE(sum((aml.debit - aml.credit)),0.00)';
			END IF;
		END IF;
					
                 IF account_id IS NOT NULL THEN
                        sql := sql || ' AND aml.account_id =$1';
	            END IF;
	            
    IF  fiscal_year>0 THEN
      sql := sql || ' AND fiscalyear.id = $2';
    END IF;

    IF  start_date > end_date and start_date is not null and end_date is not null THEN
      sql := sql || ' AND account_move.date between $3 and $4';
    END IF;

     IF  start_date = end_date and start_date is not null and end_date is not null THEN
      sql := sql || ' AND account_move.date between $3 and $4';
    END IF;

    IF  end_date is null and start_date is not null THEN
      sql := sql || ' AND account_move.date = $3';
    END IF;

     IF   start_date is null and end_date is not null THEN
      sql := sql || ' AND account_move.date = $4';
    END IF;

    IF start_period_id >0  and end_period_id >0 and start_period_id is not null and end_period_id is not null  THEN
      sql := sql || ' AND aml.period_id between $5 and $6';
    END IF;
    
   IF start_period_id >0  and end_period_id is null and start_period_id is not null THEN
      sql := sql || ' AND aml.period_id = $5 ';
    END IF;
       
   IF end_period_id >0  and start_period_id is null and end_period_id is not null THEN
      sql := sql || ' AND aml.period_id = $6 ';
    END IF;
    
    IF $7 = 'posted' THEN
       sql := sql || ' AND account_move.state = $7';
    END IF;
    sql = sql_cond|| sql;
    RAISE NOTICE ' SQL (%)', sql;
    EXECUTE sql into amount USING account_id,fiscal_year,start_date,end_date,start_period_id,end_period_id,state_cond;
    IF amount < 0 THEN
    amount = amount;
    END IF;

   return  amount;
  END;
  $BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;