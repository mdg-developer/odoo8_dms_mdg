import os
from datetime import datetime
from datetime import timedelta  
from dateutil.relativedelta import relativedelta
from dateutil import parser
import time
import openerp.addons.decimal_precision as dp

from openerp.osv import fields , osv
from openerp.tools.translate import _
import datetime
from openerp.osv.fields import _column

class prodcut_agree_rate(osv.osv):
    _name ="product.agree.rate"
    _description="Product Agree Rate"
    _columns ={
        'name':fields.char("Description",required = True),
        'from_date':fields.date("From Date",required = True),
        'date':fields.date("To Date",required = True),
        'partner_id':fields.many2one("res.partner","Supplier"),
        'currency':fields.many2one('res.currency','Purchase Currency',required=True),
        'rate':fields.float("Rate",required = True),
        'agress_lines':fields.one2many('product.agree.rate.line', 'line_id', 'Product Lines',copy=True),
}

class product_agree_rate_line(osv.osv):
    _name ="product.agree.rate.line"
    _description="Product Agree Rate Line"
    
    _columns ={
              'line_id':fields.many2one('product.agree.rate',"Product Line",required=True),
              'product_id':fields.many2one('product.product',"Product Name",required=True),
              'agreed_price':fields.float('Agreed Price',required =True, digits_compute=dp.get_precision('Cost Price')),
#               'currency':fields.many2one('res.currency','Currency',required=True),
#               'rate':fields.float("Rate",required = True),
              }
    

