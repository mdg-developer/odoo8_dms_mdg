from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.exceptions import except_orm, Warning, RedirectWarning
from openerp.osv import orm

class product_service_claim(osv.osv):

    _name = "product.service.claim"    
    
    def _get_default_branch(self, cr, uid, context=None):
        branch_id = self.pool.get('res.users')._get_branch(cr, uid, context=context)
        if not branch_id:
            raise osv.except_osv(_('Error!'), _('There is no default branch for the current user!'))
        return branch_id        
    def on_change_branch_id(self, cr, uid, ids, branch_id, context=None):
        values = {}
        if branch_id:
            warehouse_id = self.pool.get('stock.warehouse').search(cr, uid, [('branch_id', '=', branch_id)], context=context)[0]
            if warehouse_id:
                warehouse_id = warehouse_id
            else:
                warehouse_id = None
            values = {
                'warehouse_id':warehouse_id,
            }
        return {'value': values}  
            
    def on_change_warehouse_id(self, cr, uid, ids, warehouse_id, context=None):
        values = {}
        if warehouse_id:
            warehouse = self.pool.get('stock.warehouse').browse(cr, uid, warehouse_id, context=context)
            location_id = warehouse.out_type_id.default_location_src_id.id
            values = {
                'location_id':location_id,
            }
        return {'value': values}      
    def on_change_principle_id(self, cr, uid, ids, principle_id, context=None):
        values = {}
        if principle_id:
            journal_id = self.pool.get('account.journal').search(cr, uid, [('claim_journal', '=', True)], context=context)[0]
            if journal_id:
                journal_id = journal_id
            else:
                journal_id = None
            values = {
                'journal_id':journal_id,
            }
        return {'value': values}          
    
    def get_issue_date(self, cr, uid, ids, field, arg, context=None):
        
        res = {}
        for data in self.browse(cr, uid, ids, context=context):
            res[data.id] = len(data.plan_line)
            print 'res', res
        return res                
    _columns = {
        'name': fields.char('Ref ID', readonly=True),
        'date': fields.date('Request Date', required=True),
        'user_id': fields.many2one('res.partner', 'Receiver', required=True),
        'branch_id': fields.many2one('res.branch', 'Branch', required=True),
        'warehouse_id': fields.many2one('stock.warehouse', 'Issue Warehouse', required=True),
        'location_id': fields.many2one('stock.location', 'Issue Location', required=True),
        'product_lines': fields.one2many('product.service.claim.line', 'line_id', 'Items Lines', copy=True),
         'is_claim_attachment': fields.boolean('Memo Attached'),
         'claim_attachment':fields.char('Credit Note Ref No'),
         'memo_refno':fields.char('Memo Ref No'),
         'issue_type':fields.selection([
            ('donation', 'Donation'),
            ('sampling', 'Sampling'),
            ('destruction', 'Destruction'),
            ('other', 'Others'),
            ], 'Issue Type'),
          'is_claim': fields.boolean('To Claim'),
          # 'principle_id': fields.many2one('product.maingroup', 'Principle'),
          'principle_id'  : fields.many2one('res.partner', 'Principle' , domain=[('supplier', '=', True)]),
          'principle_support': fields.float('Principle Support'),
          'picking_id': fields.many2one('stock.picking', 'DO Ref No', readonly=True),
         'debit_note':fields.many2one('account.invoice', 'Debit Note Ref No', readonly=True),
         # 'receive_date': fields.function(type='date',string='Issue Date', required=False),
          'receive_date': fields.related('picking_id', 'date_done', type='datetime', string='Issue Date', store=False, readonly=True),
        'journal_id': fields.many2one('account.journal', 'Journal', required=False),
       'pricelist_id': fields.many2one('product.pricelist', 'Price list', required=False),
        'note': fields.text('Remark'),
         'state': fields.selection([
            ('draft', 'Draft'),
            ('approve', 'Awaiting Claimed'),
            ('cancel', 'Cancelled'),
            ('done', 'Done'),
            ], 'Status', readonly=True, copy=False, help="Gives the status of the quotation or sales order.\
              \nThe exception status is automatically set when a cancel operation occurs \
              in the invoice validation (Invoice Exception) or in the picking list process (Shipping Exception).\nThe 'Waiting Schedule' status is set when the invoice is confirmed\
               but waiting for the scheduler to run on the order date.", select=True),
    }
    _defaults = {        
         'date':fields.datetime.now,
          'user_id':lambda obj, cr, uid, context: uid,
          'issue_type':'donation',
        'branch_id': _get_default_branch,
        'state': 'draft',
       # 'receive_date':fields.datetime.now,
                  }    
    

        
    def create(self, cursor, user, vals, context=None):
        id_code = self.pool.get('ir.sequence').get(cursor, user,
                                                'product.service.claim.code') or '/'
        vals['name'] = id_code

        return super(product_service_claim, self).create(cursor, user, vals, context=context)
    
    def approve(self, cr, uid, ids, context=None):
       
        return self.write(cr, uid, ids, {'state': 'approve'})    
    
    def sumit(self, cr, uid, ids, context=None):
        sell_data = self.browse(cr, uid, ids, context=context)
        name = sell_data.name
        journal_id = sell_data.journal_id.id
        partner_id = sell_data.principle_id.id
        note = sell_data.note
        issue_type = sell_data.issue_type
        product_line_obj = self.pool.get('product.service.claim.line')
        invoice_obj = self.pool.get('account.invoice')   
        invoice_line_obj = self.pool.get('account.invoice.line')   
        payment_obj = self.pool.get('account.payment.term')   
        currency_obj = self.pool.get('res.currency')   
        payment_id = payment_obj.search(cr, uid, [('name', '=', 'Immediate Payment')], context=context)
        currency_id = currency_obj.search(cr, uid, [('name', '=', 'MMK')], context=context)
        inv = {
            'name': name,
            'origin': name,
            'type': 'in_refund',
            'journal_id': journal_id,
            'reference': name,
            'is_nonsale':True,
         #   'account_id': a,
            'partner_id': partner_id,
            # 'invoice_line': [(6, 0, lines_ids)],
            'currency_id': currency_id[0],
            'comment': note,
            'payment_term': payment_id[0],
            'fiscal_position': sell_data.principle_id.property_account_position.id
        }
        inv_id = invoice_obj.create(cr, uid, inv, context=context)
        product_line_ids = product_line_obj.search(cr, uid, [('line_id', '=', ids[0])], context=context)
        if product_line_ids and inv_id:
            for product_line_id in product_line_ids:  
                invoice_line = product_line_obj.browse(cr, uid, product_line_id, context=context)

                if  issue_type == 'donation':
                    account_id = invoice_line.product_id.product_tmpl_id.categ_id.property_account_income_categ.id
                if  issue_type == 'sampling':
                    account_id = invoice_line.product_id.product_tmpl_id.categ_id.property_account_income_categ.id           
                if  issue_type == 'other':
                    account_id = invoice_line.product_id.product_tmpl_id.categ_id.property_account_income_categ.id
                if  issue_type == 'destruction':
                    account_id = invoice_line.product_id.product_tmpl_id.categ_id.property_account_income_categ.id
                inv_line = {'name': invoice_line.product_id.name,
                            'invoice_id':inv_id,
                    'account_id': account_id,
                    'price_unit': invoice_line.claim_price or 0.0,
                    'quantity': invoice_line.quantity,
                    'product_id': invoice_line.product_id.id or False,
                    'uos_id': invoice_line.uom_id.id or False,
                    'agreed_price':invoice_line.quantity *  invoice_line.claim_price ,
                    'gross_margin':0.0,
                    }
                invoice_line_obj.create(cr, uid, inv_line, context=context)
        return self.write(cr, uid, ids, {'state': 'done', 'debit_note':inv_id, })        
    
    def cancel(self, cr, uid, ids, context=None):
        sell_data = self.browse(cr, uid, ids, context=context)
        picking_obj = self.pool.get('stock.picking')
        if sell_data.receive_date:
            raise osv.except_osv(_('Warning'),
                                 _('You Cannot Cancel This Form!')) 
        picking_id =sell_data.picking_id
        if picking_id:
            picking_obj.action_cancel(cr, uid, picking_id.id, context=context)
        return self.write(cr, uid, ids, {'state': 'cancel'})       
            
    def show_claim_price(self, cr, uid, ids, context=None):
        sell_data = self.browse(cr, uid, ids, context=context)
        principle_support = sell_data.principle_support
        sell_line_obj = self.pool.get('product.service.claim.line')
        for line_data in sell_data.product_lines:
            if principle_support > 0:
                product_qty = line_data.quantity
                price_unit = line_data.price_unit
                total_price = price_unit * product_qty
                claim_price = price_unit * (principle_support / 100)
                total_claim = total_price * (principle_support / 100)
                cr.execute("update product_service_claim_line set claim_price =%s,claim_total=%s where id =%s", (claim_price, total_claim, line_data.id,))
        return True               
    
product_service_claim()   

class product_service_claim_line(osv.osv):

    _name = "product.service.claim.line"    
    
    def _amount_total(self, cr, uid, ids, prop, arg, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            product_qty = line.quantity
            price_unit = line.price_unit
            total_price = price_unit * product_qty
            res[line.id] = total_price
        return res    
    
#     def create(self, cr, uid, values, context=None):
#         if values.get('line_id') and values.get('product_id') and  any(f not in values for f in ['price_unit', 'quantity', 'uom_id']):
#             order = self.pool['product.nonsell.issue'].read(cr, uid, values['line_id'], ['pricelist_id'], context=context)
#             defaults = self.on_change_product_id(cr, uid, [], values['product_id'], order['pricelist_id'][0], context=dict(context or {}))['value']
#             values = dict(defaults, **values)
#         return super(product_service_claim_line, self).create(cr, uid, values, context=context)
    

    _columns = {
        'line_id': fields.many2one('product.service.claim', 'Master Data'),
        'product_id': fields.many2one('product.product', 'Product Name', required=True),
        'uom_id': fields.many2one('product.uom', 'UoM', required=True),
        'quantity': fields.float('Qty', required=True),
        'price_unit': fields.float('Unit Price', required=False),
        'sub_total':fields.function(_amount_total, string='Sub Total', store=True),
        'claim_price':fields.float('Claim Price' , readonly=True),
        'claim_total':fields.float('Claim Total' , readonly=True),
        'sequence':fields.integer('Sequence'),
    }
    
    def on_change_product_id(self, cr, uid, ids, product_id, context=None):
        values = {}
        domain = {}     
        if product_id:
            product = self.pool.get('product.product').browse(cr, uid, product_id, context=context)
            cr.execute("""SELECT uom.id FROM product_product pp 
                          LEFT JOIN product_template pt ON (pp.product_tmpl_id=pt.id)
                          LEFT JOIN product_template_product_uom_rel rel ON (rel.product_template_id=pt.id)
                          LEFT JOIN product_uom uom ON (rel.product_uom_id=uom.id)
                          WHERE pp.id = %s""", (product.id,))
            uom_list = cr.fetchall()
            print 'UOM-->>', uom_list            
            domain = {'uom_id':
                        [('id', 'in', uom_list)], }          
            values = {
                'uom_id': product.product_tmpl_id.uom_id and product.product_tmpl_id.uom_id.id or False,
                'sequence':product.sequence,
                'quantity':1,                
            }
        return {'value': values, 'domain': domain}


product_service_claim_line()   

