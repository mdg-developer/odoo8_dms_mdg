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

class field_audit_question(osv.osv):
    
    _name = "audit.question"  
      
    _columns = {
        'name':fields.char('Myanmar Name'),
        'english_name':fields.char('English Name'),
        'sequence':fields.integer('Sequence'),
        'note':fields.text("Note"),
  }     
