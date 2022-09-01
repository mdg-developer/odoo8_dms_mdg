import xmlrpclib
from openerp import models, fields, api
import logging

class stock_transfer_details(models.TransientModel):
    _inherit = 'stock.transfer_details'

    @api.one
    def do_detailed_transfer(self):
        import pdb
        pdb.set_trace()
        result = super(stock_transfer_details, self).do_detailed_transfer()
        for transfer in self:
            logging.warning("########################################3")
            picking = transfer.picking_id
            picking_code = picking.picking_type_id.code
            po_number = picking.origin
            po_obj = self.env['purchase.order'].search([('name', '=', po_number)])
            sd_uid, url, db, password = self.env['cwh.connection'].get_connection_data()
            models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(url))
            po_vals = {}
            for line in transfer.item_ids:

                po_vals['order_line'] = []
                po_vals['picking_type_id'] = 1
                po_vals['partner_id'] = 7
                po_vals['order_line'].append([0, False, {'name': 'joj-s',
                                                         'product_id': 1704,
                                                         'product_qty': 2,
                                                         'product_uom_qty': 2,
                                                         'product_uom': 740,
                                                         'price_unit': 0.00,
                                                         }])

                order_id = models.execute_kw(db, sd_uid, password, 'purchase.order', 'create', [po_vals])
        return result