from openerp.osv import osv, fields
from openerp import netsvc
from openerp.tools.translate import _
from openerp import tools


COMPARATORS = [
    ('==', _('equals')),
    ('!=', _('not equal to')),
    ('>', _('greater than')),
    ('>=', _('greater than or equal to')),
    ('<', _('less than')),
    ('<=', _('less than or equal to')),
]

class customer_rebate_config(osv.Model):
    "Customer Rebate"
    _name = "customer.rebate.config"
    _columns = {
        
        'code':fields.char('Code', required=True),
        'name':fields.char('Description', required=True),
        'date':fields.date('Date', required=True),
        'sale_channel_id':fields.many2many('sale.channel', string='Sales Channels'),
        'branch_id':fields.many2one('res.branch', string='Branch'),
        'remark':fields.text('Remark'),                  
        'from_date':fields.date('From Date',required=True),
        'to_date':fields.date('To Date',required=True),
        'expressions':fields.one2many('customer.rebate.config.conditions.exps' , 'rebate' ,string='Expressions/Conditions'),
        
    }
    
class customer_rebate_config_Exprs(osv.Model):
    "Expressions for conditions"
    _name = 'customer.rebate.config.conditions.exps'
 
    _columns = {
        'product_id':fields.many2one('product.product', string='Product' ,required=True),
        'product_uom_id':fields.many2one('product.uom', string='UOM'),
        'sale_qty':fields.float(string='Qty',required=True), 
        'comparator':fields.selection(COMPARATORS, 'Comparator', required=True),
        'rebate_percentage':fields.float(string='Rebate Percentage'),
        'rebate_amount':fields.float('Rebate Amount'),
        'foc_qty':fields.float('FOC Quantity'),
        'foc_product_id':fields.many2one('product.product', string='FOC To Give Product'),
        'rebate': fields.many2one('customer.rebate.config', 'Promotion'),
    }
    _defaults = {
        'comparator': lambda * a:'==',
        }