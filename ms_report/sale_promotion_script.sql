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


-- View: public.pre_directsale_with_promotion

-- DROP VIEW public.pre_directsale_with_promotion;

CREATE OR REPLACE VIEW public.pre_directsale_with_promotion AS 
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
            pso.customer_code,
            promo.pro_id
           FROM pre_sale_order_line psol,
            pre_sale_order pso,
            pre_promotion_line promo
          WHERE psol.order_id = pso.id AND promo.promo_line_id = pso.id AND pso.m_status::text = 'done'::text AND pso.void_flag::text = 'none'::text AND pso.is_convert = true
        UNION
         SELECT mso.name,
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
            mso_promotion_line promo
          WHERE msol.order_id = mso.id AND promo.promo_line_id = mso.id AND mso.m_status::text = 'done'::text AND mso.void_flag::text = 'none'::text) presale_directsale;

ALTER TABLE public.pre_directsale_with_promotion
  OWNER TO odoo;


-- View: public.promotion_sale_temp_report

-- DROP VIEW public.promotion_sale_temp_report;

CREATE OR REPLACE VIEW public.promotion_sale_temp_report AS 
SELECT DISTINCT (aa.code::text || '-'::text) || aa.name::text as account_name,
    aa.name AS account_desc,
    partner.customer_code AS customer_id,
    partner.name AS customer,
    ai.number AS invoice_no,
    sale_team.name AS sale_team,
    product.default_code AS default_code,
    product.id as product_id,
    product.name_template AS product_desc,
    pt.description_sale,
    invoice_line.quantity AS qty,
     
    CASE WHEN invoice_line.foc=True THEN 'Y'
            ELSE 'N'
       END as foc,
    invoice_line.discount_amt,
    uom.name AS uom,
    invoice_line.price_unit AS unit_price,
    invoice_line.price_subtotal AS sub_total,
    promotion.description AS promotion,
    promotion.id as promotion_id,
    ai.branch_id,
    ai.date_invoice,
    sale_team.id team_id
   FROM sale_order so,
    account_invoice ai,
    account_invoice_line invoice_line,
    pre_directsale_with_promotion promodata,
    account_account aa,
    res_partner partner,
    crm_case_section sale_team,
    product_product product,
    product_uom uom,
    product_template pt,
    promos_rules promotion
  WHERE so.name::text = ai.origin::text AND pt.id =product.product_tmpl_id AND ai.id = invoice_line.invoice_id AND promodata.name::text = so.tb_ref_no::text AND invoice_line.product_id = promodata.product_id AND aa.id = invoice_line.account_id AND so.partner_id = partner.id AND so.section_id = sale_team.id AND invoice_line.product_id = product.id AND invoice_line.uos_id = uom.id AND promotion.id = promodata.pro_id
  ORDER BY ai.number;

  
ALTER TABLE public.promotion_sale_temp_report
  OWNER TO odoo;