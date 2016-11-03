from openerp.osv import fields, osv
from openerp.osv import orm
from openerp.tools.translate import _
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
        'user_id':fields.many2one('res.users', 'Salesman Name'),
        'mso_latitude':fields.float('Geo Latitude'),
        'mso_longitude':fields.float('Geo Longitude'),
        'amount_total':fields.float('Total Amount'),
        'type':fields.selection([
                ('credit', 'Credit'),
                ('cash', 'Cash'),
                ('consignment', 'Consignment'),
                ('advanced', 'Advanced')
            ], 'Payment Type'),
        'delivery_remark':fields.selection([
                ('partial', 'Partial'),
                ('delivered', 'Delivered'),
                ('none', 'None')
            ], 'Deliver Remark'),
        'date':fields.datetime('Date'),
        'note':fields.text('Note'),
        'order_line': fields.one2many('pre.sale.order.line', 'order_id', 'Order Lines', copy=True),
        'delivery_order_line': fields.one2many('pre.products.to.deliver', 'sale_order_id', 'Delivery Order Lines', copy=True),
        'tablet_id':fields.many2one('tablets.information', 'Tablet ID'),
        'sale_plan_day_id':fields.many2one('sale.plan.day', 'Sale Plan Day'),
        'sale_plan_trip_id':fields.many2one('sale.plan.trip', 'Sale Plan Trip'),
        'warehouse_id' : fields.many2one('stock.warehouse', 'Warehouse'),
        'sale_team':fields.many2one('crm.case.section', 'Sale Team'),
        'location_id'  : fields.many2one('stock.location', 'Location'),
        'deduction_amount':fields.float('Deduction Amount'),
        'm_status':fields.selection([('draft', 'Draft'),
                                     
                                                      ('done', 'Complete')], string='Status'),
     'promos_line_ids':fields.one2many('pre.promotion.line', 'promo_line_id', 'Promotion Lines'),
     'pricelist_id': fields.many2one('product.pricelist', 'Price List', select=True, ondelete='cascade'),
       'payment_line_ids':fields.one2many('customer.payment', 'pre_order_id', 'Payment Lines'),
      'branch_id': fields.many2one('res.branch', 'Branch', required=True),
             'void_flag':fields.selection([
                ('voided', 'Voided'),
                ('none', 'Unvoid')
            ], 'Void'),
    }
    _order = 'id desc'
    _defaults = {
        'date': datetime.now(),
        'm_status' : 'draft',
       
    }
    
    def create_presaleorder(self, cursor, user, vals, context=None):
        print 'vals', vals
        sale_order_name_list = []
        try : 
            saleManId = branch_id = None
            mobile_sale_order_obj = self.pool.get('pre.sale.order')
            mobile_sale_order_line_obj = self.pool.get('pre.sale.order.line')
            str = "{" + vals + "}"
            str = str.replace(":''", ":'")  # change Order_id
            str = str.replace("'',", "',")  # null
            str = str.replace(":',", ":'',")  # due to order_id
            str = str.replace("}{", "}|{")
            new_arr = str.split('|')
            result = []
            for data in new_arr:
                x = ast.literal_eval(data)
                result.append(x)
            sale_order = []
            sale_order_line = []
            for r in result:
                print "length", len(r)
                if len(r) >= 17:
                    sale_order.append(r)
                else:
                    sale_order_line.append(r)
            
            if sale_order:
                for so in sale_order:
                    print 'Sale Man Id', so['user_id']
                    cursor.execute('select id,branch_id From res_users where id  = %s ', (so['user_id'],))
                    data = cursor.fetchall()
                    
                    if data:
                        saleManId = data[0][0]
                        branch_id = data[0][1]
                    else:
                        saleManId = None						 
						 
                    cursor.execute('select id From res_partner where customer_code  = %s ', (so['customer_code'],))
                    data = cursor.fetchall()                
                    if data:
                        partner_id = data[0][0]
                       
                    else:
                        partner_id = None

                    mso_result = {
                        'customer_code':so['customer_code'],
                        'paid': True,
                        'warehouse_id':so['warehouse_id'],
                        'tablet_id':so['tablet_id'],
                        'delivery_remark':so['delivery_remark'],
                        'location_id':so['location_id'],
                        'user_id':so['user_id'],
                        'name':so['name'],
                        'type':so['type'],
                        'partner_id':partner_id,
                        'sale_plan_name':so['sale_plan_day_name'],
                        'amount_total':so['amount_total'],
                        'sale_team':so['sale_team'],
                        'date':so['date'],
						'void_flag':so['void_flag'],
                        'sale_plan_day_id':so['sale_plan_day_id'],
                        'mso_longitude':so['mso_longitude'],
                        'mso_latitude':so['mso_latitude'],
                        'pricelist_id':so['pricelist_id'],
                        'branch_id':branch_id,
                    }
                    s_order_id = mobile_sale_order_obj.create(cursor, user, mso_result, context=context)
                    print "Create Sale Order", so['name']
                    for sol in sale_order_line:
                        if sol['so_name'] == so['name']:
                                cursor.execute('select id From product_product where id  = %s ', (sol['product_id'],))
                                data = cursor.fetchall()
                                if data:
                                    productId = data[0][0]
                                else:
                                    productId = None
                                if sol['price_unit'] == '0':
                                    foc_val = True
                                else:
                                    foc_val = False								
                                mso_line_res = {                                                            
                                  'order_id':s_order_id,
                                  'product_id':productId,
                                  'price_unit':sol['price_unit'],
								  'foc':foc_val,
                                  'product_uos_qty':sol['product_uos_qty'],
                                  'discount':sol['discount'],
                                  'discount_amt':sol['discount_amt'],
                                  'sub_total':sol['sub_total'],
                                  'uom_id':sol['uom_id']
                                }
                                mobile_sale_order_line_obj.create(cursor, user, mso_line_res, context=context) 
                                print 'Create Order line', sol['so_name']                     
                    sale_order_name_list.append(so['name'])
            print 'True'
            return True       
        except Exception, e:
            print 'False'
            return False 

    def create_invoices(self, cr, uid, ids, context=None):
        """ create invoices for the active sales orders """
        print 'Sale Order ID', ids  
        sale_obj = self.pool.get('sale.order')
        sale_ids = ids
        if sale_ids:
            # create the final invoices of the active sales orders
            print 'YOOOOOOOOOOOOO', sale_ids
            try:
                print 'Create Invoice Context', context
                res = sale_obj.manual_invoice(cr, uid, sale_ids, context=context)          
                print 'ressssssssssssss',res
                return res['res_id']
            except Exception, e:
                return False
                
    def action_convert_presaleorder(self, cr, uid, ids, context=None):
        msoObj = self.pool.get('mobile.sale.order')
        presaleorderObj = self.pool.get('pre.sale.order')
        saleOrderObj = self.pool.get('sale.order')
        saleOrderLineObj = self.pool.get('sale.order.line')
        invObj = self.pool.get("sale.advance.payment.inv")
        invoiceObj = self.pool.get('account.invoice')        
        so_id = pricelist_id = sale_foc = productName = None
        priceUnit = 0.0
        saleOrderResult = {}
        detailResult = {}
        if ids:
            try:
                # default price list need in sale order form
#                 cr.execute("""select id from product_pricelist""")
#                 data = cr.fetchall()
#                 if data:
#                     pricelist_id = data[0][0]
                for preObj_ids in presaleorderObj.browse(cr, uid, ids[0], context=context):
                    if preObj_ids:
                        print 'Sale Team', preObj_ids.sale_team
                        cr.execute('select delivery_team_id from crm_case_section where id = %s ', (preObj_ids.sale_team.id,))
                        data = cr.fetchall()
                        if data:
                            delivery_id = data[0][0]
                        else:
                            delivery_id = None
                        cr.execute('select company_id from res_users where id=%s', (preObj_ids.user_id.id,))
                        company_id = cr.fetchone()[0]
                        if preObj_ids.void_flag == 'voided':  # they work while payment type not 'cash' and 'credit'
                            so_state = 'cancel'
                        elif preObj_ids.void_flag == 'none':
                            so_state = 'manual'
                        print 'so_ssssssssssssstae',so_state
                        saleOrderResult = {'partner_id':preObj_ids.partner_id.id,
                                                        'customer_code':preObj_ids.customer_code,
                                                        'sale_plan_name':preObj_ids.sale_plan_name,
                                                        'sale_plan_day_id':preObj_ids.sale_plan_day_id.id,
                                                        'sale_plan_trip_id':preObj_ids.sale_plan_trip_id.id,
                                                        'date_order':preObj_ids.date,
                                                        'tb_ref_no':preObj_ids.name,
                                                        'warehouse_id':preObj_ids.warehouse_id.id,
                                                        'delivery_remark':preObj_ids.delivery_remark,
                                                        'so_latitude':preObj_ids.mso_latitude,
                                                        'so_longitude':preObj_ids.mso_longitude,
                                                        'user_id':preObj_ids.user_id.id,
                                                        'section_id':preObj_ids.sale_team.id,
                                                        'deduct_amt':preObj_ids.deduction_amount,
#                                                         'client_order_ref':preObj_ids.tablet_id.name,
                                                         'state':so_state,
                                                         'payment_type':preObj_ids.type,
                                                        'pricelist_id':preObj_ids.pricelist_id.id,
                                                        'pre_order':True,
                                                        'delivery_id':delivery_id,
                                                        'branch_id':preObj_ids.branch_id.id,
                                                        'company_id':company_id,
                                                         }
                        so_id = saleOrderObj.create(cr, uid, saleOrderResult, context=context)
                    if so_id and preObj_ids.order_line:
                        for line_id in preObj_ids.order_line:
                            if line_id:
                                
                                if line_id.foc == True:
                                    sale_foc = line_id.foc
                                    priceUnit = 0
                                    productName = 'FOC'
                                else:
                                    sale_foc = line_id.foc
                                    priceUnit = line_id.price_unit
                                    productName = line_id.product_id.name
                                    
                                detailResult = {'order_id':so_id,
                                                        'product_id':line_id.product_id.id,
                                                        'name':productName,
                                                        'product_uom':line_id.uom_id.id,
                                                        'product_uom_qty':line_id.product_uos_qty,
                                                        'discount':line_id.discount,
                                                        'discount_amt':line_id.discount_amt,
                                                        'sale_foc':sale_foc,
                                                        'price_unit':priceUnit,
                                                        'company_id':company_id,  # company_id,
                                                        }   
                                saleOrderLineObj.create(cr, uid, detailResult, context=context)
                    if so_id and  so_state != 'cancel':
                        solist = []
                        solist.append(so_id)
                        saleOrderObj.button_dummy(cr, uid, [so_id], context=context)
                        # Do Open
                        saleOrderObj.action_button_confirm(cr, uid, [so_id], context=context)
                        print 
                        invoice_id = self.create_invoices(cr, uid, solist, context=context)
                            #id update partner form (temporay)
                        cr.execute('update account_invoice set payment_type=%s ,branch_id =%s,pre_order=True where id =%s',(preObj_ids.type,preObj_ids.branch_id.id,invoice_id,))                            
                        invoiceObj.button_reset_taxes(cr, uid, [invoice_id], context=context)
                        if invoice_id :
                            invlist = []
                            invlist.append(invoice_id)
                            # call the api function
                            # invObj contain => account.invoice(1,) like that
                            invObj = invoiceObj.browse(cr, uid, invoice_id, context=context)
                            print 'invoice_id', invObj
                            invObj.action_date_assign()
                            invObj.action_move_create()
                            invObj.action_number()
                            # validate invoice
                            #invObj.invoice_validate()                        
                        
                        
            except Exception, e:
                raise orm.except_orm(_('Error :'), _("Error Occured while Convert Mobile Sale Order! \n [ %s ]") % (e))
            self.write(cr, uid, ids[0], {'m_status':'done'}, context=context)                        
        return True
    
# Create Sync for promotion line by kzo
    def create_promotion_line(self, cursor, user, vals, context=None):
        
        try : 
            mso_promotion_line_obj = self.pool.get('pre.promotion.line')
            str = "{" + vals + "}"
                
            str = str.replace("'',", "',")  # null
            str = str.replace(":',", ":'',")  # due to order_id
            str = str.replace("}{", "}|{")
            new_arr = str.split('|')
            result = []
            for data in new_arr:
                x = ast.literal_eval(data)
                result.append(x)
            promo_line = []
            for r in result:                
                promo_line.append(r)  
            if promo_line:
                for pro_line in promo_line:
                
                    cursor.execute('select id From pre_sale_order where name  = %s ', (pro_line['promo_line_id'],))
                    data = cursor.fetchall()
                    if data:
                        saleOrder_Id = data[0][0]
                    else:
                        saleOrder_Id = None
                                    
                    promo_line_result = {
                        'promo_line_id':saleOrder_Id,
                        'pro_id':pro_line['pro_id'],
                        'from_date':pro_line['from_date'],
                        'to_date':pro_line['to_date'] ,
                        }
                    mso_promotion_line_obj.create(cursor, user, promo_line_result, context=context)
            return True
        except Exception, e:
            return False
pre_sale_order()
class pre_sale_order_line(osv.osv):
    
    _name = "pre.sale.order.line"
    _description = "Mobile Sales Order"
    
    def _get_uom_from_product(self, cr, uid, ids, field_name, arg, context=None):
        result = {}
        for rec in self.browse(cr, uid, ids, context=context):
            result[rec.id] = rec.product_id.uom_id
        return result       
    
    _columns = {
        'product_id':fields.many2one('product.product', 'Products'),
        'product_uos_qty':fields.float('Quantity'),
#        'uom_id':fields.function(_get_uom_from_product, type='many2one', relation='product.uom', string='UOM'),
        'uom_id':fields.many2one('product.uom', 'UOM', readonly=False),
        'price_unit':fields.float('Unit Price'),
        'discount':fields.float('Discount (%)'),
        'discount_amt':fields.float('Discount (Amt)'),
        'order_id': fields.many2one('pre.sale.order', 'Sale Order'),
        'sub_total':fields.float('Sub Total'),
        'foc':fields.boolean('FOC'),
    }
    _defaults = {
       'product_uos_qty':1.0,
    }
pre_sale_order_line()

class pre_promotion_line(osv.osv):
    _name = 'pre.promotion.line'
    _columns = {
              'promo_line_id':fields.many2one('pre.sale.order', 'Promotion line'),
              'pro_id': fields.many2one('promos.rules', 'Promotion Rule', change_default=True, readonly=False),
              'from_date':fields.datetime('From Date'),
              'to_date':fields.datetime('To Date')
              }
    
    def onchange_promo_id(self, cr, uid, ids, pro_id, context=None):
            result = {}
            promo_pool = self.pool.get('promos.rules')
            datas = promo_pool.read(cr, uid, pro_id, ['from_date', 'to_date'], context=context)
    
            if datas:
                result.update({'from_date':datas['from_date']})
                result.update({'to_date':datas['to_date']})
            return {'value':result}
            
pre_promotion_line()


class pre_product_yet_to_deliver_line(osv.osv):
    
    _name = "pre.products.to.deliver"
    _description = "Product Yet To Deliver"

    def _get_uom_from_product(self, cr, uid, ids, field_name, arg, context=None):
        result = {}
        for rec in self.browse(cr, uid, ids, context=context):
            result[rec.id] = rec.product_id.uom_id
        return result       
                           
    _columns = {
        'product_id':fields.many2one('product.product', 'Products'),
        'uom':fields.function(_get_uom_from_product, type='many2one', relation='product.uom', string='UOM'),
        'product_qty':fields.float('Quantity'),
        'product_qty_to_deliver':fields.float('Quantity To Deliver'),
        'sale_order_id': fields.many2one('pre.sale.order', 'Sale Order'),
                }
    
pre_product_yet_to_deliver_line()
