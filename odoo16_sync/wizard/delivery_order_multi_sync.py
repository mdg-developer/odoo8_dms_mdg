import time
from openerp.osv import fields, osv
from openerp import http
from openerp.http import request
from openerp.tools import html_escape as escape
import json


class delivery_order_multi_sync(osv.osv_memory):
    _name = 'delivery.order.multi.sync'
    _description = 'Delivery Order Multi Sync'
    _columns = {
        'sync': fields.boolean("Sync", required=True),

    }

    _defaults = {
        'sync': True,
    }

    def delivery_order_sync(self, cr, uid, ids, context=None):
        data = self.read(cr, uid, ids, context=context)[0]
        picking_obj = self.pool.get('stock.picking')

        picking_lists = context.get('active_ids', [])
        for picking_list_id in self.pool['stock.picking'].browse(cr, uid, picking_lists, context=None):
            picking_obj.sync_to_odoo(cr, uid, [picking_list_id.id], context=None)
        return True



