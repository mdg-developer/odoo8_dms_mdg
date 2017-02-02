CREATE OR REPLACE FUNCTION dcode (pid integer)
RETURNS text AS $total$
declare
	total text;
BEGIN
   SELECT default_code into total FROM product_product where id=pid;
   RETURN total;
END;
$total$ LANGUAGE plpgsql;