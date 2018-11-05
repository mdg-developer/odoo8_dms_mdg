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
import time
from openerp.osv import fields, osv

class batching_plant_multi(osv.osv_memory):
    _name = 'product.price.multi'
    _description = 'Product Price Multi'
    _columns = {
        
        'default_price_margin': fields.float("Default Price Margin")
    }

    _defaults = {
         'default_price_margin': 0.0,         
    }

    def print_report(self, cr, uid, ids, context=None):
        data = self.browse(cr, uid, ids, context=context)[0]
        product_obj = self.pool.get('product.template')
        datas = {
             'ids': context.get('active_ids', []),
             'model': 'product.template',
             'form': data
            }
        product_tmp_ids=datas['ids']
        default_price_margin = data.default_price_margin
        for tmp_id in product_obj.browse(cr,uid,product_tmp_ids,context=context):
            if default_price_margin != 0:
                price = margin = 0
                list_price = tmp_id.list_price
                margin = list_price * ((default_price_margin or 0.0) / 100.0)
                price = list_price + margin
                product_obj.write(cr, uid, tmp_id.id,{'list_price':price},context=context)    
