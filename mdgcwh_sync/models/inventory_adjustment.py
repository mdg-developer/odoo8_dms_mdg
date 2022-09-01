from openerp.osv import fields, osv
import xmlrpclib

class stock_inventory(osv.osv):
    _inherit = "stock.inventory"


    def action_done(self, cr, uid, ids, context=None):
        inv_adj_values = {}
        try:
            result = super(stock_inventory, self).action_done(cr, uid, ids, context=context)
            for inv_adj in self.browse(cr, uid, ids, context=context):
                sd_uid,url,db,password = self.pool['cwh.connection'].get_connection_data(cr, uid, context=None)
                models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(url))

                for line in inv_adj.line_ids:
                    location_id = False
                    if (line.theoretical_qty != line.product_qty) and line.location_id.is_cwh_location is True:
                        product_ids = models.execute_kw(db, sd_uid, password,'product.product', 'search',[[('default_code', '=',line.product_id.default_code)]],{'limit': 1})
                        location_ids = models.execute_kw(db, sd_uid, password, 'stock.location', 'search',[[('name','=','Stock')]],{'limit':1})
                        if location_ids:

                            location_id = location_ids[0]
                        if product_ids:
                            # product_id = models.execute_kw(db, sd_uid, password, 'product.product', 'read', [product_ids])[0]
                            product_id = product_ids[0]
                            # uom_id = models.execute_kw(db, sd_uid, password, 'uom.uom', 'search',[[('name', '=', line.product_uom.name)]],{'limit': 1})
                            if product_id:
                                inv_adj_values['product_id'] = product_id
                                inv_adj_values['location_id'] = location_id
                                # inv_adj_values['lot_id'] =
                                inv_adj_values['inventory_quantity']=line.product_qty
                                # inv_adj_values['product_uom_id'] =

                                models.execute_kw(db, sd_uid, password, 'stock.quant', 'create', [inv_adj_values])
        except Exception , e:
            print "error inventory_adjustment",inv_adj_values
            # if order_id:
            #     models.execute_kw(db, sd_uid, password, 'purchase.order', 'unlink', [[order_id]])
            raise e

class stock_location(osv.osv):
    _inherit = "stock.location"

    _columns = {
        'is_cwh_location': fields.boolean('Is CWH Location?'),
    }

    _defaults = {
        'is_cwh_location': False,

    }
