-- Function: calculate_credit_datasum(integer, integer, date, integer, boolean)

-- DROP FUNCTION calculate_credit_datasum(integer, integer, date, integer, boolean);

CREATE OR REPLACE FUNCTION calculate_credit_datasum(IN section_ids integer, IN user_ids integer, IN from_date date, IN pricelist integer, IN presale boolean)
  RETURNS TABLE(open_amt numeric, deduct_amt double precision, paidamount numeric, amount_total numeric) AS
$BODY$
DECLARE
	open_amt numeric;	
	deduct_amt double precision;	
	paidamount numeric;	
	amount_total numeric;		
BEGIN
	return query	
	with
	opening_tbl as (select sum(bbb.open_amt) as open_amt,123321 as myid from (select sum(debit-credit) as open_amt,l.partner_id as inv_partid 
	from account_move_line l,account_move m, sale_order so
	where l.account_id in (select  id from account_account where user_type in (select id from account_account_type where code in ('Receivable','Payable')))
	and l.date < from_date
	and l.move_id = m.id
	and so.partner_id=m.partner_id
	and ((so.date_order at time zone 'utc' )at time zone 'asia/rangoon')::date = from_date
	and m.period_id in (select p.id  from account_fiscalyear f,account_period p  where  p.fiscalyear_id = f.id and f.date_start <=from_date and  f.date_stop >= from_date)
	group by l.partner_id) bbb),

	paidamt_tbl as (select sum(asdf.paidamount)as paidamount,123321 as myid from (select ai.payment_type,sum(avl.amount) as  paidamount,
	rp.name as customer_name,rp.customer_code as customer_code,rp.id as customer_id
	from sale_order so, res_partner rp, account_invoice ai,account_move_line aml ,account_voucher_line avl,account_voucher  av
	where ai.move_id=aml.move_id 
	and aml.id=avl.move_line_id 	
	and rp.id=so.partner_id
	and ai.partner_id=so.partner_id
	and av.id = avl.voucher_id
	and ((so.date_order at time zone 'utc' )at time zone 'asia/rangoon')::date = from_date
	and so.section_id = section_ids
	and so.user_id  = user_ids
	and so.pricelist_id=pricelist
	and so.pre_order=presale
	and ai.payment_type='credit'
	and av.date::date = from_date
	group by rp.name,rp.id,ai.payment_type) asdf),

	deduction_tbl as (select sum(aaa.deduct_amt) as deduct_amt,123321 as myid from (select rp.id,rp.name,so.deduct_amt
	from sale_order so,res_partner rp	
	where rp.id=so.partner_id	
	and ((so.date_order at time zone 'utc' )at time zone 'asia/rangoon')::date = from_date
	and so.section_id = section_ids
	and so.user_id  = user_ids
	and so.pricelist_id=pricelist
	and so.pre_order=presale
	and so.payment_type='credit'
	group by so.deduct_amt,rp.name,rp.customer_code,rp.id)aaa)
	
	select opening_tbl.open_amt,deduction_tbl.deduct_amt, paidamt_tbl.paidamount,amount_total_tbl.amount_total
	from (select sum(sss.amount_total) as amount_total,123321 as myid from (select sum( so.amount_total) as amount_total,rp.name as customer_name,rp.id as customer_id
	from sale_order so, res_partner rp
	where rp.id=so.partner_id
	and ((so.date_order at time zone 'utc' )at time zone 'asia/rangoon')::date = from_date
	and so.section_id = section_ids
	and so.user_id  = user_ids
	and so.pricelist_id=pricelist
	and so.pre_order=presale
	and so.payment_type='credit' 
	group by rp.name,rp.id)sss) as amount_total_tbl
	left join deduction_tbl on deduction_tbl.myid=amount_total_tbl.myid
	left join opening_tbl on opening_tbl.myid=amount_total_tbl.myid
	left join paidamt_tbl on paidamt_tbl.myid=amount_total_tbl.myid;	
			
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100
  ROWS 1000;
ALTER FUNCTION calculate_credit_datasum(integer, integer, date, integer, boolean)
  OWNER TO odoo;
