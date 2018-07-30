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
  
-- Function: financial_report_balance_current(integer, integer, date, date, integer, integer, text)

-- DROP FUNCTION financial_report_balance_current(integer, integer, date, date, integer, integer, text);

CREATE OR REPLACE FUNCTION financial_report_balance_current(report_id integer, fiscal_year integer, start_date date, end_date date, start_period_id integer, end_period_id integer, state_cond text)
  RETURNS numeric AS
$BODY$
  DECLARE
    balance numeric;
    account_ids int[];
    temp_account_id int[];
    period integer;
    r account_account_financial_report%rowtype;
    sql text :=   'SELECT case when aml.account_id in (select aa.id from account_account aa , account_account_type  acc_type where aa.user_type = acc_type.id and acc_type.report_type in (''income'',''liability'')) then  COALESCE(sum((aml.credit - aml.debit)),0.00)
		    else COALESCE(sum((aml.debit - aml.credit)),0.00)
		    end as financial_report_balance
		    from account_move_line aml,
                    account_period period,
                    account_fiscalyear fiscalyear,
                    account_move
                  WHERE
                    aml.period_id = period.id AND
                    aml.move_id = account_move.id AND
                    period.fiscalyear_id = fiscalyear.id';

  BEGIN
                      select  id into  period from account_period where fiscalyear_id =$2 and special is false  limit 1;
                      start_period_id = period ;
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
    sql := sql || 'group by aml.account_id';
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
  
-- Function: financial_report_balance_prior_current(integer, integer, integer, integer, text)

-- DROP FUNCTION financial_report_balance_prior_current(integer, integer, integer, integer, text);

CREATE OR REPLACE FUNCTION financial_report_balance_prior_current(report_id integer, fiscal_year integer, start_period_id integer, end_period_id integer, state_cond text)
  RETURNS numeric AS
$BODY$
  DECLARE
    balance numeric;
    account_ids int[];
    account_account_ids int[];
    current_period_account_ids  int[];
    temp_account_id int[];
    retain boolean;
    yyear integer;
    r account_account_financial_report%rowtype;
    sql text := 'SELECT case when aml.account_id in (select aa.id from account_account aa , account_account_type  acc_type where aa.user_type = acc_type.id and acc_type.report_type in (''income'',''liability'')) then  COALESCE(sum((aml.credit - aml.debit)),0.00)
				else COALESCE(sum((aml.debit - aml.credit)),0.00)
				end as financial_report_balance
		    from account_move_line aml,
                    account_period period,
                    account_fiscalyear fiscalyear,
                    account_move
		    WHERE
                    aml.period_id = period.id AND
                    aml.move_id = account_move.id AND
                    period.fiscalyear_id = fiscalyear.id';

  BEGIN

			retain = false;
			--select id into yyear_id from account_period where fiscalyear_id=$2 limit 1;
			select  id into  yyear from account_period where fiscalyear_id =$2 and special is true ;
                     -- select account_id from account_account_financial_report where report_line_id=report_id
                    FOR r IN select *  from account_account_financial_report where report_line_id=$1
                    LOOP
                    raise NOTICE ' searching id(%)',r.account_id;
			select array_cat(account_ids,array_agg(id)) into account_ids from account_tree where r.account_id = ANY(PATH);
                    END LOOP;
                    FOR r IN  select *  from account_account_financial_report where report_line_id in ( select id from account_financial_report where retain_earning is true)
                    LOOP
                    raise NOTICE ' searching id(%)',r.account_id;
			select array_cat(account_ids,array_agg(id)) into account_account_ids  from account_tree where r.account_id = ANY(PATH);
                    END LOOP;
                    FOR r IN  select *  from account_account_financial_report where report_line_id = 3464
                    LOOP
                    raise NOTICE ' searching id(%)',r.account_id;
			select array_cat(account_ids,array_agg(id)) into current_period_account_ids  from account_tree where r.account_id = ANY(PATH);
                    END LOOP;
                    --there is not account and return null for that
		     IF account_ids IS NULL THEN
			return null;
		     END IF;
                    IF account_ids IS NOT NULL THEN
                        sql := sql || ' AND aml.account_id in ('|| array_to_string(account_ids, ',') ||')';
	            END IF;
		    RAISE NOTICE ' SQL (%)', sql;
                    IF account_account_ids IS NOT NULL THEN
                        sql := sql || ' AND aml.account_id in ('|| array_to_string(account_account_ids, ',') ||')';
			IF  fiscal_year>0 THEN
				sql := sql || ' AND fiscalyear.id < $2';
               	        END IF;
                        retain = true;
                           IF $5 = 'posted' THEN
				       sql := sql || ' AND account_move.state = $5';
				    END IF;
					sql := sql || 'group by aml.account_id';
				    RAISE NOTICE ' SQL (%)', sql;
				     EXECUTE sql into balance USING account_ids,fiscal_year,start_period_id,end_period_id,state_cond;
				    IF balance < 0 THEN
				    balance = balance;
				    END IF;
					RAISE NOTICE 'balance (%)', balance;
					
				   return balance;
                     END IF;

                    IF account_account_ids IS NOT NULL and retain IS TRUE THEN
                         IF  fiscal_year>0   THEN
                            sql := sql || ' AND fiscalyear.id = $2';
                         END IF;
                         IF  current_period_account_ids IS NOT NULL THEN
				sql := sql || ' AND aml.account_id in ('|| array_to_string(current_period_account_ids, ',') ||')';
				IF start_period_id >0  and end_period_id >0 and start_period_id is not null and end_period_id is not null  THEN
					sql := sql ||  ' AND aml.period_id> = yyear and aml.period_id <= $4';
				END IF;
                        END IF;
			IF $5 = 'posted' THEN
			       sql := sql || ' AND account_move.state = $5';
			END IF;
				sql := sql || 'group by aml.account_id';
			 RAISE NOTICE ' SQL (%)', sql;
			EXECUTE sql into balance USING account_ids,fiscal_year,start_period_id,end_period_id,state_cond;
			 IF balance < 0 THEN
			    balance = balance;
			END IF;
				RAISE NOTICE 'balance (%)', balance;
				

			 return balance;
			 
                      
                     END IF;
  END;
  $BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;

-- View: account_analytic_tree

-- DROP VIEW account_analytic_tree;

CREATE OR REPLACE VIEW account_analytic_tree AS 
 WITH RECURSIVE account_analytic_tree(id, name, depth, path) AS (
         SELECT tn.id,
            tn.name,
            1 AS depth,
            ARRAY[tn.id] AS path,
            tn.parent_id
           FROM account_analytic_account tn
          WHERE parent_id IS NULL
        UNION ALL
         SELECT c.id,
            c.name,
            p.depth + 1 AS depth,
            p.path || c.id,
            c.parent_id
           FROM account_analytic_tree p,
            account_analytic_account c
          WHERE c.parent_id = p.id
        )
 SELECT n.parent_id,
    n.id,
    n.name,
    n.depth,
    n.path
   FROM account_analytic_tree n
  ORDER BY n.path;
  
--Function: financial_report_balance_analytic(integer, integer, date, date, integer, integer, text, integer)

--DROP FUNCTION financial_report_balance_analytic(integer, integer, date, date, integer, integer, text, integer);

CREATE OR REPLACE FUNCTION financial_report_balance_analytic(report_id integer, fiscal_year integer, start_date date, end_date date, start_period_id integer, end_period_id integer, state_cond text, analytic_id integer)
 RETURNS numeric AS
$BODY$
 DECLARE
   balance numeric;
   analytic_account_ids int[];
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
 

			
			    select array_agg(id) into analytic_account_ids 
			    from analytic_report_tree  where analytic_id  = ANY(PATH);

			    FOR r IN select *  from account_account_financial_report where report_line_id=$1

			    LOOP
			    
				select array_cat(account_ids,array_agg(id)) into account_ids from account_tree where r.account_id = ANY(PATH);

			    END LOOP;
			    
			    
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

   EXECUTE sql into balance USING analytic_account_ids,fiscal_year,start_date,end_date,start_period_id,end_period_id,state_cond;
   IF balance < 0 THEN
   balance = balance * -1;
   END IF;
  return balance;
 END;
 $BODY$
 LANGUAGE plpgsql VOLATILE
 COST 100;
 
-- Function: financial_report_balance_analytic_current(integer, integer, date, date, integer, integer, text, integer)

-- DROP FUNCTION financial_report_balance_analytic_current(integer, integer, date, date, integer, integer, text, integer);

CREATE OR REPLACE FUNCTION financial_report_balance_analytic_current(report_id integer, fiscal_year integer, start_date date, end_date date, start_period_id integer, end_period_id integer, state_cond text, analytic_id integer)
  RETURNS numeric AS
$BODY$
  DECLARE
    balance numeric;
    analytic_account_ids int[];
    account_ids int[];
    temp_account_id int[];
    period integer;
    r account_account_financial_report%rowtype;
    sql text :=   'SELECT case when aml.account_id in (select aa.id from account_account aa , account_account_type  acc_type where aa.user_type = acc_type.id and acc_type.report_type in (''income'',''liability'')) then  COALESCE(sum((aml.credit - aml.debit)),0.00)
		    else COALESCE(sum((aml.debit - aml.credit)),0.00)
		    end as financial_report_balance
		    from account_move_line aml,
                    account_period period,
                    account_fiscalyear fiscalyear,
                    account_move
                  WHERE
                    aml.period_id = period.id AND
                    aml.move_id = account_move.id AND
                    period.fiscalyear_id = fiscalyear.id';

  BEGIN  
  
 
			     select  id into  period from account_period where fiscalyear_id =$2 and special is false  limit 1;
			     start_period_id = period ;
			    select array_agg(id) into analytic_account_ids 
			    from analytic_report_tree  where analytic_id  = ANY(PATH);

			    FOR r IN select *  from account_account_financial_report where report_line_id=$1

			    LOOP
			    
				select array_cat(account_ids,array_agg(id)) into account_ids from account_tree where r.account_id = ANY(PATH);

			    END LOOP;
			    
			    
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
    sql := sql || 'group by aml.account_id';
    EXECUTE sql into balance USING analytic_account_ids,fiscal_year,start_date,end_date,start_period_id,end_period_id,state_cond;
    IF balance < 0 THEN
    balance = balance * -1;
    END IF;
   return balance;
  END;
  $BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
  
-- Function: financial_report_balance_analytic_prior(integer, integer, integer, integer, text, integer)

-- DROP FUNCTION financial_report_balance_analytic_prior(integer, integer, integer, integer, text, integer);

CREATE OR REPLACE FUNCTION financial_report_balance_analytic_prior(report_id integer, fiscal_year integer, start_period_id integer, end_period_id integer, state_cond text, analytic_id integer)
  RETURNS numeric AS
$BODY$
  DECLARE
    balance numeric;
    analytic_account_ids int[];
    account_ids int[];
    temp_account_id int[];
    r account_account_financial_report%rowtype;
    sql text :=   'SELECT case when aml.account_id in (select aa.id from account_account aa , account_account_type  acc_type where aa.user_type = acc_type.id and acc_type.report_type in (''income'',''liability'')) then  COALESCE(sum((aml.credit - aml.debit)),0.00)
		    else COALESCE(sum((aml.debit - aml.credit)),0.00)
		    end as financial_report_balance
		    from account_move_line aml,
                    account_period period,
                    account_fiscalyear fiscalyear,
                    account_move
                  WHERE
                    aml.period_id = period.id AND
                    aml.move_id = account_move.id AND
                    period.fiscalyear_id = fiscalyear.id';

  BEGIN  
  
 
			
			    select array_agg(id) into analytic_account_ids 
			    from analytic_report_tree  where analytic_id  = ANY(PATH);

			    FOR r IN select *  from account_account_financial_report where report_line_id=$1

			    LOOP
			    
				select array_cat(account_ids,array_agg(id)) into account_ids from account_tree where r.account_id = ANY(PATH);

			    END LOOP;
			    
			    
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
		    
    IF  fiscal_year>0 THEN
      sql := sql || ' AND fiscalyear.id < $2';
    END IF;
       
    IF $5 = 'posted' THEN
       sql := sql || ' AND account_move.state = $5';
    END IF;
    sql := sql || 'group by aml.account_id';
    EXECUTE sql into balance USING analytic_account_ids,fiscal_year,start_period_id,end_period_id,state_cond;
    IF balance < 0 THEN
    balance = balance * -1;
    END IF;
   return balance;
  END;
  $BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
  
-- View: analytic_report_tree

-- DROP VIEW analytic_report_tree;

CREATE OR REPLACE VIEW analytic_report_tree AS 
 WITH RECURSIVE aa_report_tree(id, name, depth, path, spacer) AS (
         SELECT tn.id,
            tn.name,
            1 AS depth,
            ARRAY[tn.id] AS path,
            '    '::text AS spacer
           FROM account_analytic_tree tn
          WHERE tn.parent_id IS NULL
        UNION ALL
         SELECT c.id,
            (p.spacer || '    '::text) || c.name::text,
            p.depth + 1 AS depth,
            (p.path || (p.depth + 1)) || c.id,
            p.spacer || '    '::text AS spacer
           FROM aa_report_tree p,
            account_analytic_tree c
          WHERE c.parent_id = p.id
        )
 SELECT n.path[1] AS parent_id,
    n.id,
    n.name,
    n.depth,
    n.path
   FROM aa_report_tree n
  ORDER BY n.path;

-- Function: currency_account_report(integer, character varying, character varying, date, date)

-- DROP FUNCTION currency_account_report(integer, character varying, character varying, date, date);

CREATE OR REPLACE FUNCTION currency_account_report(IN param_fiscal_id integer, IN param_status character varying, IN param_account character varying, IN from_date date, IN to_date date)
  RETURNS TABLE(s_id integer, t_date date, t_id character varying, t_type character varying, dsc character varying, is_qty numeric, r_qty numeric, bln numeric, p_state character varying) AS
$BODY$
declare 
	stock RECORD ;
	product_data RECORD;
	trans_data RECORD;
	tran_ref character varying;
	opening_balance numeric;
	t_id integer=1;
	new_balance numeric=0;	
	row_data record;
	s_no integer =0;
	
	begin  
	
		RAISE NOTICE 'Starting Store Procedure.......';	 
	--Deleting Temp Table
	
		DELETE FROM account_temp_report;
		select coalesce(sum(debit+credit),0) into opening_balance from (
		select AM.date,AML.ref as ref,RP.name  as name,AML.name as description,0 as debit, AML.amount_currency as credit,AM.state
		from account_move AM,account_move_line AML,account_account AA,res_partner RP,account_period AP,account_fiscalyear AF
		where AM.id=AML.move_id
		and AA.id=AML.account_id
		and AML.amount_currency<0
		and AML.partner_id=RP.id
		and AP.fiscalyear_id=AF.id
                and AML.period_id=AP.id
                and AF.id=param_fiscal_id
		and AA.name=param_account
		and AM.date<from_date
		Union all
		select AM.date,AML.ref as ref,null  as name,AML.name as description,0 as debit, AML.amount_currency as credit,AM.state
		from account_move AM,account_move_line AML,account_account AA,account_period AP,account_fiscalyear AF
		where AM.id=AML.move_id
		and AA.id=AML.account_id
		and AML.amount_currency<0
		and AML.partner_id is Null
		and AP.fiscalyear_id=AF.id
                and AML.period_id=AP.id
                and AF.id=param_fiscal_id
		and AA.name=param_account
		and AM.date<from_date

		Union all
		select AM.date,AML.ref as ref,RP.name as name,AML.name as description,AML.amount_currency as debit,0 as credit,AM.state
		from account_move AM,account_move_line AML,account_account AA,res_partner RP,account_period AP,account_fiscalyear AF
		where AM.id=AML.move_id
		and AA.id=AML.account_id
		and AML.amount_currency>0
		and AML.partner_id=RP.id
		and AP.fiscalyear_id=AF.id
                and AML.period_id=AP.id
                and AF.id=param_fiscal_id
		and AA.name=param_account
		and AM.date<from_date
		Union all
		select AM.date,AML.ref as ref,null as name,AML.name as description,AML.amount_currency as debit,0 as credit,AM.state
		from account_move AM,account_move_line AML,account_account AA,account_period AP,account_fiscalyear AF
		where AM.id=AML.move_id
		and AA.id=AML.account_id
		and AML.amount_currency>0
		and AML.partner_id is Null
		and AP.fiscalyear_id=AF.id
                and AML.period_id=AP.id
                and AF.id=param_fiscal_id
		and AA.name=param_account
		and AM.date<from_date)A;

        RAISE NOTICE 'opening_balance=0.......%',opening_balance;	
	--first loop init with dummy data

	FOR product_data
		IN
		select date_of_month::date  from (
				select from_date::date + sun *'1day'::interval as date_of_month
						from generate_series(0,(select (to_date::date  - from_date::date))) sun
						)A

	LOOP	
		INSERT INTO account_temp_report(
			    trans_date, trans_type, trans_id, description, rec_qty, 
			    iss_qty,balance,state)
		    VALUES (product_data.date_of_month, '-','-', '-', 0, 
			    0,opening_balance,'-');	
			    
	END LOOP; 
	RAISE NOTICE 'date=----.......%',product_data.date_of_month;
	
	--second loop with real data 
	
	FOR trans_data 

		IN
		select date,ref,name,date,description,debit,credit,state
		from
		(
			select AM.date,AML.ref as ref,RP.name  as name,AML.name as description,0 as debit, -(AML.amount_currency) as credit,AM.state
			from account_move AM,account_move_line AML,account_account AA,res_partner RP,account_period AP,account_fiscalyear AF
			where AM.id=AML.move_id
			and AA.id=AML.account_id
			and AML.amount_currency<0
			and AML.partner_id=RP.id
			and AP.fiscalyear_id=AF.id
			and AML.period_id=AP.id
			and AF.id=param_fiscal_id
			and AA.name=param_account
			and AM.date between from_date and to_date
			Union all
			select AM.date,AML.ref as ref,null  as name,AML.name as description,0 as debit, -(AML.amount_currency) as credit,AM.state
			from account_move AM,account_move_line AML,account_account AA,account_period AP,account_fiscalyear AF
			where AM.id=AML.move_id
			and AA.id=AML.account_id
			and AML.amount_currency<0
			and AML.partner_id is Null
			and AP.fiscalyear_id=AF.id
			and AML.period_id=AP.id
			and AF.id=param_fiscal_id
			and AA.name=param_account
			and AM.date between from_date and to_date
			Union all
			select AM.date,AML.ref as ref,RP.name as name,AML.name as description,AML.amount_currency as debit,0 as credit,AM.state
			from account_move AM,account_move_line AML,account_account AA,res_partner RP,account_period AP,account_fiscalyear AF
			where AM.id=AML.move_id
			and AA.id=AML.account_id
			and AML.amount_currency>0
			and AML.partner_id=RP.id
			and AP.fiscalyear_id=AF.id
			and AML.period_id=AP.id
			and AF.id=param_fiscal_id
			and AA.name=param_account
			and AM.date between from_date and to_date
			
			Union all
			select AM.date,AML.ref as ref,null as name,AML.name as description,AML.amount_currency as debit,0 as credit,AM.state
			from account_move AM,account_move_line AML,account_account AA,account_period AP,account_fiscalyear AF
			where AM.id=AML.move_id
			and AA.id=AML.account_id
			and AML.amount_currency>0
			and AML.partner_id is Null
			and AP.fiscalyear_id=AF.id
			and AML.period_id=AP.id
			and AF.id=param_fiscal_id
			and AA.name=param_account			
			and AM.date between from_date and to_date
		)A		
		
	LOOP
	
 		
		select trans_id into tran_ref from account_temp_report where trans_date = trans_data.date order by trans_data.date;
		if tran_ref = '-' then
				
			update account_temp_report set trans_id = trans_data.ref,trans_type=trans_data.name,
			description = 	trans_data.description,rec_qty = trans_data.credit,
			iss_qty = trans_data.debit,state=trans_data.state where trans_date = trans_data.date ;
	 		   
		else
		
			INSERT INTO account_temp_report(trans_date,trans_id,trans_type,description, rec_qty, 
				    iss_qty,balance,state)
			    VALUES (trans_data.date,trans_data.ref,trans_data.name, trans_data.description, trans_data.credit, 
				    trans_data.debit,opening_balance,trans_data.state);	
		end if;
	END LOOP;
	FOR row_data 
	IN
		select rec_qty,iss_qty,coalesce(balance,0) as balance,id from account_temp_report order by trans_date,id desc

	LOOP    
	        delete from account_temp_report where description='-'and rec_qty=0 and iss_qty=0;

                RAISE NOTICE 'rec_qty=0.......%',row_data.rec_qty;
                RAISE NOTICE 'iss_qty=0.......%',row_data.iss_qty;
                RAISE NOTICE 'balance=0.......%',row_data.balance;
                


	        

		if new_balance = 0 then
			select row_data.balance+(row_data.iss_qty-row_data.rec_qty) into new_balance from account_temp_report; 
			--where id = row_data.id;
			RAISE NOTICE 'new_balance=0.......%',new_balance;		
			update account_temp_report set balance = new_balance
			where id = row_data.id;		
	
		else
			row_data.balance=new_balance;
			RAISE NOTICE 'balance.......%',row_data.balance;
				
			select row_data.balance+(row_data.iss_qty-row_data.rec_qty) into new_balance from account_temp_report ;
			--where id = row_data.id;
			RAISE NOTICE 'total.......%',row_data.rec_qty - row_data.iss_qty;			
			RAISE NOTICE 'id-1.......%',row_data.id;
			RAISE NOTICE 'new_balance.......%',new_balance;		
			update account_temp_report set balance = new_balance where id = row_data.id;			
			
		end if;

	END LOOP;

	RAISE NOTICE 'Ending Store Procedure.......';
	if param_status = 'draft' then

	RETURN QUERY select  id as s_id,trans_date as t_date, trans_id as ref, trans_type as type, description as dsc,  
			    iss_qty as is_qty ,rec_qty as r_qty,balance as bln,state as p_state from 
			    account_temp_report where state = param_status order by t_date,s_id desc
			    ;
		    
	elseif param_status = 'posted' then

	RETURN QUERY select  id as s_id,trans_date as t_date, trans_id as ref, trans_type as type, description as dsc,  
			    iss_qty as is_qty ,rec_qty as r_qty,balance as bln,state as p_state from 
			    account_temp_report where state = param_status order by t_date,s_id desc
			    ;
	else
	RETURN QUERY select  id as s_id,trans_date as t_date, trans_id as ref, trans_type as type, description as dsc,  
			    iss_qty as is_qty ,rec_qty as r_qty,balance as bln,state as p_state from 
			    account_temp_report  order by t_date,s_id desc 
			    ;
	end if;
	END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100
  ROWS 1000;

-- Table: account_temp_report

-- DROP TABLE account_temp_report;

CREATE TABLE account_temp_report
(
  balance numeric,
  trans_date date,
  trans_type character varying,
  trans_id character varying,
  description character varying,
  rec_qty numeric,
  iss_qty numeric,
  id serial NOT NULL,
  state character varying
)
WITH (
  OIDS=FALSE
);

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

-- Function: financial_report_monthly_balance_analytic(integer, integer, integer, text, integer)

-- DROP FUNCTION financial_report_monthly_balance_analytic(integer, integer, integer, text, integer);

CREATE OR REPLACE FUNCTION financial_report_monthly_balance_analytic(report_id integer, fiscal_year integer, period_id integer, state_cond text, analytic_id integer)
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

		select array_agg(id) into analytic_account_ids 
		from account_analytic_tree  where analytic_id  = ANY(PATH); 
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
EXECUTE sql into balance USING analytic_account_ids,fiscal_year,period_id,state_cond;
IF balance < 0 THEN
	balance = balance * -1;
END IF;

  return balance;
  END;
  $BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;

-- Function: financial_report_yearly_balance_sheet_report_analytic(integer, integer, integer, text, integer)

-- DROP FUNCTION financial_report_yearly_balance_sheet_report_analytic(integer, integer, integer, text, integer);

CREATE OR REPLACE FUNCTION financial_report_yearly_balance_sheet_report_analytic(report_id integer, start_fiscal_year integer, end_fiscal_year integer, state_cond text, analytic_id integer)
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
		    select array_agg(id) into analytic_account_ids 
			    from account_analytic_tree  where analytic_id  = ANY(PATH);
                      
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
    
    EXECUTE sql into balance USING analytic_account_ids,start_fiscal_year,end_fiscal_year,state_cond;
    IF balance < 0 THEN
    balance = balance * -1;
    END IF;

   return balance;
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