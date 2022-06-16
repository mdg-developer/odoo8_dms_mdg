from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
import time

class transport_type(osv.osv):
    _name = "transport.type"
    _columns = {
        'name': fields.char('Name'),
        'notes': fields.text('Note'),
                }

class stock_picking(osv.osv):
    _inherit = "stock.picking"    
    _columns = {
        'dispatched_from':fields.many2one('stock.warehouse', 'Dispatched from'),
        'dispatched_to':fields.many2one('stock.warehouse', 'Dispatched To'),
        'waybill_no': fields.char('Way Bill', select=True, states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}, copy=False),
        'is_waybill':fields.boolean('Is Way Bill', copy=False),
        'loading_date' : fields.datetime('Loading Date & Time' , states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}, copy=False),
        'loading_by': fields.char('Loading By', states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}, copy=False),
        'checked_by':fields.char("Checked By", states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}, copy=False),
        'approved_by': fields.char('Approved By', states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}, copy=False),
        'transport_type': fields.many2one('transport.type', 'Transport Type', states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}, copy=False),
        'transport_mode': fields.char('Transport Mode', states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}, copy=False),
        'vehicle_no': fields.char('Vehicle No', states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}, copy=False),
        'consignee': fields.char('Consignee', states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}, copy=False),
        'departure_date' : fields.datetime('Departure Date & Time', states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}, copy=False),
        'transported_by': fields.char('Transported By', states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}, copy=False),
        'received_by':fields.char("Received By" , states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}, copy=False),
               }
    _defaults = {  
                 'is_waybill':False,
                 }  
    
class stock_picking_type(osv.osv):
    _inherit = "stock.picking.type"
    _description = "The picking type determines the picking view"
    _order = 'sequence'    
    
    def _get_picking_way_bill(self, cr, uid, ids, field_names, arg, context=None):
        obj = self.pool.get('stock.picking')
        domains = {
            'count_picking_way_bill': [('state', 'in', ('assigned', 'waiting', 'confirmed', 'partially_available')), ('is_transfer_request', '=', True), ('waybill_no', '=', None)],
        }
        result = {}
        for field in domains:
            data = obj.read_group(cr, uid, domains[field] + 
                [('state', 'not in', ('done', 'cancel'))],
                ['picking_type_id'], ['picking_type_id'], context=context)
            count = dict(map(lambda x: (x['picking_type_id'] and x['picking_type_id'][0], x['picking_type_id_count']), data))
            for tid in ids:
                result.setdefault(tid, {})[field] = count.get(tid, 0)
        return result
    
    _columns = {
        'count_picking_way_bill': fields.function(_get_picking_way_bill,
            type='integer', multi='_get_picking_way_bill'),
                }
