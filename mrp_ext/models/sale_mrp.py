from openerp.osv import fields, osv
from openerp.tools.translate import _

class mrp_production(osv.osv):
    
    _inherit='mrp.production'
    
    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}
        if vals.get('name', '/') == '/':
            vals['name'] = self.pool['ir.sequence'].get(cr, uid, 'mrp.production', context=context) or '/'
        ctx = dict(context or {}, mail_create_nolog=True)
        new_id = super(mrp_production, self).create(cr, uid, vals, context=ctx)
        return new_id    
    
    _columns={                
        'name': fields.char('Reference', required=True, copy=False,
            readonly=True, select=True),              
              }   
    
    _defaults = {        
        'name': lambda obj, cr, uid, context: '/',
         }
        

