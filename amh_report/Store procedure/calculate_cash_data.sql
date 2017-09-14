-- Function: calculate_cash_data(integer, integer, integer, date)

-- DROP FUNCTION calculate_cash_data(integer, integer, integer, date);

CREATE OR REPLACE FUNCTION calculate_cash_data(IN customer_id integer, IN section_ids integer, IN user_ids integer, IN from_date date)
  RETURNS TABLE(open_amt numeric, deduct_amt double precision, paidamount numeric, amount_total numeric, sale_amt numeric) AS
$BODY$
DECLARE
	open_amt numeric;	
	deduct_amt double precision;	
	paidamount numeric;	
	amount_total numeric;	
	sale_amt numeric;		
BEGIN
	return query	
	with 
	cd_amount_tbl as (select ai.payment_type,sum(avl.amount) as  paidamount,
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
	and ai.payment_type='cash'
	and av.date::date = from_date
	and so.partner_id=customer_id
	and ai.residual=0.00
	group by ai.payment_type,rp.name,rp.customer_code,rp.id),

	deduction_tbl as (select rp.id,rp.name,sum(so.deduct_amt) as deduct_amt
	from sale_order so, res_partner rp
	where rp.id=so.partner_id
	and ((so.date_order at time zone 'utc' )at time zone 'asia/rangoon')::date = from_date 
	and so.section_id = section_ids
	and so.user_id  = user_ids
	and so.payment_type='cash'
	and rp.id=customer_id
	group by rp.name,rp.id),

	saleamtbl as (select rp.id,rp.name,sum(sol.product_uom_qty * sol.price_unit) as sale_amt
	from sale_order so, sale_order_line sol, res_partner rp	
	where  rp.id=so.partner_id
	and sol.order_id=so.id
	and ((so.date_order at time zone 'utc' )at time zone 'asia/rangoon')::date = from_date
	and so.section_id =section_ids
	and so.user_id  = user_ids
	and so.payment_type='cash'
	and rp.id=customer_id		
	group by rp.name,rp.id),

	opening_tbl as (select sum(debit-credit) as open_amt,l.partner_id as inv_partid 
	from account_move_line l,account_move m
	where l.account_id in (select  id from account_account where user_type in (select id from account_account_type where code in ('Receivable','Payable')))
	and l.partner_id=customer_id
	and l.date < from_date
	and l.move_id = m.id
	and m.period_id in (select p.id  from account_fiscalyear f,account_period p  where  p.fiscalyear_id = f.id and f.date_start <= from_date and  f.date_stop >= from_date)
	group by l.partner_id) 

	select opening_tbl.open_amt,deduction_tbl.deduct_amt,cd_amount_tbl.paidamount,netsale_tbl.amount_total,saleamtbl.sale_amt

	from (select rp.id,rp.name,sum(so.amount_total) amount_total
	from sale_order so, res_partner rp
	where  rp.id=so.partner_id	
	and ((so.date_order at time zone 'utc' )at time zone 'asia/rangoon')::date = from_date
	and so.section_id = section_ids
	and so.user_id  = user_ids	
	and so.payment_type='cash'
	and so.partner_id=customer_id		
	group by rp.name,rp.id)  netsale_tbl
	left join opening_tbl on opening_tbl.inv_partid=netsale_tbl.id
	left join deduction_tbl on deduction_tbl.id=netsale_tbl.id
	left join saleamtbl on saleamtbl.id=netsale_tbl.id
	left join cd_amount_tbl on  cd_amount_tbl.customer_id=netsale_tbl.id;
			
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100
  ROWS 1000;
ALTER FUNCTION calculate_cash_data(integer, integer, integer, date)
  OWNER TO odoo;
