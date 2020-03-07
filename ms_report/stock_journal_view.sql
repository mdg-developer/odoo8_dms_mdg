-- View: public.stock_journal_view
--select * from stock_journal_view limit 1
-- DROP VIEW public.stock_journal_view;

CREATE OR REPLACE VIEW public.stock_journal_view
 AS
 SELECT sm.id,so.name AS sale_order,
    sp.name AS do_number,
    timezone('asia/rangoon'::text, timezone('utc'::text, sp.date))::date AS do_date,
    timezone('asia/rangoon'::text, timezone('utc'::text, so.date_order))::date AS so_date,
    timezone('asia/rangoon'::text, timezone('utc'::text, sm.date))::date AS stock_move_date,
    age(sp.date, so.date_order) AS duration_info,
    wh.code AS warehouse,
    ( SELECT replace(stock_location.complete_name::text, 'Physical Locations /'::text, ''::text) AS replace
           FROM stock_location
          WHERE stock_location.id = sm.location_id) AS from_location,
    ( SELECT replace(stock_location.complete_name::text, 'Partner Locations /'::text, ''::text) AS replace
           FROM stock_location
          WHERE stock_location.id = sm.location_dest_id) AS destination,
    rp.name AS customer,
    so.customer_code,
    ccs.name AS sales_team,
    oo.name AS outlet_type,
    spt.name AS picking_type,
    rb.name AS branch,
    region.name AS region,
    pp.default_code AS product_code,
    pp.name_template AS product_name,
	categ.name AS category,
	maingroup.name AS main_group,
    sm.product_uom_qty,
    uom.name AS uom,
    sm.price_unit AS product_cost,
    sm.product_uom_qty::double precision * sm.price_unit AS sub_total,
    so.state AS so_status,
    sp.state AS do_status,
    sm.state AS stock_move_status,
	sq.in_date,
	sq.qty,
	sq.qty / round(1::numeric /
(select uom.factor FROM product_uom  where id = pt.report_uom_id))
as big_uom_qty ,
(select uom.name FROM product_uom  where id = pt.report_uom_id) as big_uom,
sq.cost
   FROM stock_picking sp
     LEFT JOIN stock_picking_type spt ON sp.picking_type_id = spt.id
     LEFT JOIN sale_order so ON sp.origin::text = so.name::text
     LEFT JOIN stock_move sm ON sp.id = sm.picking_id
     LEFT JOIN res_partner rp ON so.partner_id = rp.id
     LEFT JOIN product_product pp ON sm.product_id = pp.id
	 lEFT JOIN product_template pt ON pp.product_tmpl_id = pt.id 
	 lEFT JOIN product_category categ ON pt.categ_id = categ.id 
	 lEFT JOIN product_maingroup maingroup ON pt.main_group = maingroup.id 
     LEFT JOIN product_uom uom ON uom.id = sm.product_uom
     LEFT JOIN crm_case_section ccs ON ccs.id = so.section_id
     LEFT JOIN res_branch rb ON rb.id = so.branch_id
     LEFT JOIN res_branch_region region ON region.id = rb.branch_region_id
     LEFT JOIN outlettype_outlettype oo ON oo.id = rp.outlet_type
     LEFT JOIN stock_warehouse wh ON wh.id = spt.warehouse_id 
	 LEFT JOIN stock_quant_move_rel rel on rel.move_id = sm.id
	 LEFT JOIN stock_quant sq on sq.id= rel.quant_id
  WHERE so.state::text <> ALL (ARRAY['draft'::character varying, 'cancel'::character varying]::text[]) 
  and sp.date >= '2019-01-01' 
  and sm.date >= '2019-01-01' 
  and so.date_order >= '2019-01-01' 
  ORDER BY sp.id;

ALTER TABLE public.stock_journal_view
    OWNER TO odoo;

