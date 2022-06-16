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
    }
    _depends = {
        'account.invoice.line': ['price_unit','price_subtotal','discount_amt'],
    }

    def _select(self):
        return  super(account_invoice_report, self)._select() + ", sub.price_unit as price_unit, (sub.price_subtotal + sub.discount_amt) as sale_amount, sub.discount_amt as discount_amt,sub.price_subtotal ,sub.product_type as product_type,sub.number as invoice_no"

    def _sub_select(self):
        return  super(account_invoice_report, self)._sub_select() + ", ai.number,ail.price_unit,ail.discount_amt,ail.price_subtotal,pt.type as product_type"

    def _group_by(self):
        return super(account_invoice_report, self)._group_by() + ", ai.number,ail.price_unit,ail.discount_amt,ail.price_subtotal,pt.type"

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
