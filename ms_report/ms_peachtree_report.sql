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