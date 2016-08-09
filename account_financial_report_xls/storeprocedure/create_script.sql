-- Function: financial_report_balance(integer, integer, date, date, integer, integer, text)

-- DROP FUNCTION financial_report_balance(integer, integer, date, date, integer, integer, text);

CREATE OR REPLACE FUNCTION financial_report_balance(
    report_id integer,
    fiscal_year integer,
    start_date date,
    end_date date,
    start_period_id integer,
    end_period_id integer,
    state_cond text)
  RETURNS numeric AS
$BODY$
  DECLARE
    balance numeric;
    account_ids int[];
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


                     -- select account_id from account_account_financial_report where report_line_id=report_id
                    FOR r IN select *  from account_account_financial_report where report_line_id=$1
                    LOOP
                    raise NOTICE ' searching id(%)',r.account_id;
			select array_cat(account_ids,array_agg(id)) into account_ids from account_tree where r.account_id = ANY(PATH);
                    END LOOP;
                    --there is not account and return null for that
		     IF account_ids IS NULL THEN
			return null;
		     END IF;
                    IF account_ids IS NOT NULL THEN
                        sql := sql || ' AND aml.account_id in ('|| array_to_string(account_ids, ',') ||')';
	            END IF;
		    RAISE NOTICE ' SQL (%)', sql;
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
    RAISE NOTICE ' SQL (%)', sql;
    EXECUTE sql into balance USING account_ids,fiscal_year,start_date,end_date,start_period_id,end_period_id,state_cond;
    IF balance < 0 THEN
    balance = balance * -1;
    END IF;
        RAISE NOTICE 'balance (%)', balance;

   return balance;
  END;
  $BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;

-- View: financial_report_tree

CREATE OR REPLACE VIEW financial_report_tree AS 
 WITH RECURSIVE report_tree(id, name, sign, style_overwrite, sequence, depth, path, spacer) AS (
         SELECT tn.id,
            tn.name,
            tn.sign,
            tn.style_overwrite,
            tn.sequence,
            1 AS depth,
            ARRAY[tn.id] AS path,
            '    '::text AS spacer
           FROM account_financial_report tn
          WHERE tn.parent_id IS NULL
        UNION ALL
         SELECT c.id,
            (p.spacer || '    '::text) || c.name::text,
            c.sign,
            c.style_overwrite,
            c.sequence,
            p.depth + 1 AS depth,
            ((p.path || (p.depth + 1)) || c.sequence) || c.id,
            p.spacer || '    '::text AS spacer
           FROM report_tree p,
            account_financial_report c
          WHERE c.parent_id = p.id
        )
 SELECT row_number() OVER (ORDER BY n.path) AS row_number,
	    n.path[1] AS parent_id,
	    n.id,
	    n.name,
	    n.sign,
	    n.style_overwrite,
	    n.sequence,
	    n.depth,
	    n.path
   FROM report_tree n
  ORDER BY n.path;

ALTER TABLE financial_report_tree
  OWNER TO postgres;

-- View: account_tree

-- DROP VIEW account_tree;

CREATE OR REPLACE VIEW account_tree AS 
 WITH RECURSIVE account_tree(id, name, depth, path) AS (
         SELECT tn.id,
            tn.name,
            1 AS depth,
            ARRAY[tn.id] AS path,
            tn.parent_left,
            tn.parent_right
           FROM account_account tn
          WHERE tn.id = 1
        UNION ALL
         SELECT c.id,
            c.name,
            p.depth + 1 AS depth,
            p.path || c.id,
            c.parent_left,
            c.parent_right
           FROM account_tree p,
            account_account c
          WHERE c.parent_id = p.id
        )
 SELECT n.parent_left AS parent_id,
	    n.id,
	    n.name,
	    n.depth,
	    n.path,
	    n.parent_left,
	    n.parent_right
FROM account_tree n
ORDER BY n.path;
ALTER TABLE account_tree
  OWNER TO postgres;






-- Function: financial_report_monthly_balance(integer, integer, date, date, integer, text)

-- DROP FUNCTION financial_report_monthly_balance(integer, integer, date, date, integer, text);

CREATE OR REPLACE FUNCTION financial_report_monthly_balance(report_id integer, fiscal_year integer, start_date date, end_date date, period_id integer, state_cond text)
  RETURNS numeric AS
$BODY$
  DECLARE
    balance numeric;
    account_ids int[];
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
    IF  fiscal_year>0 THEN
      sql := sql || ' AND fiscalyear.id = $2';
    END IF;

    IF  start_date > end_date and start_date is not null and end_date is not null THEN
      sql := sql || ' AND account_move.date between $3 and $4';
    END IF;

    IF  end_date is null and start_date is not null THEN
      sql := sql || ' AND account_move.date = $3';
    END IF;

     IF   start_date is null and end_date is not null THEN
      sql := sql || ' AND account_move.date = $4';
    END IF;

    
    IF period_id >0  and period_id is not null THEN
      sql := sql || ' AND aml.period_id = $5 ';
    END IF;
    
    
    IF $6 = 'posted' THEN
       sql := sql || ' AND account_move.state = $6';
    END IF;
    RAISE NOTICE ' SQL (%)', sql;
    EXECUTE sql into balance USING account_ids,fiscal_year,start_date,end_date,period_id,state_cond;
    IF balance < 0 THEN
    balance = balance * -1;
    END IF;

   return balance;
  END;
  $BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION financial_report_monthly_balance(integer, integer, date, date, integer, text)
  OWNER TO openerp;

 --Trail balance
 -- Function: trail_balance_amount(integer, integer, date, date, integer, integer, text, text)

-- DROP FUNCTION trail_balance_amount(integer, integer, date, date, integer, integer, text, text);

CREATE OR REPLACE FUNCTION trail_balance_amount(account_id integer, fiscal_year integer, start_date date, end_date date, start_period_id integer, end_period_id integer, state_cond text, credit_debit_balance text)
  RETURNS numeric AS
$BODY$
 DECLARE
    amount numeric;
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

		IF credit_debit_balance = 'B' THEN
			sql_cond := 'SELECT COALESCE(sum((aml.debit - aml.credit)),0.00)';
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
    amount = amount * -1;
    END IF;

   return  amount;
  END;
  $BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION trail_balance_amount(integer, integer, date, date, integer, integer, text, text)
  OWNER TO postgres;

  

  
  --query
  select code,name,
trail_balance_amount(id,2,to_date('2015-01-01','YYYY-MM-DD'),to_date('2015-02-01','YYYY-MM-DD'),
15,16,'all','C') as credit,
trail_balance_amount(id,2,to_date('2015-01-01','YYYY-MM-DD'),to_date('2015-02-01','YYYY-MM-DD'),
15,16,'all','D') as debit,
trail_balance_amount(id,2,to_date('2015-01-01','YYYY-MM-DD'),to_date('2015-02-01','YYYY-MM-DD'),
15,16,'all','B') as balance
 from account_account
 order by code 
 
 --birt
 select code,name,
trail_balance_amount(id,?,?,?,
?,?,?,'C') as credit,
trail_balance_amount(id,?,?,?,
?,?,?,'D') as debit,
trail_balance_amount(id,?,?,?,
?,?,?,'B') as balance 
 from account_account
 order by code 
 
 
 --- balance sheet monthly report
 -- Function: financial_report_monthly_balance_sheet(integer, integer, date, date, integer, integer, text)

-- DROP FUNCTION financial_report_monthly_balance_sheet(integer, integer, date, date, integer, integer, text);

CREATE OR REPLACE FUNCTION financial_report_monthly_balance_sheet(report_id integer, fiscal_year integer, start_date date, end_date date, start_period_id integer, end_period_id integer, state_cond text)
  RETURNS numeric AS
$BODY$
  DECLARE
    balance numeric;
    account_ids int[];
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
    IF  fiscal_year>0 THEN
      sql := sql || ' AND fiscalyear.id = $2';
    END IF;

    IF  start_date > end_date and start_date is not null and end_date is not null THEN
      sql := sql || ' AND account_move.date between $3 and $4';
    END IF;

    IF  end_date is null and start_date is not null THEN
      sql := sql || ' AND account_move.date = $3';
    END IF;

     IF   start_date is null and end_date is not null THEN
      sql := sql || ' AND account_move.date = $4';
    END IF;

    
    IF start_period_id >0 and  end_period_id >0 and start_period_id is not null and end_period_id is not null THEN
      sql := sql || ' AND aml.period_id >= $5 and aml.period_id <= $6 ';
    END IF;
    
    
    IF $7 = 'posted' THEN
       sql := sql || ' AND account_move.state = $7';
    END IF;
    RAISE NOTICE ' SQL (%)', sql;
    EXECUTE sql into balance USING account_ids,fiscal_year,start_date,end_date,start_period_id,end_period_id,state_cond;
    IF balance < 0 THEN
    balance = balance * -1;
    END IF;

   return balance;
  END;
  $BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION financial_report_monthly_balance_sheet(integer, integer, date, date, integer, integer, text)
  OWNER TO postgres;
