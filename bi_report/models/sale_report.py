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

from openerp import tools
from openerp.osv import fields, osv

class sale_report(osv.osv):
    _inherit = "sale.report"
    _columns = {
       'group_id': fields.many2one('product.group','Group of Product', readonly=True),
       'main_group_id': fields.many2one('product.maingroup','Main Group of Product', readonly=True),
       'division_id': fields.many2one('product.division','Division of Product', readonly=True),
       'township_id': fields.many2one('res.township','Township', readonly=True),
       'branch_id': fields.many2one('res.branch','Branch', readonly=True),
       'product_id': fields.many2one('product.product','Product', readonly=True),
       'demarcation_id': fields.many2one('sale.demarcation','Demarcation', readonly=True),
       'state_id': fields.many2one('res.country.state','Region', readonly=True),
       'city': fields.many2one('res.city','City', readonly=True),
       'partner_id': fields.many2one('res.partner', 'Customer', readonly=True),
       'yearly_target_amount': fields.float('Yearly Target Amount', readonly=True),
       'monthly_target_amount': fields.float('Monthly Target Amount', readonly=True),
       'weekly_target_amount': fields.float('Weekly Target Amount', readonly=True),
       'invoiced_target': fields.float('Invoiced Target', readonly=True),
    }
    
    
    def _select(self):
        select_str = """
            WITH currency_rate (currency_id, rate, date_start, date_end) AS (
                    SELECT r.currency_id, r.rate, r.name AS date_start,
                        (SELECT name FROM res_currency_rate r2
                        WHERE r2.name > r.name AND
                            r2.currency_id = r.currency_id
                         ORDER BY r2.name ASC
                         LIMIT 1) AS date_end
                    FROM res_currency_rate r
                )
             SELECT min(l.id) as id,
                    l.product_id as product_id,
                    t.uom_id as product_uom,
                    sum(l.product_uom_qty / u.factor * u2.factor) as product_uom_qty,
                    sum(l.product_uom_qty * l.price_unit / cr.rate * (100.0-l.discount) / 100.0) as price_total,
                    count(*) as nbr,
                    s.date_order as date,
                    s.date_confirm as date_confirm,
                    s.partner_id as partner_id,
                    s.user_id as user_id,
                    s.company_id as company_id,
                    extract(epoch from avg(date_trunc('day',s.date_confirm)-date_trunc('day',s.create_date)))/(24*60*60)::decimal(16,2) as delay,
                    l.state,
                    t.categ_id as categ_id,
                    s.pricelist_id as pricelist_id,
                    s.project_id as analytic_account_id,
                    s.section_id as section_id,
                    s.branch_id as branch_id,
                    s.township as township_id,
                    s.state_id as state_id,
                    rp.city as city,
                    rp.demarcation_id as demarcation_id,
                    t.group as group_id,
                    t.main_group as main_group_id,
                    t.division as division_id,
                    ccs.yearly_target_amount,
                    ccs.monthly_target_amount,
                    ccs.weekly_target_amount,
                    ccs.invoiced_target
        """
        return select_str

    def _from(self):
        from_str = """
                sale_order_line l
                    join sale_order s on (l.order_id=s.id)
                    join res_partner rp on (rp.id=s.partner_id)
                    left join product_product p on (l.product_id=p.id)
                    left join product_template t on (p.product_tmpl_id=t.id)
                    left join product_uom u on (u.id=l.product_uom)
                    left join product_uom u2 on (u2.id=t.uom_id)
                    left join product_pricelist pp on (s.pricelist_id = pp.id)
                    join currency_rate cr on (cr.currency_id = pp.currency_id and
                        cr.date_start <= coalesce(s.date_order, now()) and
                        (cr.date_end is null or cr.date_end > coalesce(s.date_order, now())))
                    join crm_case_section ccs on (ccs.id=s.section_id)
                    
        """
        return from_str

    def _group_by(self):
        group_by_str = """
            GROUP BY l.product_id,
                    l.order_id,
                    t.uom_id,
                    t.categ_id,
                    s.date_order,
                    s.date_confirm,
                    s.partner_id,
                    s.user_id,
                    s.company_id,
                    l.state,
                    s.pricelist_id,
                    s.project_id,
                    s.section_id,
                    s.branch_id,
                    t.group,
                    t.main_group,
                    t.division,
                    s.township,
                    s.state_id,
                    rp.city,
                    rp.demarcation_id,
                    ccs.yearly_target_amount,
                    ccs.monthly_target_amount,
                    ccs.weekly_target_amount,
                    ccs.invoiced_target
        """
        return group_by_str

    def init(self, cr):
        # self._table = sale_report
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (
            %s
            FROM ( %s )
            %s
            )""" % (self._table, self._select(), self._from(), self._group_by()))


     