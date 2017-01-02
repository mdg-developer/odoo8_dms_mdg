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
                  and aml.journal_id in (select id from account_journal where name=''Cash'')';

  BEGIN

    IF date_from is not null and date_to is not null  THEN 
	 sql := sql || ' AND aml.period_id=(select id from account_period where special=true and fiscalyear_id in (select id from account_fiscalyear where ''' || date_from || ''' between date_start and date_stop))';
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
  RETURNS TABLE(move_date date, ref character varying, partner character varying, account_type character varying, debit numeric, credit numeric, state character varying, seq integer) AS
$BODY$
DECLARE 
           
 BEGIN

	if state_cond='posted' then 
		RETURN QUERY 		
			select am.date as move_date,am.name as ref,rp.name as partner,aj.name as account_type,COALESCE(sum(aml.debit),0) debit,0 as credit,am.state,1 as seq
			from account_move_line aml,account_move am,account_period period,res_partner rp,account_journal aj
			where aml.move_id = am.id
			and period.id=am.period_id
			and rp.id=aml.partner_id
			and aj.id=am.journal_id
			and aml.journal_id in (select id from account_journal where name='Cash')
			and am.date between date_from and date_to
			and special=false	
			and am.state='posted'	
			group by am.date,am.name,rp.name,aj.name,am.state
			union
			select am.date as move_date,am.name as ref,rp.name as partner,aj.name as account_type,0 as debit,COALESCE(sum(aml.credit),0) credit,am.state,2 as seq
			from account_move_line aml,account_move am,account_period period,res_partner rp,account_journal aj
			where aml.move_id = am.id
			and period.id=am.period_id
			and rp.id=aml.partner_id
			and aj.id=am.journal_id
			and aml.journal_id in (select id from account_journal where name='Cash')
			and am.date between date_from and date_to
			and special=false	
			and am.state='posted'	
			group by am.date,am.name,rp.name,aj.name,am.state
			order by seq;
	else
		RETURN QUERY 		
			select am.date as move_date,am.name as ref,rp.name as partner,aj.name as account_type,COALESCE(sum(aml.debit),0) debit,0 as credit,am.state,1 as seq
			from account_move_line aml,account_move am,account_period period,res_partner rp,account_journal aj
			where aml.move_id = am.id
			and period.id=am.period_id
			and rp.id=aml.partner_id
			and aj.id=am.journal_id
			and aml.journal_id in (select id from account_journal where name='Cash')
			and am.date between date_from and date_to
			and special=false			
			group by am.date,am.name,rp.name,aj.name,am.state
			union
			select am.date as move_date,am.name as ref,rp.name as partner,aj.name as account_type,0 as debit,COALESCE(sum(aml.credit),0) credit,am.state,2 as seq
			from account_move_line aml,account_move am,account_period period,res_partner rp,account_journal aj
			where aml.move_id = am.id
			and period.id=am.period_id
			and rp.id=aml.partner_id
			and aj.id=am.journal_id
			and aml.journal_id in (select id from account_journal where name='Cash')
			and am.date between date_from and date_to
			and special=false
			group by am.date,am.name,rp.name,aj.name,am.state
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

	if state_cond='posted' then 
		select COALESCE(sum(aml.debit-aml.credit),0) into amount
		from account_move_line aml,account_move am,account_period period,res_partner rp,account_journal aj
		where aml.move_id = am.id
		and period.id=am.period_id
		and rp.id=aml.partner_id
		and aj.id=am.journal_id
		and aml.journal_id in (select id from account_journal where name='Cash')
		and am.date between date_from and date_to
		and special=false	
		and am.state='posted';
	else
		select COALESCE(sum(aml.debit-aml.credit),0) into amount
		from account_move_line aml,account_move am,account_period period,res_partner rp,account_journal aj
		where aml.move_id = am.id
		and period.id=am.period_id
		and rp.id=aml.partner_id
		and aj.id=am.journal_id
		and aml.journal_id in (select id from account_journal where name='Cash')
		and am.date between date_from and date_to
		and special=false;			
	end if;
	balance=initial_balance+amount;

   return balance;
  END;
  $BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;