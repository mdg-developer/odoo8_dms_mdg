import datetime
from lxml import etree
import math
import pytz
import urlparse
import openerp
from openerp import tools, api
from openerp.osv import osv, fields
from openerp.osv.expression import get_unaccent_wrapper
from openerp.tools.translate import _

class sales_group(osv.osv):
    
    _name = "sales.group"  
      
    _columns = {
        'name':fields.char('Name'),
#         'branch_id': fields.many2one('res.branch', 'Branch', required=True),
        'product_ids':fields.many2many('product.product', 'product_sale_group_rel', 'sale_group_id', 'product_id', string='Products'),
        'sales_team_line_ids':fields.one2many('crm.case.section', 'sale_group_id', string='Sales Teams'),        
  }     
