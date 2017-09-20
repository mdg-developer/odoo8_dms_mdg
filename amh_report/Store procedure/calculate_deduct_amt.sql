-- Function: calculate_deduct_amt(integer, date, date)

-- DROP FUNCTION calculate_deduct_amt(integer, date, date);

CREATE OR REPLACE FUNCTION calculate_deduct_amt(IN customer_id integer, IN from_date date, IN to_date date)
  RETURNS SETOF double precision AS
$BODY$
DECLARE	
	deduct_amt double precision;			
BEGIN
	return query	
	select deduction_tbl.deduct_amt

	from (select rp.id,rp.name,sum(so.deduct_amt) as deduct_amt
	from sale_order so, res_partner rp
	where rp.id=so.partner_id
	and ((so.date_order at time zone 'utc' )at time zone 'asia/rangoon')::date between from_date and to_date 
	and so.partner_id=customer_id
	group by rp.name,rp.id)  deduction_tbl;
			
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100
  ROWS 1000;
ALTER FUNCTION calculate_deduct_amt(integer, date, date)
  OWNER TO odoo;
