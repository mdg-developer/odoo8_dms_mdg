from openerp.osv import orm
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
from openerp.osv.fields import _column
import xmlrpclib
from openerp.tools.translate import _

class sale_order(osv.osv):
    _inherit = "sale.order"

    def action_reverse(self, cr, uid, ids, context=None):
        #res = super(sale_order, self).action_reverse(cr, uid, ids, context=context)
        
        #data = self.browse(cr,uid,ids[0],context=None)
        move_ids = []
        for data in self.browse(cr,uid,ids[0],context=None):
            if data.partner_id.sd_customer == True:
    #             pick_obj = self.pool.get('stock.picking')
    #             invoice_obj = self.pool.get('account.invoice')
    #             move_obj = self.pool.get('stock.move')
    #             stockDetailObj = self.pool.get('stock.transfer_details')
    #             detailObj = None
                
                so_no=data.name
                
                pick_ids = []
                sd_uid,url,db,password = self.pool['sd.connection'].get_connection_data(cr, uid, context=None)
                models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(url))
                pick_ids = models.execute_kw(db, sd_uid, password,
                    'stock.picking', 'search',                
                    [[['origin', '=', so_no], ['state', '=', 'done']]]
                    )       
                
                move_ids = []
                invoice_ids = self.pool['account.invoice'].search(cr, uid,[('origin','=',so_no),('state','=','open')],context=None)
                for inv in self.pool['account.invoice'].browse(cr, uid,invoice_ids,context=None):
                    if inv.type == 'out_invoice' and inv.partner_id.sd_customer == True and sd_uid and inv.date_invoice >='2020-02-01':
                        branch_id = models.execute_kw(db, sd_uid, password,
                        'res.branch', 'search',
                        [[['name', '=', inv.branch_id.name]]],
                        {'limit': 1})
                        if not branch_id:
                            raise Warning(_("""Branch doesn't exit in SD!"""))
                        stock_location_group_id = models.execute_kw(db, sd_uid, password,
                        'stock.location.group', 'search',
                        [[['name', '=', 'Transit']]],
                        {'limit': 1})
                        if not stock_location_group_id:
                            raise Warning(_("""Transit location group doesn't exit in SD!"""))
                        transit_location_id = models.execute_kw(db, sd_uid, password,
                        'stock.location', 'search',
                        [[['branch_id', '=', branch_id[0]],['stock_location_group_id', '=', stock_location_group_id[0]]]],
                        {'limit': 1})
                        if not transit_location_id:
                            raise Warning(_("""Transit location doesn't exit in SD!"""))
                        
                        warehouse_id = models.execute_kw(db, sd_uid, password,
                        'stock.warehouse', 'search',
                        [[['name', 'like', inv.section_id.warehouse_id.name]]],
                        {'limit': 1})
                        dest_loc_id = models.execute_kw(db, sd_uid, password,
                        'stock.location', 'search',
                        [[['name', 'like', 'loss']]],
                        {'limit': 1})
                        loc_id = models.execute_kw(db, sd_uid, password,
                        'stock.location', 'search',
                        [[['name', 'like', inv.section_id.location_id.name]]],
                        {'limit': 1})
                        if warehouse_id:
                            picking_type_id = models.execute_kw(db, sd_uid, password,
                            'stock.picking.type', 'search',
                            [[['warehouse_id', '=', warehouse_id[0]], ['name', 'like', 'Transfers']]],
                            {'limit': 1})
                            reverse_name = 'Reverse ' + str(inv.origin)
                            reverse_id = models.execute_kw(db, sd_uid, password,
                            'stock.picking', 'search',
                            [[['origin', 'like',reverse_name]]],
                            {'limit': 1})
                            if reverse_id:
                                result = super(sale_order, self).action_reverse(cr, uid, ids, context=context)
                                return result                                
                            res = {
                                    'origin': reverse_name,
                                    'move_type':'direct',
                                    'invoice_state':'none',
                                    'picking_type_id':picking_type_id[0],
                                    'priority':'1'}
                        picking_id = models.execute_kw(db, sd_uid, password, 'stock.picking', 'create', [res])
                        for line in inv.invoice_line:
                            if not warehouse_id and transit_location_id and dest_loc_id and picking_type_id:
                                raise orm.except_orm(_('Error :'), _("Warehouse and Location doesn't exit in SD"))
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
                                      'origin':reverse_name,
                                      'location_id':transit_location_id[0],
                                      'location_dest_id':dest_loc_id[0],
                                      'create_date':inv.date_invoice,
                                      'picking_type_id':picking_type_id[0],
                                      'picking_id':picking_id,
                                      'state':'done'}
                                move_id = models.execute_kw(db, sd_uid, password, 'stock.move', 'create', [move_val])
                                move_ids.append(move_id)    
                            
                        for move in move_ids:
                            models.execute_kw(db, sd_uid, password, 'stock.move', 'action_done', [move])
                        bgin_id = models.execute_kw(db, sd_uid, password,
                        'branch.good.issue.note', 'search',
                        [[['internal_reference', '=',inv.origin]]],
                        {'limit': 1})
                        if bgin_id:
                            models.execute_kw(db, uid, password, 'branch.good.issue.note', 'write', [[bgin_id[0]], {
                                'state': 'reversed'
                            }])
            
            value = {}
        
        result = super(sale_order, self).action_reverse(cr, uid, ids, context=context)
        return result    

        
        