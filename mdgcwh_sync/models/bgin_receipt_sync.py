from openerp.osv import fields, osv
import xmlrpclib
from openerp.tools.translate import _

class branch_good_issue_note(osv.osv):
    _inherit = "branch.good.issue.note"

    def receive(self, cr, uid, ids, context=None):
        try:
            result = super(branch_good_issue_note, self).receive(cr, uid, ids, context=context)
            gin_id = self.browse(cr, uid, ids, context=context)
            request_warehouse = gin_id.from_location_id.name
            requesting_location = gin_id.to_location_id.name
            inventory_line = False
            move_array = []
            picking_val = {}
            if (request_warehouse in ('MDGCWH2-Sellable','MDGCWH1-Sellable','MDGCWHB-Sellable','MDGCWHA-Sellable') and requesting_location in ('MDGCWH2-Sellable','MDGCWH1-Sellable','MDGCWHB-Sellable','MDGCWHA-Sellable')) or (request_warehouse in ('MDGCWH2-Sellable','MDGCWH1-Sellable','MDGCWHB-Sellable','MDGCWHA-Sellable')):
                sd_uid, url, db, password = self.pool['cwh.connection'].get_connection_data(cr, uid, context=None)
                models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(url))
                warehouse_ids_b = models.execute_kw(db, sd_uid, password, 'stock.warehouse', 'search',
                                                [[['name', '=', 'MDGCentralWHB']]], {'limit': 1})
                warehouse_ids_a = models.execute_kw(db, sd_uid, password, 'stock.warehouse', 'search',
                                                [[['name', '=', 'MDGCentralWHA']]], {'limit': 1})
                type_ids_a = models.execute_kw(db, sd_uid, password, 'stock.picking.type', 'search',
                                           [[['warehouse_id', '=', warehouse_ids_a[0]], ['name', '=', 'Receipts']]],
                                           {'limit': 1})
                type_ids_b = models.execute_kw(db, sd_uid, password, 'stock.picking.type', 'search',
                                           [[['warehouse_id', '=', warehouse_ids_b[0]], ['name', '=', 'Receipts']]],
                                           {'limit': 1})
                location_ids_stage_b = models.execute_kw(db, sd_uid, password, 'stock.location', 'search',
                                                     [[('complete_name', '=', 'CWHB/STAGE')]], {'limit': 1})
                location_ids_stage_a = models.execute_kw(db, sd_uid, password, 'stock.location', 'search',
                                                     [[('complete_name', '=', 'CWHA/STAGE')]], {'limit': 1})
                location_ids_team_b = models.execute_kw(db, sd_uid, password, 'stock.location', 'search',
                                                        [[('complete_name', '=', 'CWHB/Team Location')]], {'limit': 1})
                location_ids_team_a = models.execute_kw(db, sd_uid, password, 'stock.location', 'search',
                                                        [[('complete_name', '=', 'CWHA/Team Location')]], {'limit': 1})

                if request_warehouse in ('MDGCWH2-Sellable','MDGCWHB-Sellable') and requesting_location in ('MDGCWH1-Sellable','MDGCWHA-Sellable'):
                    picking_type = type_ids_b[0]
                    source_loc_id = location_ids_team_a[0]
                    dest_loc_id = location_ids_stage_b[0]
                    type= 'a_to_b'
                elif request_warehouse in ('MDGCWH1-Sellable','MDGCWHA-Sellable') and requesting_location in ('MDGCWH2-Sellable','MDGCWHB-Sellable'):
                    picking_type = type_ids_a[0]
                    source_loc_id = location_ids_team_b[0]
                    dest_loc_id = location_ids_stage_a[0]
                    type = 'b_to_a'
                elif request_warehouse in ('MDGCWH2-Sellable','MDGCWHB-Sellable'):
                    picking_type = type_ids_b[0]
                    source_loc_id = location_ids_team_b[0]
                    dest_loc_id = location_ids_stage_b[0]
                    type = 'team_to_b'
                elif request_warehouse in ('MDGCWH1-Sellable','MDGCWHA-Sellable'):
                    picking_type = type_ids_a[0]
                    source_loc_id = location_ids_team_a[0]
                    dest_loc_id = location_ids_stage_a[0]
                    type = 'team_to_a'
                else:
                    return result

                picking_val = {
                    'origin': str(gin_id.name),
                    'move_type': 'direct',
                    'picking_type_id': picking_type,
                    'priority': '1',
                    'partner_id': 7,
                    'location_dest_id': dest_loc_id,
                    'location_id': source_loc_id,
                    'move_ids_without_package': []
                }
                picking_id = models.execute_kw(db, sd_uid, password, 'stock.picking', 'create', [picking_val])
                for line in gin_id.p_line:
                    inventory_line = True
                    product_ids = models.execute_kw(db, sd_uid, password,'product.product', 'search',
                                                    [[('default_code', '=', line.product_id.default_code)]],{'limit': 1})


                    base_uom = line.product_id.product_tmpl_id.uom_id
                    report_uom = line.product_id.product_tmpl_id.report_uom_id
                    if base_uom == line.product_uom:
                        uom_id = models.execute_kw(db, sd_uid, password, 'uom.uom', 'search',
                                                   [[('name', '=', line.product_uom.name)]], {'limit': 1})
                        quantity = line.receive_quantity
                    elif report_uom == line.product_uom:
                        uom_id = models.execute_kw(db, sd_uid, password, 'uom.uom', 'search',
                                                   [[('name', '=', base_uom.name)]], {'limit': 1})
                        quantity = line.receive_quantity * report_uom.factor_inv
                    else:
                        raise osv.except_osv(_('Error!'), _('Check the uom of wms and portal.'))

                    # uom_id = models.execute_kw(db, sd_uid, password, 'uom.uom', 'search',
                    #                            [[('name', '=', line.product_uom.name)]], {'limit': 1})
                    if product_ids and line.receive_quantity != 0:
                        product_id = models.execute_kw(db, sd_uid, password, 'product.product', 'read', [product_ids])[0]
                        move_value = {
                            'name': product_id['name'],
                            'product_id': product_ids[0],
                            # 'product_uom_qty': line.receive_quantity,
                            # 'quantity_done': line.receive_quantity,
                            'product_uom_qty': quantity,
                            'quantity_done': quantity,
                            'product_uom': uom_id[0],
                            'picking_id': picking_id,
                            'state': 'draft',
                        }
                        if type == 'a_to_b':
                            move_value['location_id'] = source_loc_id
                            move_value['location_dest_id'] = dest_loc_id
                        if type == 'b_to_a':
                            move_value['location_id'] = source_loc_id
                            move_value['location_dest_id'] = dest_loc_id
                        if type == 'team_to_b':
                            move_value['location_id'] = source_loc_id
                            move_value['location_dest_id'] = dest_loc_id
                        if type == 'team_to_a':
                            move_value['location_id'] = source_loc_id
                            move_value['location_dest_id'] = dest_loc_id
                        move_array.append(move_value)

                if inventory_line == True:
                    models.execute_kw(db, sd_uid, password, 'stock.move', 'create', [move_array])
                    models.execute_kw(db, sd_uid, password, 'stock.picking', 'action_confirm', [picking_id])
                    # return result
                else:
                    models.execute_kw(db, sd_uid, password, 'stock.picking', 'unlink', [[picking_id]])

            return result
        except Exception, e:
            raise e