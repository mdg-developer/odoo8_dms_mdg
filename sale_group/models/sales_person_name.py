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

class sales_person_name(osv.osv):
    
    _name = "sales.person.name"  
      
    _columns = {
                'name':fields.char('Name'),
                'branch_id': fields.many2one('res.branch', 'Branch'),    
                'active':fields.boolean('Active' , default=True),   
            }     
