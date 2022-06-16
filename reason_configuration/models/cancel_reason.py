from openerp import tools
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import SUPERUSER_ID, models

class CancelReason(osv.osv):
    _name = "cancel.reason"
    _description = "Cancel Reason"
    
    _columns = {
        'name':fields.char('Name'),        
        'active':fields.boolean('Active',default=True),      
    }    
   
