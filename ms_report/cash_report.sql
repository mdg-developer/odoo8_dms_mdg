-- Function: cash_report_opening(date, date, text)

-- DROP FUNCTION cash_report_opening(date, date, text);

CREATE OR REPLACE FUNCTION cash_report_opening(date_from date, date_to date, state_cond text)
  RETURNS numeric AS
$BODY$
  DECLARE
    balance numeric;
    date_start date;
    date_stop date;
    date_record record;
    sql text :=   'select
                    COALESCE(sum((aml.debit)),0)
                  from account_move_line aml,                    
                    account_move
                  WHERE                    
                    aml.move_id = account_move.id                  
                  and aml.account_id in (select id from account_account where name in (''Cash (MMK)'',''Cash Donation''))';

  BEGIN

    IF date_from is not null and date_to is not null  THEN 
	 sql := sql || ' AND aml.period_id=(select min(id) from account_period)';
    END IF;  
    IF state_cond = 'posted' THEN
       sql := sql || ' AND account_move.state = $1';
    END IF;
    RAISE NOTICE ' SQL (%)', sql;
    EXECUTE sql into balance USING state_cond;
    RAISE NOTICE 'balance (%)', balance;

   return balance;
  END;
  $BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
  
-- Function: cash_report(date, date, text)

-- DROP FUNCTION cash_report(date, date, text);

CREATE OR REPLACE FUNCTION cash_report(IN date_from date, IN date_to date, IN state_cond text)
  RETURNS TABLE(move_date date, ref character varying, partner character varying, account_type character varying, debit numeric, credit numeric, state character varying, seq integer, reference_no character varying) AS
$BODY$
DECLARE 
           
 BEGIN

	if state_cond='posted' then 
		RETURN QUERY 		
			select am.date as move_date,am.name as ref,rp.name as partner,aj.name as account_type,COALESCE(sum(aml.debit),0) debit,0.0 as credit,am.state,1 as seq,am.ref as reference_no
			from account_move_line aml,account_move am,account_period period,res_partner rp,account_journal aj
			where aml.move_id = am.id
			and period.id=am.period_id
			and rp.id=aml.partner_id
			and aj.id=am.journal_id			
			and am.ref like 'SO%'
			and am.date between date_from and date_to		
			and am.state='posted'	
			group by am.date,am.name,rp.name,aj.name,am.state,am.ref
			union
			select am.date as move_date,am.name as ref,rp.name as partner,aj.name as account_type,0.0 as debit,COALESCE(sum(aml.credit),0) credit,am.state,2 as seq,am.ref as reference_no
			from account_move_line aml,account_move am,account_period period,res_partner rp,account_journal aj
			where aml.move_id = am.id
			and period.id=am.period_id
			and rp.id=aml.partner_id
			and aj.id=am.journal_id			
			and am.ref like 'PO%'
			and am.date between date_from and date_to				
			and am.state='posted'	
			group by am.date,am.name,rp.name,aj.name,am.state,am.ref
			order by seq;
	else
		RETURN QUERY 		
			select am.date as move_date,am.name as ref,rp.name as partner,aj.name as account_type,COALESCE(sum(aml.debit),0) debit,0.0 as credit,am.state,1 as seq,am.ref as reference_no
			from account_move_line aml,account_move am,account_period period,res_partner rp,account_journal aj
			where aml.move_id = am.id
			and period.id=am.period_id
			and rp.id=aml.partner_id
			and aj.id=am.journal_id			
			and am.ref like 'SO%'
			and am.date between date_from and date_to		
			group by am.date,am.name,rp.name,aj.name,am.state,am.ref
			union
			select am.date as move_date,am.name as ref,rp.name as partner,aj.name as account_type,0.0 as debit,COALESCE(sum(aml.credit),0) credit,am.state,2 as seq,am.ref as reference_no
			from account_move_line aml,account_move am,account_period period,res_partner rp,account_journal aj
			where aml.move_id = am.id
			and period.id=am.period_id
			and rp.id=aml.partner_id
			and aj.id=am.journal_id			
			and am.ref like 'PO%'
			and am.date between date_from and date_to			
			group by am.date,am.name,rp.name,aj.name,am.state,am.ref
			order by seq;
	end if;
	

 END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100
  ROWS 1000;
  
-- Function: cash_report_closing(date, date, text)

-- DROP FUNCTION cash_report_closing(date, date, text);

CREATE OR REPLACE FUNCTION cash_report_closing(date_from date, date_to date, state_cond text)
  RETURNS numeric AS
$BODY$
  DECLARE
    balance numeric;
    initial_balance numeric;
    amount numeric;
  BEGIN

	EXECUTE 'select * from cash_report_opening($1,$2,$3)' USING date_from,date_to,state_cond INTO initial_balance;
	RAISE NOTICE ' initial_balance (%)', initial_balance;
	EXECUTE 'select COALESCE(sum(debit-credit),0) from cash_report($1,$2,$3)' USING date_from,date_to,state_cond INTO amount;
	RAISE NOTICE ' amount (%)', amount;
	balance=initial_balance+amount;

   return balance;
  END;
  $BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
  
-- Function: calculate_opening_balance(date, date, text)

-- DROP FUNCTION calculate_opening_balance(date, date, text);

CREATE OR REPLACE FUNCTION calculate_opening_balance(date_from date, date_to date, state_cond text)
  RETURNS numeric AS
$BODY$
  DECLARE
    balance numeric;
    p_id integer;
  BEGIN

    select id into p_id from account_period where id=(select min(id) from account_period) and date_from between date_start and date_stop;
    if p_id is not null then
	EXECUTE 'select * from cash_report_opening($1,$2,$3)' USING date_from,date_to,state_cond INTO balance;
    else
	EXECUTE 'select * from cash_report_closing($1,$2,$3)' USING date_from-1,date_to,state_cond INTO balance;
    end if;

    RAISE NOTICE 'balance (%)', balance;

   return balance;
  END;
  $BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;