from openerp.osv import fields, osv
from openerp.osv.fields import _column
import xmlrpclib

class stock_return(osv.osv):
    _inherit = "stock.return"

    def received(self, cr, uid, ids, context=None):
        try:
            result = super(stock_return, self).received(cr, uid, ids, context=context)
            receipt_inv = {}
            move_array = []

            data = self.browse(cr, uid, ids[0])
            if not data.to_location.is_cwh_location:
                return
            sd_uid, url, db, password = self.pool['cwh.connection'].get_connection_data(cr, uid, context=None)
            models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(url))
            inventory_line = False
            warehouse_ids_b = models.execute_kw(db, sd_uid, password, 'stock.warehouse', 'search',
                                         [[['name', '=', 'MDGCentralWHB']]], {'limit': 1})
            warehouse_ids_a = models.execute_kw(db, sd_uid, password, 'stock.warehouse', 'search',
                                                [[['name', '=', 'MDGCentralWHA']]], {'limit': 1})
            type_ids_a = models.execute_kw(db, sd_uid, password, 'stock.picking.type', 'search',
                                         [[['warehouse_id', '=', warehouse_ids_a[0]], ['name', '=', 'Receipts']]], {'limit': 1})
            type_ids_b = models.execute_kw(db, sd_uid, password, 'stock.picking.type', 'search',
                                           [[['warehouse_id', '=', warehouse_ids_b[0]], ['name', '=', 'Receipts']]],{'limit': 1})
            location_ids_stage_b = models.execute_kw(db, sd_uid, password, 'stock.location', 'search',
                                             [[('complete_name', '=', 'CWHB/STAGE')]], {'limit': 1})
            location_ids_stage_a = models.execute_kw(db, sd_uid, password, 'stock.location', 'search',
                                                     [[('complete_name', '=', 'CWHA/STAGE')]], {'limit': 1})
            location_ids_team_b = models.execute_kw(db, sd_uid, password, 'stock.location', 'search',
                                                     [[('complete_name', '=', 'CWHB/Team Location')]], {'limit': 1})
            location_ids_team_a = models.execute_kw(db, sd_uid, password, 'stock.location', 'search',[[('complete_name', '=', 'CWHA/Team Location')]], {'limit': 1})
            if data.to_location.name in ('MDGCWH1-Sellable','MDGCWHA-Sellable'):
                receipt_inv = {
                    'origin': str(data.name),
                    'move_type': 'direct',
                    'picking_type_id': type_ids_a[0],
                    'priority': '1',
                    'partner_id': 7,
                    'location_dest_id': location_ids_stage_a[0],
                    'location_id': location_ids_team_a[0],
                    'move_ids_without_package': []
                }

            if data.to_location.name in ('MDGCWH2-Sellable','MDGCWHB-Sellable'):
                receipt_inv = {
                    'origin': str(data.name),
                    'move_type': 'direct',
                    'picking_type_id': type_ids_b[0],
                    'priority': '1',
                    'partner_id': 7,
                    'location_dest_id': location_ids_stage_b[0],
                    'location_id': location_ids_team_b[0],
                    'move_ids_without_package': []
                }
            picking = models.execute_kw(db, sd_uid, password, 'stock.picking', 'create', [receipt_inv])


            for line in data.p_line:
                product_ids = models.execute_kw(db, sd_uid, password, 'product.product', 'search',
                                                [[('default_code', '=', line.product_id.default_code)]], {'limit': 1})
                uom_id = models.execute_kw(db, sd_uid, password, 'uom.uom', 'search',
                                           [[('name', '=', line.product_uom.name)]], {'limit': 1})
                if product_ids:
                    inventory_line = True
                    product_id = models.execute_kw(db, sd_uid, password, 'product.product', 'read', [product_ids])[0]
                    move_value = {
                        'name': product_id['name'],
                        'product_id': product_ids[0],
                        'product_uom_qty': line.actual_return_quantity,
                        'quantity_done':line.actual_return_quantity,
                        'product_uom': uom_id[0],
                        # 'location_id': 5,
                        # 'location_dest_id': 9,
                        'picking_id': picking,
                        'state': 'draft',
                    }
                    if data.to_location.name in ('MDGCWH1-Sellable','MDGCWHA-Sellable'):
                        move_value['location_id'] = location_ids_team_a[0]
                        move_value['location_dest_id'] = location_ids_stage_a[0]
                    if data.to_location.name in ('MDGCWH2-Sellable','MDGCWHB-Sellable'):
                        move_value['location_id'] = location_ids_team_b[0]
                        move_value['location_dest_id'] = location_ids_stage_b[0]
                    move_array.append(move_value)
            if inventory_line == True:
                move_id = models.execute_kw(db, sd_uid, password, 'stock.move', 'create', [move_array])

            models.execute_kw(db, sd_uid, password, 'stock.picking', 'action_confirm', [picking])


        except Exception, e:
            raise e


