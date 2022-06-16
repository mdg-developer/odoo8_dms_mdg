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
    balance = balance * -1;
    END IF;

   return balance;
  END;
  $BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION financial_report_yearly_balance_sheet_report(integer, integer, integer, text)
  OWNER TO postgres;
  
  
  -- Function: balance_sheet_report_this_year(integer, integer, text)

-- DROP FUNCTION balance_sheet_report_this_year(integer, integer, text);

--CREATE OR REPLACE FUNCTION balance_sheet_report_this_year(report_id integer, start_fiscal_year integer, state_cond text)
--  RETURNS numeric AS
--$BODY$
--  DECLARE
--    balance numeric;
--    account_ids int[];
--  --  opening_period int;
--    temp_account_id int[];
--    r account_account_financial_report%rowtype;
--    sql text :=   'select
--                    COALESCE(sum((aml.debit - aml.credit)),0)
--                  from account_move_line aml,
--                    account_period period,
--                    account_fiscalyear fiscalyear,
--                    account_move
--                  WHERE
--                    aml.period_id = period.id AND
--                    aml.move_id = account_move.id AND
--                    period.fiscalyear_id = fiscalyear.id';
--
--  BEGIN
--
--                       -- opening_period=(start_period_id-1);
--                     -- select account_id from account_account_financial_report where report_line_id=report_id
--                    FOR r IN select *  from account_account_financial_report where report_line_id=$1
--                    LOOP
--			select array_cat(account_ids,array_agg(id)) into account_ids from account_tree where r.account_id = ANY(PATH);
--                    END LOOP;
--                    --there is not account and return null for that
--		     IF account_ids IS NULL THEN
--			return null;
--		     END IF;
--                    IF account_ids IS NOT NULL THEN
--                        sql := sql || ' AND aml.account_id in ('|| array_to_string(account_ids, ',') ||')';
--	            END IF;
--
--     --IF  start_fiscal_year >0 and end_fiscal_year > 0 and start_fiscal_year is not null and end_fiscal_year is not null THEN
--      sql := sql || ' AND fiscalyear.id = $2';
--    --END IF;
--
--    IF $3 = 'posted' THEN
--       sql := sql || ' AND account_move.state = $3';
--    END IF;
--    RAISE NOTICE ' SQL (%)', sql;
--    
--    EXECUTE sql into balance USING account_ids,start_fiscal_year,state_cond;
--    IF balance < 0 THEN
--    balance = balance * -1;
--    END IF;
--
--   return balance;
--  END;
--  $BODY$
--  LANGUAGE plpgsql VOLATILE
--  COST 100;
--ALTER FUNCTION balance_sheet_report_this_year(integer, integer, text)
--  OWNER TO postgres;

-- Function: balance_sheet_report_last_year(integer, integer, text)

-- DROP FUNCTION balance_sheet_report_last_year(integer, integer, text);

--CREATE OR REPLACE FUNCTION balance_sheet_report_last_year(report_id integer, start_fiscal_year integer, state_cond text)
--  RETURNS numeric AS
--$BODY$
--  DECLARE
--    balance numeric;
--    account_ids int[];
--  --  opening_period int;
--    temp_account_id int[];
--    r account_account_financial_report%rowtype;
--    sql text :=   'select
--                    COALESCE(sum((aml.debit - aml.credit)),0)
--                  from account_move_line aml,
--                    account_period period,
--                    account_fiscalyear fiscalyear,
--                    account_move
--                  WHERE
--                    aml.period_id = period.id AND
--                    aml.move_id = account_move.id AND
--                    period.fiscalyear_id = fiscalyear.id';
--
--  BEGIN
--
--                       -- opening_period=(start_period_id-1);
--                     -- select account_id from account_account_financial_report where report_line_id=report_id
--                    FOR r IN select *  from account_account_financial_report where report_line_id=$1
--                    LOOP
--			select array_cat(account_ids,array_agg(id)) into account_ids from account_tree where r.account_id = ANY(PATH);
--                    END LOOP;
--                    --there is not account and return null for that
--		     IF account_ids IS NULL THEN
--			return null;
--		     END IF;
--                    IF account_ids IS NOT NULL THEN
--                        sql := sql || ' AND aml.account_id in ('|| array_to_string(account_ids, ',') ||')';
--	            END IF;
--
--     --IF  start_fiscal_year >0 and end_fiscal_year > 0 and start_fiscal_year is not null and end_fiscal_year is not null THEN
--      sql := sql || ' AND fiscalyear.id = $2-1';
--    --END IF;
--
--    IF $3 = 'posted' THEN
--       sql := sql || ' AND account_move.state = $3';
--    END IF;
--    RAISE NOTICE ' SQL (%)', sql;
--    
--    EXECUTE sql into balance USING account_ids,start_fiscal_year,state_cond;
--    IF balance < 0 THEN
--    balance = balance * -1;
--    END IF;
--
--   return balance;
--  END;
--  $BODY$
--  LANGUAGE plpgsql VOLATILE
--  COST 100;
--ALTER FUNCTION balance_sheet_report_last_year(integer, integer, text)
--  OWNER TO postgres;

-- Function: financial_report_balance_prior_current_this_year(integer, integer, text)

-- DROP FUNCTION financial_report_balance_prior_current_this_year(integer, integer, text);

--CREATE OR REPLACE FUNCTION financial_report_balance_prior_current_this_year(report_id integer, fiscal_year integer, state_cond text)
--  RETURNS numeric AS
--$BODY$
--  DECLARE
--    balance numeric;
--    account_ids int[];
--    account_account_ids int[];
--    current_period_account_ids  int[];
--    temp_account_id int[];
--    retain boolean;
--    yyear integer;
--    r account_account_financial_report%rowtype;
--    sql text :=   'select
--                    COALESCE(sum((aml.debit - aml.credit)),0)
--                  from account_move_line aml,
--                    account_period period,
--                    account_fiscalyear fiscalyear,
--                    account_move
--                  WHERE
--                    aml.period_id = period.id AND
--                    aml.move_id = account_move.id AND
--                    period.fiscalyear_id = fiscalyear.id';
--
--  BEGIN
--
--			retain = false;
--			--select id into yyear_id from account_period where fiscalyear_id=$2 limit 1;
--			select  id into  yyear from account_period where fiscalyear_id =$2 and special is true ;
--                     -- select account_id from account_account_financial_report where report_line_id=report_id
--                    FOR r IN select *  from account_account_financial_report where report_line_id=$1
--                    LOOP
--                    raise NOTICE ' searching id(%)',r.account_id;
--			select array_cat(account_ids,array_agg(id)) into account_ids from account_tree where r.account_id = ANY(PATH);
--                    END LOOP;
--                    FOR r IN  select *  from account_account_financial_report where report_line_id in ( select id from account_financial_report where retain_earning is true)
--                    LOOP
--                    raise NOTICE ' searching id(%)',r.account_id;
--			select array_cat(account_ids,array_agg(id)) into account_account_ids  from account_tree where r.account_id = ANY(PATH);
--                    END LOOP;
--                    FOR r IN  select *  from account_account_financial_report where report_line_id = 3464
--                    LOOP
--                    raise NOTICE ' searching id(%)',r.account_id;
--			select array_cat(account_ids,array_agg(id)) into current_period_account_ids  from account_tree where r.account_id = ANY(PATH);
--                    END LOOP;
--                    --there is not account and return null for that
--		     IF account_ids IS NULL THEN
--			return null;
--		     END IF;
--                    IF account_ids IS NOT NULL THEN
--                        sql := sql || ' AND aml.account_id in ('|| array_to_string(account_ids, ',') ||')';
--	            END IF;
--		    RAISE NOTICE ' SQL (%)', sql;
--                    IF account_account_ids IS NOT NULL THEN
--                        sql := sql || ' AND aml.account_id in ('|| array_to_string(account_account_ids, ',') ||')';
--			IF  fiscal_year>0 THEN
--				sql := sql || ' AND fiscalyear.id between 1 and $2-1';
--               	        END IF;
--                        retain = true;
--                           IF $3 = 'posted' THEN
--				       sql := sql || ' AND account_move.state = $3';
--				    END IF;
--				    RAISE NOTICE ' SQL (%)', sql;
--				    EXECUTE sql into balance USING account_ids,fiscal_year,state_cond;
--				    IF balance < 0 THEN
--				    balance = balance;
--				    END IF;
--					RAISE NOTICE 'balance (%)', balance;
--					
--				   return balance;
--                     END IF;
--
--                    IF account_account_ids IS NOT NULL and retain IS TRUE THEN
--                         IF  fiscal_year>0   THEN
--                            sql := sql || ' AND fiscalyear.id = $2';
--                         END IF;
--                         IF  current_period_account_ids IS NOT NULL THEN
--				sql := sql || ' AND aml.account_id in ('|| array_to_string(current_period_account_ids, ',') ||')';
--                        END IF;
--			IF $3 = 'posted' THEN
--			       sql := sql || ' AND account_move.state = $3';
--			END IF;
--			 RAISE NOTICE ' SQL (%)', sql;
--			
--			EXECUTE sql into balance USING account_ids,fiscal_year,state_cond;
--			 IF balance < 0 THEN
--			    balance = balance;
--			END IF;
--				RAISE NOTICE 'balance (%)', balance;
--				
--
--			 return balance;
--			 
--                      
--                     END IF;
--
--  END;
--  $BODY$
--  LANGUAGE plpgsql VOLATILE
--  COST 100;
--ALTER FUNCTION financial_report_balance_prior_current_this_year(integer, integer, text)
--  OWNER TO postgres;

  
-- Function: financial_report_balance_prior_current_last_year(integer, integer, text)

-- DROP FUNCTION financial_report_balance_prior_current_last_year(integer, integer, text);

--CREATE OR REPLACE FUNCTION financial_report_balance_prior_current_last_year(report_id integer, fiscal_year integer, state_cond text)
--  RETURNS numeric AS
--$BODY$
--  DECLARE
--    balance numeric;
--    account_ids int[];
--    account_account_ids int[];
--    current_period_account_ids  int[];
--    temp_account_id int[];
--    retain boolean;
--    yyear integer;
--    r account_account_financial_report%rowtype;
--    sql text :=   'select
--                    COALESCE(sum((aml.debit - aml.credit)),0)
--                  from account_move_line aml,
--                    account_period period,
--                    account_fiscalyear fiscalyear,
--                    account_move
--                  WHERE
--                    aml.period_id = period.id AND
--                    aml.move_id = account_move.id AND
--                    period.fiscalyear_id = fiscalyear.id';
--
--  BEGIN
--
--			retain = false;
--			--select id into yyear_id from account_period where fiscalyear_id=$2 limit 1;
--			select  id into  yyear from account_period where fiscalyear_id =$2 and special is true ;
--                     -- select account_id from account_account_financial_report where report_line_id=report_id
--                    FOR r IN select *  from account_account_financial_report where report_line_id=$1
--                    LOOP
--                    raise NOTICE ' searching id(%)',r.account_id;
--			select array_cat(account_ids,array_agg(id)) into account_ids from account_tree where r.account_id = ANY(PATH);
--                    END LOOP;
--                    FOR r IN  select *  from account_account_financial_report where report_line_id in ( select id from account_financial_report where retain_earning is true)
--                    LOOP
--                    raise NOTICE ' searching id(%)',r.account_id;
--			select array_cat(account_ids,array_agg(id)) into account_account_ids  from account_tree where r.account_id = ANY(PATH);
--                    END LOOP;
--                    FOR r IN  select *  from account_account_financial_report where report_line_id = 3464
--                    LOOP
--                    raise NOTICE ' searching id(%)',r.account_id;
--			select array_cat(account_ids,array_agg(id)) into current_period_account_ids  from account_tree where r.account_id = ANY(PATH);
--                    END LOOP;
--                    --there is not account and return null for that
--		     IF account_ids IS NULL THEN
--			return null;
--		     END IF;
--                    IF account_ids IS NOT NULL THEN
--                        sql := sql || ' AND aml.account_id in ('|| array_to_string(account_ids, ',') ||')';
--	            END IF;
--		    RAISE NOTICE ' SQL (%)', sql;
--                    IF account_account_ids IS NOT NULL THEN
--                        sql := sql || ' AND aml.account_id in ('|| array_to_string(account_account_ids, ',') ||')';
--			IF  fiscal_year>0 THEN
--				sql := sql || ' AND fiscalyear.id between 1 and $2-1';
--               	        END IF;
--                        retain = true;
--                           IF $3 = 'posted' THEN
--				       sql := sql || ' AND account_move.state = $3';
--				    END IF;
--				    RAISE NOTICE ' SQL (%)', sql;
--				    EXECUTE sql into balance USING account_ids,fiscal_year,state_cond;
--				    IF balance < 0 THEN
--				    balance = balance;
--				    END IF;
--					RAISE NOTICE 'balance (%)', balance;
--					
--				   return balance;
--                     END IF;
--
--                    IF account_account_ids IS NOT NULL and retain IS TRUE THEN
--                         IF  fiscal_year>0   THEN
--                            sql := sql || ' AND fiscalyear.id = $2-1';
--                         END IF;
--                         IF  current_period_account_ids IS NOT NULL THEN
--				sql := sql || ' AND aml.account_id in ('|| array_to_string(current_period_account_ids, ',') ||')';
--                        END IF;
--			IF $3 = 'posted' THEN
--			       sql := sql || ' AND account_move.state = $3';
--			END IF;
--			 RAISE NOTICE ' SQL (%)', sql;
--			EXECUTE sql into balance USING account_ids,fiscal_year,state_cond;
--			 IF balance < 0 THEN
--			    balance = balance;
--			END IF;
--				RAISE NOTICE 'balance (%)', balance;
--				
--
--			 return balance;
--			 
--                      
--                     END IF;
--
--  END;
--  $BODY$
--  LANGUAGE plpgsql VOLATILE
--  COST 100;
--ALTER FUNCTION financial_report_balance_prior_current_last_year(integer, integer, text)
--  OWNER TO postgres;

  
-- Function: financial_report_balance_current_this_year(integer, integer, text)

-- DROP FUNCTION financial_report_balance_current_this_year(integer, integer, text);

--CREATE OR REPLACE FUNCTION financial_report_balance_current_this_year(report_id integer, fiscal_year integer, state_cond text)
--  RETURNS numeric AS
--$BODY$
--  DECLARE
--    balance numeric;
--    account_ids int[];
--    temp_account_id int[];
--    period integer;
--    r account_account_financial_report%rowtype;
--    sql text :=   'select
--                    COALESCE(sum((aml.debit - aml.credit)),0)
--                  from account_move_line aml,
--                    account_period period,
--                    account_fiscalyear fiscalyear,
--                    account_move
--                  WHERE
--                    aml.period_id = period.id AND
--                    aml.move_id = account_move.id AND
--                    period.fiscalyear_id = fiscalyear.id';
--
--  BEGIN
--                      select  id into  period from account_period where fiscalyear_id =$2 and special is false  limit 1;
--                      --start_period_id = period ;
--                     -- select account_id from account_account_financial_report where report_line_id=report_id
--                    FOR r IN select *  from account_account_financial_report where report_line_id=$1
--                    LOOP
--                    raise NOTICE ' searching id(%)',r.account_id;
--			select array_cat(account_ids,array_agg(id)) into account_ids from account_tree where r.account_id = ANY(PATH);
--                    END LOOP;
--                    --there is not account and return null for that
--		     IF account_ids IS NULL THEN
--			return null;
--		     END IF;
--                    IF account_ids IS NOT NULL THEN
--                        sql := sql || ' AND aml.account_id in ('|| array_to_string(account_ids, ',') ||')';
--	            END IF;
--		    RAISE NOTICE ' SQL (%)', sql;
--    IF  fiscal_year>0 THEN
--      sql := sql || ' AND fiscalyear.id = $2';
--    END IF;
--    
--    IF $3 = 'posted' THEN
--       sql := sql || ' AND account_move.state = $3';
--    END IF;
--    RAISE NOTICE ' SQL (%)', sql;
--    EXECUTE sql into balance USING account_ids,fiscal_year,state_cond;
--    IF balance < 0 THEN
--    balance = balance;
--    END IF;
--        RAISE NOTICE 'balance (%)', balance;
--
--   return balance;
--  END;
--  $BODY$
--  LANGUAGE plpgsql VOLATILE
--  COST 100;
--ALTER FUNCTION financial_report_balance_current_this_year(integer, integer, text)
--  OWNER TO postgres;

  
-- Function: financial_report_balance_current_last_year(integer, integer, text)

-- DROP FUNCTION financial_report_balance_current_last_year(integer, integer, text);

--CREATE OR REPLACE FUNCTION financial_report_balance_current_last_year(report_id integer, fiscal_year integer, state_cond text)
--  RETURNS numeric AS
--$BODY$
--  DECLARE
--    balance numeric;
--    account_ids int[];
--    temp_account_id int[];
--    period integer;
--    r account_account_financial_report%rowtype;
--    sql text :=   'select
--                    COALESCE(sum((aml.debit - aml.credit)),0)
--                  from account_move_line aml,
--                    account_period period,
--                    account_fiscalyear fiscalyear,
--                    account_move
--                  WHERE
--                    aml.period_id = period.id AND
--                    aml.move_id = account_move.id AND
--                    period.fiscalyear_id = fiscalyear.id';
--
--  BEGIN
--                      select  id into  period from account_period where fiscalyear_id =$2 and special is false  limit 1;
--                      --start_period_id = period ;
--                     -- select account_id from account_account_financial_report where report_line_id=report_id
--                    FOR r IN select *  from account_account_financial_report where report_line_id=$1
--                    LOOP
--                    raise NOTICE ' searching id(%)',r.account_id;
--			select array_cat(account_ids,array_agg(id)) into account_ids from account_tree where r.account_id = ANY(PATH);
--                    END LOOP;
--                    --there is not account and return null for that
--		     IF account_ids IS NULL THEN
--			return null;
--		     END IF;
--                    IF account_ids IS NOT NULL THEN
--                        sql := sql || ' AND aml.account_id in ('|| array_to_string(account_ids, ',') ||')';
--	            END IF;
--		    RAISE NOTICE ' SQL (%)', sql;
--    IF  fiscal_year>0 THEN
--      sql := sql || ' AND fiscalyear.id = $2-1';
--    END IF;
--    IF $3 = 'posted' THEN
--       sql := sql || ' AND account_move.state = $3';
--    END IF;
--    RAISE NOTICE ' SQL (%)', sql;
--    EXECUTE sql into balance USING account_ids,fiscal_year,state_cond;
--    IF balance < 0 THEN
--    balance = balance;
--    END IF;
--        RAISE NOTICE 'balance (%)', balance;
--
--   return balance;
--  END;
--  $BODY$
--  LANGUAGE plpgsql VOLATILE
--  COST 100;
--ALTER FUNCTION financial_report_balance_current_last_year(integer, integer, text)
--  OWNER TO postgres;

  
  
  
  
  
  
  
