# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013-Today OpenERP SA (<http://www.openerp.com>).
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

from openerp import api
from openerp.osv import osv, fields
import uuid
import time
import product
import datetime

import openerp.addons.decimal_precision as dp

class landed_cost_template(osv.osv):
    _name = "landed.cost.template"
    _description = "Landed-cost Template"
    _columns = {
        'name': fields.char('Landed-cost Template', required=True),
        'website_description': fields.html('Description', translate=True),
        'landed_cost_line': fields.one2many('landed.cost.line', 'landed_cost_id', 'Landed Template Lines', copy=True),
        'note': fields.text('Terms and conditions'),
    }
  

class landed_cost_line(osv.osv):
    _name = "landed.cost.line"
    _description = "Landed Template Lines"
    _columns = {
        'landed_cost_id': fields.many2one('landed.cost.template', 'Landed-cost Template Reference', required=True, ondelete='cascade', select=True),
        'name': fields.text('Description', required=True, translate=True),
        'product_id': fields.many2one('product.product', 'Product', required=True),
        'price_unit': fields.float('Cost', required=True, digits_compute= dp.get_precision('Product Price')),
        'account_id': fields.many2one('account.account', 'Account', domain=[('type', '<>', 'view'), ('type', '<>', 'closed')]),
        'split_method': fields.selection(product.SPLIT_METHOD, string='Split Method'),
    
    }

    def on_change_product_id(self, cr, uid, ids, product, context=None):
        vals = {}
        product_obj = self.pool.get('product.product').browse(cr, uid, product, context=context)
        name = product_obj.name
        if product_obj.description_sale:
            name += '\n' + product_obj.description_sale
      
        vals.update({
            'price_unit': product_obj.lst_price,
            'name': name,
            'account_id': product_obj.property_account_expense and product_obj.property_account_expense.id or product_obj.categ_id.property_account_expense_categ.id,
            'split_method' : product_obj.split_method,
        })
        return {'value': vals}


    def write(self, cr, uid, ids, values, context=None):
        values = self._inject_quote_description(cr, uid, values, context)
        return super(landed_cost_line, self).write(cr, uid, ids, values, context=context)

