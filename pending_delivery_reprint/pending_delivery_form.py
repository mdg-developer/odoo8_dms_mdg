from openerp.osv import orm
from openerp.osv import fields, osv
import xlrd
from xlrd import open_workbook
from openerp.tools.translate import _
from openerp.http import request
from openerp.addons.connector.queue.job import job, related_action
from openerp.addons.connector.session import ConnectorSession
from openerp.addons.connector.exception import FailedJobError
from openerp.addons.connector.jobrunner.runner import ConnectorRunner

@job(default_channel='root.deliverytransfer')
def automatic_pending_delivery_stock_transfer(session,order_ids,delivery_date):
    context = session.context.copy()
    cr = session.cr
    uid = session.uid
    date=delivery_date
    context = {'lang': 'en_US', 'params': {'action': 458}, 'tz': 'Asia/Rangoon', 'uid': 1}    
    soObj = session.pool.get('sale.order')
    for order_data in soObj.browse(cr, uid, order_ids, context=context):
        So_id = order_data.id
        shipped=order_data.shipped
        if shipped!=True:
            stockPickingObj = session.pool.get('stock.picking')        
            stockDetailObj = session.pool.get('stock.transfer_details')
            stockViewResult = soObj.action_view_delivery(cr, uid, So_id, context=context)
            if stockViewResult:
                # stockViewResult is form result
                # stocking id =>stockViewResult['res_id']
                # click force_assign
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
                cr.execute('update stock_picking set date_done =%s where origin=%s', (date, order_data.name,))
                cr.execute('update stock_move set date = %s where origin =%s', (date, order_data.name,))
                picking_id = stockViewResult['res_id']
                print 'picking_id', picking_id
                pick_date = stockPickingObj.browse(cr, uid, picking_id, context=context)
                cr.execute(
                    "update account_move_line set date= %s from account_move move where move.id=account_move_line.move_id and move.ref= %s",
                    (date, pick_date.name,))
                cr.execute('''update account_move set period_id=p.id,date=%s
                            from (
                            select id,date_start,date_stop
                            from account_period
                            where date_start != date_stop
                            ) p
                            where p.date_start <= %s and  %s <= p.date_stop
                            and account_move.ref=%s''', (date, date, date, pick_date.name,))    
    return True

class pendingdelivery(osv.osv):
    _name = 'pending.delivery'
    _columns = {
                'delivery_date':fields.date('Delivery Date',readonly=True),
                'due_date':fields.date('Order Date',readonly=True),          
                'order_id':fields.many2one('sale.order','Order No',readonly=True),
                'miss':fields.boolean('Miss',readonly=True),
                'state':fields.selection([('draft', 'Draft'),
                                                ('done', 'Complete')], string='Status',readonly=True),     
                'delivery_team_id':fields.many2one('crm.case.section','Delivery Team',readonly=True),
                'latitude':fields.float('Geo Latitude',  digits=(16, 5), readonly=True),
                'longitude':fields.float('Geo Longitude',  digits=(16, 5), readonly=True),
                'distance_status':fields.char('Distance Status', readonly=True),
                'geo_point':fields.char('Geo Point'),
              }
#     def create_automation_pending_delivery(self, cr, uid, pending_ids, context=None):
#         session = ConnectorSession(cr, uid, context)
#         jobid=automation_pending_delivery.delay(session,pending_ids,priority=1, eta=10)
#         print "Job",jobid
#         runner = ConnectorRunner()
#         runner.run_jobs()
#         return jobid 

    def action_convert_pending_delivery(self, cr, uid, ids, context=None):
        context = {'lang':'en_US', 'params':{'action':458}, 'tz': 'Asia/Rangoon', 'uid': 1}
        soObj = self.pool.get('sale.order')        
        invoiceObj = self.pool.get('account.invoice')                
        stockPickingObj = self.pool.get('stock.picking')
        stockDetailObj = self.pool.get('stock.transfer_details')        
        pending_obj =self.pool.get('pending.delivery')        
        mobile_obj =self.pool.get('mobile.sale.order')       
        voucherObj = self.pool.get('account.voucher')
        voucherLineObj = self.pool.get('account.voucher.line')
        noteObj = self.pool.get('account.creditnote')        
         
        solist=[]
        invlist = []
        if ids:
            for pending_id in pending_obj.browse(cr, uid, ids[0], context=context):
                if pending_id:
                    if pending_id.miss == True:
                        cr.execute('update sale_order set is_generate = false, due_date = %s where id=%s', (pending_id.due_date, pending_id.order_id.id,))
                        cr.execute('select tb_ref_no from sale_order where id=%s', (pending_id.order_id.id,))
                        ref_no = cr.fetchone()[0]
                        cr.execute("update pre_sale_order set void_flag = 'voided' where name=%s", (ref_no,))
                    else:
                        So_id=pending_id.order_id.id
                        solist = pending_id.order_id.id
                        pre_order_no =pending_id.order_id.tb_ref_no   
                        delivery_date=pending_id.delivery_date   
                        cr.execute('select branch_id,section_id,delivery_remark,payment_type,payment_term from sale_order where id=%s', (pending_id.order_id.id,))
                        data = cr.fetchone()
                        if data:
                            branch_id = data[0]
                            section_id = data[1]
                            delivery_remark = data[2]
                            payment_type= data[3]
                            payment_term=data[4]
                        cr.execute('select delivery_team_id from crm_case_section where id=%s', (section_id,))
                        delivery = cr.fetchone()
                        if delivery:
                            delivery_team_id = delivery[0]
                        else:
                            delivery_team_id = None
                        cr.execute('select id from pre_sale_order where name=%s', (pre_order_no,))
                        pre_data = cr.fetchone()
                        if pre_data:
                            pre_order_id  = pre_data[0]
                        else:
                            pre_order_id = None
                        invoice_id = mobile_obj.create_invoices(cr, uid, [solist], context=context)
                        cr.execute('update account_invoice set date_invoice = %s, branch_id =%s ,payment_type=%s,delivery_remark =%s ,section_id=%s,user_id=%s, payment_term = %s where id =%s', (delivery_date,branch_id,payment_type, delivery_remark, delivery_team_id, uid,payment_term, invoice_id,))                                                
                                                     
                        invoiceObj.button_reset_taxes(cr, uid, [invoice_id], context=context)
                        if invoice_id:
                            self.pool['account.invoice'].signal_workflow(cr, uid, [invoice_id], 'invoice_open')
                            # pre_order =True
                            invoiceObj.write(cr, uid, invoice_id, {'pre_order':True}, context)      
                            if payment_type=='credit':
                                invoiceObj.credit_approve(cr, uid, [invoice_id], context=context)
                            inv_data=self.pool['account.invoice'].browse(cr, uid, invoice_id,context=None)
                            ms_ids=self.pool['pre.sale.order'].browse(cr, uid, pre_order_id,context=None)
                            invoiceObj.invoice_pay_customer(cr, uid, invlist, context=context)
                            for payment_line in ms_ids.payment_line_ids:
                                    journal_id=payment_line.journal_id.id
                                    journal_name=payment_line.journal_id.name
                                    payment_amount =payment_line.amount
                                    if journal_name=='Credit Note': 
                                        note_id = noteObj.search(cr, uid, [('name', '=',  payment_line.cheque_no)],context=None)
                                        note_data = noteObj.browse(cr, uid, note_id, context=context)
                                        accountId=note_data.principle_id.property_trade_payable_account.id                                        
                                        note_data.write({'state':'redeemed','issued_date':inv_data.date_invoice,'invoice_number':inv_data.number,'sale_team_id':inv_data.section_id.id,'user_id':inv_data.user_id.id})
                                    else:
                                        cr.execute('select default_debit_account_id from account_journal where id=%s', (journal_id,))
                                        data = cr.fetchall()
                                        if data:
                                            accountId = data[0]
                                    if journal_id and accountId:  # cash journal and cash account. If there no journal id or no account id, account invoice is not make payment.
                                        accountVResult = {
                                                        'partner_id':inv_data.partner_id.id,
                                                        'amount':payment_amount,
                                                        'journal_id':journal_id,
                                                        'date':inv_data.date_invoice,
                                                        'period_id':inv_data.period_id.id,
                                                        'account_id':accountId,
                                                        'pre_line':True,
                                                        'type':'receipt',
                                                        'company_id':3
                                                        }
                                        # create register payment voucher
                                        voucherId = voucherObj.create(cr, uid, accountVResult, context=context)
                                         
                                    if voucherId:
                                        vlist = []
                                        vlist.append(voucherId)
                                        # get the voucher lines
                                        vlresult = voucherObj.recompute_voucher_lines(cr, uid, vlist, inv_data.partner_id.id, journal_id, inv_data.amount_total, 120, 'receipt', inv_data.date_invoice, context=None)
                                        if vlresult:
                                            #result = vlresult['value']['line_cr_ids'][0]
                                            for v_line_data in vlresult['value']['line_cr_ids']:
                                                if v_line_data['name']==inv_data.number:
                                                    result =v_line_data
                                                    result['voucher_id'] = voucherId
                                                    result['amount'] = payment_amount
                                                    voucherLineObj.create(cr, uid, result, context=context)
                                            # create the voucher lines
                                        # invoice register payment done
                                        voucherObj.button_proforma_voucher(cr, uid, vlist , context=context)
                                                              
                            session = ConnectorSession(cr, uid, context)
                            jobid = automatic_pending_delivery_stock_transfer.delay(session, [solist], delivery_date, priority=20)
                            runner = ConnectorRunner()
                            runner.run_jobs()                                                                 
            self.write(cr, uid, ids[0], {'state':'done'}, context=context)                        
        return True
            