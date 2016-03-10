from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp

class sales_return(osv.osv):
    _name = 'sales.return'

    def get_total(self, cr, uid, ids, field, arg, context=None):
        # ~ import ipdb;ipdb.set_trace();
        res = {}
        for data in self.browse(cr, uid, ids, context=context):
            res[data.id] = {
                'amount': 0,
            }
            val = 0
            for line in data.return_line:
                val += line.price_unit * line.product_uom_qty
            res[data.id] = val
        print 'res',res
        return res    

    def get_qty(self, cr, uid, ids, field, arg, context=None):
        # ~ import ipdb;ipdb.set_trace();
        res = {}
        for data in self.browse(cr, uid, ids, context=context):
            res[data.id] = {
                'qty': 0,
            }
            val = 0
            for line in data.return_line:
                val +=line.product_uom_qty
            res[data.id] = int(val)
        return res      
    
    def onchange_customer_id(self, cr, uid, ids, customer_id, context=None):
        cust_obj = self.pool.get('res.partner')
        customer_code = False        
        if customer_id:
            customer = cust_obj.browse(cr, uid, customer_id, context=context)
            customer_code = customer.customer_code           
        return {'value': {'customer_code': customer_code}}  
      
    _columns = {
                'date':fields.date('Return Date'),
                'customer_id':fields.many2one('res.partner','Customer'),
                'customer_code':fields.char('Customer Code'),
                'sale_team':fields.many2one('crm.case.section','Sale Team'),
                'qty' : fields.function(get_qty,string='Qty', readonly=True, store=True,type='integer'),
                'amount' : fields.function(get_total, string='Amount', readonly=True, store=True),
                'notes':fields.text('Notes'),
                'user_id': fields.many2one('res.users', 'Saleman Name', help='The internal user that is in charge of communicating with this contact if any.'),
                'return_line' : fields.one2many('sales.return.line', 'return_id', string='Sale Return Line', copy=True)                
                }
sales_return()

class sales_return_line(osv.osv):

    _name = 'sales.return.line'
            
    def _amount_line(self, cr, uid, ids, field_name, arg, context=None):

        res = {}
        if context is None:
            context = {}
        for line in self.browse(cr, uid, ids, context=context):
            price = line.price_unit * line.product_uom_qty
            res[line.id] =price
        return res

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
                
                'invoice_no':fields.char('Invoice No', required=True),
                'sales_product_name':fields.many2one('product.product', 'Product Name', required=True),
                'product_uom_qty':fields.integer('Quantity', required=True),
                'product_uom':fields.many2one('product.uom','UOM' , required=True),
                'return_id':fields.many2one('sales.return', string='Sales Return', required=True, ondelete='cascade', index=True, copy=False),
                 'price_unit':fields.float('Unit Price', required=True, digits=dp.get_precision('Product Price'), default=0.0),
                 'is_foc':fields.boolean('FOC'),
                'price_subtotal' : fields.function(_amount_line, string='Subtotal', readonly=True, store=True)
                } 
      
    _defaults = {
        'product_uom' : 1,    
        'product_uom_qty':1,
        }