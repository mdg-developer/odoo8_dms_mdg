
from openerp import tools
from openerp.osv import fields, osv
from openerp.tools.translate import _

class res_users(osv.osv):
    _inherit = "res.users"
    _description = "Users"
    
    _columns = {
        'section_ids':fields.many2many('crm.case.section','section_users_rel','uid','section_id','Teams',required=True),
    }
res_users()