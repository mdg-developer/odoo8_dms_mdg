from openerp.osv import fields, osv
from datetime import datetime
from openerp.tools.translate import _
from openerp.fields import Many2one
from openerp import tools

class stock_move(osv.osv):
    
    _inherit = 'stock.move'
    _columns = {
                'manual': fields.boolean('Manual'),        
               }
    
class stock_picking(osv.osv):
    _inherit = 'stock.picking'
    
    def create(self, cr, user, vals, context=None):
        context = context or {}
        id_code = self.pool.get('ir.sequence').get(cr, user,
                                                'picking.code') or '/'        #if ('name' not in vals) or (vals.get('name') in ('/', False)):
            #ptype_id = vals.get('picking_type_id', context.get('default_picking_type_id', False))
            #sequence_id = self.pool.get('stock.picking.type').browse(cr, user, ptype_id, context=context).sequence_id.id
        vals['name'] = id_code
        return super(stock_picking, self).create(cr, user, vals,  context=context)    
    
    