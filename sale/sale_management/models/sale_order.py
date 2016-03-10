
'''
Created on Jan 22, 2016

@author: 7th Computing
'''

from openerp.osv import fields, osv
from openerp.tools.misc import DEFAULT_SERVER_DATE_FORMAT
from openerp.tools.translate import _
import time
from openerp import netsvc
# from openerp.exceptions import UserError

import openerp.addons.decimal_precision as dp

class sale_order(osv.osv):
    _inherit = "sale.order"
         
    _columns = {
               'tb_ref_no':fields.char('Order Reference'),
               'payment_type':fields.selection([
                    ('credit', 'Credit'),
                    ('cash', 'Cash'),
                    ('consignment', 'Consignment'),
                    ('advanced', 'Advanced')
                    ], 'Payment Type'),
               'delivery_remark':fields.selection([
                    ('partial', 'Partial'),
                    ('delivered', 'Delivered'),
                    ('none', 'None')
               ], 'Deliver Remark'),
               'due_date':fields.date('Due Date'),
               'so_latitude':fields.float('Geo Latitude'),
               'so_longitude':fields.float('Geo Longitude'),               
               'customer_code':fields.char('Customer Code'),
               'sale_plan_name':fields.char('Sale Plan Name'),
               'sale_plan_day_id':fields.many2one('sale.plan.day', 'Sale Plan Day'),
               'sale_plan_trip_id':fields.many2one('sale.plan.trip', 'Sale Plan Trip'),
               'validity_date':fields.date(string='Expiration Date', readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}),                   
               }
  
    def action_confirm(self, cr, uid, ids, context=None):
        if not context:
            context = {}                    
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'
        self.signal_workflow(cr, uid, ids, 'order_confirm') 
        sale_order_obj = self.pool.get('sale.order')
        self = sale_order_obj.browse(cr, uid, ids[0], context=context)       
        for order in self:
            order.state = 'sale'
            if self.env.context.get('send_email'):
                self.force_quotation_send()
            order.order_line._action_procurement_create()
            if not order.project_id:
                for line in order.order_line:
                    if line.product_id.invoice_policy == 'cost':
                        order._create_analytic_account()
                        break
        if self.env['ir.values'].get_default('sale.config.settings', 'auto_done_setting'):
            self.action_done()
             
        sale_line_obj = self.pool.get('sale.order.line')
        sale_order_obj = self.pool.get('sale.order')
        picking_obj = self.pool.get('stock.picking')
        move_obj = self.pool.get('stock.move')
        invoice_obj = self.pool.get('account.invoice')
        invoice_line_obj = self.pool.get('account.invoice.line')
        acc_move_obj = self.pool.get('account.move')
        move_line_obj = self.pool.get('account.move.line')
        voucher_obj = self.pool.get('account.voucher')
        voucher_line_obj = self.pool.get('account.voucher.line')
        currency_obj = self.pool.get('res.currency')


        if ids:
            print 'iddddddddddddddd', ids
            so_value = sale_order_obj.browse(cr, uid, ids[0], context=context)
            origin = so_value.name
            print 'origin', origin
            print 'so_value.delivery_remark', so_value.delivery_remark
 
             
            if so_value.delivery_remark == 'delivered':
                cr.execute("select project_id from sale_order where name=%s", (origin,))
                analytic_id = cr.fetchone()
                cr.execute("update stock_picking set state='done' where origin=%s", (origin,))
                cr.execute("select id from stock_move where origin=%s", (origin,))
                sm_id = cr.fetchall()
                print 'sm_id,sm_id', sm_id
                 
                for move_id in sm_id:
                    print 'idddddddddd', move_id
                    rs1 = move_obj.action_done(cr, uid, move_id, context=context)
                    print 'rsssssss', rs1, analytic_id
                    if analytic_id and analytic_id[0] is not None:
                        cr.execute("select sp.name from stock_picking sp,stock_move sm where sp.id=sm.picking_id and sm.id=%s", (move_id,))
                        wh_name = cr.fetchone()[0]
                        # cr.execute("update account_move set analytic_account_id=%s where ref=%s",(analytic_id[0],wh_name,))
                        cr.execute("update account_move_line set analytic_account_id=%s where ref=%s", (analytic_id[0], wh_name,))
                             
                    
                     
            if so_value.delivery_remark == 'none':
                cr.execute("update stock_picking set state='confirmed' where origin=%s", (origin,))
                cr.execute("update stock_move set state='confirmed' where origin=%s", (origin,))
            if so_value.payment_type == 'credit':     
                
                cr.execute("select project_id from sale_order where name=%s", (origin,))
                analytic_id = cr.fetchone()
                sale_line_ids = sale_line_obj.search(cr, uid, [('order_id', 'in', ids), ('invoice_status', '=', 'no')], context=context) 
                a = so_value.partner_id.property_account_receivable_id.id
                 
                if sale_line_ids:
                    created_lines = sale_line_obj.invoice_line_create(cr, uid, sale_line_ids, context=context)
                inv = {
                    'name': so_value.client_order_ref or '',
                    'origin': so_value.name,
                    'type': 'out_invoice',
                    'tb_ref_no':so_value.tb_ref_no,
                    'reference': so_value.name,
                    'account_id': a,
                    'partner_id': so_value.partner_invoice_id.id,
                    'invoice_line': [(6, 0, created_lines)],
                    'currency_id' : so_value.pricelist_id.currency_id.id,
                    'comment': so_value.note,
                    'payment_term': so_value.payment_term.id,
                    'fiscal_position': so_value.fiscal_position.id or so_value.partner_id.property_account_position.id,
                    'user_id': so_value.user_id and so_value.user_id.id or False,
                    'company_id': so_value.company_id and so_value.company_id.id or False,
                    'date_invoice': fields.date.today(),
                    'discount_total':so_value.total_dis,
                    'deduct_amt':so_value.deduct_amt,
                    'state':'draft',
                    'date_due':fields.date.today(),
                }
                cr.execute("update sale_order set state='progress' where id=%s", (ids[0],))
                print 'inv', inv
                inv_id = self.pool.get('account.invoice').create(cr, uid, inv)

                cr.execute('INSERT INTO sale_order_invoice_rel \
                    (order_id,invoice_id) values (%s,%s)', (ids[0], inv_id))
                # print 'inv_id=[]',inv_id
                # invoice_line_obj.move_line_get(cr, uid,inv_id)
               # invoice_obj._compute_residual(cr, uid,inv_id)

                res_1 = invoice_obj.action_move_create(cr, uid, inv_id)
                print 'res_1', res_1                                
                res_2 = invoice_obj.invoice_validate(cr, uid, inv_id, context=context)
                invoice_obj.invoice_validate(cr, uid, inv_id, context=context)
                print 'res_2', res_2

                if analytic_id:
                    cr.execute("update account_move set analytic_account_id=%s where ref=%s", (analytic_id[0], origin,))

                    cr.execute("update account_move_line set analytic_account_id=%s where ref=%s", (analytic_id[0], origin,))
            cr.execute("delete from account_move_line where ref=%s and name='FOC'", (origin,))

#             if so_value.payment_type=='cash' or so_value.payment_type=='consignment' or so_value.payment_type=='advanced':     
#                 
#                 print 'ids',ids
#                 cr.execute("select project_id from sale_order where name=%s",(origin,))
#                 analytic_id=cr.fetchone()
#                 sale_line_ids = sale_line_obj.search(cr, uid, [('order_id', 'in', ids)], context=context) 
#                 print 'sale_line_ids',sale_line_ids
#                 qty=0
#                 for sale_line in sale_line_ids:
#                     qty=qty+sale_line.qty_to_invoice
#                 a = so_value.partner_id.property_account_receivable_id.id
#                  
#                 if sale_line_ids:
#                     created_lines = sale_line_obj.invoice_line_create(self, sale_line_ids,qty)
#                 inv = {
#                     'name': so_value.client_order_ref or '',
#                     'origin': so_value.name,
#                     'type': 'out_invoice',
#                     'tb_ref_no':so_value.tb_ref_no,
#                     'reference': so_value.name,
#                     'account_id': a,
#                     'partner_id': so_value.partner_invoice_id.id,
#                     'invoice_line': [(6, 0, created_lines)],
#                     'currency_id' : so_value.pricelist_id.currency_id.id,
#                     'comment': so_value.note,
#                     'payment_term': so_value.payment_term.id,
#                     'fiscal_position': so_value.fiscal_position.id or so_value.partner_id.property_account_position.id,
#                     'user_id': so_value.user_id and so_value.user_id.id or False,
#                     'company_id': so_value.company_id and so_value.company_id.id or False,
#                     'date_invoice': fields.date.today(),
#                     'discount_total':so_value.total_dis,
#                     'deduct_amt':so_value.deduct_amt,
#                     'state':'draft',
#                     'date_due':fields.date.today(),
#                 }
#                 cr.execute("update sale_order set state='progress' where id=%s",(ids[0],))
#                 
#                 inv_id = self.pool.get('account.invoice').create(cr, uid, inv)
# 
#                 cr.execute('INSERT INTO sale_order_invoice_rel \
#                     (order_id,invoice_id) values (%s,%s)', (ids[0], inv_id))
#                 #print 'inv_id=[]',inv_id
#                 #invoice_line_obj.move_line_get(cr, uid,inv_id)
#                
#                 res_1 = invoice_obj.action_move_create(cr, uid,inv_id)
#                 print 'res_1',res_1                                
#                 res_2 = invoice_obj.invoice_validate(cr, uid, inv_id, context=context)
#                 print 'res_2',res_2
#          
#                 if analytic_id and analytic_id[0] is not None:
#                     cr.execute("update account_move set analytic_account_id=%s where ref=%s",(analytic_id[0],origin,))
#                     cr.execute("update account_move_line set analytic_account_id=%s where ref=%s",(analytic_id[0],origin,))
#                 cr.execute("delete from account_move_line where ref=%s and name='FOC'",(origin,))
#                 
#                 cr.execute("select move_id,account_id,amount_total from account_invoice where id=%s",(inv_id,))
#                 data_id=cr.fetchone()
#                 move_id=data_id[0]
#                 ar_acc=data_id[1]
#                 amount=data_id[2]
#                 
#                 cr.execute('select journal_id from account_move where id=%s',(move_id,))
#                 journal_id=cr.fetchone()[0]
#                 cr.execute("select id from account_journal where code ='BNK1'")
#                 j_id=cr.fetchone()[0]
#                 cr.execute('select default_credit_account_id from account_journal where id=%s',(j_id,))
#                 default_credit_account_id=cr.fetchone()[0]
#                 cr.execute('select currency_id from account_move_line  where move_id=%s',(move_id,))
#                 currency_id=cr.fetchone()[0]
#                 print 'j_idj_id',j_id
# 
#                 voucher_res = {          'type': 'receipt',
#                                         'account_id':default_credit_account_id,                                    
#                                         'partner_id': so_value.partner_invoice_id.id,
#                                         'journal_id': j_id,
#                                         'company_id':  so_value.company_id and so_value.company_id.id or False,
#                                         'currency_id': currency_id,
#                                         'date': fields.date.today(),
#                                         'amount':amount,
#                                         }
#                 print 'voucher_res',voucher_res,
#                 voucher_amount=amount
#                 voucher_id = voucher_obj.create(cr, uid, voucher_res, context=context)
#                 print 'voucher_id',voucher_id
#                 voucher_line_dict =  {}
#                 result=voucher_obj.onchange_partner_id(cr, uid, [], partner_id=so_value.partner_invoice_id.id, journal_id=j_id, amount=voucher_amount, currency_id=currency_id, ttype='receipt', date= fields.date.today(), context=context)
# 
#                 for line_dict in result['value']['line_cr_ids'] + result['value']['line_dr_ids']:
#                     move_line = move_line_obj.browse(cr, uid, line_dict['move_line_id'], context)
#                     if move_id== move_line.move_id.id:
#                         print 'line_dict',line_dict
#                         voucher_line_dict = line_dict
# 
#                 if voucher_line_dict:
#                     print 'voucher_line_dict',voucher_line_dict
#                     cr.execute('update account_voucher_line set amount=%s where voucher_id=%s',(voucher_amount,voucher_id))
# 
#                     voucher_line_dict.update({'voucher_id': voucher_id,'amount':voucher_amount})
# 
#                     voucher_line_obj.create(cr, uid, voucher_line_dict, context=context) 
#                 
#                 voucher_obj.proforma_voucher(cr,uid,voucher_id,context=context)
#                 cr.execute('select move_id from account_voucher where id=%s',(voucher_id,))
#                 v_id=cr.fetchone()[0]
#                 cr.execute("update account_move set analytic_account_id=%s where id=%s",(analytic_id[0],v_id,))
#                 cr.execute("update account_move_line set analytic_account_id=%s where move_id=%s",(analytic_id[0],v_id,))
#                 invoice_obj.confirm_paid(cr,uid,inv_id,context=context)
#                 cr.execute("update sale_order set state='done' where id=%s",(ids[0],)) 

         
#         return {
#             'type': 'ir.actions.act_window',
#             'name': _('Sales Order'),
#             'res_model': 'sale.order',
#             'res_id': ids[0],
#             'view_type': 'form',
#             'view_mode': 'form',
#             'view_id': view_id,
#             'target': 'current',
#             'nodestroy': True,
#         }      
    
    def geo_location(self, cr, uid, ids, context=None):
        result = {
                 'name'     : 'Go to Report',
                 'res_model': 'ir.actions.act_url',
                 'type'     : 'ir.actions.act_url',
                 'target'   : 'new',
               }
        data = self.browse(cr, uid, ids)[0]
        latitude = data.so_latitude
        longitude = data.so_longitude
        print 'latitude', latitude
        print 'longitude', longitude
        print 'https://www.google.com/maps/@' + str(latitude) + ',' + str(longitude) + ',18z'
        result['url'] = 'https://www.google.com/maps/@' + str(latitude) + ',' + str(longitude) + ',18z'
             
        return result
    

#     def _prepare_invoice(self, cr, uid, order, lines, context=None):
#         """
#         Prepare the dict of values to create the new invoice for a sales order. This method may be
#         overridden to implement custom invoice generation (making sure to call super() to establish
#         a clean extension chain).
#         """
#         self.ensure_one()
#         journal_id = self.env['account.invoice'].default_get(['journal_id'])['journal_id']
#         if not journal_id:
#             raise osv.except_osv(_('UserError!'), _('Please define an accounting sale journal for this company.'))  
# #             raise UserError(_('Please define an accounting sale journal for this company.'))
#         invoice_vals = {
#             'name': self.client_order_ref or '',
#             'origin': self.name,
#             'type': 'out_invoice',
#             'reference': self.client_order_ref or self.name,
#             'account_id': self.partner_invoice_id.property_account_receivable_id.id,
#             'partner_id': self.partner_invoice_id.id,
#             'journal_id': journal_id,
#             'currency_id': self.pricelist_id.currency_id.id,
#             'comment': self.note,
#             'payment_term_id': self.payment_term_id.id,
#             'fiscal_position_id': self.fiscal_position_id.id or self.partner_invoice_id.property_account_position_id.id,
#             'company_id': self.company_id.id,
#             'user_id': self.user_id and self.user_id.id,
#             'team_id': self.team_id.id,
#             'tb_ref_no':self.tb_ref_no,     
#         }       
#         return invoice_vals

    def _prepare_invoice(self, cr, uid, order, lines, context=None):

        """Prepare the dict of values to create the new invoice for a
           sales order. This method may be overridden to implement custom
           invoice generation (making sure to call super() to establish
           a clean extension chain).
           :param browse_record order: sale.order record to invoice
           :param list(int) line: list of invoice line IDs that must be attached to the invoice
           :return: dict of value to create() the invoice
        """
        if context is None:
            context = {}
        journal_ids = self.pool.get('account.journal').search(cr, uid,
            [('type', '=', 'sale'), ('company_id', '=', order.company_id.id)],
            limit=1)
        if not journal_ids:
            raise osv.except_osv(_('Error!'),
                _('Please define sales journal for this company: "%s" (id:%d).') % (order.company_id.name, order.company_id.id))
        invoice_vals = {
            'name': order.client_order_ref or '',
            'origin': order.name,
            'type': 'out_invoice',
            'reference': order.client_order_ref or order.name,
            'account_id': order.partner_id.property_account_receivable.id,
            'partner_id': order.partner_invoice_id.id,
            'journal_id': journal_ids[0],
            'invoice_line': [(6, 0, lines)],
            'currency_id': order.pricelist_id.currency_id.id,
            'comment': order.note,
            'payment_term': order.payment_term and order.payment_term.id or False,
            'fiscal_position': order.fiscal_position.id or order.partner_id.property_account_position.id,
            'date_invoice': context.get('date_invoice', False),
            'company_id': order.company_id.id,
            'user_id': order.user_id and order.user_id.id or False,
            'section_id' : order.section_id.id,
            'tb_ref_no':order.tb_ref_no,

        }
        # Care for deprecated _inv_get() hook - FIXME: to be removed after 6.1
        invoice_vals.update(self._inv_get(cr, uid, order, context=context))
        return invoice_vals    

sale_order()   


class sale_order_line(osv.osv):

    _inherit = 'sale.order.line'
    
    def foc_change(self, cr, uid, ids, product, qty=0, context=None):
        product_obj = self.pool.get('product.product')
        domain = {}
        result = {}
        if not product:
            return {'value': {'th_weight': 0,
                'product_uom_qty': qty}, 'domain': {'product_uom': [],
                   'product_uom': []}}
        if qty == 0 :
            raise osv.except_osv(_('No Qty Defined!'), _("Please enter Qty"))
        else:
            result['name'] = 'FOC'
            result['price_unit'] = 0
            result['price_subtotal'] = 0
        return {'value': result, 'domain': domain}    
        
    _columns = { 
               'sale_foc':fields.boolean('FOC')               
               }      
