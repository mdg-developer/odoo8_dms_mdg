from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
from datetime import datetime, timedelta
import calendar
from openerp import tools
from openerp.tools.translate import _

class stock_requestion(osv.osv):
    _inherit = 'stock.requisition'


    def reassign_warhouse(self, cr, uid, ids, context=None):
        if not ids: return []
        dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'reassign_rfiwarehouse', 'view_rfi_reassign_location')
        inv = self.browse(cr, uid, ids[0], context=context)
        return {
            'name':_("Reassign Warehouse"),
            'view_mode': 'form',
            'view_id': view_id,
            'view_type': 'form',
            'res_model': 'rfi.reassign.location',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]',
            'context': {
            'default_section_id': inv.sale_team_id.id,
            'default_request_id':inv.id,
            }
        }