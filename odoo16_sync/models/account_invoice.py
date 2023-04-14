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
                context = dict(self.env.context)            
                
                warehouse_id = models.execute_kw(db, sd_uid, password,
                'stock.warehouse', 'search',
                [[['name', 'like', inv.section_id.warehouse_id.name]]],
                {'limit': 1})
                loc_id = models.execute_kw(db, sd_uid, password,
                'stock.location', 'search',
                [[['name', 'like', 'loss']]],
                {'limit': 1})
                dest_loc_id = models.execute_kw(db, sd_uid, password,
                'stock.location', 'search',
                [[['name', 'like', inv.section_id.location_id.name]]],
                {'limit': 1})
                
                if warehouse_id:
                    picking_type_id = models.execute_kw(db, sd_uid, password,
                    'stock.picking.type', 'search',
                    [[['warehouse_id', '=', warehouse_id[0]], ['name', 'like', 'Transfers']]],
                    {'limit': 1})
                    sd_move_id = models.execute_kw(db, sd_uid, password,
                            'stock.picking', 'search',
                            [[['origin', 'like','Import '+ str(inv.origin)]]],
                            {'limit': 1})
                    if sd_move_id:
                        return result    
                    res = {
                            'origin': 'Import '+ str(inv.origin),
                            'move_type':'direct',
                            'invoice_state':'none',
                            'picking_type_id':picking_type_id[0],
                            'priority':'1'}    
                    
                picking_id = models.execute_kw(db, sd_uid, password, 'stock.picking', 'create', [res])
                for line in self.invoice_line:
                    if not warehouse_id and loc_id and dest_loc_id and picking_type_id:
                        raise Warning(_("""Warehouse and Location doesn't exit in SD"""))
                    if line.product_id.type != 'service' :
                        
                        move_val = {
                              'name':'Import',
                              'product_id':line.product_id.id,
                              'product_uom_qty':line.quantity,
                              'product_uos_qty':line.quantity,
                              'product_uom':line.uos_id.id,
                              'selection':'none',
                              'priority':'1',
                              'company_id':inv.company_id.id,
                              'date_expected':inv.date_invoice,
                              'date':inv.date_invoice,
                              'origin':'Import '+ str(inv.origin),
                              'location_id':loc_id[0],
                              'location_dest_id':dest_loc_id[0],
                              'create_date':inv.date_invoice,
                              'picking_type_id':picking_type_id[0],
                              'picking_id':picking_id,
                              'state':'done'}
                        move_id = models.execute_kw(db, sd_uid, password, 'stock.move', 'create', [move_val])
                        move_ids.append(move_id)    
                    
                for move in move_ids:
                    models.execute_kw(db, sd_uid, password, 'stock.move', 'action_done', [move])
        return result
    
      