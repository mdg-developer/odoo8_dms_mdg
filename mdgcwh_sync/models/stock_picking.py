from openerp.osv import fields, osv
import xmlrpclib

class stock_picking(osv.osv):
    _inherit = "stock.picking"

    def create(self, cr, user, vals, context=None):
        try:
            is_cwh_approve = False
            cwh_location = False
            internal_transfer_inv = {}
            move_array = []
            result = super(stock_picking, self).create(cr, user, vals, context=context)
            for sp in self.browse(cr, user, result, context=context):
                type_id= False
                default_source_id = False
                default_destination_id = False
                # if sp.picking_type_id.code == 'internal' and type_ids_a and type_ids_b:
                if sp.picking_type_id.code == 'internal' and sp.picking_type_id.warehouse_id.name in ('MDGCWH1','MDGCWHA','MDGCWH2','MDGCWHB'):
                    sd_uid, url, db, password = self.pool['cwh.connection'].get_connection_data(cr, user, context=None)
                    models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(url))
                    warehouse_ids_b = models.execute_kw(db, sd_uid, password, 'stock.warehouse', 'search',
                                                        [[['name', '=', 'MDGCentralWHB']]], {'limit': 1})
                    warehouse_ids_a = models.execute_kw(db, sd_uid, password, 'stock.warehouse', 'search',
                                                        [[['name', '=', 'MDGCentralWHA']]], {'limit': 1})
                    type_ids_a = models.execute_kw(db, sd_uid, password, 'stock.picking.type', 'search',
                                                   [[['warehouse_id', '=', warehouse_ids_a[0]],
                                                     ['name', '=', 'Receipts']]],
                                                   {'limit': 1})
                    type_ids_b = models.execute_kw(db, sd_uid, password, 'stock.picking.type', 'search',
                                                   [[['warehouse_id', '=', warehouse_ids_b[0]],
                                                     ['name', '=', 'Receipts']]],
                                                   {'limit': 1})

                    location_ids_stage_b = models.execute_kw(db, sd_uid, password, 'stock.location', 'search',
                                                             [[('complete_name', '=', 'CWHB/STAGE')]], {'limit': 1})
                    location_ids_stage_a = models.execute_kw(db, sd_uid, password, 'stock.location', 'search',
                                                             [[('complete_name', '=', 'CWHA/STAGE')]], {'limit': 1})

                    location_ids_team_b = models.execute_kw(db, sd_uid, password, 'stock.location', 'search',
                                                            [[('complete_name', '=', 'CWHB/Team Location')]],
                                                            {'limit': 1})
                    location_ids_team_a = models.execute_kw(db, sd_uid, password, 'stock.location', 'search',
                                                            [[('complete_name', '=', 'CWHA/Team Location')]],
                                                            {'limit': 1})
                    inventory_line = False
                    # picking_type_id = models.execute_kw(db, sd_uid, password, 'stock.picking.type', 'read', type_ids[0])
                    if sp.picking_type_id.warehouse_id.name in ('MDGCWH1','MDGCWHA'):
                        default_source_id = location_ids_team_a[0]
                        default_destination_id = location_ids_stage_a[0]
                        type_id = type_ids_a[0]
                    elif sp.picking_type_id.warehouse_id.name in ('MDGCWH2','MDGCWHB'):
                        default_source_id = location_ids_team_b[0]
                        default_destination_id = location_ids_stage_b[0]
                        type_id = type_ids_b[0]
                    if type_id and default_source_id and default_destination_id:
                        internal_transfer_inv = {
                                'origin': str(vals['name']),
                                'move_type': 'direct',
                                'picking_type_id': type_id,
                                'partner_id': 7,
                                'location_dest_id': default_destination_id,
                                'location_id': default_source_id,
                                # 'name': 'In from odoo 8',
                                'move_ids_without_package': []
                            }
                        picking = models.execute_kw(db, sd_uid, password, 'stock.picking', 'create', [internal_transfer_inv])


                        for line in sp.move_lines:
                            product_ids = models.execute_kw(db, sd_uid, password, 'product.product', 'search',
                                                            [[('default_code', '=', line.product_id.default_code)]], {'limit': 1})
                            uom_id = models.execute_kw(db, sd_uid, password, 'uom.uom', 'search',
                                                       [[('name', '=', line.product_uom.name)]], {'limit': 1})
                            # cwh_location = line.location_id.is_cwh_location and line.location_dest_id.is_cwh_location
                            cwh_location = line.location_dest_id.is_cwh_location
                            if line.location_dest_id.name.startswith("MDGCWH2") or line.location_dest_id.name.startswith("MDGCWHB"):
                                default_destination_id = location_ids_stage_b[0]
                            if line.location_dest_id.name.startswith("MDGCWH1") or line.location_dest_id.name.startswith("MDGCWHA"):
                                default_destination_id = location_ids_stage_a[0]
                            if product_ids and cwh_location:
                                inventory_line = True
                                product_id = models.execute_kw(db, sd_uid, password, 'product.product', 'read', [product_ids])[0]
                                move_value = {
                                    'name': product_id['name'],
                                    'product_id': product_ids[0],
                                    'product_uom_qty': line.product_uom_qty,
                                    'product_uom': uom_id[0],
                                    'location_id': default_source_id,
                                    'location_dest_id': default_destination_id,
                                    'picking_id': picking,
                                    'state': 'draft',
                                }
                                move_array.append(move_value)
                        if inventory_line == True:
                            move_id = models.execute_kw(db, sd_uid, password, 'stock.move', 'create', [move_array])
                        else:
                            models.execute_kw(db, sd_uid, password, 'stock.picking', 'unlink', [[picking]])
            return result
        except Exception, e:
            print "Stock Picking: Internal Transfer ", internal_transfer_inv
            raise e



