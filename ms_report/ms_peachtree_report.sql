-- Function: get_msol_seq(integer, integer)

-- DROP FUNCTION get_msol_seq(integer, integer);

CREATE OR REPLACE FUNCTION get_msol_seq(ms_id integer, msl_id integer)
  RETURNS integer AS
$BODY$
DECLARE
	msol_seq integer=0;
BEGIN

	WITH get_sequence AS (
		select row_number() over (order by id) as seq,id from mobile_sale_order_line where order_id=ms_id order by id
	)
	select seq into msol_seq from get_sequence where id=msl_id;

	RETURN msol_seq;

END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
  
-- Function: get_smaller_qty(integer, double precision, integer)

-- DROP FUNCTION get_smaller_qty(integer, double precision, integer);

CREATE OR REPLACE FUNCTION get_smaller_qty(product_uom_id integer, product_qty double precision, product_id integer)
  RETURNS integer AS
$BODY$
DECLARE
	ratio numeric;
	big_uom_id integer;
	product_uos_qty integer;
BEGIN

	select pt.big_uom_id into big_uom_id from product_product pp left join product_template pt on (pp.product_tmpl_id=pt.id) where pp.id=product_id;
	
	select floor(round(1/factor,2)) into ratio from product_uom where active = true and id=product_uom_id;

	if product_uom_id=big_uom_id then
		product_uos_qty = ratio * product_qty;
	else 
		product_uos_qty=product_qty;
	end if;
	
	RETURN product_uos_qty;

END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;