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
import datetime

import openerp.addons.decimal_precision as dp

class sale_order(osv.osv):
    _inherit = 'stock.landed.cost'

    _columns = {
        
        'template_id': fields.many2one('landed.cost.template', 'Landed-cost Template', states={'done': [('readonly', True)]}, copy=False),
     
    }
  

    def onchange_template_id(self, cr, uid, ids, template_id,  context=None):
        if not template_id:
            return True
        
        lines = [(5,)]
        landed_cost_template = self.pool.get('landed.cost.template').browse(cr, uid, template_id, context=context)
        for line in landed_cost_template.landed_cost_line:
            print 'tttt',line
            res = self.pool.get('landed.cost.line').on_change_product_id(cr, uid,ids,line.product_id.id, context)
            data = res.get('value', {})

            data.update({
                'name': line.name,
                'product_id': line.product_id.id,
                'price_unit': line.price_unit,
                'account_id': line.account_id.id,
                'split_method':line.split_method,
            })
            lines.append((0, 0, data))
        
        data = {'cost_lines': lines, }
        print 'data',data
        return {'value': data}

    

