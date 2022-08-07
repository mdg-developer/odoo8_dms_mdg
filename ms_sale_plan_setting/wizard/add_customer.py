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
from datetime import datetime
from dateutil import relativedelta

from openerp.osv import fields, osv
from openerp.tools.translate import _

class plan_trip_customer(osv.osv_memory):

    _name ='plan.trip.customer'
    _description = 'Plan Trip for all selected employees'
    _columns = {
        'partner_ids': fields.many2many('res.partner', 'res_partner_trip_rel', 'trip_id', 'partner_id', 'Customers'),
    }
    
    def insert_data(self, cr, uid, ids, context=None):
        plan_trip_obj = self.pool.get('sale.plan.trip.setting')
        plan_line_obj= self.pool.get('sale.plan.trip.setting.line')
        partner_obj=self.pool.get('res.partner')
        if context is None:
            context = {}
        customer_data=self.browse(cr, uid, ids, context=context)
        partner_ids=customer_data.partner_ids
        #print 'partner_ids',partner_ids
        for partner_id in partner_ids:
            par_id = plan_line_obj.search(cr, uid, [('partner_id', '=', partner_id.id),('line_id', '=', customer_data.id)], context=context)
            if par_id:
                partner = partner_obj.browse(cr, uid,partner_id.id, context=context)
                raise osv.except_osv(_('Warning!'),_('You inserted this customer name (%s ,%s).')%(partner.name,partner.customer_code,))    
            else:
                partner = partner_obj.browse(cr, uid, partner_id.id, context=context)
                cr.execute("select max(id) from sale_plan_trip_setting")
                exp_id_rec = cr.fetchone()
                max_id = exp_id_rec[0]
                cr.execute("select date_order::date from sale_order  where partner_id =%s and state !='cancel' order by id desc",(partner_id.id,))
                last_order=cr.fetchone()
                if last_order:
                    last_order_date=last_order[0]
                else:
                    last_order_date=False         
                    plan_line_obj.create(cr, uid,{
                                    'code':partner.customer_code,
                                     'class':partner.class_id.id,
                                    'partner_id': partner_id.id,
                                    'purchase_date':last_order_date,
                                    'frequency':partner.frequency_id.id,
                                    'line_id':max_id,
                                              }, context=context) 
                    print 'create------------------------------------------------'    
        return True


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
