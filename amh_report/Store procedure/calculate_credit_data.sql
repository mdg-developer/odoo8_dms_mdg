-- Function: calculate_credit_data(integer, integer, integer, date)

-- DROP FUNCTION calculate_credit_data(integer, integer, integer, date);

CREATE OR REPLACE FUNCTION calculate_credit_data(IN customer_id integer, IN section_ids integer, IN user_ids integer, IN from_date date)
  RETURNS TABLE(deduction_amt double precision, paidamount numeric, open_amt numeric, amount_total numeric) AS
$BODY$
DECLARE
	deduction_amt double precision;	
	paidamount numeric;	
	open_amt numeric;	
	amount_total numeric;		
BEGIN
	return query	
	with 
	openingamounttbl as (select sum(debit-credit) as open_amt,l.partner_id as inv_partid 
	from account_move_line l,account_move m
	where l.account_id in (select  id from account_account where user_type in (select id from account_account_type where code in ('Receivable','Payable')))
	and l.partner_id=customer_id
	and l.date < from_date
	and l.move_id = m.id
	and m.period_id in (select p.id  from account_fiscalyear f,account_period p  where  p.fiscalyear_id = f.id and f.date_start <= from_date and  f.date_stop >= from_date)
	group by l.partner_id),

	paidamounttbl as (select ai.payment_type,sum(avl.amount) as  paidamount,
	rp.name as customer_name,rp.customer_code as customer_code,rp.id as customer_id
	from sale_order so, res_partner rp, account_invoice ai,account_move_line aml ,account_voucher_line avl,account_voucher  av
	where ai.move_id=aml.move_id 
	and aml.id=avl.move_line_id 	
	and rp.id=so.partner_id
	and ai.origin=so.name
	and ai.partner_id=so.partner_id
	and av.id = avl.voucher_id
	--and ((so.date_order at time zone 'utc' )at time zone 'asia/rangoon')::date = from_date
	and so.section_id = section_ids
	and so.user_id  = user_ids
	and ai.payment_type='credit'
	and av.date::date = from_date
	and rp.id=customer_id
	group by rp.name,rp.id,ai.payment_type),
	
	deductamttbl as (select rp.id,rp.name,sum(so.deduct_amt) as deduct_amt
	from sale_order so, res_partner rp	
	where  rp.id=so.partner_id
	and ((so.date_order at time zone 'utc' )at time zone 'asia/rangoon')::date = from_date
	and so.section_id =section_ids
	and so.user_id  = user_ids
	and so.payment_type='credit' 
	and rp.id=customer_id	
	group by rp.name,rp.id)

	Select deductamttbl.deduct_amt,paidamounttbl.paidamount,openingamounttbl.open_amt,netamttbl.amount_total
	from (select sum(so.amount_total) as amount_total,rp.name as customer_name,rp.id as customer_id
	from sale_order so,res_partner rp
	where  rp.id=so.partner_id	
	and ((so.date_order at time zone 'utc' )at time zone 'asia/rangoon')::date = from_date
	and so.section_id =section_ids
	and so.user_id  = user_ids
	and so.payment_type='credit' 
	and rp.id=customer_id
	group by rp.name,rp.id) as netamttbl

	left join deductamttbl on deductamttbl.id=netamttbl.customer_id
	left join paidamounttbl on paidamounttbl.customer_id=netamttbl.customer_id
	left join openingamounttbl on openingamounttbl.inv_partid=netamttbl.customer_id;
			
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100
  ROWS 1000;
ALTER FUNCTION calculate_credit_data(integer, integer, integer, date)
  OWNER TO odoo;
