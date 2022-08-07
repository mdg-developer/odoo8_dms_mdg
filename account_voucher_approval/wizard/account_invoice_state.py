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

class account_invoice_state(osv.osv_memory):
    _name = 'account.invoice.state'
    _description = 'Account Invoice State'
    _columns = {
        'fm_approve':fields.boolean('Finance Validate'),
        'cashier_approve':fields.boolean('Cashier Validate')        
    }

    _defaults = {
         'fm_approve': False,
         'cashier_approve': False,
         
    }

    def print_report(self, cr, uid, ids, context=None):
        data = self.read(cr, uid, ids, context=context)[0]
        invoice_obj = self.pool.get('account.invoice')
        
        datas = {
             'ids': context.get('active_ids', []),
             'model': 'account.invoice',
             'form': data
            }
        invoice_id=datas['ids']
        fm_approve=data['fm_approve']
        cashier_approve=data['cashier_approve']
        
        
        if fm_approve==True:
            for invoice in invoice_id: 
                invoice_obj.finance_approve(cr, uid, invoice, context=context)                                                                             
        if cashier_approve==True:
            for invoice in invoice_id: 
                invoice_obj.action_date_assign(cr, uid, invoice, context=context)                             
                invoice_obj.action_move_create(cr, uid, invoice, context=context)                             
                invoice_obj.action_number(cr, uid, invoice, context=context)                             
                invoice_obj.invoice_validate(cr, uid, invoice, context=context)                               
            
               


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
