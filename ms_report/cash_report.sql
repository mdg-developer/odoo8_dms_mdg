-- Function: calculate_opening_balance(date, date, text)

-- DROP FUNCTION calculate_opening_balance(date, date, text);

CREATE OR REPLACE FUNCTION calculate_opening_balance(date_from date, date_to date, state_cond text)
  RETURNS numeric AS
$BODY$
  DECLARE
    balance numeric=0;
    opening integer;
    opening_debit numeric;
    max_date date;
    closing_balance numeric=0;
    min_date date;
    opening_balance numeric=0;
    move_record record;
    initial_balance numeric;
    amount numeric;
  BEGIN

	select date into min_date
	from account_move
	where journal_id in (select id from account_journal where name like 'Opening%') and date between date_from and date_to;
	RAISE NOTICE 'min_date(%)',min_date;
			
	if min_date = date_from or (min_date>=date_from and min_date<=date_to) then
	
		if state_cond='posted' then
			select COALESCE(sum((aml.debit)),0) into opening_debit
			from account_move_line aml,account_move am
			where aml.move_id = am.id                  
			and aml.account_id in (select id from account_account where name in ('Cash (MMK)','Cash Donation'))			
			and am.date=min_date 
			and am.state=state_cond;
		else
			select COALESCE(sum((aml.debit)),0) into opening_debit
			from account_move_line aml,account_move am
			where aml.move_id= am.id                  
			and aml.account_id in (select id from account_account where name in ('Cash (MMK)','Cash Donation'))			
			and am.date=min_date;			
		end if;	
		balance=opening_debit;
		RAISE NOTICE 'balance(%)',balance;
				
	elsif date_from < min_date then
		balance=0;
	else
		select max(date) into max_date
		from account_move
		where date<date_from;
		RAISE NOTICE 'max_date(%)',max_date;
		if max_date is not null then
			EXECUTE 'select * from calculate_closing_balance($1,$2,$3)' USING max_date,max_date,state_cond INTO closing_balance;
			balance=closing_balance;
		end if;
	end if;

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
			select am.date as move_date,am.name as ref,rp.name as partner,aj.code as account_type,COALESCE(sum(aml.debit),0) debit,0.0 as credit,am.state,1 as seq,am.ref as reference_no
			from account_move_line aml,account_move am,account_period period,res_partner rp,account_journal aj,account_account aa
			where aml.move_id = am.id
			and period.id=am.period_id
			and rp.id=aml.partner_id
			and aj.id=am.journal_id	
			and aa.id=aml.account_id		
			and am.date between date_from and date_to		
			and am.state='posted'
			and aa.name in ('Cash (MMK)','Cash Donation')
			and aj.name='Cash'
			group by am.date,am.name,rp.name,aj.code,am.state,am.ref
			union
			select am.date as move_date,am.name as ref,rp.name as partner,aj.code as account_type,0.0 as debit,COALESCE(sum(aml.credit),0) credit,am.state,2 as seq,am.ref as reference_no
			from account_move_line aml,account_move am,account_period period,res_partner rp,account_journal aj,account_account aa
			where aml.move_id = am.id
			and period.id=am.period_id
			and rp.id=aml.partner_id
			and aj.id=am.journal_id
			and aa.id=aml.account_id				
			and am.date between date_from and date_to				
			and am.state='posted'	
			and aa.name in ('Cash (MMK)','Cash Donation')
			and aj.name='Cash'
			group by am.date,am.name,rp.name,aj.code,am.state,am.ref
			order by seq,move_date;
	else
		RETURN QUERY 		
			select am.date as move_date,am.name as ref,rp.name as partner,aj.code as account_type,COALESCE(sum(aml.debit),0) debit,0.0 as credit,am.state,1 as seq,am.ref as reference_no
			from account_move_line aml,account_move am,account_period period,res_partner rp,account_journal aj,account_account aa
			where aml.move_id = am.id
			and period.id=am.period_id
			and rp.id=aml.partner_id
			and aj.id=am.journal_id	
			and aa.id=aml.account_id		
			and aa.name in ('Cash (MMK)','Cash Donation')
			and aj.name='Cash'
			and am.date between date_from and date_to		
			group by am.date,am.name,rp.name,aj.code,am.state,am.ref
			union
			select am.date as move_date,am.name as ref,rp.name as partner,aj.code as account_type,0.0 as debit,COALESCE(sum(aml.credit),0) credit,am.state,2 as seq,am.ref as reference_no
			from account_move_line aml,account_move am,account_period period,res_partner rp,account_journal aj,account_account aa
			where aml.move_id = am.id
			and period.id=am.period_id
			and rp.id=aml.partner_id
			and aj.id=am.journal_id	
			and aa.id=aml.account_id
			and aa.name in ('Cash (MMK)','Cash Donation')
			and aj.name='Cash'
			and am.date between date_from and date_to			
			group by am.date,am.name,rp.name,aj.code,am.state,am.ref
			order by seq,move_date;
	end if;
	

 END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100
  ROWS 1000;
  
-- Function: calculate_closing_balance(date, date, text)

-- DROP FUNCTION calculate_closing_balance(date, date, text);

CREATE OR REPLACE FUNCTION calculate_closing_balance(date_from date, date_to date, state_cond text)
  RETURNS numeric AS
$BODY$
  DECLARE
    balance numeric;
    initial_balance numeric=0;
    amount numeric=0;
  BEGIN

	EXECUTE 'select * from calculate_opening_balance($1,$2,$3)' USING date_from,date_to,state_cond INTO initial_balance;
	EXECUTE 'select COALESCE(sum(debit-credit),0) from cash_report($1,$2,$3)' USING date_from,date_to,state_cond INTO amount;
	RAISE NOTICE ' amount (%)', amount;
	balance=initial_balance+amount;

   return balance;
  END;
  $BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;