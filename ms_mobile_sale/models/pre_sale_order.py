from openerp.osv import fields, osv
from openerp.osv import orm
from openerp.tools.translate import _
from datetime import datetime
import ast
from openerp import api
from openerp.addons.connector.queue.job import job, related_action
from openerp.addons.connector.session import ConnectorSession
from openerp.addons.connector.exception import FailedJobError

from openerp.addons.connector.jobrunner.runner import ConnectorRunner

@job(default_channel='root.preorder')
def automation_pre_order(session,list_mobile):
    context = session.context.copy()
    cr = session.cr
    uid = session.uid
    print 'automation pre order:',list_mobile
    mobile_obj = session.pool.get('pre.sale.order')
    #list_mobile = mobile_obj.search(cr, uid, [('void_flag', '=', 'none'), ('m_status', '=', 'draft'), ('partner_id', '!=', None)])            
    for mobile in list_mobile: 
        mobile_obj.action_convert_presaleorder(cr, uid, [mobile], context=context)    
    return True

class pre_sale_order(osv.osv):
    
    _name = "pre.sale.order"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = "Pre Sales Order"
   
    _columns = {
        'name': fields.char('Order Reference', size=64),
        'partner_id':fields.many2one('res.partner', 'Customer',track_visibility='always'),
        'customer_code':fields.char('Customer Code',track_visibility='always'),
        'sale_plan_name':fields.char('Sale Plan Name',track_visibility='always'),
        'user_id':fields.many2one('res.users', 'Salesman Name',track_visibility='always'),
        'mso_latitude':fields.float('Geo Latitude',track_visibility='always'),
        'mso_longitude':fields.float('Geo Longitude',track_visibility='always'),
        'amount_total':fields.float('Total Amount',compute='_compute_paid_amount',track_visibility='always'),
        'type':fields.selection([
                ('credit', 'Credit'),
                ('cash', 'Cash'),
                ('consignment', 'Consignment'),
                ('advanced', 'Advanced')
            ], 'Payment Type',track_visibility='always'),
        'delivery_remark':fields.selection([
                ('partial', 'Partial'),
                ('delivered', 'Delivered'),
                ('none', 'None')
            ], 'Deliver Remark',track_visibility='always'),
        'date':fields.datetime('Order Date',track_visibility='always'),
		'due_date':fields.date('Due Date',track_visibility='always'),
        'note':fields.text('Note',track_visibility='always'),
        'order_line': fields.one2many('pre.sale.order.line', 'order_id', 'Order Lines', copy=True,track_visibility='always'),
        'delivery_order_line': fields.one2many('pre.products.to.deliver', 'sale_order_id', 'Delivery Order Lines', copy=True,track_visibility='always'),
        'tablet_id':fields.many2one('tablets.information', 'Tablet ID',track_visibility='always'),
        'sale_plan_day_id':fields.many2one('sale.plan.day', 'Sale Plan Day',track_visibility='always'),
        'sale_plan_trip_id':fields.many2one('sale.plan.trip', 'Sale Plan Trip',track_visibility='always'),
        'warehouse_id' : fields.many2one('stock.warehouse', 'Warehouse',track_visibility='always'),
        'sale_team':fields.many2one('crm.case.section', 'Sale Team',track_visibility='always'),
        'location_id'  : fields.many2one('stock.location', 'Location',track_visibility='always'),
        'deduction_amount':fields.float('Deduction Amount',track_visibility='always'),
        'm_status':fields.selection([('draft', 'Draft'),
                                     
                                                      ('done', 'Complete')], string='Status',track_visibility='always'),
     'promos_line_ids':fields.one2many('pre.promotion.line', 'promo_line_id', 'Promotion Lines',track_visibility='always'),
     'pricelist_id': fields.many2one('product.pricelist', 'Price List', select=True, ondelete='cascade',track_visibility='always'),
       'payment_line_ids':fields.one2many('customer.payment', 'pre_order_id', 'Payment Lines',track_visibility='always'),
      'branch_id': fields.many2one('res.branch', 'Branch', required=True,track_visibility='always'),
             'void_flag':fields.selection([
                ('voided', 'Voided'),
                ('none', 'Unvoid')
            ], 'Void',track_visibility='always'),
      'is_convert':fields.boolean('Is Convert',readonly=True,track_visibility='always'),
      'print_count':fields.integer('RePrint Count',track_visibility='always'),
      'rebate_later':fields.boolean('Rebate Later',track_visibility='always'),
      'schedule_date':fields.datetime('Date to deliver',track_visibility='always'),
      'customer_sign':fields.binary('Customer Sign',track_visibility='always'),
      'payment_term_id': fields.many2one('account.payment.term', 'Payment Term',track_visibility='always'),
    }
    _order = 'id desc'
    _defaults = {
        'date': datetime.now(),
        'm_status' : 'draft',
        'is_convert':False,
       
    }
    @api.multi
    @api.depends('order_line.sub_total') 
    def _compute_paid_amount(self):
        for record in self:
            record.amount_total = sum(line.sub_total for line in record.order_line)
            
    
    def create_presaleorder(self, cursor, user, vals, context=None):
        print 'vals', vals

        sale_order_name_list = []
        try : 
            saleManId = branch_id = promotion_id=None
            mobile_sale_order_obj = self.pool.get('pre.sale.order')
            mobile_sale_order_line_obj = self.pool.get('pre.sale.order.line')
            str = "{" + vals + "}"
            str = str.replace(":''", ":'")  # change Order_id
            str = str.replace("'',", "',")  # null
            str = str.replace(":',", ":'',")  # due to order_id
            str = str.replace("}{", "}|{")
            new_arr = str.split('|')
            result = []
            so_ids=[]
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
                    if so['rebate'] == 'T':
                        rebate = True
                    else:
                        rebate = False                    
                    mso_result = {
                        'customer_code':so['customer_code'],
                        'paid': True,
                        'warehouse_id':so['warehouse_id'],
                        'tablet_id':so['tablet_id'],
                        'delivery_remark':so['delivery_remark'],
                        'location_id':so['location_id'],
                        'user_id':int(so['user_id']),
                        'name':so['name'],
                        'type':so['type'],
                        'note':so['note'],
                        'partner_id':partner_id,
                        'sale_plan_name':so['sale_plan_day_name'],
                        'amount_total':so['amount_total'],
                        'sale_team':so['sale_team'],
                        'date':so['date'],
						'due_date':so['due_date'],
						'void_flag':so['void_flag'],
                        'sale_plan_day_id':so['sale_plan_day_id'],
                        'mso_longitude':so['mso_longitude'],
                        'mso_latitude':so['mso_latitude'],
                        'pricelist_id':so['pricelist_id'],
                        'branch_id':branch_id,
                        'print_count':so['print_count'],
                        'rebate_later':rebate,
                        'schedule_date':so['date_to_deliver'],
                        'customer_sign':so['customerSign'],
                        'payment_term_id':so.get('paymentTermID')
                    }
                    s_order_id = mobile_sale_order_obj.create(cursor, user, mso_result, context=context)
                    so_ids.append(s_order_id)
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
                                if sol['manual_foc'] == 'T':
                                    manual_foc = True
                                else:
                                    manual_foc = False       
                                if sol['promotion_action'] and  sol['promotion_action']!='null':
                                    cursor.execute("select promotion from promos_rules_actions where id =%s",(sol['promotion_action'],))
                                    promotion_id = cursor.fetchone()[0]
                                else:
                                    promotion_id=False
                                if sol['manual_promotion'] and sol['manual_promotion'] != 'null':
                                    promotion_id = sol['manual_promotion']  
                                price =sol['price_unit']
#                                 if  float(price) < 0:
#                                     product_price= 0
#                                     discount_amt =-1 * float(price)
#                                 else:
                                product_price=sol['price_unit']
                                discount_amt=sol['discount_amt']
                                                                      			
                                mso_line_res = {                                                            
                                  'order_id':s_order_id,
                                  'product_id':productId,
                                  'price_unit':product_price,
								  'foc':foc_val,
                                  'product_uos_qty':sol['product_uos_qty'],
                                  'discount':sol['discount'],
                                  'discount_amt':discount_amt,
                                  'sub_total':sol['sub_total'],
                                  'uom_id':sol['uom_id'],
                                  'manual_foc':manual_foc,
                                  'promotion_id':promotion_id,
                                }
                                mobile_sale_order_line_obj.create(cursor, user, mso_line_res, context=context) 
                                print 'Create Order line', sol['so_name']                     
                    sale_order_name_list.append(so['name'])
            print 'True'
            
            session = ConnectorSession(cursor, user, context)
            jobid=automation_pre_order.delay(session,so_ids, priority=10)
            print "Job",jobid
            runner = ConnectorRunner()
            runner.run_jobs()
            return True 
                  
        except Exception, e:
            print 'False'
            print e
            return False 
    
    def create_presaleorder_by_old_code(self, cursor, user, vals, context=None):
        print 'vals', vals

        sale_order_name_list = []
        try : 
            saleManId = branch_id = promotion_id=None
            mobile_sale_order_obj = self.pool.get('pre.sale.order')
            mobile_sale_order_line_obj = self.pool.get('pre.sale.order.line')
            str = "{" + vals + "}"
            str = str.replace(":''", ":'")  # change Order_id
            str = str.replace("'',", "',")  # null
            str = str.replace(":',", ":'',")  # due to order_id
            str = str.replace("}{", "}|{")
            new_arr = str.split('|')
            result = []
            so_ids=[]
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

                    cursor.execute('select id From res_partner where old_code  = %s ', (so['customer_code'],))
                    data = cursor.fetchall()                
                    if data:
                        partner_id = data[0][0]
                       
                    else:
                        partner_id = None
                    if so['rebate'] == 'T':
                        rebate = True
                    else:
                        rebate = False                    
                    mso_result = {
                        'customer_code':so['customer_code'],
                        'paid': True,
                        'warehouse_id':so['warehouse_id'],
                        'tablet_id':so['tablet_id'],
                        'delivery_remark':so['delivery_remark'],
                        'location_id':so['location_id'],
                        'user_id':int(so['user_id']),
                        'name':so['name'],
                        'type':so['type'],
                        'note':so['note'],
                        'partner_id':partner_id,
                        'sale_plan_name':so['sale_plan_day_name'],
                        'amount_total':so['amount_total'],
                        'sale_team':so['sale_team'],
                        'date':so['date'],
                        'due_date':so['due_date'],
                        'void_flag':so['void_flag'],
                        'sale_plan_day_id':so['sale_plan_day_id'],
                        'mso_longitude':so['mso_longitude'],
                        'mso_latitude':so['mso_latitude'],
                        'pricelist_id':so['pricelist_id'],
                        'branch_id':branch_id,
                        'print_count':so['print_count'],
                        'rebate_later':rebate,
                        'schedule_date':so['date_to_deliver'],
                        'customer_sign':so['customerSign'],
                        'payment_term_id':so.get('paymentTermID')
                    }
                    s_order_id = mobile_sale_order_obj.create(cursor, user, mso_result, context=context)
                    so_ids.append(s_order_id)
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
                                if sol['manual_foc'] == 'T':
                                    manual_foc = True
                                else:
                                    manual_foc = False       
                                if sol['promotion_action'] and  sol['promotion_action']!='null':
                                    cursor.execute("select promotion from promos_rules_actions where id =%s",(sol['promotion_action'],))
                                    promotion_id = cursor.fetchone()[0]
                                else:
                                    promotion_id=False
                                if sol['manual_promotion'] and sol['manual_promotion'] != 'null':
                                    promotion_id = sol['manual_promotion']  
                                price =sol['price_unit']
#                                 if  float(price) < 0:
#                                     product_price= 0
#                                     discount_amt =-1 * float(price)
#                                 else:
                                product_price=sol['price_unit']
                                discount_amt=sol['discount_amt']
                                                                                  
                                mso_line_res = {                                                            
                                  'order_id':s_order_id,
                                  'product_id':productId,
                                  'price_unit':product_price,
                                  'foc':foc_val,
                                  'product_uos_qty':sol['product_uos_qty'],
                                  'discount':sol['discount'],
                                  'discount_amt':discount_amt,
                                  'sub_total':sol['sub_total'],
                                  'uom_id':sol['uom_id'],
                                  'manual_foc':manual_foc,
                                  'promotion_id':promotion_id,
                                }
                                mobile_sale_order_line_obj.create(cursor, user, mso_line_res, context=context) 
                                print 'Create Order line', sol['so_name']                     
                    sale_order_name_list.append(so['name'])
            print 'True'
            
            session = ConnectorSession(cursor, user, context)
            jobid=automation_pre_order.delay(session,so_ids, priority=10)
            print "Job",jobid
            runner = ConnectorRunner()
            runner.run_jobs()
            return True 
                  
        except Exception, e:
            print 'False'
            print e
            return False 
        
    def create_presaleorder_by_old_code_fix(self, cursor, user, vals, context=None):
        print 'vals', vals

        sale_order_name_list = []
        try : 
            saleManId = branch_id = promotion_id=None
            mobile_sale_order_obj = self.pool.get('pre.sale.order')
            mobile_sale_order_line_obj = self.pool.get('pre.sale.order.line')
            str = "{" + vals + "}"
            str = str.replace(":''", ":'")  # change Order_id
            str = str.replace("'',", "',")  # null
            str = str.replace(":',", ":'',")  # due to order_id
            str = str.replace("}{", "}|{")
            new_arr = str.split('|')
            result = []
            so_ids=[]
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

                    cursor.execute('select id From res_partner where old_code  = %s ', (so['customer_code'],))
                    data = cursor.fetchall()                
                    if data:
                        partner_id = data[0][0]
                       
                    else:
                        partner_id = None
                    if so['rebate'] == 'T':
                        rebate = True
                    else:
                        rebate = False                    
                    mso_result = {
                        'customer_code':so['customer_code'],
                        'paid': True,
                        'warehouse_id':so['warehouse_id'],
                        'tablet_id':so['tablet_id'],
                        'delivery_remark':so['delivery_remark'],
                        'location_id':so['location_id'],
                        'user_id':int(so['user_id']),
                        'name':so['name'],
                        'type':so['type'],
                        'note':so['note'],
                        'partner_id':partner_id,
                        'sale_plan_name':so['sale_plan_day_name'],
                        'amount_total':so['amount_total'],
                        'sale_team':so['sale_team'],
                        'date':so['date'],
                        'due_date':so['due_date'],
                        'void_flag':so['void_flag'],
                        'sale_plan_day_id':so['sale_plan_day_id'],
                        'mso_longitude':so['mso_longitude'],
                        'mso_latitude':so['mso_latitude'],
                        'pricelist_id':so['pricelist_id'],
                        'branch_id':branch_id,
                        'print_count':so['print_count'],
                        'rebate_later':rebate,
                        'schedule_date':so['date_to_deliver'],
                        'customer_sign':so['customerSign'],
                        'payment_term_id':so.get('paymentTermID')
                    }
                    s_order_id = mobile_sale_order_obj.create(cursor, user, mso_result, context=context)
                    so_ids.append(s_order_id)
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
                                if sol['manual_foc'] == 'T':
                                    manual_foc = True
                                else:
                                    manual_foc = False       
                                if sol['promotion_action'] and  sol['promotion_action']!='null':
                                    cursor.execute("select promotion from promos_rules_actions where id =%s",(sol['promotion_action'],))
                                    promotion_id = cursor.fetchone()[0]
                                else:
                                    promotion_id=False
                                if sol['manual_promotion'] and sol['manual_promotion'] != 'null':
                                    promotion_id = sol['manual_promotion']  
                                price =sol['price_unit']
#                                 if  float(price) < 0:
#                                     product_price= 0
#                                     discount_amt =-1 * float(price)
#                                 else:
                                product_price=sol['price_unit']
                                discount_amt=sol['discount_amt']
                                                                                  
                                mso_line_res = {                                                            
                                  'order_id':s_order_id,
                                  'product_id':productId,
                                  'price_unit':product_price,
                                  'foc':foc_val,
                                  'product_uos_qty':sol['product_uos_qty'],
                                  'discount':sol['discount'],
                                  'discount_amt':discount_amt,
                                  'sub_total':sol['sub_total'],
                                  'uom_id':sol['uom_id'],
                                  'manual_foc':manual_foc,
                                  'promotion_id':promotion_id,
                                }
                                mobile_sale_order_line_obj.create(cursor, user, mso_line_res, context=context) 
                                print 'Create Order line', sol['so_name']                     
                    sale_order_name_list.append(so['name'])
            print 'True'
            
            session = ConnectorSession(cursor, user, context)
            jobid=automation_pre_order.delay(session,so_ids, priority=10)
            print "Job",jobid
            runner = ConnectorRunner()
            runner.run_jobs()
            return True 
                  
        except Exception, e:
            print 'False'
            print e
            return False 

        
    def action_convert_presaleorder(self, cr, uid, ids, context=None):
        presaleorderObj = self.pool.get('pre.sale.order')
        saleOrderObj = self.pool.get('sale.order')
        saleOrderLineObj = self.pool.get('sale.order.line')
        saleOrderPromoLineObj = self.pool.get('sale.order.promotion.line')
        pre_promotion_line_obj = self.pool.get('pre.promotion.line')
        invPromoLineObj = self.pool.get('account.invoice.promotion.line')                
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
                        #for multi Sale Team
                        cr.execute("select delivery_team_id from res_partner where id =%s",(preObj_ids.partner_id.id,))
                        delivery_data=cr.fetchall()
                        if delivery_data:
                            delivery_id = delivery_data[0][0]
                            if delivery_id is None:
                                delivery_id =None
                        else:
                            delivery_id = None
                            
                        if delivery_id is None:                            
                            cr.execute('select delivery_team_id from crm_case_section where id = %s ', (preObj_ids.sale_team.id,))
                            data = cr.fetchall()
                            if data:
                                delivery_id = data[0][0]
                            else:
                                delivery_id = None
                        cr.execute('select warehouse_id from crm_case_section where id = %s ', (delivery_id,))
                        data = cr.fetchall()
                        if data:
                            warehouse_id=data[0][0]
                        else:
                            warehouse_id = None                            
                        cr.execute('select company_id from res_users where id=%s', (preObj_ids.user_id.id,))
                        company_id = cr.fetchone()[0]
                        if preObj_ids.void_flag == 'voided':  # they work while payment type not 'cash' and 'credit'
#                             so_state = 'cancel'
                            cancel_user_id = preObj_ids.user_id.id
                        elif preObj_ids.void_flag == 'none':
#                             so_state = 'manual'
                            cancel_user_id = None
                        
                        saleOrderResult = {'partner_id':preObj_ids.partner_id.id,
                                                        'customer_code':preObj_ids.customer_code,
                                                        'sale_plan_name':preObj_ids.sale_plan_name,
                                                        'sale_plan_day_id':preObj_ids.sale_plan_day_id.id,
                                                        'sale_plan_trip_id':preObj_ids.sale_plan_trip_id.id,
                                                        'date_order':preObj_ids.date,
														'due_date':preObj_ids.due_date,
                                                        'tb_ref_no':preObj_ids.name,
                                                        'warehouse_id':warehouse_id,
                                                        'delivery_remark':preObj_ids.delivery_remark,
                                                        'so_latitude':preObj_ids.mso_latitude,
                                                        'so_longitude':preObj_ids.mso_longitude,
                                                        'user_id':preObj_ids.user_id.id,
                                                        'section_id':preObj_ids.sale_team.id,
                                                        'deduct_amt':preObj_ids.deduction_amount,
                                                        'additional_discount':0,
                                                        'schedule_date':preObj_ids.schedule_date,
#                                                         'client_order_ref':preObj_ids.tablet_id.name,
                                                         'state':'draft',
                                                         'payment_type':preObj_ids.type,
                                                        'pricelist_id':preObj_ids.pricelist_id.id,
                                                        'pre_order':True,
                                                        'rebate_later':preObj_ids.rebate_later,
                                                        'delivery_id':delivery_id,
                                                        'branch_id':preObj_ids.branch_id.id,
                                                        'company_id':company_id,
                                                        'note':preObj_ids.note,
                                                        'cancel_user_id':cancel_user_id,
                                                        'ignore_credit_limit':True,
                                                        'credit_history_ids':[],
                                                        'payment_term':preObj_ids.payment_term_id.id,
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
                                product_data = self.pool.get('product.product').browse(cr, uid,line_id.product_id.id, context=context) 
                                tax_data=False    
                                taxes = product_data.taxes_id
                                if taxes:
                                    fpos = preObj_ids.partner_id.property_account_position or False
                                    tax_id = self.pool.get('account.fiscal.position').map_tax(cr, uid, fpos, taxes, context=context)                           
                                    tax_data=[[6, 0, tax_id]]
                                detailResult = {'order_id':so_id,
                                                      #  'product_type':product_data.product_tmpl_id.type,
                                                        'product_id':line_id.product_id.id,
                                                        'name':productName,
                                                        'product_uom':line_id.uom_id.id,
                                                        'product_uom_qty':line_id.product_uos_qty,
                                                        'discount':line_id.discount,
                                                        'discount_amt':line_id.discount_amt,
                                                        'sale_foc':sale_foc,
                                                        'tax_id':tax_data,
                                                        'price_unit':priceUnit,
                                                        'company_id':company_id,  
                                                         'promotion_id':line_id.promotion_id.id,# company_id,
                                                        }   
                                saleOrderLineObj.create(cr, uid, detailResult, context=context)
                    if so_id:
                        #Insert Sale Order Promotion Line
                        for so_p_line in preObj_ids.promos_line_ids:
                            pre_promo_data=pre_promotion_line_obj.browse(cr, uid, so_p_line.id, context=context)
                            so_promo_line_result = {
                                              'promo_line_id':so_id,
                                              'pro_id':pre_promo_data.pro_id.id,
                                              'from_date':pre_promo_data.from_date,
                                              'to_date':pre_promo_data.to_date,
                                              'manual':pre_promo_data.manual,
                                                          }
                            saleOrderPromoLineObj.create(cr, uid, so_promo_line_result, context=context)                                   
#                     if so_id and  so_state != 'cancel':
#                         saleOrderObj.button_dummy(cr, uid, [so_id], context=context)
                        # Do Open
#                         saleOrderObj.action_button_confirm(cr, uid, [so_id], context=context)
                        
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
                    cursor.execute("select manual from promos_rules where id=%s",(pro_line['pro_id'],))
                    manual =cursor.fetchone()[0]
                    if manual is not None:
                        manual=manual
                    else:
                        manual=False                                    
                    promo_line_result = {
                        'promo_line_id':saleOrder_Id,
                        'pro_id':pro_line['pro_id'],
                        'from_date':pro_line['from_date'],
                        'to_date':pro_line['to_date'] ,
                         'manual':manual,

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
        'product_type':fields.char('Product Type'),

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
        'manual_foc':fields.boolean('Manual Foc'),
        'promotion_id': fields.many2one('promos.rules', 'Promotion', readonly=True)  
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
              'to_date':fields.datetime('To Date'),
              'manual':fields.boolean('Manual'),
              }
    _defaults = {
        'manual':False,
    }
    
    def onchange_promo_id(self, cr, uid, ids, pro_id, context=None):
            result = {}
            promo_pool = self.pool.get('promos.rules')
            datas = promo_pool.read(cr, uid, pro_id, ['from_date', 'to_date','manual'], context=context)
    
            if datas:
                result.update({'from_date':datas['from_date']})
                result.update({'to_date':datas['to_date']})
                result.update({'manual':datas['manual']})
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

class sale_order(osv.osv):
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _inherit='sale.order'
    
    _columns = {
        'name': fields.char('Order Reference', required=True, copy=False,
            readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, select=True,track_visibility='always'),
        'origin': fields.char('Source Document', help="Reference of the document that generated this sales order request.",track_visibility='always'),
        'client_order_ref': fields.char('Reference/Description', copy=False,track_visibility='always'),
        'state': fields.selection([
            ('draft', 'Draft Quotation'),
            ('sent', 'Quotation Sent'),
            ('cancel', 'Cancelled'),
            ('waiting_date', 'Waiting Schedule'),
            ('progress', 'Sales Order'),
            ('manual', 'Sale to Invoice'),
            ('shipping_except', 'Shipping Exception'),
            ('invoice_except', 'Invoice Exception'),
            ('done', 'Done'),
            ], 'Status', readonly=True, copy=False, help="Gives the status of the quotation or sales order.\
              \nThe exception status is automatically set when a cancel operation occurs \
              in the invoice validation (Invoice Exception) or in the picking list process (Shipping Exception).\nThe 'Waiting Schedule' status is set when the invoice is confirmed\
               but waiting for the scheduler to run on the order date.", select=True,track_visibility='always'),
        'date_order': fields.datetime('Date', required=True, readonly=True, select=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, copy=False,track_visibility='always'),
        'create_date': fields.datetime('Creation Date', readonly=True, select=True, help="Date on which sales order is created.",track_visibility='always'),
        'date_confirm': fields.date('Confirmation Date', readonly=True, select=True, help="Date on which sales order is confirmed.", copy=False,track_visibility='always'),
        'user_id': fields.many2one('res.users', 'Salesperson', states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, select=True, track_visibility='onchange'),
        'partner_id': fields.many2one('res.partner', 'Customer', readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, required=True, change_default=True, select=True, track_visibility='always'),
        'partner_invoice_id': fields.many2one('res.partner', 'Invoice Address', readonly=True, required=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, help="Invoice address for current sales order.",track_visibility='always'),
        'partner_shipping_id': fields.many2one('res.partner', 'Delivery Address', readonly=True, required=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, help="Delivery address for current sales order.",track_visibility='always'),
        'order_policy': fields.selection([
                ('manual', 'On Demand'),
            ], 'Create Invoice', required=True, readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
            help="""This field controls how invoice and delivery operations are synchronized.""",track_visibility='onchange'),
        'pricelist_id': fields.many2one('product.pricelist', 'Pricelist', required=True, readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, help="Pricelist for current sales order.",track_visibility='always'),
        'currency_id': fields.related('pricelist_id', 'currency_id', type="many2one", relation="res.currency", string="Currency", readonly=True, required=True,track_visibility='always'),
        'project_id': fields.many2one('account.analytic.account', 'Contract / Analytic', readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, help="The analytic account related to a sales order.",track_visibility='always'),

        'order_line': fields.one2many('sale.order.line', 'order_id', 'Order Lines', readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, copy=True,track_visibility='always'),
        'invoice_ids': fields.many2many('account.invoice', 'sale_order_invoice_rel', 'order_id', 'invoice_id', 'Invoices', readonly=True, copy=False, help="This is the list of invoices that have been generated for this sales order. The same sales order may have been invoiced in several times (by line for example).",track_visibility='always'),
        'note': fields.text('Terms and conditions',track_visibility='always'),
        'payment_term': fields.many2one('account.payment.term', 'Payment Term',track_visibility='always'),
        'fiscal_position': fields.many2one('account.fiscal.position', 'Fiscal Position',track_visibility='always'),
        'company_id': fields.many2one('res.company', 'Company',track_visibility='always'),
        'section_id': fields.many2one('crm.case.section', 'Sales Team',track_visibility='always'),
        'procurement_group_id': fields.many2one('procurement.group', 'Procurement group', copy=False,track_visibility='always'),
        'product_id': fields.related('order_line', 'product_id', type='many2one', relation='product.product', string='Product',track_visibility='always'),
    }
        