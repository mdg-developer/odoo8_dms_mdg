from openerp.osv import fields, osv
import xmlrpclib
from openerp import models, fields, api
import logging

# class stock_picking(osv.osv):
#     _inherit = "stock.picking"
#
#     def do_enter_transfer_details(self, cr, uid, ids, context=None):
#         # try:
#             result = super(stock_picking, self).do_enter_transfer_details(cr, uid, ids, context=context)
#             for picking in self.browse(cr, uid, ids, context=context):
#                 picking_code =picking.picking_type_id.code
#                 po_number =picking.origin
#                 po = self.pool['purchase.order'].search(cr, uid, [('name', '=', po_number)], context=context)
#                 if po:
#                     po_obj = self.pool['purchase.order'].browse(cr, uid, po)[0]
#                 is_cwh_location = picking.picking_type_id.default_location_dest_id.is_cwh_location
#                 location = picking.picking_type_id.default_location_dest_id.name
#                 if picking_code == 'incoming' and is_cwh_location and po_obj and location in ('MDGCWH1-Sellable','MDGCWH2-Sellable'):
#                     sd_uid, url, db, password = self.pool['cwh.connection'].get_connection_data(cr, uid, context=None)
#                     models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(url))
#                     if location == 'MDGCWH1-Sellable':
#                         warehouse_ids = models.execute_kw(db, sd_uid, password, 'stock.warehouse', 'search',
#                                                             [[['name', '=', 'MDGCentralWHA']]], {'limit': 1})
#                         type_ids = models.execute_kw(db, sd_uid, password, 'stock.picking.type', 'search',
#                                                        [[['warehouse_id', '=', warehouse_ids[0]],
#                                                          ['name', '=', 'Receipts']]],
#                                                        {'limit': 1})
#                     if location == 'MDGCWH2-Sellable':
#                         warehouse_ids = models.execute_kw(db, sd_uid, password, 'stock.warehouse', 'search',
#                                                             [[['name', '=', 'MDGCentralWHB']]], {'limit': 1})
#                         type_ids = models.execute_kw(db, sd_uid, password, 'stock.picking.type', 'search',
#                                                        [[['warehouse_id', '=', warehouse_ids[0]],
#                                                          ['name', '=', 'Receipts']]],
#                                                        {'limit': 1})
#
#                     po_vals = {}
#                     po_vals['partner_id'] = 7
#                     po_name = po_obj.name
#                     if po_obj.partner_ref:
#                         po_partner_ref = po_obj.partner_ref
#                     else:
#                         po_partner_ref = ""
#                     flag_partner_ref = ""
#                     index = po_name.find('_')
#                     if index != -1:
#                         flag_partner_ref = po_name[0:index+1]+po_partner_ref
#                     if index == -1 and po_partner_ref != "" :
#                         flag_partner_ref = po_name+"_"+po_partner_ref
#                     if index == -1 and po_partner_ref == "" :
#                         flag_partner_ref = po_name
#                     po_vals['partner_ref']= po_obj.name
#                     po_vals['order_line']= []
#                     po_vals['origin'] = flag_partner_ref
#                     po_vals['picking_type_id'] = type_ids[0]
#                     for line in picking.move_lines:
#                         product_ids = models.execute_kw(db, sd_uid, password, 'product.product', 'search',
#                                                         [[('default_code', '=', line.product_id.default_code)]],
#                                                         {'limit': 1})
#                         product_id = models.execute_kw(db, sd_uid, password, 'product.product', 'read', [product_ids])[0]
#                         uom_id = models.execute_kw(db, sd_uid, password, 'uom.uom', 'search',
#                                                    [[('name', '=', line.product_uom.name)]], {'limit': 1})
#                         if product_id:
#                             po_create = True
#                             po_vals['order_line'].append([0, False, {'name': product_id['name'],
#                                                                  'product_id': product_id['id'],
#                                                                  'product_qty': line.product_uom_qty,
#                                                                  'product_uom_qty': line.product_uom_qty,
#                                                                  'product_uom': uom_id[0],
#                                                                  'price_unit': product_id['lst_price']
#                                                                  }])
#                         if po_create == True:
#                             print"po_vals>>>",po_vals
#                             order_id = models.execute_kw(db, sd_uid, password, 'purchase.order', 'create', [po_vals])
#                             if order_id:
#                                 print 'order_id', order_id
#                                 models.execute_kw(db, sd_uid, password, 'purchase.order', 'button_confirm', [order_id])
#             return result
#         except Exception , e:
#             print "Exception",e
#             raise e



class stock_transfer_details(models.TransientModel):
    _inherit = 'stock.transfer_details'

    @api.one
    def do_detailed_transfer(self):

        result = super(stock_transfer_details, self).do_detailed_transfer()
        for transfer in self:
                logging.warning("########################################3")
                picking = transfer.picking_id
                picking_code =picking.picking_type_id.code
                po_number =picking.origin
                po_obj = self.env['purchase.order'].search([('name', '=', po_number)])
                is_cwh_location = picking.picking_type_id.default_location_dest_id.is_cwh_location
                location = picking.picking_type_id.default_location_dest_id.name
                if picking_code == 'incoming' and is_cwh_location and po_obj and location in ('MDGCWH1-Sellable','MDGCWH2-Sellable','MDGCWHA-Sellable','MDGCWHB-Sellable'):
                    sd_uid, url, db, password = self.env['cwh.connection'].get_connection_data()
                    models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(url))
                    if location in ('MDGCWH1-Sellable','MDGCWHA-Sellable'):
                        warehouse_ids = models.execute_kw(db, sd_uid, password, 'stock.warehouse', 'search',
                                                            [[['name', '=', 'MDGCentralWHA']]], {'limit': 1})
                        type_ids = models.execute_kw(db, sd_uid, password, 'stock.picking.type', 'search',
                                                       [[['warehouse_id', '=', warehouse_ids[0]],
                                                         ['name', '=', 'Receipts']]],
                                                       {'limit': 1})
                    if location in ('MDGCWH2-Sellable','MDGCWHB-Sellable'):
                        warehouse_ids = models.execute_kw(db, sd_uid, password, 'stock.warehouse', 'search',
                                                            [[['name', '=', 'MDGCentralWHB']]], {'limit': 1})
                        type_ids = models.execute_kw(db, sd_uid, password, 'stock.picking.type', 'search',
                                                       [[['warehouse_id', '=', warehouse_ids[0]],
                                                         ['name', '=', 'Receipts']]],
                                                       {'limit': 1})

                    po_vals = {}
                    po_vals['partner_id'] = 7
                    po_name = po_obj.name
                    if po_obj.partner_ref:
                        po_partner_ref = po_obj.partner_ref
                    else:
                        po_partner_ref = ""
                    flag_partner_ref = ""
                    index = po_name.find('_')
                    if index != -1:
                        flag_partner_ref = po_name[0:index+1]+po_partner_ref
                    if index == -1 and po_partner_ref != "" :
                        flag_partner_ref = po_name+"_"+po_partner_ref
                    if index == -1 and po_partner_ref == "" :
                        flag_partner_ref = po_name
                    po_vals['partner_ref']= po_obj.name
                    po_vals['order_line']= []
                    po_vals['origin'] = flag_partner_ref
                    po_vals['picking_type_id'] = type_ids[0]
                    logging.warning("Transfer.item_ids: %s", transfer.item_ids)
                    for line in transfer.item_ids:
                        logging.warning("***************************************")
                        logging.warning("Line: %s", line)

                        product_ids = models.execute_kw(db, sd_uid, password, 'product.product', 'search',
                                                        [[('default_code', '=', line.product_id.default_code)]],
                                                        {'limit': 1})
                        product_id = models.execute_kw(db, sd_uid, password, 'product.product', 'read', [product_ids])[0]
                        uom_id = models.execute_kw(db, sd_uid, password, 'uom.uom', 'search',
                                                   [[('name', '=', line.product_uom_id.name)]], {'limit': 1})
                        if product_id:
                            po_create = True
                            po_vals['order_line'].append([0, False, {'name': product_id['name'],
                                                                 'product_id': product_id['id'],
                                                                 'product_qty': line.quantity,
                                                                 'product_uom_qty': line.quantity,
                                                                 'product_uom': uom_id[0],
                                                                 'price_unit': product_id['lst_price']
                                                                 }])
                    if po_create == True:
                        print"po_vals>>>",po_vals
                        order_id = models.execute_kw(db, sd_uid, password, 'purchase.order', 'create', [po_vals])
                        if order_id:
                            print 'order_id', order_id
                            models.execute_kw(db, sd_uid, password, 'purchase.order', 'button_confirm', [order_id])
        return result