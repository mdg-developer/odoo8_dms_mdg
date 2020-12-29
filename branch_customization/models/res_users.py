
from openerp import tools
from openerp.osv import fields, osv
from openerp.tools.translate import _

class res_users(osv.osv):
    _inherit = "res.users"
    _description = "Users"
    
    def _get_branch(self,cr, uid, context=None, uid2=False):
        if not uid2:
            uid2 = uid
        user = self.pool.get('res.users').read(cr, uid, uid2, ['branch_id'], context)
        branch_id = user.get('branch_id', False)
        return branch_id and branch_id[0] or False    
    
    _columns = {
        'branch_ids':fields.many2many('res.branch','res_branch_users_rel','user_id','bid','Branches',required=True),
        'sale_team_ids':fields.many2many('crm.case.section','res_sale_teams_rel','user_id','team_id','Sale Teams',required=True),
        'main_group_ids':fields.many2many('product.maingroup','res_main_group_rel','user_id','main_group','Main Groups',required=True),
    }
res_users()