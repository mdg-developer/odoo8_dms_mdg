-- FUNCTION: stock_movement_date_range()
-- select * from stock_movement_date_range('2022-12-01','2023-01-30','754','1396','1')
-- DROP FUNCTION stock_movement_date_range()

CREATE OR REPLACE FUNCTION stock_movement_date_range(
	from_date date,
	to_date date,
	product_ids text,
	location_ids text,
	branch_ids text)
    RETURNS TABLE(x_id integer, x_date timestamp without time zone, x_location_id integer, x_product_id integer, x_source character varying, x_uom numeric, x_from character varying, x_move_in_type character varying, x_transfer_in numeric, x_to character varying, x_move_out_type character varying, x_transfer_out numeric, x_balance numeric) 
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE PARALLEL UNSAFE
    ROWS 1000

AS $BODY$
BEGIN
    RETURN QUERY
select s.id as x_id,
   s.date as x_date,
   s.location_id as x_location_id,
   s.product_id as x_product_id,
   s.origin as x_source,
   s.product_uom as x_uom,
   move_in.team::character varying x_from,
   move_in.move_type::character varying x_move_in_type,
   floor(greatest(0,move_in.qty)) x_transfer_in,
    move_out.team::character varying x_to,
   move_out.move_type::character varying x_move_out_type,
   floor(greatest(0,move_out.qty)) x_transfer_out,
   floor(greatest(0,move_in.qty)) - floor(greatest(0,move_out.qty))
   as x_balance
   from
   (
       select tmp.id,tmp.location_id,tmp.product_id,tmp.date, tmp.origin, tmp.product_uom
       from
       (
           select s.id,s.location_id,s.product_id,s.date, s.origin,suom.factor product_uom
           from stock_move s,
           stock_location fl,
		   product_uom suom
           where s.state='done'
		   and s.product_uom=suom.id
           and s.location_id=fl.id
           and fl.usage!='supplier'
           and fl.usage!='customer'
           and fl.usage in ('internal','transit')
		   and ((s.date at time zone 'utc' )at time zone 'asia/rangoon')::date>='2023-01-01'
		   and ((s.date at time zone 'utc' )at time zone 'asia/rangoon')::date <= to_date
		   and s.product_id in (select unnest (string_to_array(product_ids, ',')::integer[]))
		   and fl.branch_id in (select unnest (string_to_array(branch_ids, ',')::integer[]))
		   and fl.id in (select unnest (string_to_array(location_ids, ',')::integer[])) 
           union
           select s.id,s.location_dest_id,s.product_id,s.date, s.origin, suom.factor product_uom
           from stock_move s,
           stock_location tl,
		   product_uom suom
           where s.state='done'
		   and s.product_uom=suom.id
           and s.location_dest_id=tl.id
           and tl.usage!='supplier'
           and tl.usage!='customer'
           and tl.usage in ('internal','transit')
		   and ((s.date at time zone 'utc' )at time zone 'asia/rangoon')::date>='2023-01-01'
		   and ((s.date at time zone 'utc' )at time zone 'asia/rangoon')::date <= to_date
		   and s.product_id in (select unnest (string_to_array(product_ids, ',')::integer[]))
		   and tl.branch_id in (select unnest (string_to_array(branch_ids, ',')::integer[]))
		   and tl.id in (select unnest (string_to_array(location_ids, ',')::integer[]))
       )tmp
	   where tmp.location_id in (select unnest (string_to_array(location_ids, ',')::integer[]))
   )
   s

   left join
   (
   select s.id,s.product_id,s.location_dest_id, s.product_qty as qty, suom.factor product_uom,
   s.date,split_part(fl.name, '-', 1) team,
   case when fl.usage in ('internal','transit') and tl.usage in ('internal','transit') and tl.scrap_location=false then 'transfer_in'
      when fl.usage='production' and tl.usage in ('internal','transit') then 'transfer_in'

   when fl.usage='supplier' and tl.usage in ('internal','transit') then 'purchase_in'
   when fl.usage='customer' and tl.usage in ('internal','transit') then 'sale_return_in'
   when fl.usage='inventory' and fl.name='Inventory loss' and tl.usage in ('internal','transit') then 'adjustment+'
   when fl.usage in ('internal','transit') and tl.usage='customer' then 'customer warehouse'
   when fl.usage in ('internal','transit') and tl.scrap_location=true then 'scrap_bin'
   when fl.usage in ('internal','transit') and tl.usage='inventory' and tl.name='Inventory loss' then 'for adjustment- (INV)'
   end as move_type
   from stock_move s,
   product_uom suom,
   stock_location fl,
   stock_location tl
   where s.state='done'
   and s.product_uom=suom.id
   and s.location_dest_id=tl.id
   and s.location_id=fl.id
   and tl.usage!='customer'
   and tl.usage!='supplier'
   and ((s.date at time zone 'utc' )at time zone 'asia/rangoon')::date>='2023-01-01'
   and ((s.date at time zone 'utc' )at time zone 'asia/rangoon')::date <= to_date
   and s.product_id in (select unnest (string_to_array(product_ids, ',')::integer[]))
   and tl.branch_id in (select unnest (string_to_array(branch_ids, ',')::integer[]))
   and (fl.id in (select unnest (string_to_array(location_ids, ',')::integer[])) or tl.id in (select unnest (string_to_array(location_ids, ',')::integer[])))	   
   ) move_in on move_in.product_id=s.product_id and move_in.location_dest_id=s.location_id
   and move_in.date=s.date and move_in.id=s.id and move_in.product_uom=s.product_uom

   left join
   (
   select s.id,s.product_id,s.location_id, s.product_qty as qty, suom.factor product_uom,
   s.date,split_part(tl.name, '-', 1) team,
   case when fl.usage in ('internal','transit') and tl.usage in ('internal','transit')and tl.scrap_location=false then 'transfer_out'
   when fl.usage in ('internal','transit') and tl.usage='production' then 'transfer_out'
   when fl.usage in ('internal','transit') and tl.usage='supplier' then 'purchase_return'
   when fl.usage in ('internal','transit') and tl.usage='customer' then 'sale_out'
   when fl.usage in ('internal','transit') and tl.scrap_location=true then 'scrap'
   when fl.usage in ('internal','transit') and tl.usage in ('internal','transit') and tl.name='Inventory loss' then 'adjustment-'
   when fl.usage='supplier' and tl.usage in ('internal','transit') then 'supplier warehouse'
   when fl.usage='inventory' and fl.name='Inventory loss' and tl.usage in ('internal','transit') then 'for adjustment+ (INV)'
   when fl.usage='customer' and tl.usage in ('internal','transit') then 'customer_return'
   end as move_type
   from stock_move s,
   product_uom suom,
   stock_location fl,
   stock_location tl
   where s.state='done'
   and s.product_uom=suom.id
   and s.location_dest_id=tl.id
   and s.location_id=fl.id
   and fl.usage!='supplier'
   and fl.usage!='customer'
   and ((s.date at time zone 'utc' )at time zone 'asia/rangoon')::date>='2023-01-01'	
   and s.product_id in (select unnest (string_to_array(product_ids, ',')::integer[]))
   and fl.branch_id in (select unnest (string_to_array(branch_ids, ',')::integer[]))
   and (fl.id in (select unnest (string_to_array(location_ids, ',')::integer[])) or tl.id in (select unnest (string_to_array(location_ids, ',')::integer[])))	   
   ) move_out on s.product_id=move_out.product_id and s.location_id=move_out.location_id
   and move_out.date=s.date and move_out.id=s.id and move_out.product_uom=s.product_uom
   union
   select si.id x_id,si.date x_date,si.location_id x_location_id,sil.product_id x_product_id,si.name x_source,
   sil.product_uom_id x_uom,'Inventory loss'::character varying x_from,
   'adjustment +'::character varying x_move_in_type,
   floor(greatest(0,sil.product_qty)) x_transfer_in,
   ''::character varying x_to,
   ''::character varying x_move_out_type,
   0 x_transfer_out,
   floor(greatest(0,sil.product_qty)) - 0
   as x_balance
	from stock_inventory si,stock_inventory_line sil,stock_location loc,product_product pp,product_template pt
	where si.id=sil.inventory_id
	and si.location_id=loc.id
	and sil.product_id=pp.id
	and pp.product_tmpl_id=pt.id
	and ((date at time zone 'utc' )at time zone 'asia/rangoon')::date = '2023-01-01'
	and si.state='done'
	and sil.product_id in (select unnest (string_to_array(product_ids, ',')::integer[]))
	and si.location_id in (select unnest (string_to_array(location_ids, ',')::integer[]))
   order by x_id,x_location_id,x_product_id,x_date,x_uom desc;
	END;
$BODY$;