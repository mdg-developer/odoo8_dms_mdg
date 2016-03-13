from openerp.osv import fields, osv
from datetime import datetime
import ast

class pre_sale_order(osv.osv):
    
    _name = "pre.sale.order"
    _description = "Pre Sales Order"
   
    _columns = {
        'name': fields.char('Order Reference', size=64),
        'partner_id':fields.many2one('res.partner', 'Customer'),
        'customer_code':fields.char('Customer Code'),
        'sale_plan_name':fields.char('Sale Plan Name'),
        'user_id':fields.many2one('res.users', 'Saleman Name'),
        'mso_latitude':fields.float('Geo Latitude'),
        'mso_longitude':fields.float('Geo Longitude'),
        'amount_total':fields.float('Total Amount'),
        'delivery_remark':fields.selection([
                ('partial', 'Partial'),
                ('delivered', 'Delivered'),
                ('none', 'None')
            ], 'Deliver Remark'),
        'date':fields.datetime('Date'),
        'note':fields.text('Note'),
        'order_line': fields.one2many('pre.sale.order.line', 'order_id', 'Order Lines', copy=True),
        'delivery_order_line': fields.one2many('products.to.deliver', 'sale_order_id', 'Delivery Order Lines', copy=True),
        'tablet_id':fields.many2one('tablets.information', 'Tablet ID'),
        'sale_plan_day_id':fields.many2one('sale.plan.day', 'Sale Plan Day'),
        'sale_plan_trip_id':fields.many2one('sale.plan.trip', 'Sale Plan Trip'),
        'warehouse_id' : fields.many2one('stock.warehouse', 'Warehouse'),
        'sale_team':fields.many2one('crm.case.section', 'Sale Team'),
        'location_id'  : fields.many2one('stock.location', 'Location'),
        'm_status':fields.char('Status'),
     'promos_line_ids':fields.one2many('mso.promotion.line', 'promo_line_id', 'Promotion Lines')                
    }
    _order = 'id desc'
    _defaults = {
        'date': datetime.now(),
        'm_status' : 'draft',
       
    }
    
    def create_presaleorder(self, cursor, user, vals, context=None):
        print 'vals',vals
        sale_order_name_list = []
        try : 
            mobile_sale_order_obj=self.pool.get('pre.sale.order')
            mobile_sale_order_line_obj=self.pool.get('pre.sale.order.line')
            str ="{"+vals+"}"
            str = str.replace(":''",":'")#change Order_id
            str = str.replace("'',","',")#null
            str = str.replace(":',",":'',")#due to order_id
            str = str.replace("}{", "}|{")
            new_arr = str.split('|')
            result = []
            for data in new_arr:
                x = ast.literal_eval(data)
                result.append(x)
            sale_order=[]
            sale_order_line = []
            for r in result:
                print "length", len(r)
                if len(r)>=17:
                    sale_order.append(r)
                else:
                    sale_order_line.append(r)
            
            if sale_order:
                for so in sale_order:
                    print 'Sale Man Id',so['user_id']
                    cursor.execute('select id From res_users where partner_id  = %s ',(so['user_id'],))
                    data = cursor.fetchall()
                    if data:
                        saleManId = data[0][0]
                    else:
                        saleManId = None
                    mso_result={
                        'customer_code':so['customer_code'],
                        'paid': True,
                        'warehouse_id':so['warehouse_id'],
                        'tablet_id':so['tablet_id'],
                        'delivery_remark':so['delivery_remark'],
                        'location_id':so['location_id'],
                        'user_id':so['user_id'],
                        'name':so['name'],
                        'partner_id':so['partner_id'],
                        'sale_plan_name':so['sale_plan_day_name'],
                        'amount_total':so['amount_total'],
#                         'type':so['type'],
#                         'void_flag':so['void_flag'],
                        'sale_team':so['sale_team'],
                        'date':so['date'],
#                         'payment_term':so['payment_term'],
                        'mso_longitude':so['mso_longitude'],
                        'mso_latitude':so['mso_latitude']
                    }
                    s_order_id = mobile_sale_order_obj.create(cursor, user, mso_result, context=context)
                    print "Create Sale Order",so['name']
                    for sol in sale_order_line:
                        if sol['so_name'] == so['name']:
                                cursor.execute('select id From product_product where product_tmpl_id  = %s ',(sol['product_id'],))
                                data = cursor.fetchall()
                                if data:
                                    productId = data[0][0]
                                else:
                                    productId = None
                                mso_line_res={                                                            
                                  'order_id':s_order_id,
                                  'product_id':productId,
                                  'price_unit':sol['price_unit'],   
                                  'product_uos_qty':sol['product_uos_qty'],   
#                                   'discount':sol['discount'],
                                  'sub_total':sol['sub_total'],
                                }
                                mobile_sale_order_line_obj.create(cursor, user, mso_line_res, context=context) 
                                print 'Create Order line',sol['so_name']                     
                    sale_order_name_list.append(so['name'])
            print 'True'
            return True       
        except Exception, e:
            print 'False'
            return False 
    
pre_sale_order()
class pre_sale_order_line(osv.osv):
    
    _name = "pre.sale.order.line"
    _description = "Mobile Sales Order"

    _columns = {
        'product_id':fields.many2one('product.product', 'Products'),
        'product_uos_qty':fields.float('Quantity'),
        'uom_id':fields.many2one('product.uom', 'UOM'),
        'price_unit':fields.float('Unit Price'),
        'discount':fields.float('Discount (%)'),
        'order_id': fields.many2one('pre.sale.order', 'Sale Order'),
        'sub_total':fields.float('Sub Total'),
        'foc':fields.boolean('FOC'),
    }
    _defaults = {
       'product_uos_qty':1.0,
    }
pre_sale_order_line()