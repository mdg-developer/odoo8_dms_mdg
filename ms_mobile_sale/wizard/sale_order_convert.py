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

class manual_sale_order(osv.osv_memory):
    _name = 'manual.sale.order'
    _description = 'Manual Sale Order'
    _columns = {
        'confirm':fields.boolean('Complete State' ,readonly=True),
    }
    _defaults = {
         'confirm': True,         
    }

    def print_report(self, cr, uid, ids, context=None):
        data = self.read(cr, uid, ids, context=context)[0]
        m_sale_obj = self.pool.get('mobile.sale.order')
        sale_obj = self.pool.get('sale.order')
        stockPickingObj=self.pool.get('stock.picking')
        invoiceObj=self.pool.get('account.invoice')
        stockDetailObj = self.pool.get('stock.transfer_details')
        datas = {
             'ids': context.get('active_ids', []),
             'model': 'sale.order',
             'form': data
            }
        sale_id=datas['ids']
        print 'mobile_id',sale_id
        for sale in sale_id: 
            sale_data=sale_obj.browse(cr,uid,sale,context=context)
            state=sale_data.state
            payment_type=sale_data.payment_type
            branch_id=sale_data.branch_id.id
            print 'state',state
            if state != 'manual':
                raise osv.except_osv(_('Warning!'), _("You shouldn't manually invoice the following sale order %s") % (sale_data.name))
            if state=='manual':
                invoice_id = sale_obj.action_invoice_create(cr, uid, [sale], context=context)                     
                sale_obj.signal_workflow(cr, uid, [o.id for o in sale_data if o.order_policy == 'manual'], 'manual_invoice')
                if invoice_id:
                    self.pool['account.invoice'].signal_workflow(cr, uid, [invoice_id], 'invoice_open')
                    cr.execute('update account_invoice set payment_type=%s ,branch_id =%s,date_invoice=current_date where id =%s', (payment_type,branch_id, invoice_id,))                            
                stockViewResult = sale_obj.action_view_delivery(cr, uid, [sale], context=context)
                
                if stockViewResult:
                    stockPickingObj.force_assign(cr, uid, stockViewResult['res_id'], context=context)
                    # transfer
                    # call the transfer wizard
                    # change list
                    pickList = []
                    pickList.append(stockViewResult['res_id'])
                    wizResult = stockPickingObj.do_enter_transfer_details(cr, uid, pickList, context=context)
                    # pop up wizard form => wizResult
                    detailObj = stockDetailObj.browse(cr, uid, wizResult['res_id'], context=context)
                    if detailObj:
                        detailObj.do_detailed_transfer()                                                                                         