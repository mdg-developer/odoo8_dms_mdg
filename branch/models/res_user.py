from openerp.osv import fields, osv

class sale_group(osv.osv):
    
    _inherit='res.users'
    _columns={
              'branch_id':fields.many2one('branch',string='Branch')
              }
     
sale_group()