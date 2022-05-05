import itertools
from lxml import etree

from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning
from openerp.tools import float_compare
import openerp.addons.decimal_precision as dp
import xmlrpclib

class account_invoice(models.Model):
    _inherit = 'account.invoice' 
    
    @api.multi
    def action_move_create(self):
        result = super(account_invoice, self).action_move_create()
        pick_obj = self.env['stock.picking']
        move_obj = self.env['stock.move']
        stockDetailObj = self.env['stock.transfer_details']
        picking_type_obj = self.env['stock.picking.type']
        warehouse_obj = self.env['stock.warehouse']

        sd_uid,url,db,password = self.env['sd.connection'].get_connection_data()
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(url))
        move_ids = []
        for inv in self:
            if inv.type == 'out_invoice' and inv.partner_id.sd_customer == True and sd_uid and inv.date_invoice >='2020-02-01':
                branch_id = False
                if (inv.branch_id.name.startswith('LSD')):
                    branch_id = models.execute_kw(db, sd_uid, password,'res.branch', 'search',[[['branch_code', '=', 'LMSD']]],{'limit': 1})
                elif (inv.branch_id.name.startswith('USD')):
                    branch_id = models.execute_kw(db, sd_uid, password, 'res.branch', 'search',[[['branch_code', '=', 'UMSD']]], {'limit': 1})
                from_location_id = models.execute_kw(db, sd_uid, password,
                'stock.location', 'search',
                [[['name', 'like', 'loss']]],
                {'limit': 1})
                to_location_id = models.execute_kw(db, sd_uid, password,
                'stock.location', 'search',
                [[['name', '=', inv.section_id.location_id.name]]],
                {'limit': 1})
                route_id = models.execute_kw(db, sd_uid, password,
                'transport.route', 'search',
                [[['name', '=', 'Yangon To Taunggyi']]],
                {'limit': 1})
                vehicle_id = models.execute_kw(db, sd_uid, password,
                'fleet.vehicle', 'search',
                [[['license_plate', '=', '1B/2168']]],
                {'limit': 1})
                supplier_id = models.execute_kw(db, sd_uid, password,
                'res.partner', 'search',
                [[['name', '=', 'Ko Kyaw Myo Lwin'],['transporter', '=', True]]],
                {'limit': 1})
                stock_location_group_id = models.execute_kw(db, sd_uid, password,
                'stock.location.group', 'search',
                [[['name', '=', 'Transit']]],
                {'limit': 1})
                if not stock_location_group_id:
                    raise Warning(_("""Transit location group doesn't exit in SD!"""))
                if not branch_id:
                    raise Warning(_("""Branch doesn't exit in SD!"""))
                if not from_location_id:
                    raise Warning(_("""Request warehouse doesn't exit in SD!"""))
                if not to_location_id:
                    raise Warning(_("""Requesting location doesn't exit in SD!"""))
                if not route_id:
                    raise Warning(_("""Route doesn't exit in SD!"""))
                if not vehicle_id:
                    raise Warning(_("""Vehicle doesn't exit in SD!"""))
                if not supplier_id:
                    raise Warning(_("""Supplier doesn't exit in SD!"""))

                branch_default_location = inv.branch_id.branch_location_id.name
                branch_transit_location = branch_default_location.replace("-Sellable", "-Transit")
                transit_location_id = models.execute_kw(db, sd_uid, password,
                'stock.location', 'search',
                [[['name', '=', branch_transit_location],['stock_location_group_id', '=',stock_location_group_id[0]]]],
                {'limit': 1})
                if not transit_location_id:
                    raise Warning(_("""Transit location doesn't exit in SD!"""))
                for line in self.invoice_line:
                    if line.product_id.type != 'service':
                        product_id = models.execute_kw(db, sd_uid, password,
                        'product.product', 'search',
                        [[['default_code', '=', line.product_id.default_code]]],
                        {'limit': 1})
                        if not product_id:
                            raise Warning(_("Product code %s doesn't exist in SD!") % line.product_id.default_code)
                        product_uom_id = models.execute_kw(db, sd_uid, password,
                        'product.uom', 'search',
                        [[['name', '=', line.uos_id.name]]],
                        {'limit': 1})
                        if not product_uom_id:
                            raise Warning(_("UOM %s doesn't exist in SD!") % line.uos_id.name)
                res = {
                    'branch_id': branch_id[0],
                    'from_location_id': from_location_id[0],
                    'to_location_id': to_location_id[0],
                    'issue_date': inv.date_invoice,
                    'loading_date': inv.date_invoice,
                    'eta_date': inv.date_invoice,
                    'route_id': route_id[0],
                    'vehicle_id': vehicle_id[0],
                    'supplier_id': supplier_id[0],
                    'internal_reference': inv.sale_order_id.name,
                    'transit_location': transit_location_id[0],
                    'issue_by': 'MDGportal',
                    'state': 'pending'
                }

                bgin_id = models.execute_kw(db, sd_uid, password, 'branch.good.issue.note', 'create', [res])
                for line in self.invoice_line:
                    if line.product_id.type != 'service':
                        product_id = models.execute_kw(db, sd_uid, password,
                        'product.product', 'search',
                        [[['default_code', '=', line.product_id.default_code]]],
                        {'limit': 1})
                        product_uom_id = models.execute_kw(db, sd_uid, password,
                        'product.uom', 'search',
                        [[['name', '=', line.uos_id.name]]],
                        {'limit': 1})
                        line_val = {
                            'product_id': product_id[0],
                            'issue_quantity': line.quantity,
                            'product_uom': product_uom_id[0],
                            'line_id': bgin_id,
                        }
                        models.execute_kw(db, sd_uid, password, 'branch.good.issue.note.line', 'create', [line_val])
                models.execute_kw(db, sd_uid, password, 'branch.good.issue.note', 'approve', [[bgin_id]])
                models.execute_kw(db, sd_uid, password, 'branch.good.issue.note', 'issue', [[bgin_id]])

                # context = dict(self.env.context)
                #
                # warehouse_id = models.execute_kw(db, sd_uid, password,
                # 'stock.warehouse', 'search',
                # [[['name', 'like', inv.section_id.warehouse_id.name]]],
                # {'limit': 1})
                # loc_id = models.execute_kw(db, sd_uid, password,
                # 'stock.location', 'search',
                # [[['name', 'like', 'loss']]],
                # {'limit': 1})
                # dest_loc_id = models.execute_kw(db, sd_uid, password,
                # 'stock.location', 'search',
                # [[['name', 'like', inv.section_id.location_id.name]]],
                # {'limit': 1})
                #
                # if warehouse_id:
                #     picking_type_id = models.execute_kw(db, sd_uid, password,
                #     'stock.picking.type', 'search',
                #     [[['warehouse_id', '=', warehouse_id[0]], ['name', 'like', 'Transfers']]],
                #     {'limit': 1})
                #     sd_move_id = models.execute_kw(db, sd_uid, password,
                #             'stock.picking', 'search',
                #             [[['origin', 'like','Import '+ str(inv.origin)]]],
                #             {'limit': 1})
                #     if sd_move_id:
                #         return result
                #     res = {
                #             'origin': 'Import '+ str(inv.origin),
                #             'move_type':'direct',
                #             'invoice_state':'none',
                #             'picking_type_id':picking_type_id[0],
                #             'priority':'1'}

                # picking_id = models.execute_kw(db, sd_uid, password, 'stock.picking', 'create', [res])
                # for line in self.invoice_line:
                #     if not warehouse_id and loc_id and dest_loc_id and picking_type_id:
                #         raise Warning(_("""Warehouse and Location doesn't exit in SD"""))
                #     if line.product_id.type != 'service' :
                #
                #         move_val = {
                #               'name':'Import',
                #               'product_id':line.product_id.id,
                #               'product_uom_qty':line.quantity,
                #               'product_uos_qty':line.quantity,
                #               'product_uom':line.uos_id.id,
                #               'selection':'none',
                #               'priority':'1',
                #               'company_id':inv.company_id.id,
                #               'date_expected':inv.date_invoice,
                #               'date':inv.date_invoice,
                #               'origin':'Import '+ str(inv.origin),
                #               'location_id':loc_id[0],
                #               'location_dest_id':dest_loc_id[0],
                #               'create_date':inv.date_invoice,
                #               'picking_type_id':picking_type_id[0],
                #               'picking_id':picking_id,
                #               'state':'done'}
                #         move_id = models.execute_kw(db, sd_uid, password, 'stock.move', 'create', [move_val])
                #         move_ids.append(move_id)
                #
                # for move in move_ids:
                #     models.execute_kw(db, sd_uid, password, 'stock.move', 'action_done', [move])
        return result
    
      