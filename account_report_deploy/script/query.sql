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
 
-- Function: financial_report_balance(integer, integer, date, date, integer, integer, text)

-- DROP FUNCTION financial_report_balance(integer, integer, date, date, integer, integer, text);

CREATE OR REPLACE FUNCTION financial_report_balance(report_id integer, fiscal_year integer, start_date date, end_date date, start_period_id integer, end_period_id integer, state_cond text)
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

                    RAISE NOTICE 'account_ids(%)',account_ids;
                    
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
    RAISE NOTICE ' final SQL (%)', sql;
    EXECUTE sql into balance USING account_ids,fiscal_year,start_date,end_date,start_period_id,end_period_id,state_cond;
    IF balance < 0 THEN
    balance = balance;
    END IF;
        RAISE NOTICE 'balance (%)', balance;

   return balance;
  END;
  $BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
  
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
  
  -- Function: financial_report_monthly_balance(integer, integer, integer, text)

-- DROP FUNCTION financial_report_monthly_balance(integer, integer, integer, text);

CREATE OR REPLACE FUNCTION financial_report_monthly_balance(report_id integer, fiscal_year integer, period_id integer, state_cond text)
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

    
    IF period_id >0  and period_id is not null THEN
      sql := sql || ' AND aml.period_id = $3 ';
    END IF;
    
    
    IF $4 = 'posted' THEN
       sql := sql || ' AND account_move.state = $4';
    END IF;
    RAISE NOTICE ' SQL (%)', sql;
    EXECUTE sql into balance USING account_ids,fiscal_year,period_id,state_cond;
    IF balance < 0 THEN
    balance = balance;
    END IF;

   return balance;
  END;
  $BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
  
  -- Function: financial_report_yearly_balance_sheet_report(integer, integer, integer, text)

-- DROP FUNCTION financial_report_yearly_balance_sheet_report(integer, integer, integer, text);

CREATE OR REPLACE FUNCTION financial_report_yearly_balance_sheet_report(report_id integer, start_fiscal_year integer, end_fiscal_year integer, state_cond text)
  RETURNS numeric AS
$BODY$
  DECLARE
    balance numeric;
    account_ids int[];
  --  opening_period int;
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

                       -- opening_period=(start_period_id-1);
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

     --IF  start_fiscal_year >0 and end_fiscal_year > 0 and start_fiscal_year is not null and end_fiscal_year is not null THEN
      sql := sql || ' AND fiscalyear.id >= $2 AND fiscalyear.id <= $3 ';
    --END IF;

    IF $4 = 'posted' THEN
       sql := sql || ' AND account_move.state = $4';
    END IF;
    RAISE NOTICE ' SQL (%)', sql;
    --EXECUTE sql into balance USING account_ids,fiscal_year,start_period_id,end_period_id,state_cond;
    EXECUTE sql into balance USING account_ids,start_fiscal_year,end_fiscal_year,state_cond;
    IF balance < 0 THEN
    balance = balance;
    END IF;
   RAISE NOTICE ' final SQL (%)', sql;
   return balance;
  END;
  $BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;