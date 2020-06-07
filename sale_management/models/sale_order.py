
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
import ast
import openerp.addons.decimal_precision as dp
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP

class sale_order(osv.osv):
    _inherit = "sale.order"

    def _get_default_warehouse(self, cr, uid, context=None):
        company_id = self.pool.get('res.users')._get_company(cr, uid, context=context)
        warehouse_ids = self.pool.get('stock.warehouse').search(cr, uid, [('company_id', '=', company_id)], context=context)
        if not warehouse_ids:
            return False
        return False
        
    def create(self, cr, uid, vals, context=None):
        credit_amt_total=0
        credit_amt=0
        invoice_obj=self.pool.get('account.invoice')
        if context is None:
            context = {}
        if vals.get('name', '/') == '/':
            vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'sale.order', context=context) or '/'
        if vals.get('partner_id'):
            defaults = self.onchange_partner_id(cr, uid, [], vals['partner_id'], context=context)['value']
            vals = dict(defaults, **vals)    
                    
        if vals.get('partner_id') and any(f not in vals for f in ['partner_invoice_id', 'partner_shipping_id', 'pricelist_id', 'fiscal_position']):
            defaults = self.onchange_partner_id(cr, uid, [], vals['partner_id'], context=context)['value']
            if not vals.get('fiscal_position') and vals.get('partner_shipping_id'):
                delivery_onchange = self.onchange_delivery_id(cr, uid, [], vals.get('company_id'), None, vals['partner_id'], vals.get('partner_shipping_id'), context=context)
                defaults.update(delivery_onchange['value'])
            vals = dict(defaults, **vals)

        ctx = dict(context or {}, mail_create_nolog=True)
        new_id = super(sale_order, self).create(cr, uid, vals, context=ctx)
        if new_id:
            sale_data=self.browse(cr, uid, new_id, context=context)   
            amount_total=sale_data.amount_total    
            partner_id=sale_data.partner_id.id
            payment_type=sale_data.payment_type
            ignore_credit_limit=sale_data.ignore_credit_limit
            invoice_ids = invoice_obj.search(cr, uid, [('payment_type','=','credit'),('partner_id', '=', partner_id),('state','=','open')], context=context)
            for invoice_id in invoice_ids:
                invoice_data=invoice_obj.browse(cr, uid, invoice_id, context=context)  
                credit_amt +=invoice_data.residual
            credit_amt_total=amount_total+credit_amt
            if credit_amt_total and partner_id and payment_type:
                partner_data=self.pool.get('res.partner').browse(cr, uid, vals.get('partner_id'), context=context) 
                credit_limit =partner_data.credit_limit
                if credit_amt_total > credit_limit and payment_type=='credit' and ignore_credit_limit==False:
                    raise osv.except_osv(_('Warning'),
                                         _('Credit Limit is Over!!!'))    
        self.message_post(cr, uid, [new_id], body=_("Quotation created"), context=ctx)
        return new_id


    def write(self, cursor, user, ids, vals, context=None):
        """
        Serialise before Write
        @param cursor: Database Cursor
        @param user: ID of User
        @param  ids: ID of current record.
        @param vals: Values of current record.
        @param context: Context(no direct use).
        """
        #Validate before save
        if type(ids) in [list, tuple] and ids:
            ids = ids[0]
            print 'vals_sale_order', vals
 
            if vals.get('partner_id'):
                partner_id = vals['partner_id']
                part = self.pool.get('res.partner').browse(cursor, user, partner_id, context=context)    
                defaults = self.onchange_partner_id_for_write(cursor, user, [], vals['partner_id'], context=context)['value']
                vals = dict(defaults, **vals)
        ctx = dict(context or {}, mail_create_nolog=True)
        new_id = super(sale_order, self).write(cursor, user, ids, vals, context=context)
        return new_id
        
    def is_generate_RFI(self, cr, uid, ids, context=None):
        print 'order', ids
        sale_obj = self.pool.get('sale.order')
        sale_obj.write(cr, uid, ids, {'is_generate': False}, context=context)
        return True    
    
    def get_due_date(self, cursor, user, ids, name, arg, context=None):
        res = {}
        #date_order_str = datetime.strptime(date_order, DEFAULT_SERVER_DATETIME_FORMAT).strftime(DEFAULT_SERVER_DATE_FORMAT)

        for sale in self.browse(cursor, user, ids, context=context):
            res[sale.id] = False
            if sale.date_order and sale.payment_term:
                from datetime import datetime
                date_invoice=datetime.strptime(sale.date_order, DEFAULT_SERVER_DATETIME_FORMAT).strftime(DEFAULT_SERVER_DATE_FORMAT)
                print  'date_invoice ',date_invoice
                pterm = self.pool.get('account.payment.term').browse(cursor, user, sale.payment_term.id, context=context)
                pterm_list = pterm.compute(value=1, date_ref=date_invoice)[0]
                if pterm_list:
                    date_due=max(line[0] for line in pterm_list)
                else:
                    date_due=date_invoice
                res[sale.id] = date_due
        return res 
    def _invoiced(self, cursor, user, ids, name, arg, context=None):
        res = {}
        for sale in self.browse(cursor, user, ids, context=context):
            res[sale.id] = True
            invoice_existence = False
            for invoice in sale.invoice_ids:
                if invoice.state != 'cancel':
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
                'FROM sale_order_invoice_rel AS rel, account_invoice AS inv ' + sale_clause + \
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
             'state': fields.selection([
                        ('draft', 'Draft Quotation'),
                        ('sent', 'Quotation Sent'),
                        ('cancel', 'Cancelled'),
                        ('reversed', 'Reversed'),
                        ('waiting_date', 'Waiting Schedule'),
                        ('progress', 'Invoiced'),
                        ('manual', 'Pending Invoice'),
                        ('shipping_except', 'Shipping Exception'),
                        ('invoice_except', 'Invoice Exception'),
                        ('done', 'Done'),
                        ], 'Status', readonly=True, copy=False, help="Gives the status of the quotation or sales order.\
                          \nThe exception status is automatically set when a cancel operation occurs \
                          in the invoice validation (Invoice Exception) or in the picking list process (Shipping Exception).\nThe 'Waiting Schedule' status is set when the invoice is confirmed\
                           but waiting for the scheduler to run on the order date.", select=True),                
                
               'tb_ref_no':fields.char('Order Reference'),
               'payment_type':fields.selection([
                    ('credit', 'Credit'),
                    ('cash', 'Cash'),
                 #   ('consignment', 'Consignment'),
#                     ('advanced', 'Advanced')
                    ], 'Payment Type', default='cash',readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}),
               'delivery_remark':fields.selection([
                    ('partial', 'Partial'),
                    ('delivered', 'Delivered'),
                    ('none', 'None')
               ], 'Deliver Remark', readonly=True, default='none'),
              # 'due_date':fields.date('Due Date', readonly=True),
              'due_date' : fields.function(get_due_date,type='date', string='Due Date', readonly=True, store=True),
               'so_latitude':fields.float('Geo Latitude', readonly=True),
               'so_longitude':fields.float('Geo Longitude', readonly=True),
                'distance_status':fields.char('Distance Status', readonly=True),
               'customer_code':fields.char('Customer Code'),
               'sale_plan_name':fields.char('Sale Plan Name'),
               'sale_plan_day_id':fields.many2one('sale.plan.day', 'Sale Plan Day'),
               'sale_plan_trip_id':fields.many2one('sale.plan.trip', 'Sale Plan Trip'),
               'validity_date':fields.date(string='Expiration Date', readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}),
               'invoiced': fields.function(_invoiced, string='Paid',
                fnct_search=_invoiced_search, type='boolean', help="It indicates that an invoice has been paid.", store=True),
                'delivery_id': fields.many2one('crm.case.section', 'Delivery Team'),
                'pre_order': fields.boolean("Pre Order" , readonly=True),
                'is_generate':fields.boolean('RFI Generated'  , readonly=True),
         'code':fields.char('Customer ID' , readonly=True),
        'street': fields.char('Street' , readonly=True),
        'street2': fields.char('Street2' , readonly=True),
        'city': fields.many2one('res.city', 'City', ondelete='restrict' , readonly=True),
        'state_id': fields.many2one("res.country.state", 'State', ondelete='restrict' , readonly=True),
        'country_id': fields.many2one('res.country', 'Country', ondelete='restrict' , readonly=True),
        'township': fields.many2one('res.township', 'Township', ondelete='restrict' , readonly=True),
         'payment_term': fields.many2one('account.payment.term', 'Payment Term', readonly=False),
         'issue_warehouse_id':fields.many2one('stock.warehouse', 'Warehouse'),
         'promos_line_ids':fields.one2many('sale.order.promotion.line', 'promo_line_id', 'Promotion Lines'),
         'credit_history_ids':fields.one2many('sale.order.credit.history', 'sale_order_id', 'Credit Lines',copy=True),
        'cancel_user_id': fields.many2one('res.users', 'Cancel By'),
        'is_entry': fields.boolean('Is Entry Data',default=False),
        'rebate_later': fields.boolean("Rebate Later" , default=False,readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}),
        'credit_allow':fields.boolean('Credit Allow',default=False),
        'ignore_credit_limit':fields.boolean('Ignore Credit Limitation',default=False,readonly=True, states={'draft': [('readonly', False)]}),
        'credit_invoice_balance' :fields.float('Credit Invoice Balance'),   
        'credit_limit_amount' :fields.float('Credit Limit'),   
        'credit_balance' :fields.float('Credit Balance'),   
        'reverse_date':fields.date('Date for Reverse',required=False),
        'pre_sale_order_id':fields.many2one('sale.order', 'Original Pre Sale Order No'),
        'order_team':fields.many2one('crm.case.section', 'Order Team'),

               }
    def action_reverse(self, cr, uid, ids, context=None):
        pick_obj = self.pool.get('stock.picking')
        invoice_obj = self.pool.get('account.invoice')
        move_obj = self.pool.get('stock.move')
        stockDetailObj = self.pool.get('stock.transfer_details')
        detailObj = None
        so_value = self.browse(cr, uid, ids[0], context=context)
        so_no=so_value.name
        reverse_date=so_value.reverse_date    
        if not reverse_date:
            raise osv.except_osv(_('Warning'),
                     _('Please Insert Reverse Date'))            
        pick_ids = []
        pick_ids = pick_obj.search(cr, uid, [('origin', '=', so_no),('state','=','done')], context=context)
        invoice_ids = invoice_obj.search(cr, uid, [('origin', '=', so_no),('state','in',('open','credit_state'))], context=context)
        #choose the view_mode accordingly
        for pick_id in pick_ids:
            pick = pick_obj.browse(cr, uid, pick_id, context=context)                
            #Create new picking for returned products
            pick_type_id = pick.picking_type_id.return_picking_type_id and pick.picking_type_id.return_picking_type_id.id or pick.picking_type_id.id
            new_picking = pick_obj.copy(cr, uid, pick.id, {
                'move_lines': [],
                'picking_type_id': pick_type_id,
                'state': 'draft',
                'origin': pick.name,
            }, context=context)
            for move in pick.move_lines:
                if move.origin_returned_move_id.move_dest_id.id and move.origin_returned_move_id.move_dest_id.state != 'cancel':
                    move_dest_id = move.origin_returned_move_id.move_dest_id.id
                else:
                    move_dest_id = False
                if move.product_uom_qty >0:                      
                    
                    move_id=move_obj.copy(cr, uid, move.id, {
                                        'product_id': move.product_id.id,
                                        'product_uom_qty': move.product_uom_qty,
                                        'product_uos_qty': move.product_uom_qty * move.product_uos_qty / move.product_uom_qty,
                                        'picking_id': new_picking,
                                        'state': 'confirmed',
                                        'location_id': move.location_dest_id.id,
                                        'location_dest_id': move.location_id.id,
                                        'picking_type_id': pick_type_id,
                                        'warehouse_id': pick.picking_type_id.warehouse_id.id,
                                        'origin_returned_move_id': move.id,
                                        'procure_method': 'make_to_stock',
                                      #  'restrict_lot_id': data_get.lot_id.id,
                                        'move_dest_id': move_dest_id,
                                        'origin':'Reverse ' + move.origin,
                                })
                    move_obj.action_done(cr, uid, move_id, context=context)  
            cr.execute("update stock_move set date=%s where origin=%s", (reverse_date, 'Reverse ' +move.origin,))

         #   pick_obj.action_confirm(cr, uid, [new_picking], context=context)
          #  pick_obj.force_assign(cr, uid, [new_picking], context)  
            #wizResult = pick_obj.do_enter_transfer_details(cr, uid, [new_picking], context=context)
            # pop up wizard form => wizResult
            #detailObj = stockDetailObj.browse(cr, uid, wizResult['res_id'], context=context)
            #if detailObj:
                #detailObj.do_detailed_transfer()
        for invoice_id in invoice_ids:
            invoice = invoice_obj.browse(cr, uid, invoice_id, context=context)  
            if invoice.payment_type=='credit': 
                invoice_obj.cancel_credit(cr, uid, [invoice_id], context=context) 
            else:    
                invoice.signal_workflow('invoice_cancel')
        return self.write(cr, uid, ids, {'state':'reversed'})    
            
    def on_change_payment_type(self, cr, uid, ids, partner_id, payment_type, context=None):
        values = {}
        print 'payment_type', payment_type
        if payment_type == 'cash':
            payment_term = 1
        elif payment_type == 'credit':
            partner = self.pool.get('res.partner').browse(cr, uid, partner_id, context=context)
            payment_term = partner.property_payment_term and partner.property_payment_term.id or False
        else:
            partner = self.pool.get('res.partner').browse(cr, uid, partner_id, context=context)
            payment_term = partner.property_payment_term and partner.property_payment_term.id or False        
        values = {
             'payment_term':payment_term, }
        domain = {'payment_term': [('id', '=', payment_term)]}
        return {'value': values, 'domain': domain}
    
    def on_change_section_id(self, cr, uid, ids, section_id, context=None):
        values = {}
        print 'payment_type', section_id
        issue_warehouse_id = False
        delivery_id = False
        branch_id = False
        if section_id:
            team = self.pool.get('crm.case.section').browse(cr, uid, section_id, context=context)
            issue_warehouse_id = team.warehouse_id and  team.warehouse_id.id or False
            delivery_id = team.delivery_team_id and  team.delivery_team_id.id or False
            branch_id = team.branch_id and  team.branch_id.id or False
        values = {
             'issue_warehouse_id':issue_warehouse_id,
             'delivery_id':delivery_id,
             'warehouse_id':issue_warehouse_id,
             'branch_id':branch_id,
              }
        return {'value': values}
    
    def onchange_partner_id(self, cr, uid, ids, part, context=None):
        invoice_obj=self.pool.get('account.invoice')
        credit_amt_total=credit_limit=credit_balance=0
        data_line = []
        if not part:
            return {'value': {'partner_invoice_id': False, 'partner_shipping_id': False, 'payment_term': False, 'fiscal_position': False}}

        part = self.pool.get('res.partner').browse(cr, uid, part, context=context)       
        addr = self.pool.get('res.partner').address_get(cr, uid, [part.id], ['delivery', 'invoice', 'contact'])
        pricelist = part.property_product_pricelist and part.property_product_pricelist.id or False
        invoice_part = self.pool.get('res.partner').browse(cr, uid, addr['invoice'], context=context)
        payment_term = invoice_part.property_payment_term and invoice_part.property_payment_term.id or False
        credit_allow=False
        if part.credit_allow == True:
            payment_type = 'credit'
            credit_allow=True
        elif part.is_consignment == True:
            payment_type = 'consignment'
        else:
            payment_type = 'cash'
            payment_term = 1
        dedicated_salesman = part.user_id and part.user_id.id or uid
        if payment_type =='credit' and part:
            invoice_ids = invoice_obj.search(cr, uid, [('payment_type','=','credit'),('partner_id', '=', part.id),('state','=','open')], context=context)
            for invoice_id in invoice_ids:
                invoice_data=invoice_obj.browse(cr, uid, invoice_id, context=context)  
                credit_amt_total +=invoice_data.residual 
                cr.execute("select %s::date - current_date",(invoice_data.date_due,))
                day=cr.fetchone()[0]
                data_line.append({
                                'date':invoice_data.date_invoice,
                                'invoice_no':invoice_data.number,
                                'invoice_amt':invoice_data.amount_total,
                                'paid_amount':invoice_data.paid_amount,
                                'balance':invoice_data.residual,
                                'due_date':invoice_data.date_due,
                                'balance_day':int(day),
                                'branch_id':invoice_data.branch_id.id,
                                'status':invoice_data.state,
                                          })   
            credit_limit =part.credit_limit
            credit_balance=credit_limit-credit_amt_total

                 
        val = {
            'partner_invoice_id': addr['invoice'],
            'partner_shipping_id': addr['delivery'],
            'customer_code': part.customer_code,
            'payment_term': payment_term,
            'user_id': dedicated_salesman,
            'payment_type':payment_type,
            'code': part.customer_code,
            'street': part.street,
            'street2': part.street2,
            'city': part.city and part.city.id or False,
            'state_id': part.state_id and part.state_id.id or False,
            'country_id': part.country_id and part.country_id.id or False,
            'township': part.township and part.township.id or False,
            'credit_allow':credit_allow,
            'credit_history_ids':data_line,
            'credit_invoice_balance' :credit_amt_total,   
            'credit_limit_amount' :credit_limit,   
            'credit_balance' :credit_balance, 
                }
        domain = {'payment_term': [('id', '=', payment_term)]}
        print 'domain', domain
        delivery_onchange = self.onchange_delivery_id(cr, uid, ids, False, part.id, addr['delivery'], False, context=context)
        val.update(delivery_onchange['value'])
        if pricelist:
            val['pricelist_id'] = pricelist
#         if not self._get_default_section_id(cr, uid, context=context) and part.section_id:
#             val['section_id'] = part.section_id.id

        sale_note = self.get_salenote(cr, uid, ids, part.id, context=context)
        if sale_note: val.update({'note': sale_note})  
        return {'value': val, 'domain': domain}
    
    def onchange_partner_id_for_write(self, cr, uid, ids, part, context=None):
        
        if not part:
            return {'value': {'partner_invoice_id': False, 'partner_shipping_id': False, 'payment_term': False, 'fiscal_position': False}}

        part = self.pool.get('res.partner').browse(cr, uid, part, context=context)       
        addr = self.pool.get('res.partner').address_get(cr, uid, [part.id], ['delivery', 'invoice', 'contact'])
        pricelist = part.property_product_pricelist and part.property_product_pricelist.id or False
        invoice_part = self.pool.get('res.partner').browse(cr, uid, addr['invoice'], context=context)
        payment_term = invoice_part.property_payment_term and invoice_part.property_payment_term.id or False
        if part.credit_allow == True:
            payment_type = 'credit'
        elif part.is_consignment == True:
            payment_type = 'consignment'
        else:
            payment_type = 'cash'
            payment_term = 1
        dedicated_salesman = part.user_id and part.user_id.id or uid
        val = {
            'partner_invoice_id': addr['invoice'],
            'partner_shipping_id': addr['delivery'],
            'customer_code': part.customer_code,
          #  'payment_term': payment_term,
            'user_id': dedicated_salesman,
          #  'payment_type':payment_type,
            'code': part.customer_code,
            'street': part.street,
            'street2': part.street2,
            'city': part.city and part.city.id or False,
            'state_id': part.state_id and part.state_id.id or False,
            'country_id': part.country_id and part.country_id.id or False,
            'township': part.township and part.township.id or False,
        }
        print 'payment_typepayment_type', payment_type
        domain = {'payment_type': [('payment_type', '=', payment_type)]}
        print 'domain', domain
        delivery_onchange = self.onchange_delivery_id(cr, uid, ids, False, part.id, addr['delivery'], False, context=context)
        val.update(delivery_onchange['value'])
        if pricelist:
            val['pricelist_id'] = pricelist
#         if not self._get_default_section_id(cr, uid, context=context) and part.section_id:
#             val['section_id'] = part.section_id.id
        sale_note = self.get_salenote(cr, uid, ids, part.id, context=context)
        if sale_note: val.update({'note': sale_note})  
        return {'value': val, 'domain': domain}    
  
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



    _defaults = {
        'warehouse_id': _get_default_warehouse,

    }
    def create_promotion_line(self, cursor, user, vals, context=None):
        
        try : 
            so_promotion_line_obj = self.pool.get('sale.order.promotion.line')
            str = "{" + vals + "}"
                
            str = str.replace("'',", "',")  # null
            str = str.replace(":',", ":'',")  # due to order_id
            str = str.replace("}{", "}|{")
            new_arr = str.split('|')
            result = []
            for data in new_arr:
                x = ast.literal_eval(data)
                result.append(x)
            promo_line = []
            for r in result:                
                promo_line.append(r)  
            if promo_line:
                for pro_line in promo_line:
                
                    cursor.execute('select id From sale_order where name  = %s ', (pro_line['promo_line_id'],))
                    data = cursor.fetchall()
                    if data:
                        saleOrder_Id = data[0][0]
                    else:
                        saleOrder_Id = None
                    cursor.execute("select manual from promos_rules where id=%s", (pro_line['pro_id'],))
                    manual = cursor.fetchone()[0]
                    if manual is not None:
                        manual = manual
                    else:
                        manual = False                                    
                    promo_line_result = {
                        'promo_line_id':saleOrder_Id,
                        'pro_id':pro_line['pro_id'],
                        'from_date':pro_line['from_date'],
                        'to_date':pro_line['to_date'] ,
                         'manual':manual,

                        }
                    so_promotion_line_obj.create(cursor, user, promo_line_result, context=context)
            return True
        except Exception, e:
            return False
    
     
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
class sale_order_credit_history(osv.osv):
    _name = 'sale.order.credit.history'
    _columns = {  
                'sale_order_id':fields.many2one('sale.order', 'Credit History'),
                'date':fields.date('Invoice Date'),
                'invoice_no':fields.char('Inv No.'),
                'invoice_amt':fields.float('Amount'),
                'paid_amount':fields.float('Paid Amount'),
                'balance':fields.float('Balance'),
                'due_date':fields.date('Due Date'),
                'balance_day':fields.integer('Balance Days'),
                'branch_id':fields.many2one('res.branch','Branch'),
                'status':fields.char('Status'),
                }
  
class sale_order_promotion_line(osv.osv):
    _name = 'sale.order.promotion.line'
    _columns = {
              'promo_line_id':fields.many2one('sale.order', 'Promotion line'),
              'pro_id': fields.many2one('promos.rules', 'Promotion Rule', change_default=True, readonly=False),
              'from_date':fields.datetime('From Date'),
              'to_date':fields.datetime('To Date'),
              'manual':fields.boolean('Manual'),
              'product_id': fields.many2one('product.product', 'Product',readonly=False),
              'is_foc': fields.boolean('Is FOC',readonly=False),
              'is_discount': fields.boolean('Is Discount',readonly=False),
              'foc_qty': fields.float('Foc Qty',readonly=False),
              'discount_amount': fields.float('Discount Amount',readonly=False),
              'discount_percent': fields.float('Discount Percent',readonly=False),                          
              }
    _defaults = {
        'manual':False,
        'is_foc':False,
        'is_discount':False,      
    }
    
    def onchange_promo_id(self, cr, uid, ids, pro_id, context=None):
            result = {}
            promo_pool = self.pool.get('promos.rules')
            datas = promo_pool.read(cr, uid, pro_id, ['from_date', 'to_date', 'manual'], context=context)
    
            if datas:
                result.update({'from_date':datas['from_date']})
                result.update({'to_date':datas['to_date']})
                result.update({'manual':datas['manual']})
            return {'value':result}
            
sale_order_promotion_line()
