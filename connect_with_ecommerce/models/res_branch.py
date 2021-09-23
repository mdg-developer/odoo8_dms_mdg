from openerp.osv import fields, osv

class branch(osv.osv):
    _inherit = 'res.branch'
    
    _columns = {                
                'city_ids': fields.many2many('res.city', 'res_branch_city_rel', 'branch_id', 'city_id', 'City'),
            }