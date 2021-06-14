from openerp.osv import fields, osv
import xmlrpclib

class purchase_order(osv.osv):
    _inherit = "purchase.order"
    
    def wkf_confirm_order(self, cr, uid, ids, context=None):
        result = super(purchase_order, self).wkf_confirm_order(cr, uid, ids, context=context)
        stock_picking_obj = self.pool.get('stock.picking')   
        for po in self.browse(cr, uid, ids, context=context):
            sd_uid,url,db,password = self.pool['cwh.connection'].get_connection_data(cr, uid, context=None)
            models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(url))
           
            picking_type_id = False           
            type_ids = models.execute_kw(db, sd_uid, password,
                    'stock.picking.type', 'search',                
                    [[['warehouse_id', '=', 4], ['name', '=', 'Receipts']]],{'limit': 1}
                    )
            if type_ids: 
                print"type_ids>>>",type_ids     
                picking_type_id=models.execute_kw(db, sd_uid, password, 'stock.picking.type', 'read', [type_ids])[0] 
    
                print"picking_type_id>>>",picking_type_id            
                print"default_locatioin_dest_id>>>",picking_type_id['default_location_dest_id']
                print"default_locatioin_dest_id2>>>",picking_type_id['default_location_dest_id'][0]
                
                
                picking_value = {'origin': po.name,
                             'location_id': 4, #physical location id
                             'location_dest_id': picking_type_id['default_location_dest_id'][0],
                             'priority': '1',
                             'move_type': 'direct',
                             'picking_type_id': picking_type_id['id'],
                             'state': 'draft'}
                picking = models.execute_kw(db, sd_uid, password, 'stock.picking', 'create', [picking_value])
                
                move_array = []  
                for line in po.order_line: 
                    product_id = False               
                    product_ids = models.execute_kw(
                    db, sd_uid, password,
                    'product.product', 'search',
                    [[('default_code', '=',line.product_id.default_code)]],
                    {'limit': 1})
                    print"product_ids>>>",product_ids 
                    if product_ids:  
                        product_id=models.execute_kw(db, sd_uid, password, 'product.product', 'read', [product_ids])[0]
                        print"product_id>>>",product_id 
                        if product_id:
                            move_value ={
                            'name': product_id['name'] + '-' + po.name,
                            'product_id': product_id['id'],
                            'product_uom_qty': line.product_qty,
                            'product_uom': product_id['uom_id'][0],#product_id.uom_id.id,
                            'location_id': 4,
                            'location_dest_id': picking_type_id['default_location_dest_id'][0],
                            'picking_id': picking,
                            'state': 'draft',
                            }
                            print"move_value>>>",move_value 
                            
                            
                            move_array.append(move_value)
                if len(move_array) > 0:
                    print"move_array>>>",move_array 
                    move_id = models.execute_kw(db, sd_uid, password, 'stock.move', 'create', [move_array])
                    print"move_id>>>",move_id 
                else:
                    models.execute_kw(db, sd_uid, password, 'stock.picking', 'unlink', [[picking]])        