-- View: account_tree_status

-- DROP VIEW account_tree_status;

CREATE OR REPLACE VIEW account_tree_status AS 
 WITH RECURSIVE account_tree(id, name, status, depth, path) AS (
                 SELECT tn.id, tn.name, tn.status, 1 AS depth, 
                    ARRAY[tn.id] AS path, tn.parent_left, tn.parent_right
                   FROM account_account tn
                  WHERE tn.id = 1
        UNION ALL 
                 SELECT c.id, c.name, c.status, p.depth + 1 AS depth, 
                    p.path || c.id, c.parent_left, c.parent_right
                   FROM account_tree p, account_account c
                  WHERE c.parent_id = p.id
        )
 SELECT n.parent_left AS parent_id, n.id, n.name, n.status, n.depth, n.path, 
    n.parent_left, n.parent_right
   FROM account_tree n
  ORDER BY n.path;
  
 -- Function: financial_report_balance_opening(integer, integer, date, date, integer, integer, text)

-- DROP FUNCTION financial_report_balance_opening(integer, integer, date, date, integer, integer, text);

CREATE OR REPLACE FUNCTION financial_report_balance_opening(
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
    period_special boolean;
    sql text :=   'select
                    COALESCE(sum((aml.credit - aml.debit)),0)
                  from account_move_line aml,
                    account_period period,
                    account_fiscalyear fiscalyear,
                    account_move
                  WHERE
                    aml.period_id = period.id AND
                    aml.move_id = account_move.id AND
                    period.fiscalyear_id = fiscalyear.id';

  BEGIN

		     select special into period_special from account_period where id = start_period_id-1;
		     raise NOTICE ' searching special(%)',period_special;
		     --select * from account_period where id = 2;
                     -- select account_id from account_account_financial_report where report_line_id=report_id
                    FOR r IN select * from account_account_financial_report where report_line_id=$1
                    LOOP
                    raise NOTICE ' searching id(%)',r.account_id;
                    IF period_special THEN
                       select array_cat(account_ids,array_agg(id)) into account_ids from account_tree_status where r.account_id = ANY(PATH) and status='O';
                    ELSE
			select array_cat(account_ids,array_agg(id)) into account_ids from account_tree_status where r.account_id = ANY(PATH) and status='C';
	            END IF;		
                    END LOOP;
                    --there is not account and return null for that
     IF account_ids IS NULL THEN
	return null;
     END IF;
    IF account_ids IS NOT NULL THEN
       sql := sql || ' AND aml.account_id in ('|| array_to_string(account_ids, ',') ||')';
    END IF;
      RAISE NOTICE ' SQL (%)', sql;
    IF  fiscal_year> 0 THEN
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

   
      sql := sql || ' AND aml.period_id <= $5-1';
    
    
    
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
ALTER FUNCTION financial_report_balance_opening(integer, integer, date, date, integer, integer, text)
  OWNER TO postgres;

  -- Function: financial_report_balance_purchase(integer, integer, date, date, integer, integer, text)

-- DROP FUNCTION financial_report_balance_purchase(integer, integer, date, date, integer, integer, text);

CREATE OR REPLACE FUNCTION financial_report_balance_purchase(
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
    p account_period%rowtype;
    period_ids int[];
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
			select array_cat(account_ids,array_agg(id)) into account_ids from account_tree_status where r.account_id = ANY(PATH) and status='P';
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
	
	
	IF $7 = 'posted' THEN
		sql := sql || ' AND account_move.state = $7';
	END IF;
	RAISE NOTICE ' SQL (%)', sql;

	EXECUTE sql into balance USING account_ids,fiscal_year,start_date,end_date,start_period_id,end_period_id,state_cond;
    
        
           --balance = balance + balance;
       
    --END LOOP;
    
        RAISE NOTICE 'balance (%)', balance;

   return balance;
  END;
  $BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION financial_report_balance_purchase(integer, integer, date, date, integer, integer, text)
  OWNER TO postgres;

  -- Function: financial_report_balance_closing(integer, integer, date, date, integer, integer, text)

-- DROP FUNCTION financial_report_balance_closing(integer, integer, date, date, integer, integer, text);

CREATE OR REPLACE FUNCTION financial_report_balance_closing(
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
                    COALESCE(sum((aml.credit - aml.debit)),0)
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
			select array_cat(account_ids,array_agg(id)) into account_ids from account_tree_status where r.account_id = ANY(PATH) and status='C';
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

   
      sql := sql || ' AND aml.period_id <= $5';
    
    
    
    IF $7 = 'posted' THEN
       sql := sql || ' AND account_move.state = $7';
    END IF;
    RAISE NOTICE ' SQL (%)', sql;
    EXECUTE sql into balance USING account_ids,fiscal_year,start_date,end_date,start_period_id,end_period_id,state_cond;
    --IF balance < 0 THEN
    --balance = balance * -1;
    --END IF;
        RAISE NOTICE 'balance (%)', balance;

   return balance;
  END;
  $BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION financial_report_balance_closing(integer, integer, date, date, integer, integer, text)
  OWNER TO postgres;
