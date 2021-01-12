from openerp.osv import fields, osv

class branch(osv.osv):
    _inherit = 'res.branch'
    
    _columns = {
                'city_id':fields.many2one('res.city','City'),
            }