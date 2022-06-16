-- View: public.product_cat_account_view

-- DROP VIEW public.product_cat_account_view;

CREATE OR REPLACE VIEW public.product_cat_account_view AS 
 WITH category_acct AS (
         SELECT replace(ir_property.value_reference::text, 'account.account,'::text, ''::text)::integer AS account_id,
            replace(ir_property.res_id::text, 'product.category,'::text, ''::text)::integer AS cat_id
           FROM ir_property
          WHERE ir_property.name::text = 'property_stock_account_output_categ'::text AND ir_property.res_id::text ~~ '%product.category%'::text
        )
 SELECT pp.id,
    pp.default_code,
    pp.name_template,
    pt.description,
    ac.account_id,
    aa.name
   FROM product_product pp,
    product_template pt,
    category_acct ac,
    account_account aa
  WHERE pp.product_tmpl_id = pt.id AND ac.cat_id = pt.categ_id AND ac.account_id = aa.id AND pt.sale_ok = true AND pt.active = true
  ORDER BY pp.id;

ALTER TABLE public.product_cat_account_view
  OWNER TO odoo;


-- View: pre_directsale_with_promotion

-- DROP VIEW pre_directsale_with_promotion;

CREATE OR REPLACE VIEW pre_directsale_with_promotion AS 
 SELECT presale_directsale.name,
    presale_directsale.product_id,
    presale_directsale.product_uos_qty,
    presale_directsale.price_unit,
    presale_directsale.sub_total,
    presale_directsale.uom_id,
    presale_directsale.foc,
    presale_directsale.discount_amt,
    presale_directsale.m_status,
    presale_directsale.sale_team,
    presale_directsale.partner_id,
    presale_directsale.date,
    presale_directsale.customer_code,
    presale_directsale.pro_id
   FROM ( SELECT a.name,
            a.product_id,
            a.product_uos_qty,
            a.price_unit,
            a.sub_total,
            a.uom_id,
            a.foc,
            a.discount_amt,
            a.m_status,
            a.sale_team,
            a.partner_id,
            a.date,
            a.customer_code,
            b.pro_id
           FROM ( SELECT mso.name,
                    msol.product_id,
                    msol.product_uos_qty,
                    msol.price_unit,
                    msol.sub_total,
                    msol.uom_id,
                    msol.foc,
                    msol.discount_amt,
                    mso.m_status,
                    mso.sale_team,
                    mso.partner_id,
                    mso.date,
                    mso.customer_code
                   FROM mobile_sale_order mso,
                    mobile_sale_order_line msol
                  WHERE msol.order_id = mso.id AND mso.m_status::text = 'done'::text AND mso.void_flag::text = 'none'::text) a
             LEFT JOIN ( SELECT mso.name,
                    msol.product_id,
                    msol.product_uos_qty,
                    msol.price_unit,
                    msol.sub_total,
                    msol.uom_id,
                    msol.foc,
                    msol.discount_amt,
                    mso.m_status,
                    mso.sale_team,
                    mso.partner_id,
                    mso.date,
                    mso.customer_code,
                    promo.pro_id
                   FROM mobile_sale_order_line msol,
                    mobile_sale_order mso,
                    mso_promotion_line promo,
                    promos_rules_product_rel rel
                  WHERE msol.order_id = mso.id AND promo.promo_line_id = mso.id AND rel.promos_rules_id = promo.pro_id AND rel.product_id = msol.product_id AND mso.m_status::text = 'done'::text AND mso.void_flag::text = 'none'::text) b ON a.name::text = b.name::text AND a.product_id = b.product_id
        UNION
         SELECT a.name,
            a.product_id,
            a.product_uos_qty,
            a.price_unit,
            a.sub_total,
            a.uom_id,
            a.foc,
            a.discount_amt,
            a.m_status,
            a.sale_team,
            a.partner_id,
            a.date,
            a.customer_code,
            b.pro_id
           FROM ( SELECT pso.name,
                    psol.product_id,
                    psol.product_uos_qty,
                    psol.price_unit,
                    psol.sub_total,
                    psol.uom_id,
                    psol.foc,
                    psol.discount_amt,
                    pso.m_status,
                    pso.sale_team,
                    pso.partner_id,
                    pso.date,
                    pso.customer_code
                   FROM pre_sale_order_line psol,
                    pre_sale_order pso
                  WHERE psol.order_id = pso.id AND pso.m_status::text = 'done'::text AND pso.void_flag::text = 'none'::text) a
             LEFT JOIN ( SELECT pso.name,
                    psol.product_id,
                    psol.product_uos_qty,
                    psol.price_unit,
                    psol.sub_total,
                    psol.uom_id,
                    psol.foc,
                    psol.discount_amt,
                    pso.m_status,
                    pso.sale_team,
                    pso.partner_id,
                    pso.date,
                    pso.customer_code,
                    promo.pro_id
                   FROM pre_sale_order_line psol,
                    pre_sale_order pso,
                    pre_promotion_line promo,
                    promos_rules_product_rel rel
                  WHERE psol.order_id = pso.id AND promo.promo_line_id = pso.id AND rel.promos_rules_id = promo.pro_id AND rel.product_id = psol.product_id AND pso.m_status::text = 'done'::text AND pso.void_flag::text = 'none'::text) b ON a.name::text = b.name::text AND a.product_id = b.product_id) presale_directsale;

ALTER TABLE pre_directsale_with_promotion
  OWNER TO odoo;
-- View: promotion_sale_temp_report

-- DROP VIEW promotion_sale_temp_report;

CREATE OR REPLACE VIEW public.promotion_sale_temp_report AS 
 SELECT a.account_name,
    a.account_desc,
    a.customer_id,
    a.customer,
    a.invoice_no,
    a.sale_team,
    a.default_code,
    a.product_id,
    a.product_desc,
    a.description_sale,
    a.qty,
    a.foc,
    a.discount_amt,
    a.uom,
    a.unit_price,
    a.net_total,
    a.discount,
    a.sub_total,
    a.promotion_des,
    a.promotion_id,
    a.branch_id,
    a.date_invoice,
    a.team_id,
    a.payment_type,
    replace(replace(a.promotion_des::text, '{'::text, ''::text), '}'::text, ''::text) AS promotion
   FROM ( SELECT DISTINCT (aa.code::text || '-'::text) || aa.name::text AS account_name,
            aa.name AS account_desc,
            partner.customer_code AS customer_id,
            partner.name AS customer,
            ai.number AS invoice_no,
            sale_team.name AS sale_team,
            product.default_code,
            product.id AS product_id,
            product.name_template AS product_desc,
            pt.description_sale,
            invoice_line.quantity AS qty,
                CASE
                    WHEN invoice_line.foc = true THEN 'Y'::text
                    ELSE 'N'::text
                END AS foc,
         --   invoice_line.discount_amt,
            (CASE WHEN invoice_line.price_subtotal < 0 THEN -1 * invoice_line.price_subtotal ELSE invoice_line.discount_amt END) as discount_amt,
            uom.name AS uom,
            --invoice_line.price_unit AS unit_price,
            (CASE WHEN invoice_line.price_unit < 0 THEN 0 ELSE invoice_line.price_unit END) AS unit_price,
            invoice_line.price_subtotal AS net_total,
            invoice_line.discount,
            invoice_line.price_subtotal::double precision + (CASE WHEN invoice_line.price_subtotal < 0 THEN -1 * invoice_line.price_subtotal ELSE invoice_line.discount_amt END) AS sub_total,
            ( SELECT array_agg(DISTINCT promos_rules.description) AS array_agg
                   FROM promos_rules
                  WHERE promos_rules.id = ANY (array_agg(DISTINCT promodata.pro_id))) AS promotion_des,
            array_agg(DISTINCT promodata.pro_id) AS promotion_id,
            ai.branch_id,
            ai.date_invoice,
            sale_team.id AS team_id,
                CASE
                    WHEN ai.payment_type::text = 'credit'::text THEN 'Credit'::text
                    ELSE 'Cash'::text
                END AS payment_type
           FROM sale_order so,
            account_invoice ai,
            account_invoice_line invoice_line,
            pre_directsale_with_promotion promodata,
            account_account aa,
            res_partner partner,
            crm_case_section sale_team,
            product_product product,
            product_uom uom,
            product_template pt
          WHERE so.name::text = ai.origin::text AND pt.id = product.product_tmpl_id AND ai.id = invoice_line.invoice_id AND promodata.name::text = so.tb_ref_no::text AND invoice_line.product_id = promodata.product_id AND aa.id = invoice_line.account_id AND so.partner_id = partner.id AND ai.section_id = sale_team.id AND invoice_line.product_id = product.id AND invoice_line.uos_id = uom.id
          GROUP BY aa.name, aa.code, partner.customer_code, partner.name, ai.number, sale_team.name, product.default_code, pt.description_sale, product.id, invoice_line.quantity, invoice_line.foc, invoice_line.discount_amt, uom.name, invoice_line.price_unit, invoice_line.price_subtotal, invoice_line.discount, ai.branch_id, ai.date_invoice, ai.payment_type, sale_team.id
          ORDER BY ai.number) a;

ALTER TABLE public.promotion_sale_temp_report
  OWNER TO odoo;
