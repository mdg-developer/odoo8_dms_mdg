from openerp.osv import fields, osv
from openerp.tools.translate import _
import xmlrpclib
import logging

class product_transactions(osv.osv):
    _inherit = "product.transactions"

    def action_convert_ep(self, cr, uid, ids, context=None):
        super(product_transactions, self).action_convert_ep(cr, uid, ids, context=context)
        sale_return_id = self.browse(cr, uid, ids, context=context)
        if sale_return_id.branch_id.subdeal:
            sd_uid, url, db, password = self.pool['sd.connection'].get_connection_data(cr, uid, context=None)
            models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(url))

            to_location_id = models.execute_kw(db, sd_uid, password,'stock.location', 'search',[[['name', 'like', 'loss']]],{'limit': 1})
            from_location_id = models.execute_kw(db, sd_uid, password,'stock.location', 'search',[[['name', '=', sale_return_id.team_id.location_id.name]]],{'limit': 1})


            for line in sale_return_id.item_line:
                product_id = models.execute_kw(db, sd_uid, password, 'product.product', 'search',
                                               [[['default_code', '=', line.product_id.default_code]]], {'limit': 1})
                product_uom_id = models.execute_kw(db, sd_uid, password,'product.uom', 'search',[[['name', '=', line.uom_id.name]]],{'limit': 1})
                stock_move_value = {
                    'name': line.product_id.name,
                    'product_id': product_id[0],
                    'location_dest_id': to_location_id[0],
                    'location_id': from_location_id[0],
                    'product_uom_qty': abs(line.product_qty),
                    'product_uom': product_uom_id[0],
                    'origin': sale_return_id.name,
                }
                logging.warning("Check inv value: %s", stock_move_value)
                move_id = models.execute_kw(db, sd_uid, password, 'stock.move', 'create', [stock_move_value])
                models.execute_kw(db, sd_uid, password, 'stock.move', 'action_done', [move_id])
                logging.warning("Move_id: %s", move_id)