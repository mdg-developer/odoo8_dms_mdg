from openerp.osv import fields, osv

class sale_group(osv.osv):
    
    _inherit='res.users'
    _columns={
              'group_id':fields.many2many('product.maingroup',string='Sale Group')
              }
     
sale_group()