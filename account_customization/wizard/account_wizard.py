import time
from lxml import etree

from openerp.osv import fields, osv
from openerp.osv.orm import setup_modifiers
from openerp.tools.translate import _

class account_wizard(osv.osv_memory):
    _name = "account.wizard"
    
    
    _columns = {
               'confrim': fields.boolean('Confrim', default=True),
            }

    def confirm_move_lines(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        active_ids = context.get('active_ids', []) or []
        move_data = self.pool['account.move']
        for move in move_data.browse(cr, uid, active_ids, context=context):
            if move.state not in ('draft'):
                raise osv.except_osv(_('Warning!'), _('Selected Entry Lines does not have any account move entries in draft state.'))
            move.button_validate()
        return {'type': 'ir.actions.act_window_close'}
        
        
        
        
        


    
