-- View: public.stock_journal

-- DROP VIEW public.stock_journal;

CREATE OR REPLACE VIEW public.stock_journal
 AS
 SELECT branch.name AS branch,
    sq.in_date::date AS stock_date,
    loc.name AS stock_location,
    pp.name_template AS product,
    category.name AS product_category,
    region.name,
	loc_group.name location_group,
    sum(sq.qty) AS small_uom_qty,
    sum(sq.qty) / round(1::numeric / uom.factor)::double precision AS big_uom_qty
   FROM stock_quant sq,
    product_product pp,
    product_template pt,
    product_uom uom,
    stock_location loc,
    res_branch branch,
    product_category category,
    res_branch_region region,
	stock_location_group loc_group
  WHERE sq.product_id = pp.id AND pp.product_tmpl_id = pt.id AND pt.report_uom_id = uom.id AND sq.location_id = loc.id AND loc.branch_id = branch.id AND branch.branch_region_id = region.id AND pt.categ_id = category.id
  AND loc.stock_location_group_id=loc_group.id
  GROUP BY pp.name_template, uom.factor, sq.in_date, loc.name, branch.name, category.name, region.name,loc_group.name
  ORDER BY pp.name_template;

ALTER TABLE public.stock_journal
    OWNER TO odoo;