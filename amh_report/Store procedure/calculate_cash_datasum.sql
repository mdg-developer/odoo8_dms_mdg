-- Function: calculate_cash_datasum(integer, integer, date)

-- DROP FUNCTION calculate_cash_datasum(integer, integer, date);

CREATE OR REPLACE FUNCTION calculate_cash_datasum(IN section_ids integer, IN user_ids integer, IN from_date date)
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
	and ai.payment_type='cash'
	and av.date::date = from_date
	group by rp.name,rp.id,ai.payment_type) asdf),
	deduct_tbl as (select sum(aaa.deduct_amt)as deduct_amt, 123321 as myid from (select rp.id,rp.name,sum(so.deduct_amt) as deduct_amt
	from sale_order so, res_partner rp
	where rp.id=so.partner_id
	and ((so.date_order at time zone 'utc' )at time zone 'asia/rangoon')::date = from_date
	and so.section_id = section_ids
	and so.user_id  = user_ids
	and so.payment_type='cash'
	group by rp.name,rp.id) aaa),
	open_tbl as (select sum(bbb.open_amt) as open_amt,123321 as myid from (SELECT sum(inv.residual) as open_amt,partner_id as inv_partid 
	FROM account_invoice inv,res_partner rp 
	where inv.partner_id = rp.id and inv.payment_type='cash' and inv.state='open' 
	and ((inv.date_invoice at time zone 'utc' )at time zone 'asia/rangoon')::date <  from_date
	and inv.section_id= section_ids 
	and inv.user_id= user_ids 
	and inv.type = 'out_invoice' and residual > 0 group by partner_id)bbb)
	Select open_tbl.open_amt,deduct_tbl.deduct_amt,paidamt_tbl.paidamount,ns_tbl.amount_total
	From (select sum(aaa.amount_total) amount_total,123321 as myid from (select rp.id,rp.name,sum(so.amount_total) amount_total
	from sale_order so, res_partner rp
	where  rp.id=so.partner_id	
	and ((so.date_order at time zone 'utc' )at time zone 'asia/rangoon')::date = from_date
	and so.section_id = section_ids
	and so.user_id  = user_ids	
	and so.payment_type='cash'		
	group by rp.name,rp.id) aaa) as ns_tbl
	left join open_tbl on open_tbl.myid=ns_tbl.myid
	left join deduct_tbl on deduct_tbl.myid=ns_tbl.myid
	left join paidamt_tbl on paidamt_tbl.myid=ns_tbl.myid;
			
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100
  ROWS 1000;
ALTER FUNCTION calculate_cash_datasum(integer, integer, date)
  OWNER TO odoo;
