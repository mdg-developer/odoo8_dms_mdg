import time

import os
from datetime import datetime
from datetime import timedelta  
from dateutil.relativedelta import relativedelta
from dateutil import parser
import time
from openerp.osv import fields , osv
from openerp.tools.translate import _
import datetime
from openerp.osv.fields import _column

class prodcut_agree_rate(osv.osv):
    _name ="product.agree.rate"
    _description="Product Agree Rate"
    _columns ={
        'name':fields.char("Description",required = True),
        'date':fields.date("Date",required = True),
        'agress_lines':fields.one2many('product.agree.rate.line', 'line_id', 'Product Lines',copy=True),
}

class product_agree_rate_line(osv.osv):
    _name ="product.agree.rate.line"
    _description="Product Agree Rate Line"
    
    _columns ={
              'line_id':fields.many2one('product.agree.rate',"Product Line",required=True),
              'product_id':fields.many2one('product.product',"Product Name",required=True),
              'agreed_price':fields.float('Agreed Price',required =True),
              'currency':fields.many2one('res.currency','Currency',required=True),
              'rate':fields.float("Rate",required = True),
              }
    

