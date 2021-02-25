-- Function: get_membership_level(integer)
-- select * from get_membership_level(248643)
-- DROP FUNCTION get_membership_level(integer);

CREATE OR REPLACE FUNCTION get_membership_level(customer_id integer)
  RETURNS character varying AS
$BODY$
DECLARE
	membership_level character varying='';
	total_point float=0;
	record RECORD;
BEGIN

	select COALESCE(sum(getting_point),0) into total_point from point_history ph where ph.partner_id=customer_id;

	if total_point > 0 then
		for record in select name,points from membership_config order by points desc
		loop
			if total_point >= record.points and total_point > 0 then
				continue;
			elsif total_point <= record.points and total_point > 0 then
				membership_level = record.name	
				break;
			end if;		
		end loop;	
	end if;
	
	RETURN membership_level;
	
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;