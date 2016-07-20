
'''
Created on Jan 22, 2016

@author: 7th Computing
'''

from openerp.osv import fields, osv
from openerp.tools.misc import DEFAULT_SERVER_DATE_FORMAT
from openerp.tools.translate import _
import time
from openerp import netsvc
from openerp import SUPERUSER_ID

# from openerp.exceptions import UserError

import openerp.addons.decimal_precision as dp

class sale_order(osv.osv):
    _inherit = "sale.order"
       
    def _invoiced(self, cursor, user, ids, name, arg, context=None):
        res = {}
        for sale in self.browse(cursor, user, ids, context=context):
            res[sale.id] = True
            invoice_existence = False
            for invoice in sale.invoice_ids:
                if invoice.state!='cancel':
                    invoice_existence = True
                    if invoice.state != 'paid':
                        res[sale.id] = False
                        break
            if not invoice_existence or sale.state == 'manual':
                res[sale.id] = False
        return res
     
    def _invoiced_search(self, cursor, user, obj, name, args, context=None):
        if not len(args):
            return []
        clause = ''
        sale_clause = ''
        no_invoiced = False
        for arg in args:
            if (arg[1] == '=' and arg[2]) or (arg[1] == '!=' and not arg[2]):
                clause += 'AND inv.state = \'paid\''
            else:
                clause += 'AND inv.state != \'cancel\' AND sale.state != \'cancel\'  AND inv.state <> \'paid\'  AND rel.order_id = sale.id '
                sale_clause = ',  sale_order AS sale '
                no_invoiced = True
 
        cursor.execute('SELECT rel.order_id ' \
                'FROM sale_order_invoice_rel AS rel, account_invoice AS inv '+ sale_clause + \
                'WHERE rel.invoice_id = inv.id ' + clause)
        res = cursor.fetchall()
        if no_invoiced:
            cursor.execute('SELECT sale.id ' \
                    'FROM sale_order AS sale ' \
                    'WHERE sale.id NOT IN ' \
                        '(SELECT rel.order_id ' \
                        'FROM sale_order_invoice_rel AS rel) and sale.state != \'cancel\'')
            res.extend(cursor.fetchall())
        if not res:
            return [('id', '=', 0)]
        return [('id', 'in', [x[0] for x in res])]
      
    _columns = {
               'tb_ref_no':fields.char('Order Reference'),
               'payment_type':fields.selection([
                    ('credit', 'Credit'),
                    ('cash', 'Cash'),
#                     ('consignment', 'Consignment'),
#                     ('advanced', 'Advanced')
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
               'invoiced': fields.function(_invoiced, string='Paid',
                fnct_search=_invoiced_search, type='boolean', help="It indicates that an invoice has been paid.",store=True),                           
               }
    
    def onchange_partner_id(self, cr, uid, ids, part, context=None):
        
        if not part:
            return {'value': {'partner_invoice_id': False, 'partner_shipping_id': False,  'payment_term': False, 'fiscal_position': False}}

        part = self.pool.get('res.partner').browse(cr, uid, part, context=context)       
        addr = self.pool.get('res.partner').address_get(cr, uid, [part.id], ['delivery','invoice','contact'])
        pricelist = part.property_product_pricelist and part.property_product_pricelist.id or False
        invoice_part = self.pool.get('res.partner').browse(cr, uid, addr['invoice'], context=context)
        payment_term = invoice_part.property_payment_term and invoice_part.property_payment_term.id or False
        dedicated_salesman = part.user_id and part.user_id.id or uid
        val = {
            'partner_invoice_id': addr['invoice'],
            'partner_shipping_id': addr['delivery'],  
            'customer_code': part.customer_code,                   
            'payment_term': payment_term,
            'user_id': dedicated_salesman,
        }
        delivery_onchange = self.onchange_delivery_id(cr, uid, ids, False, part.id, addr['delivery'], False,  context=context)
        val.update(delivery_onchange['value'])
        if pricelist:
            val['pricelist_id'] = pricelist
        if not self._get_default_section_id(cr, uid, context=context) and part.section_id:
            val['section_id'] = part.section_id.id
        sale_note = self.get_salenote(cr, uid, ids, part.id, context=context)
        if sale_note: val.update({'note': sale_note})  
        return {'value': val}


      
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
               'sale_foc':fields.boolean('FOC'),
             'analytic_account_id': fields.many2one('account.analytic.account', 'Analytic Account'),               
   
               }      
    def product_id_change(self, cr, uid, ids, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False, context=None):
        context = context or {}
        lang = lang or context.get('lang', False)
        if not partner_id:
            raise osv.except_osv(_('No Customer Defined!'), _('Before choosing a product,\n select a customer in the sales form.'))
        warning = False
        product_uom_obj = self.pool.get('product.uom')
        partner_obj = self.pool.get('res.partner')
        product_obj = self.pool.get('product.product')
        partner = partner_obj.browse(cr, uid, partner_id)
        lang = partner.lang
        context_partner = context.copy()
        context_partner.update({'lang': lang, 'partner_id': partner_id})

        if not product:
            return {'value': {'th_weight': 0,
                'product_uos_qty': qty}, 'domain': {'product_uom': [],
                   'product_uos': []}}
        if not date_order:
            date_order = time.strftime(DEFAULT_SERVER_DATE_FORMAT)

        result = {}
        warning_msgs = ''
        product_obj = product_obj.browse(cr, uid, product, context=context_partner)

        uom2 = False
        if uom:
            uom2 = product_uom_obj.browse(cr, uid, uom)
            if product_obj.uom_id.category_id.id != uom2.category_id.id:
                uom = False
        if uos:
            if product_obj.uos_id:
                uos2 = product_uom_obj.browse(cr, uid, uos)
                if product_obj.uos_id.category_id.id != uos2.category_id.id:
                    uos = False
            else:
                uos = False

        fpos = False
        if not fiscal_position:
            fpos = partner.property_account_position or False
        else:
            fpos = self.pool.get('account.fiscal.position').browse(cr, uid, fiscal_position)

        if uid == SUPERUSER_ID and context.get('company_id'):
            taxes = product_obj.taxes_id.filtered(lambda r: r.company_id.id == context['company_id'])
        else:
            taxes = product_obj.taxes_id
        result['tax_id'] = self.pool.get('account.fiscal.position').map_tax(cr, uid, fpos, taxes, context=context)

        if not flag:
            result['name'] = self.pool.get('product.product').name_get(cr, uid, [product_obj.id], context=context_partner)[0][1]
            if product_obj.description_sale:
                result['name'] += '\n'+product_obj.description_sale
        domain = {}
        if (not uom) and (not uos):
            result['product_uom'] = product_obj.uom_id.id
            if product_obj.uos_id:
                result['product_uos'] = product_obj.uos_id.id
                result['product_uos_qty'] = qty * product_obj.uos_coeff
                uos_category_id = product_obj.uos_id.category_id.id
            else:
                result['product_uos'] = False
                result['product_uos_qty'] = qty
                uos_category_id = False
            result['th_weight'] = qty * product_obj.weight
            domain = {'product_uom':
                        [('category_id', '=', product_obj.uom_id.category_id.id)],
                        'product_uos':
                        [('category_id', '=', uos_category_id)]}
        elif uos and not uom: # only happens if uom is False
            result['product_uom'] = product_obj.uom_id and product_obj.uom_id.id
            result['product_uom_qty'] = qty_uos / product_obj.uos_coeff
            result['th_weight'] = result['product_uom_qty'] * product_obj.weight
        elif uom: # whether uos is set or not
            default_uom = product_obj.uom_id and product_obj.uom_id.id
            q = product_uom_obj._compute_qty(cr, uid, uom, qty, default_uom)
            if product_obj.uos_id:
                result['product_uos'] = product_obj.uos_id.id
                result['product_uos_qty'] = qty * product_obj.uos_coeff
            else:
                result['product_uos'] = False
                result['product_uos_qty'] = qty
            result['th_weight'] = q * product_obj.weight        # Round the quantity up

        if not uom2:
            uom2 = product_obj.uom_id
        # get unit price

        if not pricelist:
            warn_msg = _('You have to select a pricelist or a customer in the sales form !\n'
                    'Please set one before choosing a product.')
            warning_msgs += _("No Pricelist ! : ") + warn_msg +"\n\n"
        else:
            ctx = dict(
                context,
                uom=uom or result.get('product_uom'),
                date=date_order,
            )
            price = self.pool.get('product.pricelist').price_get(cr, uid, [pricelist],
                    product, qty or 1.0, partner_id, ctx)[pricelist]
            if price is False:
                warn_msg = _("Cannot find a pricelist line matching this product and quantity.\n"
                        "You have to change either the product, the quantity or the pricelist.")

                warning_msgs += _("No valid pricelist line found ! :") + warn_msg +"\n\n"
            else:
                price = self.pool['account.tax']._fix_tax_included_price(cr, uid, price, taxes, result['tax_id'])
                result.update({'price_unit': price})
                if context.get('uom_qty_change', False):
                    values = {'price_unit': price}
                    if result.get('product_uos_qty'):
                        values['product_uos_qty'] = result['product_uos_qty']
                    return {'value': values, 'domain': {}, 'warning': False}
        if warning_msgs:
            warning = {
                       'title': _('Configuration Error!'),
                       'message' : warning_msgs
                    }
        
        result['analytic_account_id'] =product_obj.product_tmpl_id.analytic_account_id.id
        
        return {'value': result, 'domain': domain, 'warning': warning}