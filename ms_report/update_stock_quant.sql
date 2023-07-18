-- FUNCTION: update_stock_quant()
-- select * from update_stock_quant()
-- DROP FUNCTION update_stock_quant();

CREATE OR REPLACE FUNCTION update_stock_quant()
    RETURNS void
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE PARALLEL UNSAFE
AS $BODY$
DECLARE	
	sm record;
	product_count numeric;
	quant_count numeric;
	adj_qty numeric;
	total_qty numeric;
BEGIN	 
	 
	 FOR sm IN
				select
				s.location_id,
				s.product_id,
				(greatest(0,next_in.qty) - greatest(0,next_out.qty)) as x_balance
				from
				(
					select tmp.location_id,tmp.product_id
					from
					(
					select location_id,product_id
					from stock_move
					where state='done'
					--and location_id =1654
					union
					select location_dest_id,product_id
					from stock_move
					where state='done'
					--and location_dest_id =1654
					)tmp
				)
				s
				left join
				(
					select t.name,p.default_code,p.id
					from product_product p,
					product_template t,
					product_uom uom
					where p.product_tmpl_id=t.id
					and t.uom_id=uom.id
				)pp on s.product_id=pp.id
				left join
				(
					select complete_name,id,usage
					from stock_location
				)ll on s.location_id=ll.id
				left join
				(
					select product_id,location_dest_id,greatest(0,sum(product_qty)) as qty
					from stock_move
					where state='done'
					--and location_dest_id =1654							  
					group by location_dest_id, product_id
				) next_in on next_in.product_id=s.product_id and next_in.location_dest_id=s.location_id
				left join
				(
					select product_id,location_id,greatest(0,sum(product_qty)) as qty
					from stock_move
					where state='done'
					--and location_id =1654		 
					group by location_id, product_id
				) next_out on s.product_id=next_out.product_id and s.location_id=next_out.location_id
	loop
	select greatest(0,sum(qty)) into product_count from stock_quant where location_id=sm.location_id and product_id=sm.product_id;
	select coalesce(sum(qty),0) into total_qty from stock_quant where location_id=sm.location_id and product_id=sm.product_id;

	select qty into quant_count from stock_quant where product_id=sm.product_id and location_id=sm.location_id and id in(select id from stock_quant where product_id=sm.product_id and location_id=sm.location_id order by in_date,id limit 1);
	
	if sm.x_balance != total_qty then
		RAISE INFO 'product id (%) >>>> product_count (%)>>>> sm.x_balance (%)>>>> difference (%)>>>> stock_quant_qty (%) >>>>total_qty (%)', sm.product_id,product_count,sm.x_balance,sm.x_balance - product_count,quant_count,total_qty;
		if quant_count is null then
			insert into stock_quant(qty,cost,location_id,company_id,product_id,in_date)
			values(sm.x_balance,0,sm.location_id,3,sm.product_id,'2021-12-31 04:55:23');
			RAISE INFO 'insert data>>>>>>>>>>>>> stock_quant_qty (%) >>>>total_qty (%)', quant_count,sm.x_balance;
		else
			update stock_quant set qty= case 
			when product_count > 0 and sm.x_balance > 0 and sm.x_balance - product_count > 0 and quant_count > 0 then (sm.x_balance - product_count) + qty
			when product_count > 0 and sm.x_balance > 0 and sm.x_balance - product_count < 0 and quant_count > 0 then (sm.x_balance - product_count) + qty
			when product_count > 0 and sm.x_balance < 0 and sm.x_balance - product_count < 0 and quant_count > 0 then (sm.x_balance - product_count) + qty
			---add new condition
			--when product_count <= 0 and sm.x_balance < 0 and sm.x_balance - product_count < 0 and quant_count < 0 then (sm.x_balance - product_count) - qty
			when product_count <= 0 and sm.x_balance < 0 and sm.x_balance - product_count < 0 and quant_count < 0 then ((sm.x_balance - product_count) - qty) + qty
			when product_count <= 0 and sm.x_balance > 0 and sm.x_balance - product_count > 0 and quant_count < 0 then (sm.x_balance - total_qty) + qty
			when product_count > 0 and sm.x_balance = 0 and  quant_count > 0 then sm.x_balance
			else
			(qty + ABS(product_count) - ABS(sm.x_balance)) * -1
			end
			where product_id=sm.product_id and location_id=sm.location_id and id in(select id from stock_quant where product_id=sm.product_id and location_id=sm.location_id order by in_date,id limit 1);
		end if;
	end if;
	end loop;
	
	product_count = 0;
	quant_count = 0;
	total_qty = 0;
		
END;
$BODY$;

ALTER FUNCTION update_stock_quant()
    OWNER TO odoo;
