from openerp import tools
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import SUPERUSER_ID, models

class ReviseReason(osv.osv):
    _name = "revise.reason"
    _description = "Revise Reason"
    
    _columns = {
        'name':fields.char('Name'),        
        'active':fields.boolean('Active',default=True),      
    }    
   
