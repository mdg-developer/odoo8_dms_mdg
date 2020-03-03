-- View: public.sale_journal_raw_target_report

-- DROP VIEW public.sale_journal_raw_target_report;

CREATE OR REPLACE VIEW public.sale_journal_raw_target_report
 AS
 WITH team_target AS (
         SELECT (((((((stl.product_id || ''::text) || st.branch_id) || ''::text) || st.sale_team_id) || ''::text) || st.year::text) || ''::text) || st.month::text AS target_team_id,
            stl.product_uom_qty AS team_qty,
            stl.distribution_price AS team_distribution,
            stl.price_unit::double precision * stl.product_uom_qty AS team_target_amount
           FROM sales_target st,
            sales_target_line stl
          WHERE st.id = stl.sale_ids
        ), branch_target AS (
         SELECT (((((stbl.product_id || ''::text) || stb.branch_id) || ''::text) || stb.year::text) || ''::text) || stb.month::text AS target_branch_id,
            stbl.product_uom_qty AS branch_qty,
            stbl.distribution_price AS branch_distribution,
            stbl.price_unit::double precision * stbl.product_uom_qty AS branch_target_amount
           FROM sales_target_branch stb,
            sales_target_branch_line stbl
          WHERE stb.id = stbl.sale_ids
        )
 SELECT report.invoice_type,
    report.target_team_id,
    report.target_branch_id,
    report.date,
    report.account_id,
    report.account_description,
    report.payment_type,
    report.customer_id,
    report.frequency,
    report.township,
    report.branch,
    report.branch_region,
    report.outlet_type,
    report.tags,
    report.channel,
    report.customer_name,
    report.invoice_no,
    report.sale_team,
    report.product,
    report.item_description,
    report.qty,
    report.uom,
    report.unit_price,
    report.amount,
    report.big_uom_qty,
    report.small_uom_qty,
    report.discount_percent,
    report.discount_amount,
    report.promotion,
    report.sub_total,
    report.foc,
    report.principal_name,
    report.promotion_product,
    report.category,
    tt.team_qty,
    tt.team_distribution,
    tt.team_target_amount,
    bt.branch_qty,
    bt.branch_distribution,
    bt.branch_target_amount
   FROM ( SELECT
                CASE
                    WHEN av.type::text = 'out_refund'::text THEN 'Refund Invoice'::text
                    ELSE 'Sale Invoice'::text
                END AS invoice_type,
            (((((pp.id || ''::text) || branch.id) || ''::text) || cc.id) || ''::text) || to_char(av.date_invoice::timestamp with time zone, 'YYYYMM'::text)::integer AS target_team_id,
            (((pp.id || ''::text) || branch.id) || ''::text) || to_char(av.date_invoice::timestamp with time zone, 'YYYYMM'::text)::integer AS target_branch_id,
            av.origin AS so_no,
            av.comment AS additional_information,
            av.date_invoice AS date,
            acc.code AS account_id,
            acc.name AS account_description,
                CASE
                    WHEN av.payment_type::text = 'credit'::text THEN 'Credit'::text
                    ELSE 'Cash'::text
                END AS payment_type,
            rp.customer_code AS customer_id,
            ( SELECT plan_frequency.name
                   FROM plan_frequency
                  WHERE plan_frequency.id = rp.frequency_id) AS frequency,
            township.name AS township,
            branch.name AS branch,
            branch_region.name AS branch_region,
            outlet.name AS outlet_type,
            string_agg(p_categ.name::text, ','::text) AS tags,
            channel.name AS channel,
            rp.name AS customer_name,
            av.number AS invoice_no,
            cc.name AS sale_team,
            pp.name_template AS product,
            pt.description_sale AS item_description,
            avl.quantity AS qty,
            uom.name AS uom,
                CASE
                    WHEN avl.price_unit < 0::numeric THEN 0::numeric
                    ELSE avl.price_unit
                END AS unit_price,
            avl.quantity * avl.price_unit AS amount,
                CASE
                    WHEN avl.uos_id = pt.report_uom_id THEN avl.quantity
                    ELSE round(avl.quantity / round(1::numeric / (( SELECT product_uom.factor
                       FROM product_uom
                      WHERE product_uom.id = pt.report_uom_id)), 0), 2)
                END AS big_uom_qty,
                CASE
                    WHEN avl.uos_id = pt.uom_id THEN avl.quantity
                    ELSE avl.quantity * round(1::numeric / uom.factor, 0)
                END AS small_uom_qty,
            avl.discount AS discount_percent,
                CASE
                    WHEN avl.price_unit < 0::numeric THEN ('-1'::integer::numeric * avl.price_unit)::double precision
                    ELSE sum(avl.discount_amt)
                END AS discount_amount,
            rule.description AS promotion,
                CASE
                    WHEN avl.price_subtotal < 0::numeric THEN 0::numeric
                    ELSE avl.quantity *
                    CASE
                        WHEN avl.price_unit < 0::numeric THEN 0::numeric
                        ELSE avl.price_unit
                    END
                END AS sub_total,
                CASE
                    WHEN avl.foc = true THEN 'Y'::text
                    ELSE 'N'::text
                END AS foc,
            pm.name AS principal_name,
            ( SELECT replace(replace(array_agg(DISTINCT pp_1.name_template)::text, '{'::text, ''::text), '}'::text, ''::text) AS array_agg
                   FROM promos_rules_product_rel,
                    product_product pp_1
                  WHERE promos_rules_product_rel.promos_rules_id = avl.promotion_id AND pp_1.id = promos_rules_product_rel.product_id) AS promotion_product,
            ( SELECT pc.name
                   FROM product_category pc
                  WHERE pc.id = pt.categ_id) AS category
           FROM account_invoice av,
            account_invoice_line avl
             LEFT JOIN promos_rules rule ON avl.promotion_id = rule.id,
            account_account acc,
            res_partner rp,
            res_township township,
            res_branch branch
             LEFT JOIN res_branch_region branch_region ON branch_region.id = branch.branch_region_id,
            outlettype_outlettype outlet,
            sale_channel channel,
            crm_case_section cc,
            product_product pp,
            product_template pt,
            product_uom uom,
            product_maingroup pm,
            res_partner_res_partner_category_rel categ_rel,
            res_partner_category p_categ
          WHERE av.id = avl.invoice_id AND av.date_invoice > '2019-01-01'::date AND acc.id = avl.account_id AND (av.state::text <> ALL (ARRAY['draft'::character varying::text, 'cancel'::character varying::text])) AND rp.id = av.partner_id AND rp.township = township.id AND av.branch_id = branch.id AND outlet.id = rp.outlet_type AND channel.id = rp.sales_channel AND cc.id = av.section_id AND pp.id = avl.product_id AND pt.id = pp.product_tmpl_id AND avl.uos_id = uom.id AND pt.main_group = pm.id AND rp.id = categ_rel.partner_id AND categ_rel.category_id = p_categ.id AND pt.active = true AND (av.type::text = ANY (ARRAY['out_invoice'::character varying::text, 'out_refund'::character varying::text]))
          GROUP BY av.origin, pp.id, branch.id, cc.id, av.comment, pt.categ_id, av.date_invoice, acc.code, acc.name, av.payment_type, rp.customer_code, rp.frequency_id, township.name, branch.name, branch_region.name, outlet.name, channel.name, rp.name, av.number, cc.name, pp.name_template, pt.description_sale, avl.quantity, uom.name, pt.uom_id, pt.report_uom_id, uom.factor, avl.price_unit, avl.discount, avl.discount_amt, rule.description, pm.name, avl.price_subtotal, avl.foc, avl.promotion_id, pp.sequence, av.type, avl.id
          ORDER BY av.date_invoice, cc.name, rp.name, pp.sequence) report
     LEFT JOIN team_target tt ON report.target_team_id = tt.target_team_id
     LEFT JOIN branch_target bt ON report.target_branch_id = bt.target_branch_id;

ALTER TABLE public.sale_journal_raw_target_report
    OWNER TO odoo;

