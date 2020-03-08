-- View: public.stock_journal_view
--select * from stock_journal_view limit 1
-- DROP VIEW public.stock_journal_view;

CREATE OR REPLACE VIEW public.stock_journal_view
 AS
 select *,
	case when f.move_type in ('sale_out','sale_return') then f.x_qty end as sales,
	case when f.move_type in ('purchase_in','purchase_return') then f.x_qty end as purchase,
	case when f.move_type in ('transfer_in','sale_return_in') then f.x_qty end as transfer_in,
	case when f.move_type='transfer_out' then f.x_qty end as transfer_out,
	case when f.move_type like '%adjustment%' then f.x_qty end as adjustment
	from
	(
	select m.x_id id,
	w.name as warehouse,
	((m.x_date at time zone 'utc') at time zone 'asia/rangoon')::date as date,
	ll.complete_name as location,
	--ll.id as x_location_id,
	(select name from res_branch where id=ll.branch_id) as branch,
	pp.name as product,
	--pp.id as x_product_id,
	pp.default_code as product_code,
	pp.categ as product_category,
	pp.maingroup as product_maingroup,
	pp.pgroup as product_group,
	m.x_source source,    
	case when m.x_source like 'GIN%' then (select internal_ref from good_issue_note where name =m.x_source)
	when m.x_source like 'SO%' then  (select (select code from res_township where id in (select  township from res_partner where id= so.partner_id)) || ','||tb_ref_no from sale_order so where name =m.x_source)
	when m.x_source like 'MSRN%' then  (select (case when internal_ref is null then '' else internal_ref end ) || ' ' ||  (case when internal_ref_note is null then '' else internal_ref_note end ) from stock_return_manual where name =m.x_source)  
	end as ref,
	case when m.x_from is null then m.x_to
	when m.x_to is null then m.x_from
	end as from_to,
	case when m.x_move_in_type is null then m.x_move_out_type
	when m.x_move_out_type is null then m.x_move_in_type
	end as move_type,
	d.opening as opening,
	d.qty as x_qty,
	d.closing as closing
	from stock_movement() m
	left join
	(
	select t.name,p.default_code,p.id,pc.name as categ,pm.name as maingroup, pg.name as pgroup
	from product_product p,
	product_template t,
	product_category pc,
	product_maingroup pm,
	product_group pg
	where p.product_tmpl_id=t.id
	and t.main_group=pm.id
	and t.group=pg.id
	and t.categ_id=pc.id
	)pp on m.x_product_id=pp.id
	left join
	(
	select sl.name as complete_name,sl.id,sl.branch_id
	from stock_location sl
	)ll on m.x_location_id=ll.id
	left join
	stock_warehouse as w on w.lot_stock_id=m.x_location_id
	left join
	(
	SELECT x_id,x_location_id, x_product_id, x_date
	   , sum(x_balance) OVER (PARTITION BY x_location_id, x_product_id ORDER BY x_date,x_uom) - x_balance as opening,
	   x_balance as qty, sum(x_balance) OVER (PARTITION BY x_location_id, x_product_id ORDER BY x_date,x_uom) as closing
	FROM   stock_movement()
	ORDER  BY x_product_id, x_location_id, x_date
	) d on m.x_location_id=d.x_location_id and m.x_product_id=d.x_product_id  and m.x_date=d.x_date and m.x_id = d.x_id
	order by m.x_location_id,m.x_product_id,m.x_date,m.x_uom
	)f
	where date>='2019-01-01';

ALTER TABLE public.stock_journal_view
    OWNER TO odoo;

