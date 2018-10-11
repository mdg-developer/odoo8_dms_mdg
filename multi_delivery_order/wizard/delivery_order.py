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
from openerp.tools.translate import _

class sale_order_delivery_transfer(osv.osv_memory):
    _name = 'order.delivery.transfer'
    _description = 'Order Delivery Transfer'
    _columns = {
        'date':fields.date('Delivery Date',required=False),
        'confirm':fields.boolean('Confirm',readonly=True,required=False,default=True),

    }
    
    def print_report(self, cr, uid, ids, context=None):
        data = self.read(cr, uid, ids, context=context)[0]
        order_obj = self.pool.get('sale.order')
        datas = {
             'ids': context.get('active_ids', []),
             'model': 'sale.order',
             'form': data
            }
        order_ids=datas['ids']
        import datetime
        date = datetime.date.today()
        for order in order_ids: 
            order_data=order_obj.browse(cr,uid,order,context=context)
            shipped=order_data.shipped
            if shipped!=True:
                self.transfer_order_delivery(cr, uid, [order],date, context=context)       
                
    def transfer_order_delivery(self, cr, uid, ids,date, context=None):
        context = {'lang':'en_US', 'params':{'action':458}, 'tz': 'Asia/Rangoon', 'uid': 1}
        soObj = self.pool.get('sale.order')        
        stockPickingObj = self.pool.get('stock.picking')
        stockDetailObj = self.pool.get('stock.transfer_details')    
        invoiceObj = self.pool.get('account.invoice')             
        mobile_obj = self.pool.get('mobile.sale.order')              
        solist=[]
        if ids:
            for so_data in soObj.browse(cr, uid, ids, context=context):
                if so_data:
                        So_id=so_data.id
                        if so_data.state =='draft':
                            soObj.action_button_confirm(cr, uid, [So_id], context=context)
                            invoice_id = mobile_obj.create_invoices(cr, uid,  [So_id], context=context)
                            branch_id=so_data.branch_id.id
                            delivery_remark=so_data.delivery_remark
                            payment_type=so_data.payment_type  
                            date=so_data.date_order                      
                            cr.execute('update account_invoice set date_invoice=%s,payment_type=%s ,branch_id =%s,delivery_remark =%s where id =%s', (date,payment_type,branch_id, delivery_remark, invoice_id,))                            
                            if invoice_id:
                                invoiceObj.button_reset_taxes(cr, uid, [invoice_id], context=context)
                                invoiceObj.signal_workflow(cr, uid, [invoice_id], 'invoice_open')
                        else:
                            raise osv.except_osv(_('Warning!'),_('You cannot confirm sale order which is not draft. You should choose draft order only.'))
   
#                         stockViewResult = soObj.action_view_delivery(cr, uid, So_id, context=context)    
#                         if stockViewResult:
#                             # stockViewResult is form result
#                             # stocking id =>stockViewResult['res_id']
#                             # click force_assign
#                             stockPickingObj.force_assign(cr, uid, stockViewResult['res_id'], context=context)
#                             # transfer
#                             # call the transfer wizard
#                             # change list
#                             pickList = []
#                             pickList.append(stockViewResult['res_id'])
#                             wizResult = stockPickingObj.do_enter_transfer_details(cr, uid, pickList, context=context)
#                             # pop up wizard form => wizResult
#                             detailObj = stockDetailObj.browse(cr, uid, wizResult['res_id'], context=context)
#                             if detailObj:
#                                 detailObj.do_detailed_transfer()    
#                             cr.execute('update stock_picking set date_done =%s where origin=%s',(date,so_data.name,))        
#                             cr.execute('update stock_move set date = %s where origin =%s',(date,so_data.name,))
#                             picking_id=stockViewResult['res_id']   
#                             print 'picking_id',picking_id
#                             pick_date=stockPickingObj.browse(cr, uid, picking_id, context=context)
#                             cr.execute("update account_move_line set date= %s from account_move move where move.id=account_move_line.move_id and move.ref= %s",(date,pick_date.name,))            
#                             cr.execute('''update account_move set period_id=p.id,date=%s
#                             from (
#                             select id,date_start,date_stop
#                             from account_period
#                             where date_start != date_stop
#                             ) p
#                             where p.date_start <= %s and  %s <= p.date_stop
#                             and account_move.ref=%s''',(date,date, date,pick_date.name,))                              
#                                 
                            
                                                            
                                           
        return True          
            
               


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
