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
from openerp import http
from openerp.http import request
from openerp.tools import html_escape as escape
import json

class sale_plan_day_multi_map(osv.osv_memory):
    _name = 'sale.plan.day.multi.map'
    _description = 'Sale Plan Day Multi Map'
    _columns = {
        'date':fields.date("Date",required=True),        
        
    }

    _defaults = {
         'date': fields.datetime.now(),         
    }
    
    
    
    def open_google_map(self, cr, uid, ids, context=None):
        partner_ids = []
        data = self.read(cr, uid, ids, context=context)[0]
        plan_day_line_obj = self.pool.get('sale.plan.day.line')
        datas = {
             'ids': context.get('active_ids', []),
             'model': 'res.partner',
             'form': data
            }
        line_ids = plan_day_line_obj.search(cr, uid, [('line_id', 'in', datas['ids'])])
        for day_line_id in plan_day_line_obj.browse(cr,uid,line_ids,context=context):
            partner_ids.append(day_line_id.partner_id.id)
        partner_ids=datas['ids']
        if context.get('default_map'):
            if context.get('default_map') == 'customer_map':
                return {
                    'type': 'ir.actions.act_url',
                    'url': '/selected_partner_map?id=%s' % partner_ids,
                    'target': 'self',
                }
            else:    
                return {
                    'type': 'ir.actions.act_url',
                    'url': '/partners_polygon_map?id=%s' % partner_ids,
                    'target': 'self',
                }
                
    def open_map(self, cr, uid, ids, context=None):
        data = self.read(cr, uid, ids, context=context)[0]
        customer_target_obj = self.pool.get('res.partner')
        datas = {
             'ids': context.get('active_ids', []),
             'model': 'res.partner',
             'form': data
            }
        
        partner_ids=datas['ids']

        return {
            'type': 'ir.actions.act_url',
            'url': '/selected_partner_map?id=%s' % partner_ids,
            'target': 'self',
        }
    
    def open_polygon(self, cr, uid, ids, context=None):
        data = self.read(cr, uid, ids, context=context)[0]
        customer_target_obj = self.pool.get('res.partner')
        datas = {
                'ids': context.get('active_ids', []),
                'model': 'res.partner',
                'form': data
            }
        
        partner_ids=datas['ids']

        return {
            'type': 'ir.actions.act_url',
            'url': '/partners_polygon_map?id=%s' % partner_ids,
            'target': 'self',
        }
  
               
