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

class pre_sale_state(osv.osv_memory):
    _name = 'pre.sale.state'
    _description = 'Pre Sale State'
    _columns = {
        'confirm':fields.boolean('Complete State' ,readonly=True),
    }
    _defaults = {
         'confirm': True,         
    }

    def print_report(self, cr, uid, ids, context=None):
        data = self.read(cr, uid, ids, context=context)[0]
        mobile_obj = self.pool.get('pre.sale.order')
        
        datas = {
             'ids': context.get('active_ids', []),
             'model': 'pre.sale.order',
             'form': data
            }
        mobile_id=datas['ids']
        print 'mobile_id',mobile_id
        for mobile in mobile_id: 
            mobile_data=mobile_obj.browse(cr,uid,mobile,context=context)
            state=mobile_data.m_status
            void_flag=mobile_data.void_flag
            if state=='draft'  and void_flag =='none':
                mobile_obj.action_convert_presaleorder(cr, uid, [mobile], context=context)    
                                                                                         
            
               


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
