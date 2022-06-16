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

class res_partner_multi(osv.osv_memory):
    _name = 'res.partner.multi'
    _description = 'Partner Multi'
    _columns = {
        'date':fields.date("Date",required=True),        
        
    }

    _defaults = {
         'date': fields.datetime.now(),         
    }
    
    def automation_partner_sale_target(self, cr, uid,context=None):
        customer_target_obj = self.pool.get('customer.target')
        partner_obj = self.pool.get('res.partner')
        invoice_obj = self.pool.get('account.invoice')
        #target_list= customer_target_obj.search(cr,uid,[('partner_id','!=',None)],order='id desc')
        date=fields.datetime.now()
        partner_ids= invoice_obj.search(cr,uid,[('date_invoice','=',date),('state','=','open')],order='id desc')
        for partner_id in partner_ids: 
            target_id = self.pool.get('customer.target').search(cr,uid,[('partner_id','=',partner_id)],limit=1,order='id desc')
            if target_id:
                data = customer_target_obj.browse(cr, uid, target_id)[0]
                customer_target_obj.get_so_qty(cr, uid, [target_id], date,data.partner_id.id,data.outlet_type,context=None)
                customer_target_obj.write(cr, uid, target_id, {'updated_by':uid,'updated_time':fields.datetime.now()}, context=context)    
        return True
    
    def print_report(self, cr, uid, ids, context=None):
        data = self.read(cr, uid, ids, context=context)[0]
        customer_target_obj = self.pool.get('customer.target')
        datas = {
             'ids': context.get('active_ids', []),
             'model': 'res.partner',
             'form': data
            }
        partner_ids=datas['ids']
        print 'data>>',datas
        print 'datae>>>',data['date']
        date = data['date']
        for partner_id in partner_ids: 
            target = self.pool.get('customer.target').search(cr,uid,[('partner_id','=',partner_id)],limit=1,order='id desc')
            if target:
                data = customer_target_obj.browse(cr, uid, target)[0]
                customer_target_obj.get_so_qty(cr, uid, target, date,data.partner_id.id,data.outlet_type,context=None)
                customer_target_obj.write(cr, uid, target, {'updated_by':uid,'updated_time':fields.datetime.now()}, context=context)
            else:
                for partner in self.pool.get('res.partner').browse(cr,uid,partner_id,context=context):
                    value = {'date':date,'partner_id': partner.id,'outlet_type':partner.outlet_type.id,'township':partner.township.id,'address':partner.street,'delivery_team_id':partner.delivery_team_id.id,'branch_id':partner.branch_id.id}
                    target_id = customer_target_obj.create(cr,uid,value,context=context)
                    customer_target_obj.get_so_qty(cr, uid, [target_id], date,partner.id,partner.outlet_type,context=None)
                    customer_target_obj.write(cr, uid, target_id, {'updated_by':uid,'updated_time':fields.datetime.now()}, context=context)    
#        for batching in batching_id: 
#             batching_data=batching_obj.browse(cr,uid,batching,context=context)
#             if batching_data.state=='confirm':
        #batching_obj.convert_so(cr, uid, [batching_id],context=context)    
