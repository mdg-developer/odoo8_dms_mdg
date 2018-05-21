-- drop FUNCTION stock_movement();
-- select * from stock_movement();
CREATE OR REPLACE FUNCTION stock_movement() 
RETURNS TABLE (
			x_id integer,
			x_date timestamp without time zone,
			x_location_id integer,
			x_product_id integer,
			x_source character varying,
			x_move_in_type character varying,
			x_transfer_in numeric,
			x_move_out_type character varying,
			x_transfer_out numeric,
			x_balance numeric
		) AS $$
BEGIN
    RETURN QUERY	
	select s.id as x_id,
	s.date as x_date,
	s.location_id as x_location_id,
	s.product_id as x_product_id,
	s.origin as x_source,
	move_in.move_type::character varying x_move_in_type,
	floor(greatest(0,move_in.qty)) x_transfer_in,
	move_out.move_type::character varying x_move_out_type,
	floor(greatest(0,move_out.qty)) x_transfer_out,
	floor(greatest(0,move_in.qty)) - floor(greatest(0,move_out.qty))
	as x_balance
	from 
	(
		select tmp.id,tmp.location_id,tmp.product_id,tmp.date, tmp.origin
		from
		(
			select s.id,s.location_id,s.product_id,s.date, s.origin
			from stock_move s,
			stock_location fl
			where s.state='done'
			and s.location_id=fl.id
			and fl.usage!='supplier'
			and fl.usage!='customer'
			union
			select s.id,s.location_dest_id,s.product_id,s.date, s.origin
			from stock_move s,
			stock_location tl
			where s.state='done'
			and s.location_dest_id=tl.id
			and tl.usage!='supplier'
			and tl.usage!='customer'
		)tmp
	)
	s	

	left join
	(
	select s.id,s.product_id,s.location_dest_id,s.product_qty as qty, s.date,
	case when fl.usage='internal' and tl.usage='internal' and tl.scrap_location=false then 'transfer_in'
	when fl.usage='supplier' and tl.usage='internal' then 'purchase_in'
	when fl.usage='customer' and tl.usage='internal' then 'sale_return_in'
	when fl.usage='inventory' and fl.name='Inventory loss' and tl.usage='internal' then 'adjustment+'
	when fl.usage='internal' and tl.usage='customer' then 'customer warehouse'
	when fl.usage='internal' and tl.scrap_location=true then 'scrap_bin'
	when fl.usage='internal' and tl.usage='inventory' and tl.name='Inventory loss' then 'for adjustment- (INV)'
	end as move_type
	from stock_move s,
	stock_location fl,
	stock_location tl
	where s.state='done'
	and s.location_dest_id=tl.id
	and s.location_id=fl.id
	and tl.usage!='customer'
	and tl.usage!='supplier'
	) move_in on move_in.product_id=s.product_id and move_in.location_dest_id=s.location_id
	and move_in.date=s.date and move_in.id=s.id

	left join
	(
	select s.id,s.product_id,s.location_id,s.product_qty as qty, s.date,
	case when fl.usage='internal' and tl.usage='internal' and tl.scrap_location=false then 'transfer_out'
	when fl.usage='internal' and tl.usage='supplier' then 'purchase_return'
	when fl.usage='internal' and tl.usage='customer' then 'sale_out'
	when fl.usage='internal' and tl.scrap_location=true then 'scrap'
	when fl.usage='internal' and tl.usage='inventory' and tl.name='Inventory loss' then 'adjustment-'
	when fl.usage='supplier' and tl.usage='internal' then 'supplier warehouse'
	when fl.usage='inventory' and fl.name='Inventory loss' and tl.usage='internal' then 'for adjustment+ (INV)'
	when fl.usage='customer' and tl.usage='internal' then 'customer_return'
	end as move_type
	from stock_move s,
	stock_location fl,
	stock_location tl
	where s.state='done'
	and s.location_dest_id=tl.id
	and s.location_id=fl.id
	and fl.usage!='supplier'
	and fl.usage!='customer'
	) move_out on s.product_id=move_out.product_id and s.location_id=move_out.location_id
	and move_out.date=s.date and move_out.id=s.id
	order by s.id,s.location_id,s.product_id,s.date
    ;
END;
$$ LANGUAGE plpgsql;

