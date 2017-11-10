# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp.osv import fields, osv
from openerp.addons.decimal_precision import decimal_precision as dp
class account_invoice_report(osv.osv):
    _inherit = 'account.invoice.report'
    _columns = {
            'invoice_no':fields.char('Invoice'),
        'price_unit': fields.float('Unit Price', digits_compute= dp.get_precision('Product Price')),
        'sale_amount':fields.float('Sale Amount', digits_compute= dp.get_precision('Product Price')),
      'price_subtotal': fields.float('Net Sale Amount', digits_compute= dp.get_precision('Product Price')),
        'discount_amt': fields.float('Discount Amount', digits_compute= dp.get_precision('Product Price')),
        'product_type': fields.char('Product Type', digits_compute= dp.get_precision('Product Price')),
        'weekly_target_amount': fields.float('Weekly Target Amount', digits_compute= dp.get_precision('Product Price')),
        'monthly_target_amount': fields.float('Monthly Target Amount', digits_compute= dp.get_precision('Product Price')),
        'yearly_target_amount': fields.float('Yearly Target Amount', digits_compute= dp.get_precision('Product Price')),
    }
    _depends = {
        'account.invoice.line': ['price_unit','price_subtotal','discount_amt'],
    }

    def _select(self):
        return  super(account_invoice_report, self)._select() + ", sub.price_unit as price_unit, (sub.price_subtotal + sub.discount_amt) as sale_amount, sub.discount_amt as discount_amt,sub.price_subtotal ,sub.product_type as product_type,sub.number as invoice_no,COALESCE(sub.weekly_target_amount,0) as weekly_target_amount,COALESCE(sub.monthly_target_amount,0) as monthly_target_amount,COALESCE(sub.yearly_target_amount,0) as yearly_target_amount"

#     def _sub_select(self):
#         return  super(account_invoice_report, self)._sub_select() + ", ai.number,ail.price_unit,ail.discount_amt,ail.price_subtotal,pt.type as product_type"
    def _sub_select(self):
        select_str = """
                SELECT min(ail.id) AS id,
                    ai.date_invoice AS date,
                    ail.product_id, ai.partner_id, ai.payment_term, ai.period_id,
                    u2.name AS uom_name,
                    ai.currency_id, ai.journal_id, ai.fiscal_position, ai.user_id, ai.company_id,
                    count(ail.*) AS nbr,
                    ai.type, ai.state, pt.categ_id, ai.date_due, ai.account_id, ail.account_id AS account_line_id,
                    ai.partner_bank_id,
                    SUM(CASE
                         WHEN ai.type::text = ANY (ARRAY['out_refund'::character varying::text, 'in_invoice'::character varying::text])
                            THEN (- ail.quantity) / u.factor * u2.factor
                            ELSE ail.quantity / u.factor * u2.factor
                        END) AS product_qty,
                    SUM(CASE
                         WHEN ai.type::text = ANY (ARRAY['out_refund'::character varying::text, 'in_invoice'::character varying::text])
                            THEN - ail.price_subtotal
                            ELSE ail.price_subtotal
                        END) AS price_total,
                    CASE
                     WHEN ai.type::text = ANY (ARRAY['out_refund'::character varying::text, 'in_invoice'::character varying::text])
                        THEN SUM(- ail.price_subtotal)
                        ELSE SUM(ail.price_subtotal)
                    END / CASE
                           WHEN SUM(ail.quantity / u.factor * u2.factor) <> 0::numeric
                               THEN CASE
                                     WHEN ai.type::text = ANY (ARRAY['out_refund'::character varying::text, 'in_invoice'::character varying::text])
                                        THEN SUM((- ail.quantity) / u.factor * u2.factor)
                                        ELSE SUM(ail.quantity / u.factor * u2.factor)
                                    END
                               ELSE 1::numeric
                          END AS price_average,
                    CASE
                     WHEN ai.type::text = ANY (ARRAY['out_refund'::character varying::text, 'in_invoice'::character varying::text])
                        THEN - ai.residual
                        ELSE ai.residual
                    END / (SELECT count(*) FROM account_invoice_line l where invoice_id = ai.id) *
                    count(*) AS residual,
                    ai.commercial_partner_id as commercial_partner_id,
                    partner.country_id,ai.section_id,
                    ai.number,ail.price_unit,ail.discount_amt,ail.price_subtotal,pt.type as product_type,sum(team.weekly_target_amount) as weekly_target_amount,sum(team.monthly_target_amount) as monthly_target_amount, sum(team.yearly_target_amount) as yearly_target_amount
        """
        return select_str
    
    def _from(self):
        from_str = """
                FROM account_invoice_line ail
                JOIN account_invoice ai ON ai.id = ail.invoice_id
                JOIN res_partner partner ON ai.commercial_partner_id = partner.id
                LEFT JOIN product_product pr ON pr.id = ail.product_id
                left JOIN product_template pt ON pt.id = pr.product_tmpl_id
                LEFT JOIN product_uom u ON u.id = ail.uos_id
                LEFT JOIN product_uom u2 ON u2.id = pt.uom_id
                LEFT JOIN crm_case_section team on ai.section_id=team.id
        """
        return from_str
    def _group_by(self):
        return super(account_invoice_report, self)._group_by() + ", ai.number,ail.price_unit,ail.discount_amt,ail.price_subtotal,pt.type"

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
