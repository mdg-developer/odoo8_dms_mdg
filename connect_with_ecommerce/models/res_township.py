from openerp.osv import fields, osv
from openerp.tools.translate import _

class res_city(osv.osv):
    _inherit = "res.township"
    
    _columns = {
               'delivery_team_id':fields.many2one('crm.case.section', 'Delivery Team',required=False),
               'branch_id':fields.many2one('res.branch', 'Branch',required=False),
               'pick_up':fields.boolean('Pick Up', default=False),
               }
