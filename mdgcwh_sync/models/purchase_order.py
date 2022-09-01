from openerp.osv import fields, osv
import xmlrpclib
# import logging

class purchase_order(osv.osv):
    _inherit = "purchase.order"
    
    def wkf_confirm_order(self, cr, uid, ids, context=None):
        try:
            picking = False
            order_id = False
            result = super(purchase_order, self).wkf_confirm_order(cr, uid, ids, context=context)

            stock_picking_obj = self.pool.get('stock.picking')   
            for po in self.browse(cr, uid, ids, context=context):
                if not po.location_id.is_cwh_location:
                    return result
                sd_uid,url,db,password = self.pool['cwh.connection'].get_connection_data(cr, uid, context=None)
                models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(url))
                po_vals={}
                po_vals['partner_id'] =7
                po_name = po.name
                if po.partner_ref:
                    po_partner_ref = po.partner_ref
                else:
                    po_partner_ref = ""
                flag_partner_ref = ""
                index = po_name.find('_')
                # if index != -1:
                #     flag_partner_ref = po_name[0:index+1]+po_partner_ref
                # else:
                #     flag_partner_ref = po_name+"_"+po_partner_ref
                if index != -1:
                    flag_partner_ref = po_name[0:index+1]+po_partner_ref
                if index == -1 and po_partner_ref != "" :
                    flag_partner_ref = po_name+"_"+po_partner_ref
                if index == -1 and po_partner_ref == "" :
                    flag_partner_ref = po_name
                po_vals['partner_ref']= po.name                        
                po_vals['order_line']= []
                po_vals['origin'] = flag_partner_ref
                picking_type_id = False           
                type_ids = models.execute_kw(db, sd_uid, password,'stock.picking.type', 'search',[[['warehouse_id', '=', 1], ['name', '=', 'Receipts']]],{'limit': 1})
                if type_ids: 
                    po_vals['picking_type_id'] =type_ids[0] 
                    print"type_ids>>>",type_ids
                    move_array = []  
                    for line in po.order_line: 
                        product_id = uom_id = False
                        qty = 0               
                        product_ids = models.execute_kw(db, sd_uid, password,'product.product', 'search',[[('default_code', '=',line.product_id.default_code)]],{'limit': 1})
                        print"product_ids>>>",product_ids
                        if product_ids:  
                            product_id=models.execute_kw(db, sd_uid, password, 'product.product', 'read', [product_ids])[0]
                            print"product_id>>>",product_id                            
                            uom_id=models.execute_kw(db, sd_uid, password, 'uom.uom', 'search',  [[('name', '=',line.product_uom.name)]],{'limit': 1})
                             
                            print"uom_id>>>",uom_id 
                            if product_id:
                                po_create = True                            
                                po_vals['order_line'].append([0, False, {'name': product_id['name'],
                                                                         'product_id': product_id['id'],
                                                                         'product_qty': line.product_qty,
                                                                         'product_uom_qty': line.product_qty,
                                                                         'product_uom': uom_id[0],
                                                                         'price_unit':product_id['lst_price']
                                                            }])
                    if po_create == True:
                        print"po_vals>>>",po_vals 
                        order_id = models.execute_kw(db, sd_uid, password, 'purchase.order', 'create', [po_vals])
                        if order_id:
                            print 'order_id', order_id
                            models.execute_kw(db, sd_uid, password, 'purchase.order', 'button_confirm', [order_id])
            return result
        except Exception , e:
            print "Exception",e
            if order_id:
                models.execute_kw(db, sd_uid, password, 'purchase.order', 'unlink', [[order_id]])
            raise e    
