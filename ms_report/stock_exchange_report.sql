-- View: public.exchange_detail_report

-- DROP VIEW public.exchange_detail_report;

CREATE OR REPLACE VIEW public.exchange_detail_report AS 
 SELECT ''::character varying AS account,
    ''::character varying AS account_des,
    st.total_value,
    rb.name AS branch,
    branch_region.name AS branch_region,
    categ.name AS product_category,
    ccs.name AS sales_team,
    channel.name AS channel,
    city.name AS city,
    rp.name AS customer,
    country_state.name AS customer_state,
    st.date::date AS date,
    st.name AS sen_no,
    st.transaction_id,
    st.exchange_type,
    pt.description AS item_description,
    outlet_type.name AS outlet_type,
    pm.name AS principal,
    pp.name_template AS product,
    line.trans_type AS type,
    line.product_qty AS qty,
    uom.name AS uom,
    ( SELECT product_uom.name
           FROM product_uom
          WHERE product_uom.id = pt.uom_id) AS base_uom,
    ( SELECT product_uom.name
           FROM product_uom
          WHERE product_uom.id = pt.report_uom_id) AS report_uom,
        CASE
            WHEN line.trans_type::text = 'In'::text AND line.uom_id = pt.report_uom_id THEN line.product_qty::numeric
            WHEN line.trans_type::text = 'In'::text AND line.uom_id <> pt.report_uom_id THEN round(line.product_qty::numeric / round(1::numeric / (( SELECT product_uom.factor
               FROM product_uom
              WHERE product_uom.id = pt.report_uom_id)), 0), 2)
            ELSE NULL::numeric
        END AS big_in_quantity,
        CASE
            WHEN line.trans_type::text = 'Out'::text AND line.uom_id = pt.uom_id THEN line.product_qty::numeric
            WHEN line.trans_type::text = 'Out'::text AND line.uom_id <> pt.uom_id THEN line.product_qty::numeric * round(1::numeric / uom.factor, 0)
            ELSE NULL::numeric
        END AS small_in_quantity,
        CASE
            WHEN line.trans_type::text = 'Out'::text AND line.uom_id = pt.report_uom_id THEN line.product_qty::numeric
            WHEN line.trans_type::text = 'Out'::text AND line.uom_id <> pt.report_uom_id THEN round(line.product_qty::numeric / round(1::numeric / (( SELECT product_uom.factor
               FROM product_uom
              WHERE product_uom.id = pt.report_uom_id)), 0), 2)
            ELSE NULL::numeric
        END AS big_out_quantity,
        CASE
            WHEN line.trans_type::text = 'In'::text AND line.uom_id = pt.uom_id THEN line.product_qty::numeric
            WHEN line.trans_type::text = 'In'::text AND line.uom_id <> pt.uom_id THEN line.product_qty::numeric * round(1::numeric / uom.factor, 0)
            ELSE NULL::numeric
        END AS small_out_quantity,
        CASE
            WHEN st.void_flag::text = 'none'::text THEN 'Done'::text
            ELSE 'Cancel'::text
        END AS void_status,
    township.name AS township,
    st.location_type,
    line.exp_date AS expired_date,
    line.batchno,
    line.note
   FROM product_transactions st,
    product_transactions_line line,
    product_product pp,
    crm_case_section ccs,
    res_branch rb,
    res_partner rp,
    product_uom uom,
    res_branch_region branch_region,
    product_template pt,
    product_category categ,
    sale_channel channel,
    res_city city,
    res_country_state country_state,
    outlettype_outlettype outlet_type,
    product_maingroup pm,
    res_township township
  WHERE st.id = line.transaction_id AND line.product_id = pp.id AND st.team_id = ccs.id AND st.branch_id = rb.id AND st.customer_id = rp.id AND uom.id = line.uom_id AND rb.branch_region_id = branch_region.id AND pp.product_tmpl_id = pt.id AND pt.categ_id = categ.id AND rp.sales_channel = channel.id AND rp.city = city.id AND rp.state_id = country_state.id AND rp.outlet_type = outlet_type.id AND pt.main_group = pm.id AND rp.township = township.id;

ALTER TABLE public.exchange_detail_report
  OWNER TO odoo;
