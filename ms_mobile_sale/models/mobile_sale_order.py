from openerp.osv import fields, osv
from openerp.osv import orm
from datetime import datetime, timedelta
from openerp.tools.translate import _
import ast
import time
import urllib
from openerp import netsvc
import pytz
DEFAULT_SERVER_DATE_FORMAT = "%Y-%m-%d"
from openerp.http import request
from openerp.addons.connector.queue.job import job, related_action
from openerp.addons.connector.session import ConnectorSession
from openerp.addons.connector.exception import FailedJobError
from openerp.addons.connector.jobrunner.runner import ConnectorRunner
import requests
import logging

_logger = logging.getLogger(__name__)

@job(default_channel='root.directpending')
def automation_pending_delivery(session, delivery_mobile):
    delivery_obj = session.pool['pending.delivery']    
    context = session.context.copy()
    cr = session.cr
    uid = session.uid
    for mobile in delivery_mobile: 
        delivery_obj.action_convert_pending_delivery(cr, uid, [mobile], context=context)         
    return True    
    
@job(default_channel='root.directpending')
def automation_direct_order(session, list_mobile):
    mobile_obj = session.pool['mobile.sale.order']
    context = session.context.copy()
    cr = session.cr
    uid = session.uid
    # list_mobile = mobile_obj.search(cr, uid, [('void_flag', '=', 'none'), ('m_status', '=', 'draft'), ('partner_id', '!=', None)])            
    for mobile in list_mobile: 
        mobile_obj.action_convert_so(cr, uid, [mobile], context=context)    
    return True

@job(default_channel='root.deliverytransfer')
def automatic_direct_sale_transfer(session,order_ids,de_date):
    context = session.context.copy()
    cr = session.cr
    uid = session.uid
    context = {'lang': 'en_US', 'params': {'action': 458}, 'tz': 'Asia/Rangoon', 'uid': 1}    
    soObj = session.pool.get('sale.order')
    date_change = datetime.strptime(de_date, '%Y-%m-%d %H:%M:%S')
    date = date_change.date()        
    for order_data in soObj.browse(cr, uid, order_ids, context=context):
        So_id = order_data.id
        shipped=order_data.shipped
        if shipped!=True:
            stockPickingObj = session.pool.get('stock.picking')
            stockDetailObj = session.pool.get('stock.transfer_details')
            stockViewResult = soObj.action_view_delivery(cr, uid, So_id, context=context)
            if stockViewResult:
                # stockViewResult is form result
                # stocking id =>stockViewResult['res_id']
                # click force_assign
                stockPickingObj.force_assign(cr, uid, stockViewResult['res_id'], context=context)
                # transfer
                # call the transfer wizard
                # change list
                pickList = []
                pickList.append(stockViewResult['res_id'])
                wizResult = stockPickingObj.do_enter_transfer_details(cr, uid, pickList, context=context)
                # pop up wizard form => wizResult
                detailObj = stockDetailObj.browse(cr, uid, wizResult['res_id'], context=context)
                if detailObj:
                    detailObj.do_detailed_transfer()
                cr.execute('update stock_picking set date_done =%s where origin=%s', (date, order_data.name,))
                cr.execute('update stock_move set date = %s where origin =%s', (date, order_data.name,))
                picking_id = stockViewResult['res_id']
                print 'picking_id', picking_id
                pick_date = stockPickingObj.browse(cr, uid, picking_id, context=context)
                cr.execute(
                    "update account_move_line set date= %s from account_move move where move.id=account_move_line.move_id and move.ref= %s",
                    (date, pick_date.name,))
                cr.execute('''update account_move set period_id=p.id,date=%s
                            from (
                            select id,date_start,date_stop
                            from account_period
                            where date_start != date_stop
                            ) p
                            where p.date_start <= %s and  %s <= p.date_stop
                            and account_move.ref=%s''', (date, date, date, pick_date.name,))    
    return True
class customer_payment(osv.osv):
    _name = "customer.payment"
    _columns = {               
   'payment_id':fields.many2one('mobile.sale.order', 'Line'),
   'pre_order_id'  :fields.many2one('pre.sale.order', 'Line'),
   'journal_id'  : fields.many2one('account.journal', 'Payment Method' , domain=[('type', 'in', ('cash', 'bank'))]),
   'amount':fields.float('Paid Amount'),
   'notes':fields.char('Payment Ref'),
   'date':fields.date('Date'),
   'cheque_no':fields.char('Cheque No'),
   'partner_id':fields.many2one('res.partner', 'Customer'),
   'sale_team_id':fields.many2one('crm.case.section', 'Sale Team'),
   'payment_code':fields.char('Payment Code'),
        }
    
class mobile_sale_order(osv.osv):
    
    _name = "mobile.sale.order"
    _description = "Mobile Sales Order"
   
    _columns = {
        'name': fields.char('Order Reference', size=64),
        'partner_id':fields.many2one('res.partner', 'Customer'),
        'customer_code':fields.char('Customer Code'),
        'outlet_type':fields.many2one('outlettype.outlettype', 'Outlet Type'),
        'user_id':fields.many2one('res.users', 'Salesman Name'),
        'sale_plan_name':fields.char('Sale Plan Name'),
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
        'additional_discount':fields.float('Discount'),
        'deduction_amount':fields.float('Deduction Amount'),
        'net_amount':fields.float('Net Amount'),
        'change_amount':fields.float('Change Amount'),
        'remaining_amount':fields.float('Remaining Amount'),
        'balance':fields.float('Balance'),
        'paid_amount':fields.float('Paid Amount'),
        'paid':fields.boolean('Paid'),
        'void_flag':fields.selection([
                ('voided', 'Voided'),
                ('none', 'Unvoid')
            ], 'Void'),
        'date':fields.datetime('Date'),
        'note':fields.text('Note'),
        'order_line': fields.one2many('mobile.sale.order.line', 'order_id', 'Order Lines', copy=True),
        'delivery_order_line': fields.one2many('products.to.deliver', 'sale_order_id', 'Delivery Order Lines', copy=True),
        'tablet_id':fields.many2one('tablets.information', 'Tablet ID'),
        'sale_plan_day_id':fields.many2one('sale.plan.day', 'Sale Plan Day'),
        'sale_plan_trip_id':fields.many2one('sale.plan.trip', 'Sale Plan Trip'),
        'warehouse_id' : fields.many2one('stock.warehouse', 'Warehouse'),
        'sale_team':fields.many2one('crm.case.section', 'Sale Team'),
        'location_id'  : fields.many2one('stock.location', 'Location'),
        'm_status':fields.selection([('draft', 'Draft'),
                                                      ('done', 'Complete')], string='Status'),
        'due_date':fields.date('Due Date'),
        'payment_term': fields.many2one('account.payment.term', 'Payment Term'),
       'promos_line_ids':fields.one2many('mso.promotion.line', 'promo_line_id', 'Promotion Lines'),
       'pricelist_id': fields.many2one('product.pricelist', 'Price List', select=True, ondelete='cascade'),
       'payment_line_ids':fields.one2many('customer.payment', 'payment_id', 'Payment Lines'),
      'branch_id': fields.many2one('res.branch', 'Branch', required=True),
      'is_convert':fields.boolean('Is Convert', readonly=True),
      'print_count':fields.integer('Unvoid Reprint Count'),
      'void_print_count':fields.integer('Voided Reprint Count'),
      'order_team':fields.many2one('crm.case.section', 'Order Team'),
      'rebate_later':fields.boolean('Rebate Later', readonly=True),
      'order_saleperson': fields.many2one('res.users', 'Order Saleperson'),
      'pre_sale_order_id': fields.many2one('sale.order', 'Pre Sale Order'),
      'revise_reason_id': fields.many2one('revise.reason', 'Revise Reason'),
      'cancel_reason_id': fields.many2one('cancel.reason', 'Cancel Reason'),
   #     'journal_id'  : fields.many2one('account.journal', 'Journal' ,domain=[('type','in',('cash','bank'))]),   
    }
    _order = 'id desc'
    _defaults = {
        'date': datetime.now(),
        'm_status' : 'draft',
        'is_convert':False,
       
    } 
    
    def res_partners_team_with_sync_date(self, cr, uid, section_id, late_date, context=None, **kwargs):
        
        lastdate = datetime.strptime(late_date, "%Y-%m-%d")
        print 'DateTime', lastdate
        
        cr.execute('''                                
        select A.id,A.name,A.image,A.is_company, A.image_small,replace(A.street,',',';') street,replace(A.street2,',',';') street2,A.city,A.website,
                     replace(A.phone,',',';') phone,A.township,replace(A.mobile,',',';') mobile,A.email,A.company_id,A.customer, 
                     A.customer_code,A.mobile_customer,A.shop_name ,
                     A.address,
                     A.zip,A.state_name,A.partner_latitude,A.partner_longitude,null,A.image_medium,A.credit_limit,
                     A.credit_allow,A.sales_channel,A.branch_id,A.pricelist_id,A.payment_term_id,A.outlet_type ,
                     A.city_id,A.township_id,A.country_id,A.state_id,A.unit,A.class_id,A.chiller,A.frequency_id,A.temp_customer,
                     A.is_consignment,A.hamper,A.is_bank,A.is_cheque,A.old_code,A.verify,A.pricelist
                     
                     from (
                     select RP.id,RP.name,'' as image,RP.is_company,null,
                     '' as image_small,RP.street,RP.street2,RC.name as city,RP.website,
                     RP.phone,RT.name as township,RP.mobile,RP.email,RP.company_id,RP.customer, 
                     RP.customer_code,RP.mobile_customer,OT.name as shop_name,RP.address,RP.zip ,RP.partner_latitude,RP.partner_longitude,RS.name as state_name,
                     substring(replace(cast(RP.image_medium as text),'/',''),1,5) as image_medium,RP.credit_limit,RP.credit_allow,
                     RP.sales_channel,RP.branch_id,RP.pricelist_id,RP.payment_term_id,RP.outlet_type,RP.city as city_id,RP.township as township_id,
                     RP.country_id,RP.state_id,RP.unit,RP.class_id,RP.chiller,RP.frequency_id,RP.temp_customer,RP.is_consignment,RP.hamper,
                     RP.is_bank,RP.is_cheque,RP.old_code,RP.verify,pp.name as pricelist
                     from outlettype_outlettype OT,
                                             res_partner RP ,res_country_state RS, res_city RC,res_township RT,product_pricelist pp
                                            where RS.id = RP.state_id
                                            and RP.township =RT.id
                                            and RP.city = RC.id
                                            and RP.active = true        
                                            and RP.pricelist_id = pp.id                                    
                                            and RP.outlet_type = OT.id   
                                            and RP.credit_allow =True                                         
                                            and RP.collection_team=%s
                                            and RP.write_date::date>=%s
                        )A 
                        where A.customer_code is not null
            ''', (section_id ,late_date,))
        datas = cr.fetchall()
        return datas      
        
    def send_credit_invoice_sms(self, cr, uid, customer_id, invoice_number, grand_total, due_date, context=None):    
         
        message_body = None        
        customer_obj = self.pool.get('res.partner').browse(cr, uid, customer_id, context=context)        
        if customer_obj.sms == True:                                                     
            company_credit_invoice_msg = self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.credit_invoice_msg
            if company_credit_invoice_msg:
                message_body = (company_credit_invoice_msg) % (customer_obj.name,invoice_number, grand_total, due_date,)
                vals={
                        'phone':customer_obj.mobile,
                        'message':message_body, 
                        'partner_id':customer_obj.id,
                        'name':invoice_number
                    } 
                message = self.pool.get('sms.message').create(cr,uid,vals);
                self.pool.get('sms.message').browse(cr, uid, message, context=context)                                                    
                
    def res_partners_return_day_with_sync_date(self, cr, uid, section_id, day_id, pull_date  , context=None, **kwargs):
        section = self.pool.get('crm.case.section')
        sale_team_data = section.browse(cr, uid, section_id, context=context)
        is_supervisor=sale_team_data.is_supervisor    
        lastdate = datetime.strptime(pull_date, "%Y-%m-%d")
        print 'DateTime', lastdate
        if is_supervisor==True:
            where ='and SPD.sale_team in (select id from crm_case_section where supervisor_team= %s)' % (section_id,)
        else:
            where ='and SPD.sale_team = %s' % (section_id,)
        cr.execute('''                    
                     select A.id,A.name,A.image,A.is_company, A.image_small,replace(A.street,',',';') street, replace(A.street2,',',';') street2,A.city,A.website,
                     replace(A.phone,',',';') phone,A.township, replace(A.mobile,',',';') mobile,A.email,A.company_id,A.customer, 
                     A.customer_code,A.mobile_customer,A.shop_name ,
                     A.address,
                     A.zip,A.state_name,A.partner_latitude,A.partner_longitude,A.sale_plan_day_id,A.image_medium,A.credit_limit,
                     A.credit_allow,A.sales_channel,A.branch_id,A.pricelist_id,A.payment_term_id,A.outlet_type ,
                     A.city_id,A.township_id,A.country_id,A.state_id,A.unit,A.class_id,A.chiller,A.frequency_id,A.temp_customer,
                     A.is_consignment,A.hamper,A.is_bank,A.is_cheque,A.old_code,A.verify,A.pricelist
                     from (
                     select RP.id,RP.name,'' as image,RP.is_company,RPS.line_id as sale_plan_day_id,
                     '' as image_small,RP.street,RP.street2,RC.name as city,RP.website,
                     RP.phone,RT.name as township,RP.mobile,RP.email,RP.company_id,RP.customer, 
                     RP.customer_code,RP.mobile_customer,OT.name as shop_name,RP.address,RP.zip ,RP.partner_latitude,RP.partner_longitude,RS.name as state_name,
                     substring(replace(cast(RP.image_medium as text),'/',''),1,5) as image_medium,RP.credit_limit,RP.credit_allow,
                     RP.sales_channel,RP.branch_id,RP.pricelist_id,RP.payment_term_id,RP.outlet_type,RP.city as city_id,RP.township as township_id,
                     RP.country_id,RP.state_id,RP.unit,RP.class_id,RP.chiller,RP.frequency_id,RP.temp_customer,RP.is_consignment,RP.hamper,
                     RP.is_bank,RP.is_cheque,RP.old_code,RP.verify,pp.name as pricelist
                     from sale_plan_day SPD ,outlettype_outlettype OT,
                                            sale_plan_day_line RPS , res_partner RP ,res_country_state RS, res_city RC,res_township RT,product_pricelist pp
                                            where SPD.id = RPS.line_id 
                                            and  RS.id = RP.state_id
                                            and RP.township =RT.id
                                            and RP.city = RC.id
                                            and RP.active = true
                                            and RP.outlet_type = OT.id
                                            and RPS.partner_id = RP.id 
                                            and RP.pricelist_id = pp.id
                                            %s
                                            and RPS.line_id = %%s  
                                            and RP.write_date::date >=  %%s     
                                            order by  RPS.sequence asc                         
                                                                                                                 
                        )A 
                        where A.customer_code is not null
            '''%(where),(day_id,pull_date,))
        datas = cr.fetchall()
        return datas
    
    def get_promos_datas_with_sync_date(self, cr, uid , branch_id, state, team_id,sync_date, context=None, **kwargs):
        if state == 'approve':
            status = 'approve'
            cr.execute('''select id,sequence as seq,from_date ,to_date,active,name as p_name,
                        logic ,expected_logic_result ,special, special1, special2, special3 ,description,
                        pr.promotion_count, pr.monthly_promotion ,code as p_code,manual,main_group,pr.ecommerce
                        from promos_rules pr ,promos_rules_res_branch_rel pro_br_rel
                        where pr.active = true                     
                        and pr.id = pro_br_rel.promos_rules_id
                        and pro_br_rel.res_branch_id = %s
                        and pr.state = %s
                        and pr.write_date::date >= %s
                        and  now()::date  between from_date::date and to_date::date
                        and pr.id in (
                        select a.promo_id from promo_sale_channel_rel a
                        inner join sale_team_channel_rel b
                        on a.sale_channel_id = b.sale_channel_id
                        where b.sale_team_id = %s
                        )
                        ''', (branch_id, status, sync_date, team_id,))
        else:
            status = 'draft'            
            cr.execute('''select id,sequence as seq,from_date ,to_date,active,name as p_name,
                        logic ,expected_logic_result ,special, special1, special2, special3 ,description,
                        pr.promotion_count, pr.monthly_promotion,code as p_code,manual,main_group,pr.ecommerce
                        from promos_rules pr ,promos_rules_res_branch_rel pro_br_rel
                        where pr.active = true                     
                        and pr.id = pro_br_rel.promos_rules_id
                        and pro_br_rel.res_branch_id = %s
                        and pr.state  = %s
                        and pr.write_date::date >=%s
                        and  now()::date  between from_date::date and to_date::date
                        and pr.id in (
                        select a.promo_id from promo_sale_channel_rel a
                        inner join sale_team_channel_rel b
                        on a.sale_channel_id = b.sale_channel_id
                        where b.sale_team_id = %s
                        )
                        ''', (branch_id, status,sync_date, team_id,))
        datas = cr.fetchall()        
        return datas
    
    def get_promos_act_datas_with_sync_date(self, cr, uid , branch_id, promo_id, sync_date, context=None, **kwargs):
        cr.execute('''select act.id,act.promotion,act.sequence as act_seq ,act.arguments,act.action_type,act.product_code,act.discount_product_code
                            from promos_rules r ,promos_rules_actions act,promos_rules_res_branch_rel pro_br_rel
                            where r.id = act.promotion
                            and r.active = 't'                            
                            and r.id = pro_br_rel.promos_rules_id
                            and pro_br_rel.res_branch_id = %s
                            and act.promotion = %s 
                            and act.write_date::date >= %s                   
                    ''', (branch_id, promo_id, sync_date))
        datas = cr.fetchall()
        cr.execute
        return datas
    
    def get_promos_cond_datas_with_sync_date(self, cr, uid , branch_id, promo_id,sync_date, context=None, **kwargs):
        cr.execute('''select cond.id,cond.promotion,cond.sequence as cond_seq,
                            cond.attribute as cond_attr,cond.comparator as cond_comparator,
                            cond.value as comp_value
                            from promos_rules r ,promos_rules_conditions_exps cond,promos_rules_res_branch_rel pro_br_rel
                            where r.id = cond.promotion
                            and r.active = 't'                           
                            and r.id = pro_br_rel.promos_rules_id
                            and pro_br_rel.res_branch_id = %s
                            and cond.promotion = %s  
                            and cond.write_date::date >= %s    
                    ''', (branch_id, promo_id,sync_date,))
        datas = cr.fetchall()
        cr.execute
        return datas
    
    def create_massive(self, cursor, user, vals, context=None):
        print 'vals', vals
        sale_order_name_list = []
        try : 
            mobile_sale_order_obj = self.pool.get('mobile.sale.order')
            direct_sale_job = self.pool.get('direct.sale.state')
            mobile_sale_order_line_obj = self.pool.get('mobile.sale.order.line')
            product_obj = self.pool.get('product.product')
            str = "{" + vals + "}"
            str = str.replace(":''", ":'")  # change Order_id
            str = str.replace("'',", "',")  # null
            str = str.replace(":',", ":'',")  # due to order_id
            str = str.replace("}{", "}|{")
            new_arr = str.split('|')
            result = []
            so_ids = []
            for data in new_arr:
                x = ast.literal_eval(data)
                result.append(x)
            sale_order = []
            sale_order_line = []
            for r in result:
                print "length", len(r)
                if len(r) >= 28:
                    sale_order.append(r)
                else:
                    sale_order_line.append(r)
            
            if sale_order:
                for so in sale_order:
                    if so['order_saleteam'] != 'null':
                        cursor.execute('select id from crm_case_section where name=%s', (so['order_saleteam'],))
                        order_team = cursor.fetchone()[0]
                        # so['sale_team']=order_team
                        so['sale_team'] = so['sale_team']
                    else:
                        order_team = None
                    if so['order_saleperson'] != 'null' and so['order_saleperson']:
                       # so['user_id']=so['order_saleperson']
                        so['user_id'] = so['user_id']
                        order_saleperson =so['order_saleperson']
                    else:
                        order_saleperson = None
                    if so['presaleorderid'] != 'null' and so['presaleorderid']: 
                        presaleorderid = so['presaleorderid'].replace('\\', '').replace('\\', '')   
                        cursor.execute("select id from sale_order where name = %s ",(presaleorderid,))
                        sale_order_data=cursor.fetchone()
                        if sale_order_data:
                            pre_sale_order_id =sale_order_data[0]
                        else:
                            pre_sale_order_id = None
                    else:
                        pre_sale_order_id = None 
                        
                    cursor.execute('select branch_id from crm_case_section where id=%s', (so['sale_team'],))
                    branch_id = cursor.fetchone()[0]     
                    cursor.execute('select id From res_partner where customer_code  = %s ', (so['customer_code'],))
                    data = cursor.fetchall()                
                    if data:
                        partner_id = data[0][0]
                    else:
                        partner_id = None 
                        
                    if so['type'] == 'cash':
                        paid = True
                    else:
                        paid = False
                        
                    if so['rebate'] == 'T':
                        rebate = True
                    else:
                        rebate = False
                            
                    if so['revise_reason_id'] != 'null' and so['revise_reason_id']: 
                        revise_reason_id = so['revise_reason_id']
                    else:
                        revise_reason_id = None                                           
                    if so.get('payment_ref'): 
                        payment_ref=so['payment_ref']
                    else:
                        payment_ref=None       
                    mso_result = {
                        'customer_code':so['customer_code'],
                        'sale_plan_day_id':so['sale_plan_day_id'],
                        'sale_plan_trip_id':so['sale_plan_trip_id'] ,
                        'paid': paid,
                        'warehouse_id':so['warehouse_id'],
                        'tablet_id':so['tablet_id'],
                      #  'delivery_remark':so['delivery_remark'],
                        'delivery_remark':'delivered',
                        'location_id':so['location_id'],
                        'deduction_amount':so['deduction_amount'],
                        'user_id':so['user_id'],
                        'name':so['name'],
                        'paid_amount':so['paid_amount'],
                        'partner_id': partner_id,
                        'sale_plan_name':so['sale_plan_day_name'],
                        'additional_discount':so['additional_discount'],
                        'amount_total':so['amount_total'],
                        'type':so['type'],
                        'void_flag':so['void_flag'],
                        'sale_team':so['sale_team'],
                        'date':so['date'],
                        'remaining_amount':so['remaining_amount'],
                        'change_amount':so['change_amount'],
                        'net_amount':so['discounted_total_amount'],
                        'due_date':so['due_date'],
                        'payment_term':so['payment_term'],
                        'mso_longitude':so['mso_longitude'],
                        'mso_latitude':so['mso_latitude'],
                        'outlet_type':so['outlet_type'] ,
                        'pricelist_id':so['pricelist_id'],
                        'branch_id':branch_id,
                        'note':so['note'],
                        'print_count':so['print_count'],
                        'void_print_count':so['void_print_count'],
                        'order_team':order_team,
                        'rebate_later':rebate,
                        'order_saleperson':order_saleperson,
                        'pre_sale_order_id':pre_sale_order_id,
                        'revise_reason_id':revise_reason_id,
                        'payment_ref':payment_ref                    
                    }
                    s_order_id = mobile_sale_order_obj.create(cursor, user, mso_result, context=context)
                    so_ids.append(s_order_id);
                    for sol in sale_order_line:
                        if sol['so_name'] == so['name']:
                                cursor.execute('select id From product_product where id  = %s ', (sol['product_id'],))
                                data = cursor.fetchall()
                                if data:
                                    productId = data[0][0]
                                    product = product_obj.browse(cursor, user, productId, context=context)
                                    product_type = product.product_tmpl_id.type
                                else:
                                    productId = None
                                    product_type = None
                                
                                if sol['price_unit'] == '0':
                                    foc_val = True
                                else:
                                    foc_val = False
                                if sol['manual_foc'] == 'T':
                                    manual_foc = True
                                else:
                                    manual_foc = False                 
                                if sol['promotion_action'] and sol['promotion_action'] != 'null':
                                    cursor.execute("select promotion from promos_rules_actions where id =%s", (sol['promotion_action'],))
                                    promotion_id = cursor.fetchone()[0]  
                                else:
                                    promotion_id = None   
                                if sol['manual_promotion'] and sol['manual_promotion'] != 'null':
                                    promotion_id = sol['manual_promotion']                                           
                                price = sol['price_unit']
#                                 if  float(price) < 0:
#                                     product_price= 0
#                                     discount_amt =-1 * float(price)
#                                 else:
                                product_price = sol['price_unit']
                                discount_amt = sol['discount_amt']                                          
                                mso_line_res = {                                                            
                                  'order_id':s_order_id,
                                  'product_type':product_type,
                                  'product_id':productId,
                                  'price_unit':product_price,
                                  'product_uos_qty':sol['product_uos_qty'],
                                  'foc': foc_val,
                                  'discount':sol['discount'],
                                  'discount_amt':discount_amt,
                                  'sub_total':sol['sub_total'],
                                  'uom_id':sol['uom_id'],
                                  'manual_foc':manual_foc,
                                  'promotion_id':promotion_id,
                                }
                                mobile_sale_order_line_obj.create(cursor, user, mso_line_res, context=context) 
                    # convertintablet(KM)
                                
                    # mobile_sale_order_obj.action_convert_so(cursor, user, [s_order_id], context=context)    
                    sale_order_name_list.append(so['name'])
                    
                    # convert to sale order.
            session = ConnectorSession(cursor, user, context)
            jobid = automation_direct_order.delay(session, so_ids, priority=30)
            runner = ConnectorRunner()
            runner.run_jobs()
            return True     
        except Exception, e:
            print 'False'
            print e
            return False
        
    def create_tablet_sync_log_form(self, cursor, user, vals, context=None):
             try :
                sync_obj = self.pool.get('tablet.sync.log')
                str = "{" + vals + "}"
                str = str.replace("'',", "',")  # null
                str = str.replace(":',", ":'',")  # due to order_id
                str = str.replace("}{", "}|{")
                new_arr = str.split('|')
                result = []
                import datetime
                for data in new_arr:
                    x = ast.literal_eval(data)
                    result.append(x)
                log_line = []
                for r in result:                
                   log_line.append(r)  
                if log_line:
                    for sync_log in log_line:
                        cursor.execute('select branch_id from crm_case_section where id=%s', (sync_log['section_id'],))
                        branch_id = cursor.fetchone()[0]
                        print_result = {
                            'section_id':sync_log['section_id'],
                            'user_id':user,
                            'tablet_id':sync_log['tablet_id'],
                            'sync_time':datetime.datetime.now(),
                            'status':sync_log['status'],
                            'branch_id':branch_id,
                            }
                        sync_obj.create(cursor, user, print_result, context=context)
                return True
             except Exception, e:
                return False        
            
    def create_customer_feedback(self, cursor, user, vals, context=None):
             try :
                sync_obj = self.pool.get('customer.feedback')
                str = "{" + vals + "}"
                str = str.replace("'',", "',")  # null
                str = str.replace(":',", ":'',")  # due to order_id
                str = str.replace("}{", "}|{")
                new_arr = str.split('|')
                result = []           
                for data in new_arr:
                    x = ast.literal_eval(data)
                    result.append(x)
                feedback_line = []
                for r in result:                
                   feedback_line.append(r)  
                if feedback_line:
                    for sync_log in feedback_line:
                        cursor.execute('select branch_id from crm_case_section where id=%s', (sync_log['saleteam_id'],))
                        branch_id = cursor.fetchone()[0]
                        print_result = {
                            'sale_team_id':sync_log['saleteam_id'],
                            'date':sync_log['date'],
                            'customer_id':sync_log['customer_id'],
                            'customer_code':sync_log['customer_code'],
                            'feedback_type':sync_log['feedback_type'],
                            'contents':sync_log['contents'],
                            'branch_id':branch_id,
                            'maingroup_id':sync_log['maingroup_id'],
                            'latitude':sync_log['latitude'],
                            'longitude':sync_log['longitude'],
                            }
                        sync_obj.create(cursor, user, print_result, context=context)
                return True
             except Exception, e:
                return False
                    
    def create_tablet_logout_time(self, cursor, user, vals, context=None):
        try :
                sync_obj = self.pool.get('tablet.logout.time')
                str = "{" + vals + "}"
                str = str.replace("'',", "',")  # null
                str = str.replace(":',", ":'',")  # due to order_id
                str = str.replace("}{", "}|{")
                new_arr = str.split('|')
                result = []
                import datetime
                for data in new_arr:
                    x = ast.literal_eval(data)
                    result.append(x)
                log_line = []
                for r in result:                
                    log_line.append(r)
                if log_line:
                    for sync_log in log_line:
                        cursor.execute('select branch_id from crm_case_section where id=%s', (sync_log['section_id'],))
                        branch_id = cursor.fetchone()[0]
                        print_result = {
                            'section_id':sync_log['section_id'],
                            'user_id':user,
                            'logout_time':datetime.datetime.now(),
                            'branch_id':branch_id,
                            }
                        sync_obj.create(cursor, user, print_result, context=context)
                return True
        except Exception, e:
                return False                 
            
    def create_stock_delivery_reprint(self, cursor, user, vals, context=None):
             try :
                sync_obj = self.pool.get('stock.delivery.reprint')
                str = "{" + vals + "}"
                str = str.replace("'',", "',")  # null
                str = str.replace(":',", ":'',")  # due to order_id
                str = str.replace("}{", "}|{")
                new_arr = str.split('|')
                result = []
                for data in new_arr:
                    x = ast.literal_eval(data)
                    result.append(x)
                reprint_count = []
                for r in result:                
                    reprint_count.append(r)  
                if reprint_count:
                    for sync_reprint in reprint_count:
                        cursor.execute("select id from sale_order where name = %s", (sync_reprint['presaleorder_id'].replace("\\", ""),))    
                        order_id = cursor.fetchone()[0]                                
                        cursor.execute('select branch_id from crm_case_section where id=%s', (sync_reprint['section_id'],))
                        branch_id = cursor.fetchone()[0]
                        cursor.execute("delete from stock_delivery_reprint where reprint_date =%s and presaleorder_id = %s and void_flag=%s", (datetime.now(), order_id, sync_reprint['void_flag'],)) 
                        print_result = {
                            'reprint_date':datetime.now(),
                            'branch_id':branch_id,
                            'section_id':sync_reprint['section_id'],
                            'presaleorder_id':order_id,
                            'partner_id':sync_reprint['customer'],
                            'customer_code':sync_reprint['customer_code'],
                            'total_amount':sync_reprint['total_amount'],
                            'reprint_count':sync_reprint['reprint_count'],
                            'void_flag':sync_reprint['void_flag'],
                            }
                        
                        sync_obj.create(cursor, user, print_result, context=context)
                return True
             except Exception, e:
                return False    
                            
# NZO
    def create_exchange_product(self, cursor, user, vals, context=None):
        print 'vals', vals
        try : 
            product_trans_obj = self.pool.get('product.transactions')
            product_trans_line_obj = self.pool.get('product.transactions.line')
            sale_team_obj = self.pool.get('crm.case.section')
            str = "{" + vals + "}"
            str = str.replace(":''", ":'")  # change Order_id
            str = str.replace("'',", "',")  # null
            str = str.replace(":',", ":'',")  # due to order_id
            str = str.replace(":'}", ":''}")
            str = str.replace("}{", "}|{")
            
            new_arr = str.split('|')
            result = []
            for data in new_arr:
                x = ast.literal_eval(data)
                result.append(x)
            product_trans = []
            product_trans_line = []
            for r in result:
                print "length", len(r)
                if len(r) ==15:
                    product_trans_line.append(r)                   
                else:
                    product_trans.append(r)
            
            if product_trans:
                for pt in product_trans:
                    exchange_type = pt['exchange_type']
                    print 'exchange_type', exchange_type
#                     cursor.execute('select id From res_users where partner_id  = %s ',(so['user_id'],))
#                     data = cursor.fetchall()
#                     if data:
#                         saleManId = data[0][0]
#                     else:
#                         saleManId = None
                    sale_team_id = int(pt['team_id'])
                    sale_team_data = sale_team_obj.browse(cursor, user, sale_team_id , context=None)
                    if pt['type'] == 'Normal stock returned':
                        location_type_id = sale_team_data.normal_return_location_id.id
                    elif pt['type'] == 'Expired':
                        location_type_id = sale_team_data.exp_location_id.id
                    elif pt['type'] == 'Near expiry':
                        location_type_id = sale_team_data.near_exp_location_id.id
                    elif pt['type'] == 'Fresh stock minor damage':
                        location_type_id = sale_team_data.fresh_stock_not_good_location_id.id
                    elif pt['type'] == 'Damaged':
                        location_type_id = sale_team_data.damage_location_id.id
                    if pt['date']:
                        exchange_date_time = pt['date']
                        exhange_date = datetime.strptime(exchange_date_time, '%Y-%m-%d %H:%M:%S') - timedelta(hours=6, minutes=30)
                        # check_date = date.date()                        
                    if pt['pricelist_id']:
                        price_list_name= pt['pricelist_id']
                        cursor.execute("select id from product_pricelist where name=%s",(price_list_name,))
                        pricelist_data=cursor.fetchone()
                        if pricelist_data:
                            pricelist_id =pricelist_data[0]
                        else:
                            pricelist_id=None
                        
                    mso_result = {
                                'transaction_id':pt['transaction_id'],
                                'customer_id':pt['customer_id'],
                                'customer_code':pt['customer_code'] ,
                                'team_id':pt['team_id'],
                                'date':exhange_date,
                                'exchange_type':pt['exchange_type'],
                                'void_flag':pt['void_flag'],
                                'location_id':location_type_id,  # pt['location_id'],
                                'location_type':pt['type'],
                                'latitude':pt['mosLatitude'],
                                'longitude':pt['mosLongitude'],
                                'pricelist_id':pricelist_id,
                                'total_value':pt['total_value'],
                                'ams_total':pt ['ams_total'],
                                'out_ams_percent':pt ['out_ams_percent'],
                              'ams_buget_total':pt ['ams_buget_total'],
                                'month_out_todate':pt ['month_out_todate'],
                                'balance_total':pt ['balance_total'],



                                }
                    s_order_id = product_trans_obj.create(cursor, user, mso_result, context=context)
                    
                    for ptl in product_trans_line:
                        if ptl['transaction_id'] == pt['transaction_id']:
                            
                                if ptl['exp_date'] is None:
                                    exp_date = None
                                else:
                                    exp_date = ptl['exp_date']
                                
                                if exp_date == '' :
                                    exp_date = None
                                else:
                                    exp_date = exp_date
                                
                                cursor.execute('select uom_id from product_product pp,product_template pt where pp.product_tmpl_id=pt.id and pp.id=%s', (ptl['product_id'],))
                                uom_id = cursor.fetchone()[0]
                                total_price =ptl['total_price']
                                mso_line_res = {                                                            
                                  'transaction_id':s_order_id,
                                  'product_id':ptl['product_id'],
                                  'product_qty':ptl['product_qty'],
                                  'uom_id':ptl['uom_id'],
                                  'so_No':ptl['so_No'],
                                  'trans_type':ptl['trans_type'],
                                  'transaction_name':ptl['transaction_name'],
                                  'note':ptl['note'],
                                  'exp_date':exp_date,
                                  'total_price':total_price,
                                  'batchno':ptl['batchno'],
                                }
                                product_trans_line_obj.create(cursor, user, mso_line_res, context=context)
                    product_trans_obj.action_convert_ep(cursor, user, [s_order_id], context=context)

            print 'Truwwwwwwwwwwwwwwwwwwwwwe'
            return True       
        except Exception, e:
            print 'False'
            return False


    def create_field_audit_record(self, cursor, user, vals, context=None):
        print 'vals', vals
        try : 
            product_trans_obj = self.pool.get('field.audit')
            customer_obj = self.pool.get('res.partner')
            product_trans_line_obj = self.pool.get('field.audit.line')
            str = "{" + vals + "}"
            str = str.replace(":''", ":'")  # change Order_id
            str = str.replace("'',", "',")  # null
            str = str.replace(":',", ":'',")  # due to order_id
            str = str.replace(":'}", ":''}")
            str = str.replace("}{", "}|{")
            
            new_arr = str.split('|')
            result = []
            for data in new_arr:
                x = ast.literal_eval(data)
                result.append(x)
            field_trans = []
            field_trans_line = []
            for r in result:
                print "length", len(r)
                if len(r) <10:
                    field_trans_line.append(r)                   
                else:
                    field_trans.append(r)
            
            if field_trans:
                for pt in field_trans:
                    customer_id = int(pt['customer_id'])
                    customer_data=customer_obj.browse(cursor, user, customer_id , context=None)
                    if customer_data:
                        outlet_type_id=sales_channel_id=township_id=city_id=frequency_id=class_id=None
                        outlet_type=customer_data.outlet_type
                        sales_channel=customer_data.sales_channel
                        township=customer_data.township
                        city=customer_data.city
                        address=customer_data.street
                        frequency=customer_data.frequency_id
                        class_id=customer_data.class_id
                        if outlet_type:
                            outlet_type_id=outlet_type.id
                        if sales_channel:
                            sales_channel_id=sales_channel.id
                        if township:
                            township_id=township.id
                        if city:
                            city_id=city.id
                        if frequency:
                            frequency_id=frequency.id
                        if class_id:
                            class_id=class_id.id
                        
                    if pt['createdDateTime']:
                        date_time = pt['createdDateTime']
                        trans_date = datetime.strptime(date_time, '%Y-%m-%d %I:%M:%S %p') - timedelta(hours=6, minutes=30)

                    if pt['branch']:
                        branch_name= pt['branch']
                        cursor.execute("select id from res_branch where name=%s",(branch_name,))
                        branch_data=cursor.fetchone()
                        if branch_data:
                            branch_id =branch_data[0]
                        else:
                            branch_id=None
                            
                    if pt['auditorName']:
                        team_name= pt['auditorName']
                        cursor.execute("select id from crm_case_section where name=%s",(team_name,))
                        team_data=cursor.fetchone()
                        if team_data:
                            auditor_id =team_data[0]
                        else:
                            auditor_id=None

                        
                    mso_result = {
                                'transaction_id':pt['customer_audit_id'],
                                'partner_id':pt['customer_id'],
                                'outlet_type': outlet_type_id,
                                'township_id':township_id,
                                'city_id':city_id,
                                'address':address,
                                'frequency_id':frequency_id,
                                'class_id':class_id,
                                'sales_channel':sales_channel_id,
                                'customer_code':pt['customer_code'] ,
                                'sale_team_id':pt['sale_team_id'],
                                'date':trans_date,
                                'latitude':pt['latitude'],
                                'longitude':pt['longitude'],
                                'branch_id':branch_id,
                                'total_score':pt['total_score'],
                                'total_missed':pt ['total_missed'],
                                'shop_image':pt ['shop_image'],
                                'auditor_image':pt ['saleman_image'],
                                'merchant_image1':pt ['merchant_image1'],
                                'merchant_image2':pt ['merchant_image2'],
                                'merchant_image3':pt ['merchant_image3'],
                                'merchant_image4':pt ['merchant_image4'],
                                'merchant_image5':pt ['merchant_image5'],
                                'note':pt ['note'],
                                'auditor_team_id':auditor_id,
                                }
                    s_order_id = product_trans_obj.create(cursor, user, mso_result, context=context)
                    cursor.execute("select sequence,id from audit_question")
                    question_data=cursor.fetchall()    
                    for question_ids in question_data:
                        question_result = {
                            'sequence':question_ids[0],
                            'question_id':question_ids[1],
                            'audit_id':s_order_id,
                            }
                        product_trans_line_obj.create(cursor, user, question_result, context=context)
                    
                    for ptl in field_trans_line:
                        if ptl['customer_audit_id'] == pt['customer_audit_id']:
                            cursor.execute("update field_audit_line set complete=True where audit_id =%s and question_id=%s",(s_order_id,ptl['auditline_id'],))
            
            print 'Truwwwwwwwwwwwwwwwwwwwwwe'
            return True       
        except Exception, e:
            print 'False'
            return False
            
    def create_mo(self, cursor, user, vals, context=None):
        print 'vals', vals
        try : 
            product_mo_obj = self.pool.get('product.disassembly')
            product_mo_line_obj = self.pool.get('product.disassembly.line')
            str = "{" + vals + "}"
            str = str.replace(":''", ":'")  # change Order_id
            str = str.replace("'',", "',")  # null
            str = str.replace(":',", ":'',")  # due to order_id
            str = str.replace(":'}", ":''}")
            str = str.replace("}{", "}|{")
            
            new_arr = str.split('|')
            result = []
            for data in new_arr:
                x = ast.literal_eval(data)
                result.append(x)
            product_mo = []
            product_mo_line = []
            for r in result:
                print "length", len(r)
                if len(r) >= 7:
                    product_mo_line.append(r)                   
                else:
                    product_mo.append(r)
            
            if product_mo:
                for pm in product_mo:
                    mso_result = {
                        'date':pm['date'],
                        'create_date':pm['create_datetime'],
                        'location_id':pm['location_id'],
                        'user_id':pm['user_id'] ,
                        'section_id':pm['saleteam_id'] ,
                        'product_lines':pm['mo_id'],
                    }
                    mo_id = product_mo_obj.create(cursor, user, mso_result, context=context)
                    
                    for mol in product_mo_line:
                        if mol['line_id'] == pm['mo_id']:
                                mo_line_res = {                                                            
                                  'line_id':mo_id,
                                  'product_id':mol['product_id'],
                                  'big_uom_id':mol['bigUom_id'],
                                  'big_quantity':mol['Qty'],
                                  'to_product_id':mol['toProduct_id'],
                                  'uom_id':mol['toUoM_id'],
                                  'quantity':mol['toQty'],
                                }
                                product_mo_line_obj.create(cursor, user, mo_line_res, context=context)
                    product_mo_obj.product_disassembly(cursor, user, [mo_id], context=context)

                                    
            print 'Truwwwwwwwwwwwwwwwwwwwwwe'
            return True       
        except Exception, e:
            print 'False'
            return False  
        
    def create_visit(self, cursor, user, vals, context=None):
        
        try:
            # print 'vals', vals
            customer_visit_obj = self.pool.get('customer.visit')
            str = "{" + vals + "}"    
            str = str.replace("'',", "',")  # null
            str = str.replace(":',", ":'',")  # due to order_id
            str = str.replace("}{", "}|{")
            str = str.replace(":'}{", ":''}")
            new_arr = str.split('|')
            result = []
            for data in new_arr:            
                x = ast.literal_eval(data)                
                result.append(x)
            customer_visit = []
            for r in result:                
                customer_visit.append(r)  
            if customer_visit:
                for vs in customer_visit:

                    cursor.execute('select branch_id from crm_case_section where id=%s', (vs['sale_team_id'],))
                    branch_id = cursor.fetchone()[0]
                    cursor.execute('select id from res_partner where customer_code=%s', (vs['customer_code'],))
                    customer_id = cursor.fetchone()  
                    is_image = False
                    distance_status = None
                    image_ids = []
                    if customer_id:
                        if vs['image_reference_list']:
                            is_image = True
                            image_ref_list = vs['image_reference_list']
                            # image_ref_list = ['KESGMTMVGU','WLTZPEZIHK','NXEOATLOBS','HPFZHHVQQX','GNNZJSYPUW','LBUXNOLSMA','OMOKJFSPRW']
                            _logger.info('-----------vs[image_reference_list]---------- %s', vs['image_reference_list'])
                            for ref in image_ref_list:
                                image_ids += [(0, 0, {'name':ref})]
                        if vs['distance_status']:
                                distance_status=vs['distance_status']
                        visit_result = {
                            'customer_code':vs['customer_code'],
                            'branch_id':branch_id,
                            'customer_id':customer_id[0],
                            'sale_plan_day_id':vs['sale_plan_day_id'],
                            'sale_plan_trip_id':vs['sale_plan_trip_id'] ,
                          #  'sale_plan_name':vs['sale_plan_name'],
                            # 'sale_team':vs['sale_team'],
                            'sale_team_id':vs['sale_team_id'],
                            'user_id':vs['user_id'],
                            'date':vs['date'],
                            'tablet_id':vs['tablet_id'],
                            'other_reason':vs['other_reason'],
                            'visit_reason':vs['visit_reason'],
                            'latitude':vs['latitude'],
                            'longitude':vs['longitude'],
                            'visit_image_ids': image_ids,
                            'distance_status': distance_status,

                        }
                        visit_id=customer_visit_obj.create(cursor, user, visit_result, context=context)
                        # if visit_id and not is_image1 and not is_image2 and not is_image3 and not is_image4 and not is_image5:
                        if visit_id and not is_image:
                            customer_visit_obj.is_reject(cursor, user, [visit_id], context=context)
                        #customer_visit_obj.generate_image(cursor, user, [visit_id], context=context)
                return True
        except Exception, e:
            print e            
            return False
                
    def geo_location(self, cr, uid, ids, context=None):
        result = {
                 'name'     : 'Go to Report',
                 'res_model': 'ir.actions.act_url',
                 'type'     : 'ir.actions.act_url',
                 'target'   : 'new',
               }
        data = self.browse(cr, uid, ids)[0]
        latitude = data.mso_latitude
        longitude = data.mso_longitude
        print 'latitude', latitude
        print 'longitude', longitude
        print 'https://www.google.com/maps/@' + str(latitude) + ',' + str(longitude) + ',18z'
        result['url'] = 'https://www.google.com/maps/@' + str(latitude) + ',' + str(longitude) + ',18z'
             
        return result
 
    # MMK   
    def action_convert_so(self, cr, uid, ids, context=None):
        msoObj = self.pool.get('mobile.sale.order')
        partner_obj = self.pool.get('res.partner')
        soObj = self.pool.get('sale.order')
        solObj = self.pool.get('sale.order.line')
        invObj = self.pool.get("sale.advance.payment.inv")
        invoiceObj = self.pool.get('account.invoice')
        voucherObj = self.pool.get('account.voucher')
        voucherLineObj = self.pool.get('account.voucher.line')
        stockPickingObj = self.pool.get('stock.picking')
        stockDetailObj = self.pool.get('stock.transfer_details')
        msoPromoLineObj = self.pool.get('sale.order.promotion.line')
        mso_promotion_line_obj = self.pool.get('mso.promotion.line')
        mso_inv_PromoLineObj = self.pool.get('account.invoice.promotion.line')        
        product_obj = self.pool.get('product.product')
        soResult = {}
        solResult = {}
        accountVResult = {}
        foc = False
        price_unit = 0.0
        soId = so_state = iv_state = default_code = pricelist_id = sale_team_id = analytic_id = invoice_id = journal_id = accountId = voucherId = stockViewResult = wizResult = detailObj = None
        solist = []
        invlist = []
        vlist = []
        invFlag = False
        product_name = ''
        if ids:
            # default price list need in sale order form
#             cr.execute("""select id from product_pricelist where type = 'sale' """)
#             data = cr.fetchall()
#             if data:
#                 pricelist_id = data[0][0]
# old query version 
#                 cr.execute("select TI.sale_team_id from  mobile_sale_order msol,tablets_information TI where msol.tablet_id=TI.id and msol.id=%s", (ids[0],))
#                 sale_team_id = cr.fetchone()
            sale_team_obj = self.browse(cr, uid, ids, context)
            sale_team_id = sale_team_obj.sale_team.id
            cr.execute("select cc.analytic_account_id from crm_case_section cc,mobile_sale_order mso where mso.sale_team=cc.id and mso.id=%s", (ids[0],))
            analytic_id = cr.fetchone()
            if analytic_id:
                try:
                    analytic_id = analytic_id[0][0]
                except Exception, e:
                    analytic_id = analytic_id[0]
            else:
                analytic_id = False

            for ms_ids in msoObj.browse(cr, uid, ids[0], context=context):
                if ms_ids:
                    if ms_ids.void_flag == 'voided':  # they work while payment type not 'cash' and 'credit'
                        so_state = 'cancel'
                    elif ms_ids.void_flag == 'none':
                        so_state = 'draft'
                    cr.execute("select company_id from res_users where id=%s", (ms_ids.user_id.id,))
                    company_id = cr.fetchone()[0]
                    date = datetime.strptime(ms_ids.date, '%Y-%m-%d %H:%M:%S')
                    de_date = date.date()  
                    original_ecommerce_number =None
                    ecommerce =False  
                    if  ms_ids.pre_sale_order_id:
                        pre_sale_order_id=ms_ids.pre_sale_order_id.id
                        cr.execute("select id,ecommerce,woo_order_id from sale_order where id = %s ",(pre_sale_order_id,))
                        sale_order_data=cr.fetchone()
                        if sale_order_data:
                            ecommerce =sale_order_data[1]
                            woo_order_id =sale_order_data[2]
                            if ecommerce == True :
                                original_ecommerce_number = woo_order_id
                                ecommerce = True                              
                    else:
                        pre_sale_order_id= False
                    if ms_ids.order_team:
                        order_team=ms_ids.order_team.id
                    else:
                        order_team=sale_team_id
                    
                    soResult = {
                                          'date_order':ms_ids.date,
                                           'partner_id':ms_ids.partner_id.id,
                                           'amount_untaxed':ms_ids.amount_total ,
                                           'partner_invoice_id':ms_ids.partner_id.id,
                                           'user_id':ms_ids.user_id.id,
                                           'date_confirm':ms_ids.date,
                                           'amount_total':ms_ids.amount_total,
                                           'order_policy':'manual',
                                           'company_id':company_id,
                                           'payment_term':ms_ids.payment_term.id,
                                            'state':so_state,
                                            'pricelist_id':ms_ids.pricelist_id.id,
                                            'picking_policy':'direct',
                                            'warehouse_id':ms_ids.warehouse_id.id,
                                            'project_id':analytic_id,
                                            'partner_shipping_id':ms_ids.partner_id.id,
                                            # 'shipped':'f',
                                            'tb_ref_no':ms_ids.name,
                                            'delivery_township_id':ms_ids.partner_id.township.id,
                                            'sale_plan_name':ms_ids.sale_plan_name,
                                            'payment_type':ms_ids.type,
                                            'section_id':sale_team_id,
                                            'due_date':ms_ids.due_date,
                                            'so_latitude':ms_ids.mso_latitude,
                                            'so_longitude':ms_ids.mso_longitude,
                                             'additional_discount':ms_ids.additional_discount * 100,
                                            'deduct_amt':ms_ids.deduction_amount,
                                            'delivery_remark':ms_ids.delivery_remark,
                                            'sale_plan_day_id':ms_ids.sale_plan_day_id.id,
                                            'sale_plan_trip_id':ms_ids.sale_plan_trip_id.id,
                                            'customer_code':ms_ids.customer_code,
                                            'branch_id':ms_ids.branch_id.id,
                                             'note':ms_ids.note,
                                            'rebate_later':ms_ids.rebate_later,
                                             'ignore_credit_limit':True,
                                             'credit_history_ids':[],
                                             'pre_sale_order_id':pre_sale_order_id,
                                             'order_team':order_team,
                                             'original_ecommerce_number':original_ecommerce_number,
                                             'ecommerce':ecommerce,
                                             'revise_reason_id':ms_ids.revise_reason_id.id if ms_ids.revise_reason_id else None,
                                             'cancel_reason_id':ms_ids.cancel_reason_id.id if ms_ids.cancel_reason_id else None,
                                        }
                    soId = soObj.create(cr, uid, soResult, context=context)
                    if soId:
                        # Insert Mobile Sale Order Promotion Line
                        for mso_p_line in ms_ids.promos_line_ids:
                            mso_promo_data = mso_promotion_line_obj.browse(cr, uid, mso_p_line.id, context=context)
                            mso_promo_line_result = {
                                              'promo_line_id':soId,
                                              'pro_id':mso_promo_data.pro_id.id,
                                              'from_date':mso_promo_data.from_date,
                                              'to_date':mso_promo_data.to_date,
                                              'manual':mso_promo_data.manual,
                                                          }
                            msoPromoLineObj.create(cr, uid, mso_promo_line_result, context=context)                    
                    if soId and ms_ids.order_line:
                        for line_id in ms_ids.order_line:
                            if line_id:
                                if line_id.product_id:
                                    if line_id.product_id:
                                        cr.execute("""select default_code from product_product where product_tmpl_id = %s""", (line_id.product_id.id,))
                                        data = cr.fetchall()
                                        if data:
                                            default_code = data[0][0]
                                        if default_code:
                                            product_name = line_id.product_id.name
                                        else:
                                            product_name = line_id.product_id.name
                                        product_data = product_obj.browse(cr, uid, line_id.product_id.id, context=context)
                                        tax_data = False    
                                        taxes = product_data.taxes_id
                                        if taxes:
                                            fpos = ms_ids.partner_id.property_account_position or False
                                            tax_id = self.pool.get('account.fiscal.position').map_tax(cr, uid, fpos, taxes, context=context)
                                            tax_data = [[6, 0, tax_id]]
                                        # FOC with price_unit or foc true, false
                                    if line_id.sub_total == 0.0 or line_id.foc:
                                        foc = True
                                        product_name = 'FOC'
                                        price_unit = 0.0
                                    else:
                                        foc = False
                                        price_unit = line_id.price_unit
                                solResult = {
                                             'order_id':soId,
                                              'product_id':line_id.product_id.id,
                                              'name':product_name,
                                              'price_unit':price_unit,
                                              'product_uom':line_id.uom_id.id,
                                              'product_uom_qty':line_id.product_uos_qty,
                                              'discount':line_id.discount,
                                              'discount_amt':line_id.discount_amt,
                                              'tax_id': tax_data,
                                              'company_id':company_id,  # company_id,
                                              'state':'draft',
                                              'net_total':line_id.sub_total,
                                              'sale_foc':foc,
                                             'promotion_id':line_id.promotion_id.id,

                                           }
                                
                                solObj.create(cr, uid, solResult, context=context)
                                if soId:
                                    soObj.button_dummy(cr, uid, [soId], context=context)  # update the SO
                                    
                if ms_ids and  so_state != 'cancel':
                    if ms_ids.type:
                        solist.append(soId)
                        # type > cash and delivery_remark > delivered
                        if ms_ids.type == 'cash' and ms_ids.delivery_remark == 'delivered':  # Payment Type=>Cash and Delivery Remark=>Delivered
                            # SO Confirm 
                            # journal_id = ms_ids.journal_id.id
                            soObj.action_button_confirm(cr, uid, solist, context=context)
                            # Create Invoice
                            invoice_id = self.create_invoices(cr, uid, solist, context=context)
                          
                            cr.execute('update account_invoice set payment_type=%s ,branch_id =%s,delivery_remark =%s,date_invoice=%s where id =%s', ('cash', ms_ids.branch_id.id, ms_ids.delivery_remark, de_date, invoice_id,))                            
                            invoiceObj.button_reset_taxes(cr, uid, [invoice_id], context=context)
                            if invoice_id and ms_ids.paid == True:
#                                 invlist = []
#                                 invlist.append(invoice_id)
#                                 print 'invoice_id', invoice_id
#                             
#                                 
#                                 # call the api function
#                                 # invObj contain => account.invoice(1,) like that
#                                 invObj = invoiceObj.browse(cr, uid, invoice_id, context=context)
#                                 print 'invoice_id', invObj
#                                 invObj.action_date_assign()
#                                 invObj.action_move_create()
#                                 invObj.action_number()
#                                 # validate invoice
#                                 invObj.invoice_validate()
                                self.pool['account.invoice'].signal_workflow(cr, uid, [invoice_id], 'invoice_open')                                
                                # register Payment
                                # calling the register payment pop-up
#                                 invoiceObj.invoice_pay_customer(cr, uid, invlist, context=context)
#                                 if journal_id:
#                                     cr.execute('select default_debit_account_id from account_journal where id=%s', (journal_id,))
#                                     data = cr.fetchall()
#                                     if data:
#                                         accountId = data[0]
#                                 else:
#                                         raise osv.except_osv(_('Warning!'), _("Insert Journal for Cash Sale"))
# #                                 cr.execute('select id from account_account where lower(name)=%s and active= %s', ('cash', True,))  # which account shall I choose. It is needed.
# #                                 data = cr.fetchall()
# #                                 if data:
# #                                     accountId = data[0]
#                                 if journal_id and accountId:  # cash journal and cash account. If there no journal id or no account id, account invoice is not make payment.
#                                     accountVResult = {
#                                                     'partner_id':invObj.partner_id.id,
#                                                     'amount':invObj.amount_total,
#                                                     'journal_id':journal_id,
#                                                     'date':invObj.date_invoice,
#                                                     'period_id':invObj.period_id.id,
#                                                     'account_id':accountId,
#                                                     'pre_line':True,
#                                                     'type':'receipt'
#                                                     }
#                                     # create register payment voucher
#                                     voucherId = voucherObj.create(cr, uid, accountVResult, context=context)
#                                     
#                                 if voucherId:
#                                     vlist = []
#                                     vlist.append(voucherId)
#                                     # get the voucher lines
#                                     vlresult = voucherObj.recompute_voucher_lines(cr, uid, vlist, invObj.partner_id.id, journal_id, invObj.amount_total, 120, 'receipt', invObj.date_invoice, context=None)
#                                     if vlresult:
#                                         result = vlresult['value']['line_cr_ids'][0]
#                                         result['voucher_id'] = voucherId
#                                         # create the voucher lines
#                                         voucherLineObj.create(cr, uid, result, context=context)
#                                     # invoice register payment done
#                                     voucherObj.button_proforma_voucher(cr, uid, vlist , context=context)
#                                     # invoice paid status is true
#                                     invFlag = True
                            # clicking the delivery order view button
#                             stockViewResult = soObj.action_view_delivery(cr, uid, solist, context=context)
#                              
#                             if stockViewResult:
#                                 # cr.execute('update stock_move set location_id=%s where picking_id=%s',(ms_ids.location_id.id,stockViewResult['res_id'],))
#                                 # stockViewResult is form result
#                                 # stocking id =>stockViewResult['res_id']
#                                 # click force_assign
#                                 stockPickingObj.force_assign(cr, uid, stockViewResult['res_id'], context=context)
#                                 # transfer
#                                 # call the transfer wizard
#                                 # change list
#                                 pickList = []
#                                 pickList.append(stockViewResult['res_id'])
#                                 wizResult = stockPickingObj.do_enter_transfer_details(cr, uid, pickList, context=context)
#                                 # pop up wizard form => wizResult
#                                 detailObj = stockDetailObj.browse(cr, uid, wizResult['res_id'], context=context)
#                                 if detailObj:
#                                     detailObj.do_detailed_transfer()
                                new_session = ConnectorSession(cr, uid, context)
                                jobid = automatic_direct_sale_transfer.delay(new_session, solist, ms_ids.date, priority=10)
                                cr.execute ('''select count(id) as credit_note_count from customer_payment where payment_code ='CN' and notes =%s''',(ms_ids.name,))
                                credit_note_count=cr.fetchone()[0]
                                if ms_ids.payment_ref=='credit_note':
                                    queue_id=self.pool['queue.job'].search(cr, uid, [('uuid', '=', jobid)], context=context)
                                    self.pool['queue.job'].write(cr, uid, queue_id, {'is_credit_invoice':True}, context)                                     
                                runner = ConnectorRunner()
                                runner.run_jobs()                                       
                        if ms_ids.type == 'cash' and ms_ids.delivery_remark == 'none':  # Payment Type=>Cash and Delivery Remark=>None
                            # SO Confirm 
                            soObj.action_button_confirm(cr, uid, solist, context=context)
                            # Create Invoice
                            invoice_id = self.create_invoices(cr, uid, solist, context=context)
#                             #id update partner form (temporay)
#                             partner_data = invoiceObj.browse(cr, uid, invoice_id, context=context)
#                             partner_id=partner_data.partner_id.id
#                             partner_obj.write(cr,uid,partner_id,{'property_account_receivable':629}, context)
#                             partner = partner_obj.browse(cr, uid, partner_id, context=context)
#                             account_id=partner.property_account_receivable.id
#                             invoiceObj.write(cr,uid,invoice_id,{'account_id':account_id}, context)                                    
                            cr.execute('update account_invoice set payment_type=%s ,branch_id =%s,delivery_remark =%s ,date_invoice =%s where id =%s', ('cash', ms_ids.branch_id.id, ms_ids.delivery_remark, de_date, invoice_id,))                            
                            invoiceObj.button_reset_taxes(cr, uid, [invoice_id], context=context)
                            if invoice_id and ms_ids.paid == True:
#                                 invlist = []
#                                 invlist.append(invoice_id)
#                                 # call the api function
#                                 # invObj contain => account.invoice(1,) like that
#                                 invObj = invoiceObj.browse(cr, uid, invlist, context=context)
#                                 invObj.action_date_assign()
#                                 invObj.action_move_create()
#                                 invObj.action_number()
#                                 # validate invoice
#                                 invObj.invoice_validate()
#     
                                self.pool['account.invoice'].signal_workflow(cr, uid, [invoice_id], 'invoice_open')
                            
                                # register Payment
                                # calling the register payment pop-up
#                                 invoiceObj.invoice_pay_customer(cr, uid, invlist, context=context)
#                                 cr.execute('select id from account_journal where type=%s', ('cash',))
#                                 data = cr.fetchall()
#                                 if data:
#                                     journal_id = data[0]
#                                 cr.execute('select id from account_account where lower(name)=%s and active= %s', ('cash', True,))  # which account shall I choose. It is needed.
#                                 data = cr.fetchall()
#                                 if data:
#                                     accountId = data[0]
#                                 if journal_id and accountId:  # cash journal and cash account. If there no journal id or no account id, account invoice is not make payment.
#                                     accountVResult = {
#                                                     'partner_id':invObj.partner_id.id,
#                                                     'amount':invObj.amount_total,
#                                                     'journal_id':journal_id,
#                                                     'date':invObj.date_invoice,
#                                                     'period_id':invObj.period_id.id,
#                                                     'account_id':accountId,
#                                                     'pre_line':True,
#                                                     'type':'receipt'
#                                                     }
#                                     # create register payment voucher
#                                     voucherId = voucherObj.create(cr, uid, accountVResult, context=context)
#                                     
#                                 if voucherId:
#                                     vlist = []
#                                     vlist.append(voucherId)
#                                     # get the voucher lines
#                                     vlresult = voucherObj.recompute_voucher_lines(cr, uid, vlist, invObj.partner_id.id, journal_id, invObj.amount_total, 120, 'receipt', invObj.date_invoice, context=None)
#                                     if vlresult:
#                                         result = vlresult['value']['line_cr_ids'][0]
#                                         result['voucher_id'] = voucherId
#                                         # create the voucher lines
#                                         voucherLineObj.create(cr, uid, result, context=context)
#                                     # invoice register payment done
#                                     voucherObj.button_proforma_voucher(cr, uid, vlist , context=context)
#                                     # invoice paid status is true
#                                     invFlag = True
                            # clicking the delivery order view button
                            stockViewResult = soObj.action_view_delivery(cr, uid, solist, context=context)
                            # cr.execute('update stock_move set location_id=%s where picking_id=%s',(ms_ids.location_id.id,stockViewResult['res_id'],))
                            # create the delivery with draft state
                        if ms_ids.type == 'cash' and ms_ids.delivery_remark == 'partial':  # Payment Type=>Cash and Delivery Remark=>None
                            # SO Confirm 
                            soObj.action_button_confirm(cr, uid, solist, context=context)
                            # Create Invoice
                            invoice_id = self.create_invoices(cr, uid, solist, context=context)
                            # id update partner form (temporay)
#                             partner_data = invoiceObj.browse(cr, uid, invoice_id, context=context)
#                             partner_id=partner_data.partner_id.id
#                             partner_obj.write(cr,uid,partner_id,{'property_account_receivable':629}, context)
#                             partner = partner_obj.browse(cr, uid, partner_id, context=context)
#                             account_id=partner.property_account_receivable.id
#                             invoiceObj.write(cr,uid,invoice_id,{'account_id':account_id}, context)                                    
                            cr.execute('update account_invoice set payment_type=%s ,branch_id =%s,delivery_remark =%s,date_invoice=%s  where id =%s', ('cash', ms_ids.branch_id.id, ms_ids.delivery_remark, de_date, invoice_id,))                            
                            invoiceObj.button_reset_taxes(cr, uid, [invoice_id], context=context)
                            if invoice_id and ms_ids.paid == True:
#                                 invlist = []
#                                 invlist.append(invoice_id)
#                                 # call the api function
#                                 # invObj contain => account.invoice(1,) like that
#                                 invObj = invoiceObj.browse(cr, uid, invoice_id, context=context)
#                                 invObj.action_date_assign()
#                                 invObj.action_move_create()
#                                 invObj.action_number()
#                                 # validate invoice
#                                 invObj.invoice_validate()
                                self.pool['account.invoice'].signal_workflow(cr, uid, [invoice_id], 'invoice_open')
                                
                                # register Payment
                                # calling the register payment pop-up
#                                 invoiceObj.invoice_pay_customer(cr, uid, invlist, context=context)
#                                 cr.execute('select id from account_journal where type=%s', ('cash',))
#                                 data = cr.fetchall()
#                                 if data:
#                                     journal_id = data[0]
#                                 cr.execute('select id from account_account where lower(name)=%s and active= %s and type=%s ', ('cash', True, 'liquidity',))  # which account shall I choose. It is needed.
#                                 data = cr.fetchall()
#                                 if data:
#                                     accountId = data[0]
#                                 if journal_id and accountId:  # cash journal and cash account. If there no journal id or no account id, account invoice is not make payment.
#                                     accountVResult = {
#                                                     'partner_id':invObj.partner_id.id,
#                                                     'amount':invObj.amount_total,
#                                                     'journal_id':journal_id,
#                                                     'date':invObj.date_invoice,
#                                                     'period_id':invObj.period_id.id,
#                                                     'account_id':accountId,
#                                                     'pre_line':True,
#                                                     'type':'receipt'
#                                                     }
#                                     # create register payment voucher
#                                     voucherId = voucherObj.create(cr, uid, accountVResult, context=context)
#                                     
#                                 if voucherId:
#                                     vlist = []
#                                     vlist.append(voucherId)
#                                     # get the voucher lines
#                                     vlresult = voucherObj.recompute_voucher_lines(cr, uid, vlist, invObj.partner_id.id, journal_id, invObj.amount_total, 120, 'receipt', invObj.date_invoice, context=None)
#                                     if vlresult:
#                                         result = vlresult['value']['line_cr_ids'][0]
#                                         result['voucher_id'] = voucherId
#                                         # create the voucher lines
#                                         voucherLineObj.create(cr, uid, result, context=context)
#                                     # invoice register payment done
#                                     voucherObj.button_proforma_voucher(cr, uid, vlist , context=context)
#                                     # invoice paid status is true
#                                     invFlag = True
                            # clicking the delivery order view button
                            stockViewResult = soObj.action_view_delivery(cr, uid, solist, context=context)
                            # cr.execute('update stock_move set location_id=%s where picking_id=%s',(ms_ids.location_id.id,stockViewResult['res_id'],))
                            # create the delivery with draft state
                        if ms_ids.type == 'credit' and ms_ids.delivery_remark == 'delivered':  # Payment Type=>Credit and Delivery Remark=>Delivered
                            # so Confirm
                            print 'solist', solist
                            soObj.action_button_confirm(cr, uid, solist, context=context)
                            # invoice create at draft state
                            invoice_id = self.create_invoices(cr, uid, solist, context=context)
                            # id update partner form (temporay)
#                             partner_data = invoiceObj.browse(cr, uid, invoice_id, context=context)
#                             partner_id=partner_data.partner_id.id
#                             partner_obj.write(cr,uid,partner_id,{'property_account_receivable':629}, context)
#                             partner = partner_obj.browse(cr, uid, partner_id, context=context)
#                             account_id=partner.property_account_receivable.id
#                             invoiceObj.write(cr,uid,invoice_id,{'account_id':account_id}, context)                                    
                            cr.execute('update account_invoice set payment_type=%s ,branch_id =%s,delivery_remark =%s ,date_invoice=%s where id =%s', ('credit', ms_ids.branch_id.id, ms_ids.delivery_remark, de_date, invoice_id,))                            
                            invoiceObj.button_reset_taxes(cr, uid, [invoice_id], context=context)
#                             invlist = []
#                             invlist.append(invoice_id)
#                             # call the api function
#                             # invObj contain => account.invoice(1,) like that
#                             invObj = invoiceObj.browse(cr, uid, invoice_id, context=context)
#                             invObj.action_date_assign()
#                             invObj.action_move_create()
#                             invObj.action_number()
#                             # validate invoice
#                             invObj.invoice_validate()
                            self.pool['account.invoice'].signal_workflow(cr, uid, [invoice_id], 'invoice_open')
                            self.pool['account.invoice'].credit_approve(cr, uid, [invoice_id], context=context)                                 
                            new_session_name = ConnectorSession(cr, uid, context)
                            jobid = automatic_direct_sale_transfer.delay(new_session_name, solist, ms_ids.date, priority=10)
                            queue_id=self.pool['queue.job'].search(cr, uid, [('uuid', '=', jobid)], context=context)
                            self.pool['queue.job'].write(cr, uid, queue_id, {'is_credit_invoice':True}, context)   
                            runner = ConnectorRunner()
                            runner.run_jobs() 
                            # clicking the delivery order view button
#                             stockViewResult = soObj.action_view_delivery(cr, uid, solist, context=context)
#                             if stockViewResult:
#                                 # cr.execute('update stock_move set location_id=%s where picking_id=%s',(ms_ids.location_id.id,stockViewResult['res_id'],))
#  
#                                 # stockViewResult is form result
#                                 # stocking id =>stockViewResult['res_id']
#                                 # click force_assign
#                                 stockPickingObj.force_assign(cr, uid, stockViewResult['res_id'], context=context)
#                                 # transfer
#                                 # call the transfer wizard
#                                 # change list
#                                 pickList = []
#                                 pickList.append(stockViewResult['res_id'])
#                                 wizResult = stockPickingObj.do_enter_transfer_details(cr, uid, pickList, context=context)
#                                 # pop up wizard form => wizResult
#                                 detailObj = stockDetailObj.browse(cr, uid, wizResult['res_id'], context=context)
#                                 if detailObj:
#                                     detailObj.do_detailed_transfer()

                        if ms_ids.type == 'credit' and ms_ids.delivery_remark == 'none':  # Payment Type=>Credit and Delivery Remark=>None
                            # so Confirm
                            soObj.action_button_confirm(cr, uid, solist, context=context)
                            # invoice create at draft state
                            invoice_id = self.create_invoices(cr, uid, solist, context=context)
                            # id update partner form (temporay)
#                             partner_data = invoiceObj.browse(cr, uid, invoice_id, context=context)
#                             partner_id=partner_data.partner_id.id
#                             partner_obj.write(cr,uid,partner_id,{'property_account_receivable':629}, context)
#                             partner = partner_obj.browse(cr, uid, partner_id, context=context)
#                             account_id=partner.property_account_receivable.id
#                             invoiceObj.write(cr,uid,invoice_id,{'account_id':account_id}, context)                                    
                            cr.execute('update account_invoice set payment_type=%s ,branch_id =%s,delivery_remark =%s,date_invoice=%s  where id =%s', ('credit', ms_ids.branch_id.id, ms_ids.delivery_remark, de_date, invoice_id,))                            
                            invoiceObj.button_reset_taxes(cr, uid, [invoice_id], context=context)
#                             invlist = []
#                             invlist.append(invoice_id)
#                             # call the api function
#                             # invObj contain => account.invoice(1,) like that
#                             invObj = invoiceObj.browse(cr, uid, invoice_id, context=context)
#                             invObj.action_date_assign()
#                             invObj.action_move_create()
#                             invObj.action_number()
#                             # validate invoice
#                             invObj.invoice_validate()
                            self.pool['account.invoice'].signal_workflow(cr, uid, [invoice_id], 'invoice_open')
                            self.pool['account.invoice'].credit_approve(cr, uid, [invoice_id], context=context)                                 

                            # clicking the delivery order view button
                            stockViewResult = soObj.action_view_delivery(cr, uid, solist, context=context)  # create delivery order with draft state
                            # cr.execute('update stock_move set location_id=%s where picking_id=%s',(ms_ids.location_id.id,stockViewResult['res_id'],))

                        if ms_ids.type == 'credit' and ms_ids.delivery_remark == 'partial':  # Payment Type=>Credit and Delivery Remark=>Partial
                            # so Confirm
                            soObj.action_button_confirm(cr, uid, solist, context=context)
                            # invoice create at draft state
                            invoice_id = self.create_invoices(cr, uid, solist, context=context)
                            # id update partner form (temporay)
#                             partner_data = invoiceObj.browse(cr, uid, invoice_id, context=context)
#                             partner_id=partner_data.partner_id.id
#                             partner_obj.write(cr,uid,partner_id,{'property_account_receivable':629}, context)
#                             partner = partner_obj.browse(cr, uid, partner_id, context=context)
#                             account_id=partner.property_account_receivable.id
#                             invoiceObj.write(cr,uid,invoice_id,{'account_id':account_id}, context)                                    
                            cr.execute('update account_invoice set payment_type=%s ,branch_id =%s,delivery_remark =%s ,date_invoice=%s where id =%s', ('credit', ms_ids.branch_id.id, ms_ids.delivery_remark, de_date, invoice_id,))                            
                            
                            invoiceObj.button_reset_taxes(cr, uid, [invoice_id], context=context)
#                             invlist = []
#                             invlist.append(invoice_id)
#                             # call the api function
#                             # invObj contain => account.invoice(1,) like that
#                             invObj = invoiceObj.browse(cr, uid, invoice_id, context=context)
#                             invObj.action_date_assign()
#                             invObj.action_move_create()
#                             invObj.action_number()
#                             # validate invoice
#                             invObj.invoice_validate()
                            self.pool['account.invoice'].signal_workflow(cr, uid, [invoice_id], 'invoice_open')
                            self.pool['account.invoice'].credit_approve(cr, uid, [invoice_id], context=context)                                 

                            # clicking the delivery order view button
                            stockViewResult = soObj.action_view_delivery(cr, uid, solist, context=context)
                            # cr.execute('update stock_move set location_id=%s where picking_id=%s',(ms_ids.location_id.id,stockViewResult['res_id'],))
                        if invoice_id:
                                # Insert account invoice promotion line
                                for mso_inv_p_line in ms_ids.promos_line_ids:
                                    mso_inv_promo_data = mso_promotion_line_obj.browse(cr, uid, mso_inv_p_line.id, context=context)
                                    mso_inv_promo_line_result = {
                                                      'promo_line_id':invoice_id,
                                                      'pro_id':mso_inv_promo_data.pro_id.id,
                                                      'from_date':mso_inv_promo_data.from_date,
                                                      'to_date':mso_inv_promo_data.to_date,
                                                      'manual':mso_inv_promo_data.manual,
                                                                  }
                                    mso_inv_PromoLineObj.create(cr, uid, mso_inv_promo_line_result, context=context)  
            self.write(cr, uid, ids[0], {'m_status':'done'}, context=context)
        return True   
    
    # MMK
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
                return res['res_id']
            except Exception, e:
                return False
            
    def get_field_audit_question(self, cr, uid,context=None, **kwargs):
        logging.warning("get_field_audit_question")
        cr.execute('''select id,sequence,name,english_name from audit_question order by sequence asc                     ''')
        datas = cr.fetchall()
        return datas 
    
    def get_stock_check_remark(self, cr, uid,context=None, **kwargs):
        cr.execute('''select id,name,active,sequence from partner_stock_check_remark''')
        datas = cr.fetchall()
        return datas     
    
    def get_supervisor_sale_team(self, cr, uid,section_id,context=None, **kwargs):
        cr.execute('''select id,name,branch_id as team_branch_id,(select name from res_branch where id =branch_id) as team_branch_name from crm_case_section 
        where supervisor_team= %s
                     ''', (section_id,))
        datas = cr.fetchall()
        return datas           
    
                
    # kzo Edit
    def get_products_by_sale_team(self, cr, uid, section_id , last_date, context=None, **kwargs):
        
        cr.execute('''select  pp.id,pt.list_price,coalesce(replace(pt.description,',',';'), ' ') as description,pt.categ_id,pc.name as categ_name,pp.default_code, 
                    pt.name,substring(replace(cast(pt.image_small as text),'/',''),1,5) as image_small,pt.main_group,pt.uom_ratio,
                    pp.product_tmpl_id,pt.is_foc,pp.sequence,pt.type,pt.uom_id
                    from product_sale_group_rel rel ,
                    crm_case_section ccs ,product_template pt, product_product pp , product_category pc
                    where pp.id = rel.product_id
                    and pt.id = pp.product_tmpl_id
                    and pt.active = true
                    and pp.active = true
                    and ccs.sale_group_id = rel.sale_group_id
                    and pc.id = pt.categ_id                        
                    and ccs.id = %s ''', (section_id,))
        datas = cr.fetchall()
        return datas

    def get_productMainGroup(self, cr, uid, section_id, context=None, **kwargs):
        cr.execute('''select id,name,skip_checking,active_two from product_maingroup''')
        datas = cr.fetchall()        
        return datas
    
    def get_revise_reason(self, cr, uid, context=None, **kwargs):    
        cr.execute('''select id,name,active from revise_reason where active=True''')
        datas = cr.fetchall()        
        return datas
    
    def get_cancel_reason(self, cr, uid, context=None, **kwargs):    
        cr.execute('''select id,name,active from cancel_reason where active=True''')
        datas = cr.fetchall()        
        return datas
        
    def get_salePlanDays_by_sale_team(self, cr, uid, section_id , context=None, **kwargs):
        cr.execute('''select id,name,date,sale_team from sale_plan_day where sale_team=%s ''', (section_id,))
        datas = cr.fetchall()
        print 'get_salePlanDays_by_sale_team',datas

        return datas
    
    # get promotion datas from database
    def get_products_categ_by_sale_team(self, cr, uid, section_id , context=None, **kwargs):
        cr.execute('''select distinct categ_id,categ_name from (
                        select pp.product_tmpl_id,pt.list_price , pt.description,pt.categ_id,pc.name as categ_name 
                        from product_sale_group_rel rel,
                        crm_case_section ccs ,product_template pt, product_product pp , product_category pc
                        where pp.id = rel.product_id
                        and pt.id = pp.product_tmpl_id
                        and ccs.sale_group_id = rel.sale_group_id
                        and pc.id = pt.categ_id
                        and ccs.id = %s
                )A ''', (section_id,))
        datas = cr.fetchall()
        cr.execute
        return datas
    # get promotion datas from database    
    def get_promos_datas(self, cr, uid , branch_id, state, team_id, context=None, **kwargs):
        if state == 'approve':
            status = 'approve'
            cr.execute('''select distinct id,sequence as seq,from_date ,to_date,active,name as p_name,
                        logic ,expected_logic_result ,special, special1, special2, special3 ,description,
                        pr.promotion_count, pr.monthly_promotion ,code as p_code,manual,main_group,pr.ecommerce
                        from promos_rules pr
                        left join promos_rules_res_branch_rel pro_br_rel on (pr.id = pro_br_rel.promos_rules_id)
                        left join promos_rules_product_rel pro_pp_rel on (pr.id=pro_pp_rel.promos_rules_id)
                        where pr.active = true                     
                        and pro_br_rel.res_branch_id = %s
                        and pr.state = %s
                        and now()::date  between from_date::date and to_date::date
                        and pr.id in (
                            select a.promo_id from promo_sale_channel_rel a
                            inner join sale_team_channel_rel b
                            on a.sale_channel_id = b.sale_channel_id
                            where b.sale_team_id = %s
                        )
                        and pro_pp_rel.product_id in (
                            select product_id
                            from crm_case_section ccs,product_sale_group_rel rel
                            where ccs.sale_group_id=rel.sale_group_id
                            and ccs.id=%s
                        )
                        ''', (branch_id, status, team_id, team_id,))
        else:
            status = 'draft'            
            cr.execute('''select distinct id,sequence as seq,from_date ,to_date,active,name as p_name,
                        logic ,expected_logic_result ,special, special1, special2, special3 ,description,
                        pr.promotion_count, pr.monthly_promotion,code as p_code,manual,main_group,pr.ecommerce
                        from promos_rules pr
                        left join promos_rules_res_branch_rel pro_br_rel on (pr.id = pro_br_rel.promos_rules_id)
                        left join promos_rules_product_rel pro_pp_rel on (pr.id=pro_pp_rel.promos_rules_id)
                        where pr.active = true                     
                        and pro_br_rel.res_branch_id = %s
                        and pr.state  = %s
                        and now()::date between from_date::date and to_date::date
                        and pr.id in (
                            select a.promo_id from promo_sale_channel_rel a
                            inner join sale_team_channel_rel b
                            on a.sale_channel_id = b.sale_channel_id
                            where b.sale_team_id = %s
                        )
                        and pro_pp_rel.product_id in (
                            select product_id
                            from crm_case_section ccs,product_sale_group_rel rel
                            where ccs.sale_group_id=rel.sale_group_id
                            and ccs.id = %s
                        )
                        ''', (branch_id, status, team_id, team_id,))
        datas = cr.fetchall()        
        return datas
    
    def get_promos_act_datas(self, cr, uid , branch_id, promo_id, context=None, **kwargs):
        cr.execute('''select act.id,act.promotion,act.sequence as act_seq ,act.arguments,act.action_type,act.product_code,act.discount_product_code
                            from promos_rules r ,promos_rules_actions act,promos_rules_res_branch_rel pro_br_rel
                            where r.id = act.promotion
                            and r.active = 't'                            
                            and r.id = pro_br_rel.promos_rules_id
                            and pro_br_rel.res_branch_id = %s
                            and act.promotion = %s                    
                    ''', (branch_id, promo_id,))
        datas = cr.fetchall()
        cr.execute
        return datas
    
    def get_promos_cond_datas(self, cr, uid , branch_id, promo_id, context=None, **kwargs):
        cr.execute('''select cond.id,cond.promotion,cond.sequence as cond_seq,
                            cond.attribute as cond_attr,cond.comparator as cond_comparator,
                            cond.value as comp_value
                            from promos_rules r ,promos_rules_conditions_exps cond,promos_rules_res_branch_rel pro_br_rel
                            where r.id = cond.promotion
                            and r.active = 't'                           
                            and r.id = pro_br_rel.promos_rules_id
                            and pro_br_rel.res_branch_id = %s
                            and cond.promotion = %s  
                    ''', (branch_id, promo_id,))
        datas = cr.fetchall()
        cr.execute
        return datas
    
    def get_promos_joint_rules(self, cr, uid, branch_id, context=None, **kwargs):
        cr.execute('''
        select distinct prj.promos_rules_id,join_promotion_id from promos_rules pr,promos_rules_res_branch_rel rb ,promos_rules_join_rel prj 
        where
        pr.active=true and
        pr.monthly_promotion=true and
        pr.id=rb.promos_rules_id and 
        rb.promos_rules_id = pr.id and 
        rb.res_branch_id = %s''', (branch_id,))
        datas = cr.fetchall()
        return datas   

    def get_exclusive_promo_rules(self, cr, uid, branch_id, context=None, **kwargs):
        cr.execute('''
        select distinct pcl.partner_categ_id,pcl.promotion_id  from promos_rules pr ,partner_cate_rules_join_rel pcl ,promos_rules_res_branch_rel rb
        where
        pr.active=true and
        pr.id=rb.promos_rules_id and 
        rb.promos_rules_id = pr.id and 
        rb.res_branch_id = %s''', (branch_id,))
        datas = cr.fetchall()
        return datas   
        
    def get_promos_rule_partner_datas(self, cr, uid , context=None, **kwargs):
        cr.execute('''select category_id,rule_id from rule_partner_cat_rel''')
        datas = cr.fetchall()
        cr.execute
        return datas
    def get_promos_category_datas(self, cr, uid , context=None, **kwargs):
        cr.execute('''select id,name from res_partner_category''')
        datas = cr.fetchall()
        cr.execute
        return datas
    # get Mobile Sale Order Datas
    def get_mobile_so_datas(self, cr, uid, todayDateNormal, saleTeamId, saleorderList, context=None, **kwargs):
        saleOrderName = ', '.join(saleorderList) 
        print "sale", str(tuple(saleorderList))
        saleorder = str(tuple(saleorderList))
        mobile_sale_order_obj = self.pool.get('mobile.sale.order')
        list_val = None
        list_val = mobile_sale_order_obj.search(cr, uid, [('due_date', '>', todayDateNormal), ('sale_team', '=', saleTeamId), ('name', 'not in', saleorderList), ('type', '=', 'credit')])
        print 'list_val', list_val
        list = []
        if list_val:
            for val in list_val:
                cr.execute('select id,void_flag,name,create_date,date,partner_id,customer_code,sale_plan_trip_id,sale_plan_day_id,user_id,amount_total,type,delivery_remark,additional_discount,deduction_amount,paid_amount,paid,tablet_id,warehouse_id,location_id,sale_team,due_date,payment_term,mso_latitude,mso_longitude,remaining_amount,change_amount,net_amount from mobile_sale_order where id=%s', (val,))
                result = cr.fetchall()
                list.append(result)
                print' list', list
        return list
    # get Mobile Sale Order Line Datas
    def get_mobile_soline_datas(self, cr, uid, todayDateNormal, so_ids, context=None, **kwargs):
        print 'So_ids', so_ids
        order_ids = so_ids
#         order_ids = map(int, so_ids)
#         print 'Map Order Id',order_ids
        mobile_so_line_obj = self.pool.get('mobile.sale.order.line')
        list_val = None
        list_val = mobile_so_line_obj.search(cr, uid, [('create_date', '>', todayDateNormal), ('order_id', 'in', order_ids)])
        print 'list_val', list_val
        list = []
        if list_val:
            for val in list_val:
                cr.execute('select id,product_id,product_uos_qty,price_unit,discount,sub_total,order_id from mobile_sale_order_line where id=%s', (val,))
                result = cr.fetchall()
                list.append(result)
                print' list', list
        return list    

    def get_pricelist_datas(self, cr, uid , section_id, context=None, **kwargs):
        cr.execute('''select ppl.id,ppl.name,ppl.type, ppl.active , cpr.is_default,consumer
                 from price_list_line cpr , product_pricelist ppl
                 where ppl.id = cpr.property_product_pricelist 
                 and ppl.active = true
                 and cpr.team_id = %s''', (section_id,))
        datas = cr.fetchall()
        print 'Price List Data', datas
        return datas
    
    def get_pricelist_version_datas(self, cr, uid, pricelist_id, context=None, **kwargs):
        cr.execute('''select pv.id,date_end,date_start,pv.active,pv.name,pv.pricelist_id 
                        from product_pricelist_version pv, product_pricelist pp where pv.pricelist_id = pp.id   
                        and pv.active = true                                                         
                        and pv.pricelist_id = %s''', (pricelist_id,))
        datas = cr.fetchall()
        return datas
    
    def get_pricelist_item_datas(self, cr, uid, version_id, context=None, **kwargs):
        cr.execute('''select pi.id,pi.price_discount,pi.sequence,pi.product_tmpl_id,pi.name,pp.id base_pricelist_id,
                    pi.product_id,pi.base,pi.price_version_id,pi.min_quantity,
                    pi.categ_id,pi.new_price price_surcharge,pi.product_uom_id
                    from product_pricelist_item pi, product_pricelist_version pv, product_pricelist pp
                    where pv.pricelist_id = pp.id                             
                    and pv.id = pi.price_version_id
                    and pi.price_version_id = %s''', (version_id,))
        datas = cr.fetchall()        
        return datas

    def get_product_uoms(self, cr, uid , saleteam_id, context=None, **kwargs):
        cr.execute('''
                    select distinct uom_id,uom_name,ratio,template_id,product_id from(
                    select  pu.id as uom_id,pu.name as uom_name ,floor(round(1/factor,2)) as ratio,
                    pur.product_template_id as template_id,pp.id as product_id
                    from product_uom pu , product_template_product_uom_rel pur ,
                    product_product pp,
                    product_sale_group_rel rel,crm_case_section ccs
                    where pp.product_tmpl_id = pur.product_template_id
                    and rel.product_id = pp.id
                    and pu.id = pur.product_uom_id
                    and rel.sale_group_id=ccs.sale_group_id
                    and ccs.id = %s        
                )A''' , (saleteam_id,))
        datas = cr.fetchall()
        cr.execute
        return datas

    # Get Res Partner and Res Partner Category res_partner_res_partner_category_rel
    def get_res_partner_category_datas(self, cr, uid , context=None, **kwargs):
#         cr.execute('''
#         select a.category_id, a.partner_id ,b.name
#         from res_partner_res_partner_category_rel a , res_partner_category b
#         where a.category_id = b.id
#         ''')
        team_obj = self.pool.get('crm.case.section')
        cr.execute('''select default_section_id from res_users where id =%s''',(uid,))   
        sale_team_data=cr.fetchone() 
        if sale_team_data:
            sale_team_id =sale_team_data[0]
        else:
            sale_team_id=False
        team_data=team_obj.browse(cr, uid, sale_team_id, context=context)     
        section_id=  team_data.id                            
        is_supervisor=team_data.is_supervisor    
        if is_supervisor==True:
            cr.execute('''(select distinct a.category_id, a.partner_id ,(select name from res_partner_category where id = a.category_id) as name from res_partner_res_partner_category_rel a,
                     sale_plan_day_line b
                     , sale_plan_day p
                    where a.partner_id = b.partner_id
                    and b.line_id = p.id
                    and p.sale_team in (select id from crm_case_section where supervisor_team= %s)
                    )
                    UNION ALL
                    (select distinct a.category_id, a.partner_id ,(select name from res_partner_category where id = a.category_id) as name 
                    from res_partner_res_partner_category_rel a,sale_plan_trip p,
                     res_partner_sale_plan_trip_rel b
                    where a.partner_id = b.partner_id
                    and b.sale_plan_trip_id = p.id
                    and p.sale_team in (select id from crm_case_section where supervisor_team= %s))
                    UNION ALL
                    (select distinct a.category_id,a.partner_id,(select name from res_partner_category where id = a.category_id) as name 
                    from sale_order so,res_partner_res_partner_category_rel a
                    WHERE  a.partner_id = so.partner_id
                    AND so.pre_order = TRUE 
                    AND so.delivery_id in (select id from crm_case_section where supervisor_team= %s)
                    AND shipped = False
                    AND invoiced = False
                    AND ecommerce =TRUE)
                    ''', (section_id, section_id,section_id,))
            datas = cr.fetchall()     
        else:
            cr.execute('''(select distinct a.category_id, a.partner_id ,(select name from res_partner_category where id = a.category_id) as name from res_partner_res_partner_category_rel a,
             sale_plan_day_line b
             , sale_plan_day p
            where a.partner_id = b.partner_id
            and b.line_id = p.id
            and p.sale_team = %s
            )
            UNION ALL
            (select distinct a.category_id, a.partner_id ,(select name from res_partner_category where id = a.category_id) as name from res_partner_res_partner_category_rel a,sale_plan_trip p,
             res_partner_sale_plan_trip_rel b
            where a.partner_id = b.partner_id
            and b.sale_plan_trip_id = p.id
            and p.sale_team = %s
            )
            UNION ALL            
            (select distinct a.category_id,a.partner_id,(select name from res_partner_category where id = a.category_id) as name 
            from sale_order so,res_partner_res_partner_category_rel a
            WHERE  a.partner_id = so.partner_id
            AND so.pre_order = TRUE 
            AND so.delivery_id = %s
            AND shipped = False
            AND invoiced = False
            AND ecommerce =TRUE
            )            
            ''', (section_id, section_id,section_id,))
            datas = cr.fetchall()    
        return datas
    
    def get_sale_team_members_datas(self, cr, uid , member_id, saleteam_id, context=None, **kwargs):
        cr.execute('''select u.id as id,u.active as active,u.login as login,u.password as password,u.partner_id as partner_id,p.name as name from res_users u, res_partner p
                   where u.partner_id = p.id and u.id in(select member_id from crm_case_section cr, sale_member_rel sm where sm.section_id = cr.id and cr.id =%s)''', (saleteam_id,)) 
        datas = cr.fetchall()
        cr.execute
        return datas
    
    def sale_team_return(self, cr, uid, section_id , saleTeamId, context=None, **kwargs):
        cr.execute('''select DISTINCT cr.id,cr.complete_name,cr.warehouse_id,cr.name,sm.member_id,cr.code,rel.product_id,cr.location_id,cr.allow_foc,cr.allow_tax,cr.branch_id,state.name,cr_deli.name as delivery_team,cr.is_supervisor
                    from crm_case_section cr, sale_member_rel sm,product_sale_group_rel rel,res_country_state state,crm_case_section cr_deli
                    where sm.section_id = cr.id and cr.sale_group_id=rel.sale_group_id  
                    and state.id =cr.default_division 
                    and cr.delivery_team_id =cr_deli.id
                    and sm.member_id =%s
                    and cr.id = %s
            ''', (section_id, saleTeamId,))
        datas = cr.fetchall()
        cr.execute
        return datas
    
    
    def get_good_issue_note(self, cr, uid, section_id, context=None, **kwargs):
        cr.execute('''select count(*) from good_issue_note where issue_date::date=current_date and state ='issue' and sale_team_id=%s''', (section_id,))
        datas = cr.fetchall()
        return datas

    def getResPatrnerCategoryRel(self, cr, uid, section_id, context=None, **kwargs):
        
        cr.execute('''select * from res_partner_res_partner_category_rel''')
        datas = cr.fetchall()
        return datas       
       
    def sale_plan_day_return(self, cr, uid, section_id, pull_date , context=None, **kwargs):
        lastdate = datetime.strptime(pull_date, "%Y-%m-%d")
        print 'DateTime', lastdate
        section = self.pool.get('crm.case.section')
        sale_team_data = section.browse(cr, uid, section_id, context=context)
        is_supervisor=sale_team_data.is_supervisor
        if is_supervisor==True:
            cr.execute('''            
                select p.id,p.date,p.sale_team,p.name,p.principal,p.week from sale_plan_day p
                join  crm_case_section c on p.sale_team=c.id
                where p.sale_team in (select id from crm_case_section where supervisor_team= %s) and p.active = true        
                ''', (section_id,))
            datas = cr.fetchall()            
            
        else:
        
            cr.execute('''            
                select p.id,p.date,p.sale_team,p.name,p.principal,p.week from sale_plan_day p
                join  crm_case_section c on p.sale_team=c.id
                where p.sale_team=%s and p.active = true        
                ''', (section_id,))
            datas = cr.fetchall()
        return datas    
    
    def sale_plan_trip_return(self, cr, uid, section_id, pull_date , context=None, **kwargs):
        section = self.pool.get('crm.case.section')
        lastdate = datetime.strptime(pull_date, "%Y-%m-%d")
        print 'DateTime', lastdate
        sale_team_data = section.browse(cr, uid, section_id, context=context)
        is_supervisor=sale_team_data.is_supervisor 
        if is_supervisor==True:
            cr.execute('''            
                select distinct p.id,p.date,p.sale_team,p.name,p.principal from sale_plan_trip p
                ,crm_case_section c,res_partner_sale_plan_trip_rel d, res_partner e
                where  p.sale_team=c.id
                and p.sale_team in (select id from crm_case_section where supervisor_team= %s) 
                and p.active = true 
                and p.id = d.sale_plan_trip_id
                and e.id = d.partner_id            
                ''', (section_id,))
            datas = cr.fetchall()        
            
        else:
            cr.execute('''            
                select distinct p.id,p.date,p.sale_team,p.name,p.principal from sale_plan_trip p
                ,  crm_case_section c,res_partner_sale_plan_trip_rel d, res_partner e
                where  p.sale_team=c.id
                and p.sale_team= %s
                and p.active = true 
                and p.id = d.sale_plan_trip_id
                and e.id = d.partner_id            
                ''', (section_id,))
            datas = cr.fetchall()                      
        return datas
        
        # kzo
    def stock_picking_type(self, cr, uid , context=None, **kwargs):
        cr.execute('''select id,code from stock_picking_type''')            
        datas = cr.fetchall()        
        return datas
    
    def stock_move_return(self, cr, uid, section_id , context=None, **kwargs):
        cr.execute('''select id,product_qty,product_id,picking_id,state,origin,picking_type_id,location_dest_id,partner_id from stock_move where location_dest_id in(select cr.location_id from crm_case_section cr, sale_member_rel sm where sm.section_id = cr.id and sm.member_id=%s)
            ''', (section_id,))
        datas = cr.fetchall()        
        return datas
    
    def tablet_info(self, cr, uid, tabetId, context=None, **kwargs):    
        cr.execute('''
            select id as tablet_id,date,create_uid,name,note,mac_address,model,type,storage_day
            ,replace(hotline,',',';') hotline,sale_team_id,is_testing
            from tablets_information 
            where name = %s
            ''', (tabetId,))
        datas = cr.fetchall()
        return datas
    
    def get_company_datas(self, cr, uid , context=None):        
        cr.execute('''select id,name from res_company''')
        datas = cr.fetchall()        
        return datas
    
    def get_res_users(self, cr, uid, user_id , context=None, **kwargs):
        cr.execute('''
            
            select id,active,login,password,partner_id,branch_id ,
            (select uid from res_groups_users_rel where gid in (select id from res_groups  
            where name='Allow To Active') and uid=%s) allow_to_active,allow_collection_team,allow_product,allow_promotion,allow_customer,allow_sale_plan_day,
            allow_sale_plan_trip,allow_stock_request,allow_stock_exchange,allow_visit_record,allow_pending_delivery,allow_credit_collection,allow_daily_order_report,
            allow_daily_sale_report,allow_pre_sale,allow_direct_sale,allow_assets,allow_customer_location_update,allow_stock_check,allow_rental,allow_feedback,allow_customer_create,allow_customer_edit,allow_visit_photo_taken,is_burmart_team
            from res_users 
            where id = %s
            ''', (user_id,user_id,))
        datas = cr.fetchall() 
        print 'userdataaaaaaaaaaaaaaa',      datas 
        return datas

    
    def get_logout_password(self, cr, uid, section_id , password, context=None, **kwargs):
        cr.execute('''
            select id,password
            from tablet_logout_auth       
            where password = %s
            ''', (str(password),))
        datas = cr.fetchall()        
        return datas
        
    def check_account(self, cr, uid, login, pwd, sale_team_id, context=None, **kwargs):
        cr.execute('''
            select c.name as TabletName,D.userid,D.login,D.login_password from(
            select name,sale_team_id from tablets_information
            )C inner join(
            select A.userid,A.login,A.login_password,B.id as saleTeamId from(
            select id as userid,login,login_password from res_users
            )A inner join(
            select DISTINCT cr.id as id,cr.complete_name,cr.warehouse_id,cr.name,sm.member_id,cr.code,cr.location_id
                    from crm_case_section cr, sale_member_rel sm
                    where sm.section_id = cr.id
            ) B on A.userid = B.member_id
            )D on c.sale_team_id = D.saleTeamId
            where c.name = %s
            and D.login= %s
            and d.login_password = crypt(%s, login_password)
            ''', (sale_team_id, login, pwd,))
        datas = cr.fetchall()
        if datas:
            flag = True
        else:
            flag = False            
        return flag  
       
 # Create Sync for promotion line by kzo
    def create_promotion_line(self, cursor, user, vals, context=None):
        
        try : 
            mso_promotion_line_obj = self.pool.get('mso.promotion.line')
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
                
                    cursor.execute('select id From mobile_sale_order where name  = %s ', (pro_line['promo_line_id'],))
                    data = cursor.fetchall()
                    if data:
                        saleOrder_Id = data[0][0]
                    else:
                        saleOrder_Id = None
                    if pro_line['pro_id']:
                        cursor.execute("select manual from promos_rules where id=%s", (pro_line['pro_id'],))
                        manual = cursor.fetchone()[0]
                        if manual is not None:
                            manual = manual
                        else:
                            manual = False
                    else:
                        manual = False
                    promo_line_result = {
                        'promo_line_id':saleOrder_Id,
                        'pro_id':pro_line['pro_id'],
                        'from_date':pro_line['from_date'],
                        'to_date':pro_line['to_date'],
                        'manual':manual,
                        }
                    mso_promotion_line_obj.create(cursor, user, promo_line_result, context=context)
            return True
        except Exception, e:
            return False
    
    def create_dsr_notes(self, cursor, user, vals, context=None):
        print 'vals', vals
        try : 
            history_obj = self.pool.get('sales.denomination')
            notes_line_obj = self.pool.get('sales.denomination.note.line')
            deno_product_obj = self.pool.get('sales.denomination.product.line')
            cheque_product_obj = self.pool.get('sales.denomination.cheque.line')
            ar_coll_obj = self.pool.get('sales.denomination.ar.line')
            bank_transfer_obj = self.pool.get('sales.denomination.bank.line')
            credit_note_obj = self.pool.get('sales.denomination.credit.note.line')
            ar_obj = self.pool.get('ar.payment')
            inv_Obj = self.pool.get('account.invoice')
            invoice_obj = self.pool.get('account.invoice.line')
            Order_obj = self.pool.get('sale.order')
            Order_Lineobj = self.pool.get('sale.order.line')
            
            ar_amount = 0.0
            product_amount = 0.0
            deno_amount = 0.0
            cheque_amount = 0.0
            bank_amount = 0.0
            dssr_ar_amount = 0.0
            trans_amount = 0.0
            diff_amount = 0.0
            discount_amount = 0.0
            discount_total = 0.0
            invoice_sub_total = 0.0
            m_discount_total = 0.0
            m_discount_amount = 0.0
            v_discount_total = 0.0
            v_discount_amount = 0.0
            str = "{" + vals + "}"
            str = str.replace(":''", ":'")
            str = str.replace("'',", "',")
            str = str.replace(":',", ":'',")
            str = str.replace(":'}", ":''}")
            str = str.replace("}{", "}|{")
            
            new_arr = str.split('|')
            result = []
            for data in new_arr:
                x = ast.literal_eval(data)
                result.append(x)
           
            history = []
            notes_line = []
            
            for r in result:                
                if len(r) >= 7:
                    history.append(r)                   
                else:
                    notes_line.append(r)
            
            if history:
                print 'hidtory', history
                for pt in history:
                    
                    print 'dateImmmm',
                    de_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")          
                    if  de_date:
                        date = datetime.strptime(de_date, '%Y-%m-%d %H:%M:%S')
                        deno_date = date.date()
                    current_date = datetime.now() 
                    # + timedelta(hours=6.5)
                    cursor.execute("delete from sales_denomination where ((date at time zone 'utc') at time zone 'asia/rangoon')::date=%s and sale_team_id=%s and user_id=%s", (deno_date, pt['sale_team_id'], pt['user_id'],))
                    deno_result = {
                        'invoice_count':pt['invoice_count'],
                        'sale_team_id':pt['sale_team_id'],
                        'company_id':pt['company_id'] ,
                        'note':pt['note'],
                        'date': current_date,
                        'tablet_id':pt['tablet_id'],
                        'user_id':pt['user_id'],
                        'denomination_note_line':False,
                        'denomination_product_line':False,
                        'denomination_ar_line':False,
                        'denomination_cheque_line':False,
                        'denomination_bank_line':False,
                        'branch_id':pt['branch_id'],
                        'total_amount':0,
                        'diff_amount':0,
                        'product_amount':0,
                        'discount_amount':0,
                        'discount_total':0,
                        'invoice_sub_total':0,
                    }
                    deno_id = history_obj.create(cursor, user, deno_result, context=context)
                    for ptl in notes_line:
                                deno_amount += float(ptl['amount'])
                                note_line_res = {                                                            
                                  'denomination_note_ids':deno_id,
                                  'note_qty':ptl['note_qty'],
                                  'notes':ptl['notes'],
                                  'amount':ptl['amount'],
                                }
                                notes_line_obj.create(cursor, user, note_line_res, context=context)
                de_date = pt['date']
                user_id = pt['user_id']      
                pre_mobile_ids = []
                total_mobile_ids = []
                                
                mobile_ids = []
                mobile_sale_obj = self.pool.get('mobile.sale.order')        
                mobile_sale_order_obj = self.pool.get('mobile.sale.order.line')
                pre_sale_order_obj = self.pool.get('pre.sale.order.line')
                payment_obj = self.pool.get('customer.payment')
                cursor.execute("select default_section_id from res_users where id=%s", (user_id,))
                team_id = cursor.fetchone()[0]            
                print 'team_id', team_id, de_date
                cursor.execute("select id from customer_payment where date=%s and sale_team_id=%s and payment_code='CHEQ' ", (de_date, team_id,))
                payment_ids = cursor.fetchall()
                cursor.execute("select id from ar_payment where date=%s and sale_team_id=%s and payment_code='CHEQ' ", (de_date, team_id,))
                ar_payment_ids = cursor.fetchall()
                cursor.execute("select id from customer_payment where date=%s and sale_team_id=%s and payment_code='BNK' ", (de_date, team_id,))
                bank_ids = cursor.fetchall()
                cursor.execute("select id from customer_payment where date=%s and sale_team_id=%s and payment_code='CN' ", (de_date, team_id,))
                credit_note_ids = cursor.fetchall()
                cursor.execute("select id from ar_payment where date=%s and sale_team_id=%s and payment_code='CN' ", (de_date, team_id,))
                ar_credit_note_ids = cursor.fetchall()
                cursor.execute("select id from ar_payment where date=%s and sale_team_id=%s and payment_code='BNK' ", (de_date, team_id,))
                ar_bank_ids = cursor.fetchall()                              
                cursor.execute("select id from mobile_sale_order where due_date=%s and user_id=%s and m_status !='done' and void_flag != 'voided' and type='cash'", (de_date, user_id))
                m_mobile_ids = cursor.fetchall()
#                 cursor.execute("select id from account_invoice where date_invoice=%s and section_id =%s and state='open' and payment_type='cash' ", (de_date, team_id,))
#                 invoice_ids = cursor.fetchall()       
                cursor.execute("select order_id from pending_delivery pd,sale_order so where pd.order_id =so.id and so.payment_type ='cash' and pd.delivery_date=%s and pd.delivery_team_id =%s and pd.state='draft'  and pd.miss !=True ", (de_date, team_id,))
                invoice_ids = cursor.fetchall()                       
                if invoice_ids:
                    for data_pro in invoice_ids:
                        pre_mobile_ids.append(data_pro[0])
                if pre_mobile_ids:
                    # invoice_data = inv_Obj.search(cursor, user, [('id', 'in', tuple(pre_mobile_ids))], context=context)   
                    invoice_data = Order_obj.search(cursor, user, [('id', 'in', tuple(pre_mobile_ids))], context=context)   
                    for invoice_id in invoice_data:
                        invoice = Order_obj.browse(cursor, user, invoice_id, context=context)
                        deduct_amt = invoice.deduct_amt
                        amount_total = invoice.amount_total
                        deduct_percent = invoice.additional_discount / 100
                        discount_total += amount_total * deduct_percent
                        discount_amount += deduct_amt                    
                    # line_ids = invoice_obj.search(cursor, user, [('order_id', 'in', pre_mobile_ids)], context=context)         
                    line_ids = Order_Lineobj.search(cursor, user, [('order_id', 'in', pre_mobile_ids)], context=context)         
#                     order_line_ids = Order_Lineobj.browse(cursor, user, line_ids, context=context)         
#                     cursor.execute('select product_id,sum(product_uom_qty) as quantity,sum((product_uom_qty*price_unit)-discount_amt ) as  sub_total,product_uom from sale_order_line group by product_id,product_uom', (tuple(order_line_ids.ids),))
#                     order_line = cursor.fetchall()
                    for data in line_ids:
                        order_line_data = Order_Lineobj.browse(cursor, user, data, context=context)
                        product_id = order_line_data.product_id.id      
                        product_amount += order_line_data.price_subtotal
                        pre_qty = order_line_data.product_uom_qty
                        pre_p_uom = order_line_data.product_uom.id
                        product = self.pool.get('product.product').browse(cursor, user, product_id, context=context)
                        sequence = product.sequence
                        if pre_p_uom != product.product_tmpl_id.uom_id.id:                                                                          
                            cursor.execute("select floor(round(1/factor,2)) as ratio from product_uom where active = true and id=%s", (pre_p_uom,))
                            bigger_qty = cursor.fetchone()[0]
                            bigger_qty = int(bigger_qty)
                            pre_qty = bigger_qty * pre_qty         
                        data_id = {'product_id':product_id,
                                          'product_uom_qty':pre_qty,
                                          'denomination_product_ids':deno_id,
                                          'sequence':sequence,
                                          'amount':order_line_data.price_subtotal}
                        exit_data = deno_product_obj.search(cursor, user, [('denomination_product_ids', '=', deno_id), ('product_id', '=', product_id)], context=context)         
                        if exit_data:
                            cursor.execute("update sales_denomination_product_line set product_uom_qty = product_uom_qty + %s , amount = amount + %s where denomination_product_ids = %s and product_id =%s", (pre_qty, order_line_data.price_subtotal, deno_id, product_id,))
                        else:
                            deno_product_obj.create(cursor, user, data_id, context=context)                       
                cursor.execute("select id from account_invoice where date_invoice=%s and section_id =%s and state='open' and payment_type='cash' ", (de_date, team_id,))
                total_invoice_ids = cursor.fetchall()       
                if total_invoice_ids:
                    for data_pro in total_invoice_ids:
                        total_mobile_ids.append(data_pro[0])
                if total_mobile_ids:
                    invoice_data = inv_Obj.search(cursor, user, [('id', 'in', tuple(total_mobile_ids))], context=context)   
                    for invoice_id in invoice_data:
                        invoice = inv_Obj.browse(cursor, user, invoice_id, context=context)
                        deduct_amt = invoice.deduct_amt
                        amount_total = invoice.amount_untaxed
                        deduct_percent = invoice.additional_discount / 100
                        discount_total += amount_total * deduct_percent
                        discount_amount += deduct_amt                    
                    line_ids = invoice_obj.search(cursor, user, [('invoice_id', 'in', total_mobile_ids)], context=context)         
                    order_line_ids = invoice_obj.browse(cursor, user, line_ids, context=context)         
                    cursor.execute('select product_id,sum(quantity) as quantity,sum(quantity * price_unit) as  sub_total,uos_id from account_invoice_line where id in %s group by product_id,uos_id', (tuple(order_line_ids.ids),))
                    order_line = cursor.fetchall()
                    for data in order_line:
                        product = self.pool.get('product.product').browse(cursor, user, data[0], context=context)
                        sequence = product.sequence
                        product_amount += data[2]
                        pre_qty = data[1]
                        pre_p_uom = data[3]
                        if pre_p_uom != product.product_tmpl_id.uom_id.id:                                                                          
                            cursor.execute("select floor(round(1/factor,2)) as ratio from product_uom where active = true and id=%s", (pre_p_uom,))
                            bigger_qty = cursor.fetchone()[0]
                            bigger_qty = int(bigger_qty)
                            pre_qty = bigger_qty * pre_qty         
                        data_id = {'product_id':data[0],
                                          'product_uom_qty':pre_qty,
                                          'denomination_product_ids':deno_id,
                                          'sequence':sequence,
                                          'amount':data[2]}
                        exit_data = deno_product_obj.search(cursor, user, [('denomination_product_ids', '=', deno_id), ('product_id', '=', data[0])], context=context)         
                        if exit_data:
                            cursor.execute("update sales_denomination_product_line set product_uom_qty = product_uom_qty + %s , amount = amount + %s where denomination_product_ids = %s and product_id =%s", (pre_qty, data[2], deno_id, data[0],))
                        else:
                            deno_product_obj.create(cursor, user, data_id, context=context)                                         
                if  m_mobile_ids:
                    for data_mo in m_mobile_ids:
                        mobile_ids.append(data_mo[0])
                    mobile_data = mobile_sale_obj.browse(cursor, user, tuple(mobile_ids), context=context)           
                    for mobile in mobile_data:
                        deduct_amt = mobile.deduction_amount
                        amount_total = mobile.amount_total
                        deduct_percent = mobile.additional_discount
                        discount_total += amount_total * deduct_percent
                        discount_amount += deduct_amt                             
                    line_ids = mobile_sale_order_obj.search(cursor, user, [('order_id', 'in', mobile_ids)], context=context)                        
                    order_line_ids = mobile_sale_order_obj.browse(cursor, user, line_ids, context=context)                
                    cursor.execute('select product_id,sum(product_uos_qty) as qty ,sum(sub_total) as total ,uom_id from mobile_sale_order_line where id in %s group by product_id,uom_id', (tuple(order_line_ids.ids),))
                    order_line = cursor.fetchall()
                    for data in order_line:
                        product = self.pool.get('product.product').browse(cursor, user, data[0], context=context)
                        sequence = product.sequence
                        product_amount += data[2]
                        sale_qty = int(data[1])
                        product_uom = int(data[3])
                        if product_uom != product.product_tmpl_id.uom_id.id:                                                                          
                            cursor.execute("select floor(round(1/factor,2)) as ratio from product_uom where active = true and id=%s", (product_uom,))
                            bigger_qty = cursor.fetchone()[0]
                            bigger_qty = int(bigger_qty)
                            sale_qty = bigger_qty * sale_qty
                        data_id = {'product_id':data[0],
                                          'product_uom_qty':sale_qty,
                                          'denomination_product_ids':deno_id,
                                          'sequence':sequence,
                                          'amount':data[2]}
                        exit_data = deno_product_obj.search(cursor, user, [('denomination_product_ids', '=', deno_id), ('product_id', '=', data[0])], context=context)         
                        if exit_data:
                            cursor.execute("update sales_denomination_product_line set product_uom_qty = product_uom_qty + %s , amount = amount + %s where denomination_product_ids = %s and product_id =%s", (sale_qty, data[2], deno_id, data[0],))
                        else:
                            deno_product_obj.create(cursor, user, data_id, context=context)                                 
            if  payment_ids:
                for payment in payment_ids:
                    payment_data = payment_obj.browse(cursor, user, payment, context=context)                  
                    partner_id = payment_data.partner_id.id                    
                    journal_id = payment_data.journal_id.id
                    cheque_no = payment_data.cheque_no
                    amount = payment_data.amount
                    cheque_amount += payment_data.amount
                    data_id = {'partner_id':partner_id,
                                      'journal_id':journal_id,
                                      'cheque_no':cheque_no,
                                      'amount': amount,
                                    'denomination_cheque_ids':deno_id, }                    
                    cheque_product_obj.create(cursor, user, data_id, context=context)
            if  ar_payment_ids:
                for payment in ar_payment_ids:
                    payment_data = ar_obj.browse(cursor, user, payment, context=context)                  
                    partner_id = payment_data.partner_id.id
                    journal_id = payment_data.journal_id.id
                    cheque_no = payment_data.cheque_no
                    amount = payment_data.amount
                    cheque_amount += payment_data.amount
                    data_id = {'partner_id':partner_id,
                                      'journal_id':journal_id,
                                      'cheque_no':cheque_no,
                                      'amount': amount,
                                     'denomination_cheque_ids':deno_id,
                                      }
                    cheque_product_obj.create(cursor, user, data_id, context=context)
            if  bank_ids:
                for bank in bank_ids:
                    bank_data = payment_obj.browse(cursor, user, bank, context=context)                  
                    partner_id = bank_data.partner_id.id
                    journal_id = bank_data.journal_id.id
                    amount = bank_data.amount
                    bank_amount += bank_data.amount
                    data_id = {'partner_id':partner_id,
                                      'journal_id':journal_id,
                                      'amount': amount,
                                        'denomination_bank_ids':deno_id, }
                    bank_transfer_obj.create(cursor, user, data_id, context=context)
            if  credit_note_ids:
                for credit_note in credit_note_ids:
                    credit_note_data = payment_obj.browse(cursor, user, credit_note, context=context)                  
                    partner_id = credit_note_data.partner_id.id
                    cursor.execute('select id from account_creditnote where name = %s ', (credit_note_data.cheque_no,))
                    data = cursor.fetchall()
                    if data:
                        credit_note_id = data[0][0]
                    else:
                        credit_note_id = None
                    #creditnote_id = self.pool.get('account.creditnote').search(cursor, user, [('name', '=', credit_note_data.cheque_no)], context=context)
                    #creditnote_obj = self.pool.get('account.creditnote').browse(cursor, user, creditnote_id, context=context) 
                    #credit_note_id = creditnote_obj.id
                    amount = credit_note_data.amount                    
                    data_id = {'partner_id':partner_id,
                               'credit_note_id':credit_note_id,
                               'amount': amount,
                               'denomination_credit_note_ids':deno_id, }
                    credit_note_obj.create(cursor, user, data_id, context=context)
            if  ar_credit_note_ids:
                for credit_note in ar_credit_note_ids:
                    ar_credit_note_data = ar_obj.browse(cursor, user, credit_note, context=context)                  
                    partner_id = ar_credit_note_data.partner_id.id
                    cursor.execute('select id from account_creditnote where name = %s ', (ar_credit_note_data.cheque_no,))
                    data = cursor.fetchall()
                    if data:
                        ar_credit_note_id = data[0][0]
                    else:
                        ar_credit_note_id = None                    
#                     creditnote_id = self.pool.get('account.creditnote').search(cursor, user, [('name', '=', credit_note_data.cheque_no)], context=context)
#                     creditnote_obj = self.pool.get('account.creditnote').browse(cursor, user, creditnote_id, context=context) 
#                     credit_note_id = creditnote_obj.id
                    amount = ar_credit_note_data.amount                    
                    data_id = {'partner_id':partner_id,
                               'credit_note_id':ar_credit_note_id,
                               'amount': amount,
                               'denomination_credit_note_ids':deno_id, }
                    credit_note_obj.create(cursor, user, data_id, context=context)
            if  ar_bank_ids:
                for bank in ar_bank_ids:
                    bank_data = ar_obj.browse(cursor, user, bank, context=context)                  
                    partner_id = bank_data.partner_id.id
                    journal_id = bank_data.journal_id.id
                    amount = bank_data.amount
                    bank_amount += bank_data.amount
                    data_id = {'partner_id':partner_id,
                                      'journal_id':journal_id,
                                      'amount': amount,
                                        'denomination_bank_ids':deno_id, }
                    bank_transfer_obj.create(cursor, user, data_id, context=context)
            cursor.execute("""select m.date,a.id,m.partner_id,m.payment_amount
                                from account_invoice as a,mobile_ar_collection as m
                                where m.ref_no = a.number and  m.state='draft'  and
                                m.user_id=%s and m.sale_team_id=%s and m.date = %s  
                    """, (user_id, team_id, de_date,))
            vals = cursor.fetchall()             
            print 'vals', vals
            for val in vals:
                ar_amount += val[3]
                data_id = {'invoice_id':val[1],
                            'date':val[0],
                            'partner_id':val[2],
                            'amount':val[3],
                            'payment_type':'Credit',
                         'denomination_ar_ids':deno_id, }
                ar_coll_obj.create(cursor, user, data_id, context=context)
#             dssr_ar_amount=ar_amount+product_amount- discount_amount-discount_total
#             trans_amount= deno_amount + cheque_amount + bank_amount
#             diff_amount= (ar_amount+product_amount- discount_amount-discount_total)-( deno_amount + cheque_amount + bank_amount)             
#             invoice_sub_total=product_amount - discount_amount-discount_total
#             product_amount=product_amount-discount_amount-discount_total
#             print 'discount_total',discount_total,discount_amount
            cursor.execute("update sales_denomination set discount_total=%s,discount_amount =%s where id=%s",
                           (discount_total, discount_amount, deno_id,))
                         
            print 'True'
            return True       
        except Exception, e:
            return False
 
    def create_dsr_pdf_form(self, cursor, user, vals, context=None):
         try :
            print_obj = self.pool.get('tablet.pdf.print')
            str = "{" + vals + "}"
            str = str.replace("'',", "',")  # null
            str = str.replace(":',", ":'',")  # due to order_id
            str = str.replace("}{", "}|{")
            new_arr = str.split('|')
            result = []
            for data in new_arr:
                x = ast.literal_eval(data)
                result.append(x)
            print_line = []
            for r in result:                
                print_line.append(r)  
            if print_line:
                for print_date in print_line:
                    cursor.execute('select branch_id from crm_case_section where id=%s', (print_date['section_id'],))
                    branch_id = cursor.fetchone()[0]
                    cursor.execute("delete from tablet_pdf_print where print_fname = %s ", (print_date['print_fname'],))
                    print_result = {
                        'section_id':print_date['section_id'],
                        'user_id':user,
                        'print_date':datetime.now(),
                        'print_file':print_date['print_file'],
                        'print_fname':print_date['print_fname'],
                        'branch_id':branch_id,
                        }
                    print_obj.create(cursor, user, print_result, context=context)
            return True
         except Exception, e:
            return False       
    def create_ar_collection(self, cursor, user, vals, context=None):

        ar_obj = self.pool.get('mobile.ar.collection')
        str = "{" + vals + "}"
        str = str.replace("'',", "',")  # null
        str = str.replace(":',", ":'',")  # due to order_id
        str = str.replace("}{", "}|{")
        str = str.replace(":'}{", ":''}")    
        new_arr = str.split('|')
        result = []
        for data in new_arr:
            x = ast.literal_eval(data)
            result.append(x)
        ar_collection = []
        for r in result:
            print "length", len(r)
            ar_collection.append(r)  
        if ar_collection:
            for ar in ar_collection:            
                cursor.execute('select origin from account_invoice where number=%s', (ar['ref_no'].replace('\\', ""),))
                origin = cursor.fetchone()
                if origin:
                    origin = origin[0]
                else:
                    origin = None
                    
                invoice_no = ar['ref_no'].replace('\\', "")
                cursor.execute("select id,date_due,payment_term,date_invoice from account_invoice where number =%s", (invoice_no,))
                invoice = cursor.fetchone()
                if invoice:
                    invoice_id = invoice[0]
                    due_date = invoice[1]
                    payment_term = invoice[2]
                    invoice_date = invoice[3]
                else:
                    invoice_id = None
                    due_date = None
                    payment_term = None
                    invoice_date = None
                ar_result = {
                    'customer_code':ar['customer_code'],
                    'partner_id':ar['partner_id'],
                    'credit_limit':ar['credit_limit'],
                    'date':ar['date'] ,
                    'tablet_id':ar['tablet_id'],
                    'void_flag':ar['void_flag'],
                    'payment_amount':ar['payment_amount'],
                    'so_amount':ar['so_amount'],
                    'balance':ar['balance'],
                    'ref_no':ar['ref_no'].replace('\\', ""),
                    'invoice_id':invoice_id,
                    'so_ref':origin,
                    'sale_team_id':ar['sale_team_id'],
                    'user_id':ar['user_id'],
                    'state':'draft',
                     'due_date': due_date,
                    'payment_term':payment_term,
                    'invoice_date':invoice_date,
                    'latitude':ar['latitude'],
                    'longitude':ar['longitude'],
                }
                ar_obj.create(cursor, user, ar_result, context=context)
        return True
    
    def create_sale_rental(self, cursor, user, vals, context=None):
         try:
            rental_obj = self.pool.get('sales.rental')
            str = "{" + vals + "}"
            str = str.replace("'',", "',")  # null
            str = str.replace(":',", ":'',")  # due to order_id
            str = str.replace("}{", "}|{")
            str = str.replace(":'}{", ":''}")
            new_arr = str.split('|')
            result = []
            for data in new_arr:
                x = ast.literal_eval(data)
                result.append(x)
            rental_collection = []
            for r in result:
                rental_collection.append(r)  
            if rental_collection:
                for ar in rental_collection:            
                    cursor.execute('select id From res_partner where customer_code = %s ', (ar['partner_id'],))
                    data = cursor.fetchall()
                    if data:
                        partner_id = data[0][0]
                    else:
                        partner_id = None
                    import datetime
                    if ar['date']:
                        date = datetime.datetime.strptime(ar['date'], '%d-%m-%Y %H:%M:%S %p') - timedelta(hours=6, minutes=30)
                    from_date = datetime.datetime.strptime(ar['from_date'], '%d-%m-%Y')
                    to_date = datetime.datetime.strptime(ar['to_date'], '%d-%m-%Y')
                        #date = datetime.strptime( ar['date'], '%Y-%m-%d %H:%M:%S') - timedelta(hours=6, minutes=30)
                    
                    rental_result = {
                        'partner_id':partner_id,
                        'from_date':from_date.date(),
                        'date':date,                       
                        'to_date':to_date.date(),
                        'image':ar['image1'],
                        'image1':ar['image2'],
                        'image2':ar['image3'],
                        'image3':ar['image4'],
                        'image4':ar['image5'],
                        'note':ar['note'],
                        'company_id':ar['company_id'],
                        'month_cost':ar['monthy_amt'],
                        'rental_month':ar['month'],
                        'latitude':ar['latitude'],
                        'longitude':ar['longitude'],
                  #      'address':ar['address'],
                        'name':ar['name'],
                        'total_amt':ar['total_amt'],
                    }
                    rental_obj.create(cursor, user, rental_result, context=context)
            return True
         except Exception, e:
            print 'False'
            return False
        
    def get_credit_notes(self, cr, uid, sale_team_id , noteList ,context=None, **kwargs):
        team_obj = self.pool.get('crm.case.section')
        team_data=team_obj.browse(cr, uid, sale_team_id, context=context)
        if noteList:
            noteList = str(noteList)     
            noteList = noteList.replace("[", "(") 
            noteList = noteList.replace("]", ")")  
            where ='and ac.id NOT IN %s ' % (noteList,)
        else:
            where =''
            
        section_id=  team_data.id                            
        is_supervisor=team_data.is_supervisor           
        if is_supervisor==True:
            cr.execute('''            
                    select ac.id,ac.description,ac.name as cr_no,ac.used_date,
                    ac.issued_date,ac.terms_and_conditions,ac.amount,ac.so_no,
                    ac.m_status,ac.customer_id,ac.type,res.name as customer_name,res.customer_code,ac.ref_no,program.name as program,principal.name  as principal,ac.create_date,ac.approved_date
                     from account_creditnote ac,res_partner res,program_form_design program,product_maingroup principal
                    where ac.customer_id = res.id
                    and program.id =ac.program_id 
                    and ac.state = 'approved'
                    and ac.m_status='new'
                    and principal.id=ac.principle_id
                    %s
                    AND ac.customer_id IN  (
                   select partner_id from (
                    (select distinct b.partner_id from res_partner_res_partner_category_rel a,
                 sale_plan_day_line b
                 , sale_plan_day p
                where a.partner_id = b.partner_id
                and b.line_id = p.id
                and p.sale_team in (select id from crm_case_section where supervisor_team= %%s)
                )
                UNION ALL
                (select distinct b.partner_id from res_partner_res_partner_category_rel a,sale_plan_trip p,
                 res_partner_sale_plan_trip_rel b
                where a.partner_id = b.partner_id
                and b.sale_plan_trip_id = p.id
                and p.sale_team in (select id from crm_case_section where supervisor_team= %%s)
                )
                )a group by partner_id
                )
             '''%(where), (section_id,section_id,))

            datas=cr.fetchall()            
        else:
            cr.execute('''            
                             select ac.id,ac.description,ac.name as cr_no,ac.used_date,
                            ac.issued_date,ac.terms_and_conditions,ac.amount,ac.so_no,
                            ac.m_status,ac.customer_id,ac.type,res.name as customer_name,res.customer_code,ac.ref_no,program.name as program,principal.name  as principal,ac.create_date,ac.approved_date
                             from account_creditnote ac,res_partner res,program_form_design program,product_maingroup principal
                            where ac.customer_id = res.id
                            and program.id =ac.program_id 
                            and ac.state = 'approved'
                            and ac.m_status='new'
                            and principal.id=ac.principle_id
                            %s
                            AND ac.customer_id IN  (
                           select partner_id from (
                            (select distinct b.partner_id from res_partner_res_partner_category_rel a,
                             sale_plan_day_line b
                             , sale_plan_day p
                            where a.partner_id = b.partner_id
                            and b.line_id = p.id
                            and p.sale_team = %%s)
                            UNION ALL
                            (select distinct b.partner_id from res_partner_res_partner_category_rel a,sale_plan_trip p,
                             res_partner_sale_plan_trip_rel b
                            where a.partner_id = b.partner_id
                            and b.sale_plan_trip_id = p.id
                            and p.sale_team = %%s
                            )
                            )a group by partner_id
                            )
                     '''%(where), (section_id,section_id,))                
            datas=cr.fetchall()            
        return datas
    
    def get_target_setting(self, cr, uid, sale_team_id , context=None, **kwargs):
        section = self.pool.get('crm.case.section')      
        sale_team_data = section.browse(cr, uid, sale_team_id, context=context)
        is_supervisor=sale_team_data.is_supervisor    
        if is_supervisor==True:
            cr.execute('''            
                    select ARRAY_AGG(partner_id) as  partner_id from (
                   select partner_id from (
                    (select distinct b.partner_id from res_partner_res_partner_category_rel a,
                 sale_plan_day_line b
                 , sale_plan_day p
                where a.partner_id = b.partner_id
                and b.line_id = p.id
                and p.sale_team in (select id from crm_case_section where supervisor_team= %s)
                )
                UNION ALL
                (select distinct b.partner_id from res_partner_res_partner_category_rel a,sale_plan_trip p,
                 res_partner_sale_plan_trip_rel b
                where a.partner_id = b.partner_id
                and b.sale_plan_trip_id = p.id
                and p.sale_team in (select id from crm_case_section where supervisor_team= %s)
                )
                )a group by partner_id
                )b
             ''', (sale_team_id,sale_team_id))
            partner_data=cr.fetchone()
            if partner_data:
                partner_ids =partner_data[0]
                cr.execute('''select * from get_customer_target_multi_customer(%s)''', (partner_ids,))
                datas = cr.fetchall()
            
        else:
            cr.execute('''            
                   select ARRAY_AGG(partner_id) as  partner_id from (
                   select partner_id from (
                    (select distinct b.partner_id from res_partner_res_partner_category_rel a,
                     sale_plan_day_line b
                     , sale_plan_day p
                    where a.partner_id = b.partner_id
                    and b.line_id = p.id
                    and p.sale_team = %s)
                    UNION ALL
                    (select distinct b.partner_id from res_partner_res_partner_category_rel a,sale_plan_trip p,
                     res_partner_sale_plan_trip_rel b
                    where a.partner_id = b.partner_id
                    and b.sale_plan_trip_id = p.id
                    and p.sale_team = %s
                    )
                    )a group by partner_id
                    )b
             ''', (sale_team_id,sale_team_id))                
            partner_data=cr.fetchone()
            if partner_data:
                partner_ids =partner_data[0]
                cr.execute('''select * from get_customer_target_multi_customer(%s)''', (partner_ids,))
                datas = cr.fetchall()
        return datas    
    
    def insert_target_setting(self, cr, uid, sale_team_id ,customer_id, context=None, **kwargs):
        cr.execute("select * from insert_daily_customer_target_customer(%s)",(customer_id,))
        return True
    
    def get_target_setting_with_customer(self, cr, uid, sale_team_id ,customer_id, context=None, **kwargs):
        #cr.execute("select * from insert_daily_customer_target_customer(%s)",(customer_id,))
#         sale_team_data = section.browse(cr, uid, sale_team_id, context=context)
#         is_supervisor=sale_team_data.is_supervisor    
#         if is_supervisor==True:
#             cr.execute('''            
#                     select tl.id ,target.partner_id,tl.product_id,1 as product_uom,tl.ach_qty,tl.target_qty,gap_qty as gap,month1,month2,month3,COALESCE(target.ams_total,0) as ams_total,COALESCE(target.ams_buget_total,0) as ams_buget_total,target.month_out_todate,COALESCE(target.ams_balance,0) as ams_balance
#                     from customer_target target ,customer_target_line tl,product_sale_group_rel rel,crm_case_section ccs
#                     where target.id= tl.line_id
#                     and rel.product_id=tl.product_id
#                     and rel.sale_group_id=ccs.sale_group_id
#                     and ccs.id =%s
#                     and target.partner_id =%s
#                     and tl.target_qty > 0
#                     and target.partner_id in (
#                    select partner_id from (
#                     (select distinct b.partner_id from res_partner_res_partner_category_rel a,
#                  sale_plan_day_line b
#                  , sale_plan_day p
#                 where a.partner_id = b.partner_id
#                 and b.line_id = p.id
#                 and p.sale_team in (select id from crm_case_section where supervisor_team= %s)
#                 )
#                 UNION ALL
#                 (select distinct b.partner_id from res_partner_res_partner_category_rel a,sale_plan_trip p,
#                  res_partner_sale_plan_trip_rel b
#                 where a.partner_id = b.partner_id
#                 and b.sale_plan_trip_id = p.id
#                 and p.sale_team in (select id from crm_case_section where supervisor_team= %s)
#                 )
#                 )a group by partner_id
#                 )
#              ''', (sale_team_id,customer_id,sale_team_id,sale_team_id))  
#             
#         else:
#             cr.execute('''            
#                   
#                 select tl.id ,target.partner_id,tl.product_id,1 as product_uom,tl.ach_qty,tl.target_qty,gap_qty as gap,month1,month2,month3,COALESCE(target.ams_total,0) as ams_total,COALESCE(target.ams_buget_total,0) as ams_buget_total,target.month_out_todate,COALESCE(target.ams_balance,0) as ams_balance
#                     from customer_target target ,customer_target_line tl,product_sale_group_rel rel,crm_case_section ccs
#                     where target.id= tl.line_id
#                     and rel.product_id=tl.product_id
#                     and rel.sale_group_id=ccs.sale_group_id
#                     and ccs.id =%s
#                     and tl.target_qty > 0
#                     and target.partner_id =%s
#                     and target.partner_id in (
#                     select partner_id from (
#                     (select distinct b.partner_id from res_partner_res_partner_category_rel a,
#                      sale_plan_day_line b
#                      , sale_plan_day p
#                     where a.partner_id = b.partner_id
#                     and b.line_id = p.id
#                     and p.sale_team = %s)
#                     UNION ALL
#                     (select distinct b.partner_id from res_partner_res_partner_category_rel a,sale_plan_trip p,
#                      res_partner_sale_plan_trip_rel b
#                     where a.partner_id = b.partner_id
#                     and b.sale_plan_trip_id = p.id
#                     and p.sale_team = %s
#                     )
#                     )a group by partner_id
#                     )
#              ''', (sale_team_id,customer_id,sale_team_id,sale_team_id))                
#             datas = cr.fetchall()
        cr.execute('''select * from get_customer_target(%s)''', (customer_id,))
        datas = cr.fetchall()
        return datas

    def get_all_visit_reason(self, cr, uid, sale_team_id, context=None, **kwargs):
        cr.execute('''            
                select id,name,sequence,active from visit_reason
         ''')
        datas = cr.fetchall()
        return datas
    def get_stockcheck(self, cr, uid, sale_team_id , context=None, **kwargs):
        cr.execute('''            
                  select scl.id ,sc.outlet_type,scl.product_id,scl.product_uom_qty as quantity,scl.available,scl.facing, scl.chiller from stock_check_setting sc ,stock_check_setting_line scl where sc.id=scl.stock_setting_ids
         ''')
        datas = cr.fetchall()
        return datas

    def get_all_competitor_products(self, cr, uid, sale_team_id , context=None, **kwargs):
        cr.execute('''            
            select cp.id,cp.name,product_uom_id
            from crm_case_section ccs,sales_group sg,competitor_product_sales_group_rel prel,competitor_product cp,competitor_product_product_uom_rel rel
            where ccs.sale_group_id=sg.id
            and prel.sales_group_id=sg.id
            and prel.competitor_product_id=cp.id
            and cp.id=rel.competitor_product_id
            and ccs.id=%s
         ''', (sale_team_id,))
        datas = cr.fetchall()
        return datas

    def get_all_competitor_product_images(self, cr, uid, sale_team_id, context=None, **kwargs):
        list = []
        cr.execute('''            
            select competitor_product_id
            from crm_case_section ccs,sales_group sg,competitor_product_sales_group_rel rel
            where ccs.sale_group_id=sg.id
            and rel.sales_group_id=sg.id
            and ccs.id=%s
         ''', (sale_team_id,))
        datas = cr.fetchall()
        for data in datas:
            product = self.pool.get('competitor.product').browse(cr, uid, data[0], context=context)
            if product.image:
                product_data = [data[0], product.image]
                list.append(product_data)
        return list

    def get_product_id(self, cr, uid, sale_team_id, last_date, context=None):
        list = []
        # cr.execute('''select pt.id
        #               from product_template pt
        #               where pt.write_date > %s::timestamp
        #                             ''', (last_date,))

        cr.execute('''
                    select pt.id
                    from product_template pt,product_product pp,product_sale_group_rel rel, crm_case_section ccs  
                    where pp.id = rel.product_id and
                    pt.id = pp.product_tmpl_id and
                    pt.active = true and
                    pp.active = true and
                    ccs.sale_group_id = rel.sale_group_id and
                    ccs.id = %s and
                    pt.write_date > %s::timestamp 
        ''', (sale_team_id,last_date,))

    def get_customer_id(self, cr, uid, sale_team_id, last_date, context=None):
        datas = []
        cr.execute('''
                    select RP.id
                    from sale_plan_day SPD, sale_plan_day_line RPS, res_partner RP
                    where SPD.id = RPS.line_id
                    and RPS.partner_id = RP.id
                    and SPD.sale_team = %s
                    and RP.write_date > %s::timestamp
                    ''', (sale_team_id, last_date,))
        datas = cr.fetchall()
        return datas
    def udpate_credit_notes_issue_status(self, cr, uid, sale_team_id , context=None, **kwargs):
        try:
            cr.execute('''update account_creditnote set m_Status='new' where
                        sale_team_id = %s 
             ''', (sale_team_id,))
            return True
        except Exception, e:
            return False
    
    def create_partner_photo(self, cursor, user, vals, context=None):
        
        try:
            print 'vals', vals
            customer_photo_obj = self.pool.get('partner.photo')
            str = "{" + vals + "}"    
            str = str.replace("'',", "',")  # null
            str = str.replace(":',", ":'',")  # due to order_id
            str = str.replace("}{", "}|{")        
            str = str.replace(":'}{", ":''}")
            new_arr = str.split('|')
            result = []
            for data in new_arr:
                x = ast.literal_eval(data)
                result.append(x)
            customer_photo = []
            for r in result:  
                customer_photo.append(r)
            if customer_photo:
                for vs in customer_photo:
                    customer_id =False
                    code = vs['customer_code']                                
                    cursor.execute('''select id from res_partner where id =%s''',(vs['customer_id'],))
                    customer_data=cursor.fetchone() 
                    if customer_data:
                        customer_id =customer_data[0]
                    else:
                        cursor.execute('''select id from res_partner where customer_code =%s''',(vs['customer_code'],))
                        customer_code_data=cursor.fetchone()      
                        if customer_code_data:
                            customer_id=customer_code_data[0]
                    latitude=0
                    longitude=0
                    if vs['latitude']!='null':
                        latitude=vs['latitude']
                    if vs['longitude'] !='null':
                        longitude= vs['longitude']          
                    result = {
                        'customer_code':vs['customer_code'],
                        'customer_id':customer_id,
                        'comment':vs['comment'],
                        'partner_latitude':latitude,
                        'partner_longitude':longitude,
                        'image_one':vs['image_one'].replace('\\', ""),
                        'image_two':vs['image_two'].replace('\\', ""),
                        'image_three':vs['image_three'].replace('\\', ""),
                        'image_four':vs['image_four'].replace('\\', ""),
                        'image_five':vs['image_five'].replace('\\', "")
                    }
                    customer_photo_obj.create(cursor, user, result, context=context)                
                                                                  
                    # For Custoemr Photo temp table to Res Parnter Table for Appear
                    cursor.execute('''select customer_code,image_one,image_two,image_three,image_four,
                            image_five,comment,partner_latitude,partner_longitude From partner_photo where customer_code = %s''', (code,))
                    data = cursor.fetchall()
                    for r in data:
                        code = r[0]
                        print 'customer id', code
                        cursor.execute('''update res_partner set image_one = %s, image_two = %s,
                        image_three = %s, image_four = %s, image_five = %s, comment = %s,partner_latitude=%s,partner_longitude=%s where customer_code = %s'''
                        , (r[1], r[2], r[3], r[4], r[5]
                        , r[6],r[7],r[8], code,))
                        cursor.execute('''delete from partner_photo where customer_code = %s''', (vs['customer_code'],))
            return True
        except Exception, e:
            print e
            return False
                
#     def udpate_credit_notes_used_status(self, cr, uid, sale_team_id , usedList, context=None, **kwargs):
#         try:
#             crnote = tuple(usedList)
#             note_order_obj = self.pool.get('account.creditnote')
#             list_val = None
#             list_val = note_order_obj.search(cr, uid, [('sale_team_id', '=', sale_team_id), ('m_status', '=', 'issued'), ('name', 'in', usedList)])            
#             print'credit id', list_val
#             for note_id in list_val:
#                 print'Note id', note_id
#                 cr.execute("""update account_creditnote set m_status ='used' where id = %s""", (note_id,))
#             return True
#         except Exception, e:
#             return False
    
    def get_branch_datas(self, cr, uid , context=None):        
        cr.execute('''select id,name,branch_code from res_branch where active = true''')
        datas = cr.fetchall()        
        return datas
    
    def get_sale_channel(self, cr, uid , context=None):        
        cr.execute('''select id,name from sale_channel''')
        datas = cr.fetchall()        
        return datas
        
    def get_payment_term(self, cr, uid , context=None):        
        cr.execute('''select id,name from account_payment_term where active = true''')
        datas = cr.fetchall()        
        return datas
    
    def get_promo_sale_channel(self, cr, uid , context=None):        
        cr.execute('''select rel.promo_id,rel.sale_channel_id from promo_sale_channel_rel rel,promos_rules rule where rule.id =rel.promo_id  and now()::date between from_date::date and to_date::date''')
        datas = cr.fetchall()        
        return datas    
    
#     def get_sale_team_channel(self, cr, uid, sale_team_id , context=None, **kwargs):    
#         cr.execute("""select sale_team_id,sale_channel_id from sale_team_channel_rel
#                         where sale_team_id = %s """, (sale_team_id,))                
#         datas = cr.fetchall()
#         return datas
    def get_sale_team_channel(self, cr, uid, sale_team_id , context=None, **kwargs):
        cr.execute("""select sale_team_id,sale_channel_id from sale_team_channel_rel rel,sale_channel c where rel.sale_team_id =%s  and c.id =rel.sale_channel_id order by c.create_date,c.name desc """, (sale_team_id,))
        datas = cr.fetchall()
        return datas

    def get_report_link(self, cr, uid, context=None, **kwargs):    
        cr.execute("""select value from ir_config_parameter where key ='quick_sight_report_link' """)
        datas = cr.fetchall()        
        return datas
    
    def get_suv_report_link(self, cr, uid, context=None, **kwargs):    
        cr.execute("""select value from ir_config_parameter where key ='quick_sight_report_link_sv_team' """)
        datas = cr.fetchall()        
        return datas

    def get_customer_visit_distance(self, cr, uid, context=None, **kwargs):
        cr.execute("""select value from ir_config_parameter where key ='customer_visit_distance' """)
        datas = cr.fetchall()
        return datas
    def get_uom(self, cr, uid, context=None, **kwargs):    
        cr.execute("""select id,name,floor(round(1/factor,2))  as ratio from product_uom where active = true""")
        datas = cr.fetchall()
        print 'Product UOM', datas
        return datas
    
    def get_asset_type(self, cr, uid, context=None, **kwargs):    
        cr.execute("""select conf.id,conf.name,type.name as asset_type,is_auto_fill,type,conf.active,type.active from asset_configuration conf ,asset_type type where conf.asset_type_id=type.id""")
        datas = cr.fetchall()        
        return datas
    
    def get_assets(self, cr, uid, context=None, **kwargs):    
        team_obj = self.pool.get('crm.case.section')
        cr.execute('''select default_section_id from res_users where id =%s''',(uid,))   
        sale_team_data=cr.fetchone() 
        if sale_team_data:
            sale_team_id =sale_team_data[0]
        else:
            sale_team_id=False
        team_data=team_obj.browse(cr, uid, sale_team_id, context=context)     
        section_id=  team_data.id                            
        is_supervisor=team_data.is_supervisor           
        if is_supervisor==True:
            cr.execute('''            
                    select A.name as id ,(C.name) as asset_name,A.partner_id,substring(encode(image::bytea, 'hex'),1,5) as image
                            ,A.qty,A.date,B.name,A.type,A.id as asset_db_id
                            from res_partner_asset A, asset_type B ,asset_configuration C
                            where A.asset_type = B.id
                            and A.active=True
                            and A.asset_name_id=C.id                             
                            and C.active=True                            
                    AND A.partner_id IN  (
                   select partner_id from (
                    (select distinct b.partner_id from res_partner_res_partner_category_rel a,
                 sale_plan_day_line b
                 , sale_plan_day p
                where a.partner_id = b.partner_id
                and b.line_id = p.id
                and p.sale_team in (select id from crm_case_section where supervisor_team= %s)
                )
                UNION ALL
                (select distinct b.partner_id from res_partner_res_partner_category_rel a,sale_plan_trip p,
                 res_partner_sale_plan_trip_rel b
                where a.partner_id = b.partner_id
                and b.sale_plan_trip_id = p.id
                and p.sale_team in (select id from crm_case_section where supervisor_team= %s)
                )
                )a group by partner_id
                )
             ''', (section_id,section_id,))
            datas=cr.fetchall()            
        else:
            cr.execute('''            
                           select A.name as id ,(C.name) as asset_name,A.partner_id,substring(encode(image::bytea, 'hex'),1,5) as image
                            ,A.qty,A.date,B.name,A.type,A.id as asset_db_id
                            from res_partner_asset A, asset_type B ,asset_configuration C
                            where A.asset_type = B.id
                            and A.active=True 
                            and A.asset_name_id=C.id      
                            and C.active=True                            
                            AND A.partner_id IN  (
                           select partner_id from (
                            (select distinct b.partner_id from res_partner_res_partner_category_rel a,
                             sale_plan_day_line b
                             , sale_plan_day p
                            where a.partner_id = b.partner_id
                            and b.line_id = p.id
                            and p.sale_team = %s)
                            UNION ALL
                            (select distinct b.partner_id from res_partner_res_partner_category_rel a,sale_plan_trip p,
                             res_partner_sale_plan_trip_rel b
                            where a.partner_id = b.partner_id
                            and b.sale_plan_trip_id = p.id
                            and p.sale_team = %s
                            )
                            )a group by partner_id
                            )
                     ''', (section_id,section_id,))                
            datas=cr.fetchall()            
        return datas
        
    # Get Pending Delivery
    def get_delivery_datas(self, cr, uid, saleTeamId, soList, context=None, **kwargs):
        
        sale_order_obj = self.pool.get('sale.order')
        list_val = None
        if soList:
            for list in range(len(soList)):
                content = soList[list]
                if 'EC-SONo' in content:
                    content = content.replace('EC-SONo', 'EC-SONo/')
                    content = content[:-9] + "/" + content[-9:]
                    soList[list] = content

        list_val = sale_order_obj.search(cr, uid, [('pre_order', '=', True), ('is_generate', '=', True),('state', '=', 'manual'), ('delivery_id', '=', saleTeamId), ('shipped', '=', False), ('invoiced', '=', False) , ('tb_ref_no', 'not in', soList)], context=context)
        print 'list_val', list_val
        list = []
        try:
            if list_val:
                for So_id in list_val:
                    print 'Sale Order Id', So_id
                    cr.execute('''select so.id,so.date_order,so.partner_id,so.amount_tax,so.amount_untaxed,
                    so.payment_term,so.company_id,so.pricelist_id,so.user_id,so.amount_total,replace(so.tb_ref_no,'/','') as invoice_no,
                    so.warehouse_id,so.shipped,so.sale_plan_day_id,so.sale_plan_name,so.so_longitude,so.payment_type,
                    so.due_date,so.sale_plan_trip_id,so.so_latitude,so.customer_code,so.name as so_refNo,so.total_dis,so.deduct_amt,so.coupon_code,
                    so.invoiced,so.branch_id,so.delivery_remark ,team.name,so.payment_term,so.due_date,so.rebate_later,
                    rp.name customer_name,replace(so.note,',',';') as note,so.woo_order_id,so.ecommerce ,so.delivery_township_id ,rt.name as township_name,replace(so.delivery_address,',',';') delivery_address ,replace(so.delivery_contact_no,',',';') delivery_contact_no
                    from sale_order so, crm_case_section team,res_partner rp,res_township rt                                  
                    where so.id= %s and so.state!= 'cancel'
                    and  team.id = so.section_id
                    and  so.partner_id = rp.id
                    and rt.id =so.delivery_township_id
                    ''', (So_id,))
                    result = cr.fetchall()
                    print 'Result Sale Order', result
                    list.append(result)
                    print' list', list
            return list
        except Exception, e:
            return False
    
    def get_delivery_line_datas(self, cr, uid, so_ids, context=None, **kwargs):
        print 'So_ids', so_ids
        order_ids = so_ids
        so_line_obj = self.pool.get('sale.order.line')
        list_val = None
        list_val = so_line_obj.search(cr, uid, [('order_id', 'in', order_ids)])
        print 'list_val', list_val
        list = []
        if list_val:
            for val in list_val:
                cr.execute('''select so.id,so.product_id,so.product_uom_qty,so.product_uom,so.price_unit,so.order_id,
                            so.discount,so.discount_amt ,pp.sequence,floor(round(1/pu.factor,2)) as smaller_qty,default_code,name_template,promotion_id
                            from sale_order_line so,product_product pp,product_uom pu        
                             where so.id = %s 
                            and  so.product_id = pp.id
                            and so.product_uom=pu.id''', (val,))
                result = cr.fetchall()
                list.append(result)
                print' list', list
        return list
    
    
    def update_deliver_sale_order(self, cr, uid, saleorderList, context=None):
         
            context = {'lang':'en_US', 'params':{'action':458}, 'tz': 'Asia/Rangoon', 'uid': 1}
            soObj = self.pool.get('sale.order')        
            invObj = self.pool.get("sale.advance.payment.inv")
            invoiceObj = self.pool.get('account.invoice')                
            stockPickingObj = self.pool.get('stock.picking')
            stockDetailObj = self.pool.get('stock.transfer_details')        
            partner_obj = self.pool.get('res.partner')
            pending_obj = self.pool.get('pending.delivery')
            pending_ids = []            
            str = "{" + saleorderList + "}"    
            str = str.replace("'',", "',")  # null
            str = str.replace(":',", ":'',")  # due to order_id
            str = str.replace("}{", "}|{")
            str = str.replace(":'}{", ":''}")
            new_arr = str.split('|')
            result = []
            for data in new_arr:            
                x = ast.literal_eval(data)                
                result.append(x)
            deliver_data = []
            for r in result:
                deliver_data.append(r)  
            if deliver_data:
                
                for deli in deliver_data:       
                    print 'Missssssssssssssssss', deli['miss'], deli
                    so_ref_no = deli['so_refNo'].replace('\\', '').replace('\\', '')          
                    print 'so_ref_noso_ref_no', so_ref_no
                    if deli['miss'] == 't':
                        So_id = soObj.search(cr, uid, [('pre_order', '=', True), ('shipped', '=', False), ('invoiced', '=', False)
                                                       , ('name', '=', so_ref_no)], context=context)    
                        so_data = soObj.browse(cr, uid, So_id, context=context)
                        delivery_team_id = so_data.delivery_id.id
                        delivery = {                                                            
                                  'order_id':So_id[0],
                                  'miss':True,
                                  'is_revised':False,
                                  'delivery_date':datetime.now(),
                                  'due_date':deli['due_date'],
                                  'state':'done',
                                  'delivery_team_id': delivery_team_id ,
                                 'latitude':deli['mosLatitude'],
                                  'longitude':deli['mosLongitude']    
                            }
                        pending_obj.create(cr, uid, delivery, context=context)
                        cr.execute('update sale_order set is_generate = false,is_missed=True, due_date = %s where id=%s', (deli['due_date'],So_id[0],))                                           
                    else:   
                        confirm_date=False                         
                        So_id = soObj.search(cr, uid, [('pre_order', '=', True), ('shipped', '=', False), ('invoiced', '=', False)
                                                       , ('name', '=', so_ref_no)], context=context)
                        so_data = soObj.browse(cr, uid, So_id, context=context)
                        delivery_team_id = so_data.delivery_id.id        
                        if  deli['confirm_date']:
                            #confirm_date=deli['confirm_date']
                            cr.execute ("select timestamp%s - '7 hour'::interval + '30 minutes'::interval",(deli['confirm_date'],))
                            confirm_date =cr.fetchone()[0]
                        if deli.get('payment_ref'): 
                            payment_ref=deli['payment_ref']
                        else:
                            payment_ref=None                 
                        delivery = {                                                            
                                  'order_id':So_id[0],
                                  'miss':False,
                                  'is_revised':False,
                                  'due_date':deli['due_date'],
                                  'delivery_date':datetime.now(),
                                  'confirm_date':confirm_date,
                                  'state':'draft',
                                  'delivery_team_id': delivery_team_id ,
                                  'latitude':deli['mosLatitude'],
                                  'longitude':deli['mosLongitude'],  
                                  'payment_ref':payment_ref                           
                            }
                        pending_id = pending_obj.create(cr, uid, delivery, context=context)                                                                                                                                 
                        pending_ids.append(pending_id)
            session = ConnectorSession(cr, uid, context)
            # jobid=pending_obj.create_automation_pending_delivery(cr, uid, pending_ids, context=context)       
            jobid = automation_pending_delivery.delay(session, pending_ids, priority=50)
            runner = ConnectorRunner()
            runner.run_jobs()
            return True                                                                    
#     def update_deliver_sale_order(self, cr, uid, saleorderList, context=None):
#          
#             context = {'lang':'en_US', 'params':{'action':458}, 'tz': 'Asia/Rangoon', 'uid': 1}
#             soObj = self.pool.get('sale.order')        
#             invObj = self.pool.get("sale.advance.payment.inv")
#             invoiceObj = self.pool.get('account.invoice')                
#             stockPickingObj = self.pool.get('stock.picking')
#             stockDetailObj = self.pool.get('stock.transfer_details')        
#             partner_obj = self.pool.get('res.partner')
#             pending_obj =self.pool.get('pending.delivery')
#             
#             str = "{" + saleorderList + "}"    
#             str = str.replace("'',", "',")  # null
#             str = str.replace(":',", ":'',")  # due to order_id
#             str = str.replace("}{", "}|{")
#             str = str.replace(":'}{", ":''}")
#             new_arr = str.split('|')
#             result = []
#             for data in new_arr:            
#                 x = ast.literal_eval(data)                
#                 result.append(x)
#             deliver_data = []
#             for r in result:
#                 deliver_data.append(r)  
#             if deliver_data:
#                 
#                 for deli in deliver_data:       
#                     print 'Missssssssssssssssss', deli['miss'], deli
#                     so_ref_no = deli['so_refNo'].replace('\\', '').replace('\\', '')          
#                     print 'so_ref_noso_ref_no', so_ref_no
#                     if deli['miss'] == 't':
#                         cr.execute('update sale_order set is_generate = false, due_date = %s where name=%s', (deli['due_date'], so_ref_no,))
#                         cr.execute('select tb_ref_no from sale_order where name=%s', (so_ref_no,))
#                         ref_no = cr.fetchone()[0]
#                         cr.execute("update pre_sale_order set void_flag = 'voided' where name=%s", (ref_no,))
#                         pending_obj.create
#                     else:                            
#                         So_id = soObj.search(cr, uid, [('pre_order', '=', True), ('shipped', '=', False), ('invoiced', '=', False)
#                                                        , ('name', '=', so_ref_no)], context=context)
#                         if So_id:
#                             solist = So_id                               
#                             cr.execute('select branch_id,section_id,delivery_remark from sale_order where name=%s', (so_ref_no,))
#                             data = cr.fetchone()
#                             if data:
#                                 branch_id = data[0]
#                                 section_id = data[1]
#                                 delivery_remark = data[2]
# 
#                             cr.execute('select delivery_team_id from crm_case_section where id=%s', (section_id,))
#                             delivery = cr.fetchone()
#                             if delivery:
#                                 delivery_team_id = delivery[0]
#                             else:
#                                 delivery_team_id = None
#                             
#                             # For DO
#                             stockViewResult = soObj.action_view_delivery(cr, uid, So_id, context=context)    
#                             if stockViewResult:
#                                 # stockViewResult is form result
#                                 # stocking id =>stockViewResult['res_id']
#                                 # click force_assign
#                                 stockPickingObj.force_assign(cr, uid, stockViewResult['res_id'], context=context)
#                                 # transfer
#                                 # call the transfer wizard
#                                 # change list
#                                 pickList = []
#                                 pickList.append(stockViewResult['res_id'])
#                                 wizResult = stockPickingObj.do_enter_transfer_details(cr, uid, pickList, context=context)
#                                 # pop up wizard form => wizResult
#                                 detailObj = stockDetailObj.browse(cr, uid, wizResult['res_id'], context=context)
#                                 if detailObj:
#                                     detailObj.do_detailed_transfer()    
#                                 print 'testing---------------',
#                             # Create Invoice
#                             print 'Context', context
#                             invoice_id = self.create_invoices(cr, uid, solist, context=context)
#                             print ' invoice_id', invoice_id
#                             # id update partner form (temporay)
# #                             partner_data = invoiceObj.browse(cr, uid, invoice_id, context=context)
# #                             partner_id=partner_data.partner_id.id
# #                             partner_obj.write(cr,uid,partner_id,{'property_account_receivable':629}, context)
# #                             partner = partner_obj.browse(cr, uid, partner_id, context=context)
# #                             account_id=partner.property_account_receivable.id
# #                             invoiceObj.write(cr,uid,invoice_id,{'account_id':account_id}, context)
#                             cr.execute('update account_invoice set date_invoice = now()::date , branch_id =%s ,payment_type=%s,delivery_remark =%s ,section_id=%s,user_id=%s, payment_term = %s where id =%s', (branch_id, deli['payment_type'], delivery_remark, delivery_team_id, uid, deli['payment_term'], invoice_id))                                                
#                                                         
#                             invoiceObj.button_reset_taxes(cr, uid, [invoice_id], context=context)
#                             if invoice_id:
# #                                 invlist = []
# #                                 invlist.append(invoice_id)
# #                                 # call the api function
# #                                 # invObj contain => account.invoice(1,) like that
# #                                 print 'invoice_id', invoice_id
# #                                  
# #                                 invObj = invoiceObj.browse(cr, uid, invlist, context=context)
# #                                 
# #                                 #                                                                                                                            
# #                                 invObj.action_date_assign()
# #                                 invObj.action_move_create()
# #                                 invObj.action_number()
# #                                 # validate invoice
# #                                 invObj.invoice_validate()
#                                 self.pool['account.invoice'].signal_workflow(cr, uid, [invoice_id], 'invoice_open')
# 
#                                 # pre_order =True
#                                 invoiceObj.write(cr, uid, invoice_id, {'pre_order':True}, context)                                                                                                                             
#                                                                         
#             return True 
          
    def cancel_deliver_order(self, cr, uid, saleorderList, context=None):
         
            context = {'lang':'en_US', 'params':{'action':458}, 'tz': 'Asia/Rangoon', 'uid': 1}
            soObj = self.pool.get('sale.order')            
            
            str = "{" + saleorderList + "}"    
            str = str.replace("'',", "',")  # null
            str = str.replace(":',", ":'',")  # due to order_id
            str = str.replace("}{", "}|{")
            str = str.replace(":'}{", ":''}")
            new_arr = str.split('|')
            result = []
            for data in new_arr:            
                x = ast.literal_eval(data)                
                result.append(x)
            deliver_data = []
            for r in result:
                deliver_data.append(r)  
            if deliver_data:
                
                for deli in deliver_data:            

                    so_ref_no = deli['so_refNo'].replace('\\', '').replace('\\', '')          
                    So_id = soObj.search(cr, uid, [('pre_order', '=', True), ('shipped', '=', False), ('invoiced', '=', False)
                                                   , ('name', '=', so_ref_no)], context=context)
                    if So_id:
                        print 'Sale Order Id', So_id[0]
                        if deli['revised'] == 'true':
                            is_revised =True
                        else :
                            is_revised=False
                        if deli['cancel_reason_id'] != 'null' and deli['cancel_reason_id']:
                            cancel_reason_id = deli['cancel_reason_id']
                        else :
                            cancel_reason_id=None
                        if deli['revise_reason_id'] != 'null' and deli['revise_reason_id']:
                            revise_reason_id = deli['revise_reason_id']
                        else :
                            revise_reason_id=None
                                                                             
                        cr.execute('''update sale_order set state ='cancel',cancel_user_id=%s,is_revised=%s,cancel_reason_id=%s,revise_reason_id=%s where id = %s ''', (uid,is_revised,cancel_reason_id,revise_reason_id, So_id[0],))
                        cr.execute('select tb_ref_no from sale_order where id=%s', (So_id[0],))
                        ref_no = cr.fetchone()[0]
                        cr.execute("update pre_sale_order set void_flag = 'voided' where name=%s", (ref_no,))        
                        woo_instance_obj=self.pool.get('woo.instance.ept')
                        instance=woo_instance_obj.search(cr, uid, [('state','=','confirmed')], context=context, limit=1)
                        if instance:                
                            woo_instance = woo_instance_obj.browse(cr, uid, instance[0], context=context)
                            wcapi = woo_instance.connect_for_point_in_woo()   
                        for sale in soObj.browse(cr, uid, So_id[0], context=context):                
                            if sale.woo_order_number:
                                update = sale.update_woo_order_status_action('cancelled')
                                one_signal_values = {
                                                        'partner_id': sale.partner_id.id,
                                                        'contents': "Your order " + sale.name + " is cancelled.",
                                                        'headings': "Burmart"
                                                    }     
                                self.pool.get('one.signal.notification.messages').create(cr, uid, one_signal_values, context=context)
                            if sale.getting_point > 0:
                                getting_point = -sale.getting_point
                                sale.write({'getting_point':getting_point})
                                cr.execute("select COALESCE(sum(getting_point),0) from point_history where partner_id=%s", (sale.partner_id.id,))    
                                point_data = cr.fetchall()
                                if point_data:
                                    history_point = point_data[0][0]
                                vals = { 'partner_id': sale.partner_id.id,
                                         'date': datetime.today(),
                                         'order_id': sale.id,
                                         'membership_id': sale.partner_id.membership_id.id,                                                      
                                         'balance_point': history_point + sale.getting_point,
                                         'getting_point': sale.getting_point,
                                        }
                                self.pool.get('point.history').create(cr, uid, vals, context=context)
                                if wcapi:
                                    order_response = wcapi.get('point')      
                                    order_response_data = order_response.json()                
                                    for order in order_response_data:
                                        woo_order_number = order.get('number',False)     
                                        if sale.woo_order_number == woo_order_number:
                                            customer_id = order.get('customer_id',False) 
                                            break
                                    data = { 'user_id': customer_id,
                                             'action': 'order_cancelled',
                                             'order_id': sale.woo_order_number,
                                             'amount': sale.getting_point,                                                                 
                                            }                        
                                    wcapi.post("point", data)                                                                                                                                                                                                                       
            return True  
                   
    def create_mobile_stock_return(self, cursor, user, vals, context=None):
        try :
            stock_return_obj = self.pool.get('stock.return.mobile')
            stock_return_line_obj = self.pool.get('stock.return.mobile.line')
            str = "{" + vals + "}"
            str = str.replace(":''", ":'")  # change Order_id
            str = str.replace("'',", "',")  # null
            str = str.replace(":',", ":'',")  # due to order_id
            str = str.replace(":'}", ":''}")
            str = str.replace("}{", "}|{")
            
            new_arr = str.split('|')
            result = []
            for data in new_arr:
                x = ast.literal_eval(data)
                result.append(x)
            stock = []
            stock_line = []
            for r in result:
                print "length", len(r)
                if len(r) >= 6:
                    stock_line.append(r)                   
                else:
                    stock.append(r)
            
            if stock:
                for sr in stock:
                    cursor.execute('select id from stock_return_mobile where user_id = %s and return_date=%s ', (user, sr['return_date'],))
                    data = cursor.fetchall()
                    if data:
                        stock_return_id = data[0][0]
                        cursor.execute('delete from stock_return_mobile where id = %s ', (stock_return_id,))
                        cursor.execute('delete from stock_return_mobile_line where line_id = %s ', (stock_return_id,))
                    cursor.execute("select vehicle_id from crm_case_section where id=%s", (sr['sale_team_id'],))
                    vehicle_id = cursor.fetchone()
                    if vehicle_id:
                        vehicle_id = vehicle_id[0]
                    else:
                        vehicle_id = None
                    print 'vehicle_id', vehicle_id
                    mso_result = {
                        'sale_team_id':sr['sale_team_id'],
                        'return_date':sr['return_date'],
                        'company_id':sr['company_id'],
                        'branch_id':sr['branch_id'],
                        'user_id':user,
                        'vehicle_id':vehicle_id,

                    }
                    stock_id = stock_return_obj.create(cursor, user, mso_result, context=context)                  
                    for srl in stock_line:  # return_quantity=  float(srl['return_quantity']) - (float(srl['sale_quantity'])+float(srl['foc_quantity'] ))          
                            return_quantity = srl['return_quantity']
                            mso_line_res = {                                                            
                                  'line_id':stock_id,
                                  'return_quantity':return_quantity,
                                  'sale_quantity':srl['sale_quantity'],
                                  'product_id':srl['product_id'],
                                  'product_uom':srl['product_uom'],
                                  'foc_quantity':srl['foc_quantity'],
                            }
                            stock_return_line_obj.create(cursor, user, mso_line_res, context=context)
            print 'True'
            return True       
        except Exception, e:
            print 'False'
            return False  
        
    # RFI
    def create_stock_request_from_mobile(self, cursor, user, vals, context=None):
        print 'vals', vals
        try : 
            stock_request_obj = self.pool.get('stock.requisition')
            stock_request_line_obj = self.pool.get('stock.requisition.line')
            product_obj = self.pool.get('product.product')
            str = "{" + vals + "}"
            str = str.replace(":''", ":'")  # change Order_id
            str = str.replace("'',", "',")  # null
            str = str.replace(":',", ":'',")  # due to order_id
            str = str.replace(":'}", ":''}")
            str = str.replace("}{", "}|{")
            
            new_arr = str.split('|')
            result = []
            for data in new_arr:
                x = ast.literal_eval(data)
                result.append(x)
            stock = []
            stock_line = []
            for r in result:
                print "length", len(r)
                if len(r) >= 7:
                    stock.append(r)                                    
                else:
                    stock_line.append(r)
            
            if stock:
                for sr in stock:                                    
                    cursor.execute('select vehicle_id,location_id,issue_location_id,id,receiver,branch_id,optional_issue_location_id from crm_case_section where id = %s ', (sr['sale_team_id'],))
                    data = cursor.fetchall()
                    if data:
                        vehcle_no = data[0][0]
                        from_location_id = data[0][1]
                        to_location_id = data[0][2]
                        delivery_id = data[0][3]             
                        receiver = data[0][4] 
                        branch_id = data[0][5] 
                        optional_issue_location_id = data[0][6]
                    else:
                        vehcle_no = None
                        from_location_id = None
                        to_location_id = None
                        delivery_id = None          
                        receiver = None
                        branch_id = None
                        optional_issue_location_id = None
                        
                    cursor.execute('select company_id from res_users where id = %s ', (sr['request_by'],))
                    data = cursor.fetchone()         
                    if data:
                        company_id = data[0]
                    else:
                        company_id = None
                                   

                    
                    for srl in stock_line:
                        if (sr['rfi_no'] == srl['rfi_no']):
                            cursor.execute('select a.uom_ratio,a.big_uom_id,a.uom_id,b.sequence from product_template a, product_product b where a.id = b.product_tmpl_id and b.id = %s ', (srl['product_id'],))
                            data = cursor.fetchall()
                            if data:
                                packing_unit = data[0][0]
                                big_uom_id = data[0][1]
                                small_uom_id = data[0][2]
                                sequence = data[0][3]
                            else:
                                packing_unit = None
                                big_uom_id = None
                                small_uom_id = None
                                sequence = None
                            product_data = product_obj.browse(cursor, user, int(srl['product_id']), context=context)
                            if product_data:
                                issue_category = product_data.categ_id.issue_from_optional_location   
                                principle_id= product_data.main_group.id                                
                                is_separate_transition =product_data.main_group.is_separate_transition 
                            ori_req_quantity = int(srl['req_quantity'])
                            ori_uom_id = int(srl['product_uom'])
                            # print 'product_idddddddddddd',req_quantity
#                             cursor.execute("select floor(round(1/factor,2)) as ratio from product_uom where active = true and id=%s", (big_uom_id,))
#                             bigger_qty = cursor.fetchone()[0]
#                             bigger_qty = int(bigger_qty)
                            # print ' bigger_qty',sale_qty,bigger_qty,type(sale_qty),type(bigger_qty)                        
#                             big_uom_qty = divmod(ori_req_quantity, bigger_qty)
                            # print 'big_uom_qty',big_uom_qty
#                             if  big_uom_qty:
#                                 big_req_quantity = big_uom_qty[0]
#                                 req_quantity = big_uom_qty[1]
                                # print 'big_req',big_req_quantity,req_quantity
                            cursor.execute('select  SUM(COALESCE(qty,0)) qty from stock_quant where location_id=%s and product_id=%s and qty >0 group by product_id', (to_location_id, srl['product_id'],))
                            qty_on_hand = cursor.fetchone()
                            if qty_on_hand:
                                qty_on_hand = qty_on_hand[0]
                            else:
                                qty_on_hand = 0    
                            if issue_category == True:
                                request_ids = stock_request_obj.search(cursor, user , [('issue_from_optional_location', '=', True), ('sale_team_id', '=', delivery_id), ('request_date', '=', sr['request_date']), ('so_no', '=', sr['rfi_no'])])
                                cursor.execute('select  SUM(COALESCE(qty,0)) qty from stock_quant where location_id=%s and product_id=%s and qty >0 group by product_id', (optional_issue_location_id, srl['product_id'],))
                                qty_on_hand = cursor.fetchone()
                                if qty_on_hand:
                                    qty_on_hand = qty_on_hand[0]
                                else:
                                    qty_on_hand = 0              
                                if request_ids:
                                    issue_stock_id = request_ids[0]
                                else:
                                    mso_result = {
                                        'request_date':sr['request_date'],
                                        'request_by':sr['request_by'],
                                        'issue_date':sr['issue_date'] ,
                                         's_issue_date':sr['issue_date'] ,
                                        'state': 'draft',
                                        'issue_to':receiver,
                                        'company_id':company_id,
                                        'branch_id':branch_id,
                                        'vehicle_id':vehcle_no,
                                        'from_location_id':from_location_id,
                                        'to_location_id':optional_issue_location_id,
                                        'sale_team_id':delivery_id,
                                        'issue_from_optional_location':True,
                                        'so_no':sr['rfi_no'],
                                        'principle_id':None,
                                    }
                                    issue_stock_id = stock_request_obj.create(cursor, user, mso_result, context=context)
                                mso_line_res = {                                                            
                                              'line_id':issue_stock_id,
                                              'remark':srl['remark'],
                                              'order_qty':ori_req_quantity,
                                              'ecommerce_qty':0,                                              
                                              'req_quantity':ori_req_quantity,
                                              'product_id':int(srl['product_id']),
                                              'product_uom':ori_uom_id,
                                              'uom_ratio':packing_unit ,
                                              'big_uom_id':big_uom_id,
                                              'big_req_quantity':0,
                                              'qty_on_hand':qty_on_hand,
                                              'sequence':sequence,
                                              }
                                stock_request_line_obj.create(cursor, user, mso_line_res, context=context)
                                        
                            elif is_separate_transition == True:
                                request_ids = stock_request_obj.search(cursor, user , [('principle_id', '=', principle_id),('sale_team_id', '=', delivery_id), ('request_date', '=', sr['request_date']), ('so_no', '=', sr['rfi_no'])])
                                cursor.execute('select  SUM(COALESCE(qty,0)) qty from stock_quant where location_id=%s and product_id=%s and qty >0 group by product_id', (optional_issue_location_id, srl['product_id'],))
                                qty_on_hand = cursor.fetchone()
                                if qty_on_hand:
                                    qty_on_hand = qty_on_hand[0]
                                else:
                                    qty_on_hand = 0              
                                if request_ids:
                                    issue_separate_stock_id = request_ids[0]
                                else:
                                    mso_result = {
                                        'request_date':sr['request_date'],
                                        'request_by':sr['request_by'],
                                        'issue_date':sr['issue_date'] ,
                                         's_issue_date':sr['issue_date'] ,
                                        'state': 'draft',
                                        'issue_to':receiver,
                                        'principle_id':principle_id,
                                        'company_id':company_id,
                                        'branch_id':branch_id,
                                        'vehicle_id':vehcle_no,
                                        'from_location_id':from_location_id,
                                        'to_location_id':to_location_id,
                                        'sale_team_id':delivery_id,
                                        'issue_from_optional_location':False,
                                        'so_no':sr['rfi_no'],
                                    }
                                    issue_separate_stock_id = stock_request_obj.create(cursor, user, mso_result, context=context)
                                mso_line_res = {                                                            
                                      'line_id':issue_separate_stock_id,
                                      'remark':srl['remark'],
                                      'order_qty':ori_req_quantity,
                                      'ecommerce_qty':0,                                           
                                      'req_quantity':ori_req_quantity,
                                      'product_id':int(srl['product_id']),
                                      'product_uom':ori_uom_id,
                                      'uom_ratio':packing_unit ,
                                      'big_uom_id':big_uom_id,
                                      'big_req_quantity':0,
                                      'qty_on_hand':qty_on_hand,
                                      'sequence':sequence,
                                      }
                                stock_request_line_obj.create(cursor, user, mso_line_res, context=context)
                            
                            else:
                                request_ids = stock_request_obj.search(cursor, user , [('principle_id', '=', None), ('issue_from_optional_location', '=', False), ('sale_team_id', '=', delivery_id), ('request_date', '=', sr['request_date']), ('so_no', '=', sr['rfi_no'])])          
                                if request_ids:
                                    stock_id = request_ids[0]
                                else:                                                                
                                    mso_result = {
                                                'request_date':sr['request_date'],
                                                'request_by':sr['request_by'],
                                                'issue_date':sr['issue_date'] ,
                                                 's_issue_date':sr['issue_date'] ,
                                                'state': 'draft',
                                                'issue_to':receiver,
                                                'company_id':company_id,
                                                'branch_id':branch_id,
                                                'vehicle_id':vehcle_no,
                                                'from_location_id':from_location_id,
                                                'to_location_id':to_location_id,
                                                'sale_team_id':delivery_id,
                                                'issue_from_optional_location':False,
                                                'principle_id':None,
                                                'so_no':sr['rfi_no'],
                                            }
                                    stock_id = stock_request_obj.create(cursor, user, mso_result, context=context)
                                mso_line_res = {                                                            
                                      'line_id':stock_id,
                                      'remark':srl['remark'],
                                      'order_qty':ori_req_quantity,
                                      'ecommerce_qty':0,                                              
                                      'req_quantity':ori_req_quantity,
                                      'product_id':int(srl['product_id']),
                                      'product_uom':ori_uom_id,
                                      'uom_ratio':packing_unit ,
                                      'big_uom_id':big_uom_id,
                                      'big_req_quantity':0,
                                      'qty_on_hand':qty_on_hand,
                                      'sequence':sequence,
                                      }
                                stock_request_line_obj.create(cursor, user, mso_line_res, context=context)
                                
                            # comment by EMTW           
#                             if int(srl['product_uom']) == int(big_uom_id):                                                                          
#                                 mso_line_res = {                                                            
#                                       'line_id':stock_id,
#                                       'remark':srl['remark'],
#                                       'req_quantity':req_quantity,
#                                       'product_id':int(srl['product_id']),
#                                       'product_uom':big_uom_id,
#                                       'uom_ratio':packing_unit ,
#                                       'big_uom_id':big_uom_id,
#                                       'big_req_quantity':ori_req_quantity,
#                                       'qty_on_hand':qty_on_hand,
#                                       'sequence':sequence,
#                                       }
#                             else:
#                             if issue_category == True:
#                                 master_id = issue_stock_id
#                             else:
#                                 master_id = stock_id
                            
            print 'True'
            return True       
        except Exception, e:
            print 'False'
            return False
        
    # Stock Check From Mobile
    def create_stock_check_from_mobile(self, cursor, user, vals, context=None):
        print 'vals', vals

        try : 
            stock_check_obj = self.pool.get('partner.stock.check')
            stock_check_line_obj = self.pool.get('partner.stock.check.line')
            str = "{" + vals + "}"
            str = str.replace(":''", ":'")  # change Order_id
            str = str.replace("'',", "',")  # null
            str = str.replace(":',", ":'',")  # due to order_id
            str = str.replace(":'}", ":''}")
            str = str.replace("}{", "}|{")
            
            new_arr = str.split('|')
            result = []
            for data in new_arr:
                x = ast.literal_eval(data)
                result.append(x)
            stock = []
            stock_line = []
            for r in result:
                print "length", len(r)
                if len(r) >= 10:
                    stock.append(r)                                    
                else:
                    stock_line.append(r)
            if stock:
                for sr in stock:                                    
                    cursor.execute('select id ,township ,outlet_type from res_partner where customer_code = %s ', (sr['customer_code'],))
                    customer_data = cursor.fetchone()
                    if customer_data:
                        customer_id = customer_data[0]
                        township_id = customer_data[1]
                        outlet_type = customer_data[2]

                    else:
                        customer_id = None
                        township_id = None
                        outlet_type = None
                    
                    if  sr['date']:
                        check_date_time = sr['date'].replace('\\', '').replace('\\', '').replace('/', '-')
                        date = datetime.strptime(check_date_time, '%Y-%m-%d %H:%M:%S') - timedelta(hours=6, minutes=30)
                        check_date = date.date()
                    cursor.execute("delete from partner_stock_check where check_datetime =%s and partner_id=%s", (date, customer_id,))
                    mso_result = {
                        'partner_id':customer_id,
                        'sale_team_id':sr['sale_team_id'] ,
                         'user_id':sr['user_id'] ,
                        'township_id': township_id,
                        'outlet_type':outlet_type,
                        'date':check_date,
                        'check_datetime':date,
                        'customer_code':sr['customer_code'],
                        'branch_id':sr['branch'],
                                                    'latitude':sr['latitude'],
                            'longitude':sr['longitude'],
                    }
                    stock_id = stock_check_obj.create(cursor, user, mso_result, context=context)
                    
                    for srl in stock_line:
                        if (sr['st_id'] == srl['stock_check_no']):
                            cursor.execute("select sequence from product_product where id =%s", (srl['product_id'],))
                            product_data = cursor.fetchone()
                            if  product_data:
                                sequence = product_data[0]
                            else:
                                sequence = None
                            if srl['avail'] == 'false':
                                avaliable = 'no'
                            elif srl['avail'] == 'true':
                                avaliable = 'yes'
                            else:
                                avaliable = srl['avail']
                        
                            mso_line_res = {                                                            
                                      'stock_check_ids':stock_id,
                                      'sequence':sequence,
                                      'product_id':(srl['product_id']),
                                      'product_uom':int(srl['uom_id']),
                                      'available':avaliable,
                                      'product_uom_qty':(srl['qty']),
                                      'facing':(srl['facing']),
                                      'chiller':(srl['chiller']),
                                      'remark_id':(srl['remark_id']),
                                      'description':(srl['description']),
                                      }
                            stock_check_line_obj.create(cursor, user, mso_line_res, context=context)
            print 'True'
            return True       
        except Exception, e:
            print 'False'
            return False
    def create_competitor_stock_check_from_mobile(self, cursor, user, vals, context=None):
        print 'vals', vals

        try:
            stock_check_obj = self.pool.get('partner.stock.check')
            competitor_stock_check_line_obj = self.pool.get('partner.stock.check.competitor.line')
            str = "{" + vals + "}"
            str = str.replace(":''", ":'")  # change Order_id
            str = str.replace("'',", "',")  # null
            str = str.replace(":',", ":'',")  # due to order_id
            str = str.replace(":'}", ":''}")
            str = str.replace("}{", "}|{")

            new_arr = str.split('|')
            result = []
            for data in new_arr:
                x = ast.literal_eval(data)
                result.append(x)
            stock = []
            competitor_stock_line = []
            for r in result:
                print "length", len(r)
                if len(r) >= 10:
                    stock.append(r)
                else:
                    competitor_stock_line.append(r)
            if stock:
                for sr in stock:
                    cursor.execute('select id ,township ,outlet_type from res_partner where customer_code = %s ',
                                   (sr['customer_code'],))
                    customer_data = cursor.fetchone()
                    if customer_data:
                        customer_id = customer_data[0]
                        township_id = customer_data[1]
                        outlet_type = customer_data[2]

                    else:
                        customer_id = None
                        township_id = None
                        outlet_type = None

                    if sr['date']:
                        check_date_time = sr['date'].replace('\\', '').replace('\\', '').replace('/', '-')
                        date = datetime.strptime(check_date_time, '%Y-%m-%d %H:%M:%S') - timedelta(hours=6, minutes=30)
                        check_date = date.date()
                    cursor.execute("select id from partner_stock_check where check_datetime =%s and partner_id=%s",
                                   (date, customer_id,))
                    stock_check_data = cursor.fetchone()
                    if stock_check_data:
                        stock_id =stock_check_data[0]
                    else:
                        mso_result = {
                            'partner_id': customer_id,
                            'sale_team_id': sr['sale_team_id'],
                            'user_id': sr['user_id'],
                            'township_id': township_id,
                            'outlet_type': outlet_type,
                            'date': check_date,
                            'check_datetime': date,
                            'customer_code': sr['customer_code'],
                            'branch_id': sr['branch'],
                            'latitude': sr['latitude'],
                            'longitude': sr['longitude'],
                        }
                        stock_id = stock_check_obj.create(cursor, user, mso_result, context=context)
                    for csl in competitor_stock_line:
                        if (sr['st_id'] == csl['stock_check_no']):
                            cursor.execute("select sequence from competitor_product where id =%s",(csl['product_id'],))
                            competitor_product_data = cursor.fetchone()
                            if competitor_product_data:
                                sequence = competitor_product_data[0]
                            else:
                                sequence = None
                            csl_line_res = {
                                'stock_check_ids': stock_id,
                                'sequence': sequence,
                                'competitor_product_id': (csl['product_id']),
                                'product_uom': int(csl['uom_id']),
                                'available': (csl['avail']),
                                'product_uom_qty': (csl['qty']),
                                'facing': (csl['facing']),
                                'chiller': (csl['chiller']),
                                'remark_id': (csl['remark_id']),
                                'description': (csl['description']),
                            }
                            competitor_stock_check_line_obj.create(cursor, user, csl_line_res, context=context)
            print 'True'
            return True
        except Exception, e:
            print 'False'
            return False
    def get_promos_outlet(self, cr, uid, context=None, **kwargs):    
        cr.execute("""select rel.promos_rules_id,rel.outlettype_id from promos_rules_outlettype_rel rel,promos_rules rule where rule.id =rel.promos_rules_id  and now()::date between from_date::date and to_date::date""")
        datas = cr.fetchall()        
        return datas
    
    def get_promos_branch(self, cr, uid, context=None, **kwargs):    
        cr.execute("""select rel.promos_rules_id,rel.res_branch_id from promos_rules_res_branch_rel rel,promos_rules rule where rule.id =rel.promos_rules_id  and now()::date between from_date::date and to_date::date""")
        datas = cr.fetchall()        
        return datas
    
    def get_promos_partner(self, cr, uid, context=None, **kwargs):    
        cr.execute("""select rel.promos_rules_id,rel.res_partner_id from promos_rules_res_partner_rel rel,promos_rules rule where rule.id =rel.promos_rules_id  and now()::date between from_date::date and to_date::date""")
        datas = cr.fetchall()        
        return datas
    
    def get_account_journal(self, cr, uid, context=None, **kwargs):    
        cr.execute("""select id,name from account_journal where is_tablet = true""")
        datas = cr.fetchall()        
        return datas
        
    def get_promo_product(self, cr, uid, context=None, **kwargs):    
        cr.execute('''select rel.promos_rules_id,rel.product_id from promos_rules_product_rel rel,promos_rules rule where rule.id =rel.promos_rules_id  and now()::date between from_date::date and to_date::date''')
        datas = cr.fetchall()        
        return datas
    
    def stock_deliver(self, cr, uid, ids, soId, context=None):
        sale_obj = self.pool.get('sale.order')
        if soId:
            sale_id = sale_obj.browse(cr, uid, soId, context)
            procurement_group_id = stock_picking_id = None
            cr.execute(""" select id from procurement_group where name = %s """, (sale_id.name,))
            data = cr.fetchall()
            if data:
                try:
                    procurement_group_id = data[0][0]
                except Exception, e:
                    procurement_group_id = data[0]    
            if procurement_group_id:
                procurement_group = self.pool.get('procurement.group').browse(cr, uid, procurement_group_id, context)        
            if procurement_group:
                cr.execute(""" select id from stock_picking where group_id =%s and state not in ('draft','cancel','done') """, (procurement_group.id,))
                data = cr.fetchall()
                if data:
                    try:
                        stock_picking_id = data[0][0]
                    except Exception, e:
                        stock_picking_id = data[0]
            if stock_picking_id:
                stock_picking = self.pool.get('stock.picking').browse(cr, uid, stock_picking_id, context)
            else:
                raise osv.except_osv(_('No More Stock Receive!'), _("There no stock receipt for Incoming Stock ."))
                return False
            if stock_picking:
                cr.execute(""" select id from stock_move where picking_id =%s """ , (stock_picking.id,))
                data = cr.fetchall()
                if data:
                    try:
                        move_list = data[0]
                    except Exception, e:
                        move_list = data
                if move_list:
                    result = {}
                    result = self.pool.get('stock.move').read(cr, uid, move_list[0], ['product_uom_qty'], context)
                    total_qty = result['product_uom_qty']
                if total_qty > 0:
                    print 'Stock Received Successful'
                    # first confirm the original picking, original qty - actual qty
                    cr.execute(""" update stock_move set product_uom_qty = %s where picking_id = %s """, (total_qty, stock_picking.id,))
                    move_id = None
                    cr.execute(""" select id from stock_move where picking_id = %s """ , (stock_picking.id,))
                    data = cr.fetchall()
                    if data:
                        try:
                            move_id = data[0][0]
                        except Exception, e:
                            move_id = data[0]
                    if move_id:
                        self.pool.get('stock.move').action_done(cr, uid, move_id, context)
                    self.write(cr, uid, ids, {'state':'done'}, context=None)                    
        return True
    
    def create_sale_order_payment(self, cursor, user, vals, context=None):
        
        try:
            rental_obj = self.pool.get('customer.payment')
            str = "{" + vals + "}"
            str = str.replace("'',", "',")  # null
            str = str.replace(":',", ":'',")  # due to order_id
            str = str.replace("}{", "}|{")
            str = str.replace(":'}{", ":''}")
            new_arr = str.split('|')
            result = []
            for data in new_arr:
                x = ast.literal_eval(data)
                result.append(x)
            rental_collection = []
            for r in result:
                rental_collection.append(r)  
            if rental_collection:
                for ar in rental_collection:
                    cursor.execute('select id,void_flag from mobile_sale_order where name = %s ', (ar['payment_id'],))
                    data = cursor.fetchall()
                    if data:
                        so_id = data[0][0]
                        void_flag =data[0][1]
                    else:
                        so_id = None
                        void_flag =None

                    if void_flag!='voided':
                        cursor.execute('select id from res_partner where id = %s ', (ar['partner_id'],))
                        data = cursor.fetchall()                        
                        if data:
                            parnter_id = data[0][0]
                        else:
                            parnter_id = None
                        amount = ar['amount']
                        cursor.execute("select replace(%s, ',', '')::float as amount", (amount,))
                        amount_data = cursor.fetchone()[0]
                        amount = amount_data
                        cursor.execute('select count(id) from customer_payment where journal_id= %s and payment_code = %s and  notes = %s  and date = %s and amount = %s ', (ar['journal_id'],ar['payment_code'],ar['notes'],ar['date'],amount,))
                        payment_data = cursor.fetchone()[0]
                        if payment_data==0:                    
                            rental_result = {                    
                                'payment_id':so_id,
                                'journal_id':ar['journal_id'],
                                'amount':amount,
                                'date':ar['date'],
                                'notes':ar['notes'],
                                'cheque_no':ar['cheque_no'].replace('\\', ""),
                                'partner_id':parnter_id,
                                'sale_team_id':ar['sale_team_id'],
                                'payment_code':ar['payment_code'],
                            }                            
                            rental_obj.create(cursor, user, rental_result, context=context)
                            cheque_no =ar['cheque_no'].replace('\\', "")
                            cursor.execute("update account_creditnote set m_status ='used' where name=%s",(cheque_no,))
                            #noteObj = self.pool.get('account.creditnote')
                            #note_id = noteObj.search(cursor, user,  [('name', '=',  ar['cheque_no'].replace('\\', ""))],context=None)
                            #note_data = noteObj.browse(cursor, user,  note_id, context=context)
                            #note_data.write({'m_state':'used'})                        
            return True
        except Exception, e:
            print 'False'
            return False
        
    def create_pre_order_payment(self, cursor, user, vals, context=None):
        
        try:
            rental_obj = self.pool.get('customer.payment')
            str = "{" + vals + "}"
            str = str.replace("'',", "',")  # null
            str = str.replace(":',", ":'',")  # due to order_id
            str = str.replace("}{", "}|{")
            str = str.replace(":'}{", ":''}")
            new_arr = str.split('|')
            result = []
            for data in new_arr:
                x = ast.literal_eval(data)
                result.append(x)
#             rental_collection = []
#             for r in result:
#                 rental_collection.append(r) 
            if result:
                for ar in result:
                    payment_id = ar['payment_id'].replace('\\', '').replace('\\', '')   
                    cursor.execute('select tb_ref_no from sale_order where name = %s ', (payment_id,))
                    data = cursor.fetchall()
                    if data:
                        pre_no = data[0][0]
                    else:
                        pre_no = None
                    
                    cursor.execute('select id from pre_sale_order where name = %s ', (pre_no,))
                    data = cursor.fetchall()
                    if data:
                        so_id = data[0][0]
                    else:
                        so_id = None
                    cursor.execute('select count(id) from customer_payment where journal_id= %s and payment_code = %s and  notes = %s  and date = %s and amount = %s ', (ar['journal_id'],ar['payment_code'],payment_id,ar['date'],ar['amount'],))
                    payment_data = cursor.fetchone()[0]                    
                    if payment_data==0:                              
                        rental_result = {                    
                            'pre_order_id':so_id,
                            'journal_id':ar['journal_id'],
                            'amount':ar['amount'],
                            'date':ar['date'],
                            'notes':payment_id,
                            'cheque_no':ar['cheque_no'].replace('\\', ""),
                            'partner_id':ar['partner_id'],
                            'sale_team_id':ar['sale_team_id'],
                            'payment_code':ar['payment_code'],
                        }                        
                        rental_obj.create(cursor, user, rental_result, context=context)
                        cheque_no =ar['cheque_no'].replace('\\', "")
                        cursor.execute("update account_creditnote set m_status ='used' where name=%s",(cheque_no,))                        
#                         noteObj = self.pool.get('account.creditnote')
#                         note_id = noteObj.search(cursor, user,  [('name', '=',  ar['cheque_no'].replace('\\', ""))],context=None)
#                         note_data = noteObj.browse(cursor, user,  note_id, context=context)
#                         note_data.write({'m_state':'used'})
            return True
        except Exception, e:
            print 'False'
            return False         
        
    def get_bom(self, cr, uid , context=None):        
        cr.execute('''select mbl.product_id as product,mbl.product_qty as from_qty,mbl.product_uom  as from_uom_id,mb.product_id as to_product,mb.product_qty,mb.product_uom from mrp_bom mb ,mrp_bom_line mbl
                    where mb.id=mbl.bom_id''')
        datas = cr.fetchall()        
        return datas   
    def get_country(self, cr, uid , context=None):        
        cr.execute('''select id,code,name from res_country where id between 146 and 160''')
        datas = cr.fetchall()        
        return datas
    def get_division_state(self, cr, uid , context=None):        
        cr.execute('''select id,name from res_country_state''')
        datas = cr.fetchall()        
        return datas
    
    def get_city(self, cr, uid , context=None):        
        cr.execute('''select id,code,name,state_id from res_city''')
        datas = cr.fetchall()        
        return datas
    
    def get_township(self, cr, uid , context=None):        
        cr.execute('''select id,code,name,city from res_township''')
        datas = cr.fetchall()        
        return datas

    def get_outlet_type(self, cr, uid , context=None):        
        cr.execute('''select id,name from outlettype_outlettype''')
        datas = cr.fetchall()        
        return datas
    
    def get_sale_demarcation(self, cr, uid , context=None):        
        cr.execute('''select id,name from sale_demarcation''')
        datas = cr.fetchall()        
        return datas
     
    def get_sale_class(self, cr, uid , context=None):        
        cr.execute('''select id,name from sale_class''')
        datas = cr.fetchall()        
        return datas
    
    def get_frequency(self, cr, uid , context=None):        
        cr.execute('''select id,name,frequency_count from plan_frequency''')
        datas = cr.fetchall()        
        return datas
    # Create New Customer from Tablet by kzo
    def create_new_customer(self, cursor, user, vals, context=None):
        try:
            partner_obj = self.pool.get('res.partner')
            parnter_tag_obj = self.pool.get('res.partner.res.partner.category.rel')
            str = "{" + vals + "}"
            str = str.replace("'',", "',")  # null
            str = str.replace(":',", ":'',")  # due to order_id
            str = str.replace("}{", "}|{")
            str = str.replace(":'}{", ":''}")
            new_arr = str.split('|')
            result = []
            for data in new_arr:
                x = ast.literal_eval(data)
                result.append(x)
            new_partner = []
            for r in result:
                new_partner.append(r)  
            if new_partner:
                for partner in new_partner:
                    chiller = False;
                    if 'chiller' in partner:
                        chiller = partner['chiller']
                    partner_result = {                 
                        'country_id':partner['country_id'],
                        'state_id':partner['state_id'],
                        'city':partner['city'],
                        'street':partner['street'],
                        'street2':partner['street2'],
                        'display_name':partner['name'],
                        'name':partner['name'],
                        'email':partner['email'],
                        'is_company':True,
                        'customer':True,
                        'employee':False,
                        'phone':partner['phone'],
                        'mobile':partner['mobile'],
                        'notify_email':'always',
                        'township':partner['township'],
                        'partner_latitude':partner['partner_latitude'],
                        'partner_longitude':partner['partner_longitude'],
                        'branch_id':partner['branch_id'],
                        'outlet_type':partner['outlet_type'],
                        'customer_code':partner['customer_code'],
                        'class_id':partner['class_id'],
                        'mobile_customer':True,
                        'pricelist_id':partner['pricelist_id'],
                        'chiller':chiller,
                        'unit':partner['unit'],
                        'image':partner['image'],
                        'sales_channel':partner['sales_channel'],
                        'temp_customer':partner['temp_customer'],
                        'frequency_id':partner['frequency_id'],
                        'section_id':partner['section_id'],
                    }
                    partner_id = partner_obj.create(cursor, user, partner_result, context=context)                    
                    
                    cursor.execute(''' insert into res_partner_res_partner_category_rel(category_id,partner_id) 
                    values(2,%s)''', (partner_id,))
                    
                    cursor.execute(''' insert into sale_team_customer_rel(partner_id,sale_team_id) 
                    values(%s,%s)''', (partner_id, partner['section_id'],))
                    
            return partner_id
        except Exception, e:
            print 'False'
            return 0
    
    # GET Pending DELIVER CUSTOMER
    def get_deliver_customer(self, cr, uid, saleTeamId, parnterList, context=None, **kwargs):    
        
        partner_list = None
        parnterList = str(tuple(parnterList))
        parnterList = eval(parnterList)
        print 'Param Customer List', parnterList
        
        if parnterList:
                cr.execute('''select PARTNER_ID from sale_order WHERE pre_order = TRUE AND delivery_id = %s 
                AND shipped = False
                AND invoiced = False
                AND PARTNER_ID NOT IN %s''', (saleTeamId, parnterList,))
            
        else:
            cr.execute('''select PARTNER_ID from sale_order 
                WHERE pre_order = TRUE 
                AND delivery_id = %s 
                AND shipped = False
                AND invoiced = False
                ''', (saleTeamId,))
            
        data = cr.fetchall()
        if data:
            partner_list = data
        else:
            partner_list = None
        

        result = []
        try:
            if partner_list: 
                partner_list = str(tuple(partner_list))
                partner_list = eval(partner_list)
                print 'list_val', partner_list           
                cr.execute('''select A.id,A.name,A.image,A.is_company, A.image_small,replace(A.street,',',';') street,replace(A.street2,',',';') street2,A.city,A.website,
                     replace(A.phone,',',';') phone,A.township,replace(A.mobile,',',';') mobile,A.email,A.company_id,A.customer, 
                     A.customer_code,A.mobile_customer,A.shop_name ,
                     A.address,
                     A.zip,A.state_name,A.partner_latitude,A.partner_longitude,null,A.image_medium,A.credit_limit,
                     A.credit_allow,A.sales_channel,A.branch_id,A.pricelist_id,A.payment_term_id,A.outlet_type ,
                     A.city_id,A.township_id,A.country_id,A.state_id,A.unit,A.class_id,A.chiller,A.frequency_id,A.temp_customer,
                     A.is_consignment,A.hamper,A.is_bank,A.is_cheque,A.verify,A.pricelist
                     from (

                     select RP.id,RP.name,'' as image,RP.is_company,null,
                     '' as image_small,RP.street,RP.street2,RC.name as city,RP.website,
                     RP.phone,RT.name as township,RP.mobile,RP.email,RP.company_id,RP.customer, 
                     RP.customer_code,RP.mobile_customer,OT.name as shop_name,RP.address,RP.zip ,RP.partner_latitude,RP.partner_longitude,RS.name as state_name,
                     substring(replace(cast(RP.image_medium as text),'/',''),1,5) as image_medium,RP.credit_limit,RP.credit_allow,
                     RP.sales_channel,RP.branch_id,RP.pricelist_id,RP.payment_term_id,RP.outlet_type,RP.city as city_id,RP.township as township_id,
                     RP.country_id,RP.state_id,RP.unit,RP.class_id,RP.chiller,RP.frequency_id,RP.temp_customer,RP.is_consignment,
                     RP.hamper,RP.is_bank,RP.is_cheque,RP.verify,pp.name as pricelist

                     from  res_partner RP ,res_country_state RS, res_city RC,res_township RT,
                             outlettype_outlettype OT,product_pricelist pp
                                            where RS.id = RP.state_id
                                            and RP.township =RT.id
                                            and RP.city = RC.id
                                            and RP.pricelist_id = pp.id
                                            and RP.outlet_type = OT.id
                                            and RP.id in %s                                                                                
                                            order by RP.name                                       
                        )A 
                        where A.customer_code is not null
                            ''', (partner_list ,))
                result = cr.fetchall()
            return result
        except Exception, e:
            return False
    
    def get_credit_invoice(self, cr, uid, partner_list, branch_id , invoiceList, sale_team_id, context=None):    
        data_line = []
        if partner_list:
            partner_list = str(tuple(partner_list))
            partner_list = eval(partner_list)
            invoiceList = str(tuple(invoiceList))
            invoiceList = eval(invoiceList)
            
            cr.execute('''select allow_collection_team from res_users where id= %s''',(uid,))
            is_credit_team=cr.fetchone()[0]
                
            if is_credit_team==True:
                if invoiceList:        
                    cr.execute(''' 
                        select inv.id,inv.number,inv.partner_id,rp.name customer_name,
                               rp.customer_code customer_code,inv.origin so_no,inv.date_invoice,
                               inv.amount_total,inv.residual balance,inv.payment_type,
                               inv.journal_id,crm.name,inv.date_due
                        from account_invoice inv, res_partner rp, crm_case_section crm
                        where inv.payment_type='credit' 
                        and inv.state='open' 
                        and inv.type = 'out_invoice'
                        and inv.branch_id = %s 
                        and residual > 0
                        and inv.partner_id = rp.id
                        and inv.section_id = crm.id
                        and inv.partner_id in %s
                        and inv.id NOT IN %s        
                        '''
                        , (branch_id, partner_list, invoiceList,))
                else:
                    cr.execute(''' 
                        select inv.id,inv.number,inv.partner_id,rp.name customer_name,
                               rp.customer_code customer_code,inv.origin so_no,inv.date_invoice,
                               inv.amount_total,inv.residual balance,inv.payment_type,
                               inv.journal_id,crm.name,inv.date_due
                        from account_invoice inv, res_partner rp, crm_case_section crm
                        where inv.payment_type='credit' 
                        and inv.state='open' 
                        and inv.type = 'out_invoice'
                        and inv.branch_id = %s 
                        and residual > 0
                        and inv.partner_id = rp.id
                        and inv.section_id = crm.id
                        and inv.partner_id in %s
                        '''
                        , (branch_id, partner_list,))  
            else:
                
                if invoiceList:        
                    cr.execute(''' 
                        select inv.id,inv.number,inv.partner_id,rp.name customer_name,
                               rp.customer_code customer_code,inv.origin so_no,inv.date_invoice,
                               inv.amount_total,inv.residual balance,inv.payment_type,
                               inv.journal_id,crm.name,inv.date_due
                        from account_invoice inv, res_partner rp, crm_case_section crm
                        where inv.payment_type='credit' 
                        and inv.state='open' 
                        and inv.type = 'out_invoice'
                        and inv.branch_id = %s 
                        and residual > 0
                        and inv.partner_id = rp.id
                        and inv.section_id = crm.id
                        and inv.partner_id in %s
                        and inv.id NOT IN %s        
                        and inv.section_id = %s'''
                        , (branch_id, partner_list, invoiceList, sale_team_id,))
                else:
                    cr.execute(''' 
                        select inv.id,inv.number,inv.partner_id,rp.name customer_name,
                               rp.customer_code customer_code,inv.origin so_no,inv.date_invoice,
                               inv.amount_total,inv.residual balance,inv.payment_type,
                               inv.journal_id,crm.name,inv.date_due
                        from account_invoice inv, res_partner rp, crm_case_section crm
                        where inv.payment_type='credit' 
                        and inv.state='open' 
                        and inv.type = 'out_invoice'
                        and inv.branch_id = %s 
                        and residual > 0
                        and inv.partner_id = rp.id
                        and inv.section_id = crm.id
                        and inv.partner_id in %s
                        and inv.section_id = %s'''
                        , (branch_id, partner_list, sale_team_id,))            
            data_line = cr.fetchall()                    
        print 'data_lineeeeeeeeeeeeeee', data_line        
        return data_line
    
    def get_credit_invoice_with_teamId(self, cr, uid, branch_id , invoiceList, sale_team_id, context=None):    
        data_line = []                
        cr.execute("""select ARRAY_AGG (RP.id order by  RPS.sequence asc) partner_id
                    from sale_plan_day SPD ,outlettype_outlettype OT,
                    sale_plan_day_line RPS , res_partner RP ,res_country_state RS, res_city RC,res_township RT
                    where SPD.id = RPS.line_id 
                    and  RS.id = RP.state_id
                    and RP.township =RT.id
                    and RP.city = RC.id
                    and RP.active = true
                    and RP.outlet_type = OT.id
                    and RPS.partner_id = RP.id    
                    and SPD.sale_team = %s""",(sale_team_id,))
        partner_data = cr.fetchall()        
        if partner_data:            
            partner_list = tuple(partner_data[0][0])                        
            invoiceList = str(tuple(invoiceList))
            invoiceList = eval(invoiceList)
             
            cr.execute('''select allow_collection_team from res_users where id= %s''',(uid,))
            is_credit_team=cr.fetchone()[0]
                 
            if is_credit_team==True:
                if invoiceList:        
                    cr.execute(''' 
                        select inv.id,inv.number,inv.partner_id,rp.name customer_name,
                               rp.customer_code customer_code,inv.origin so_no,inv.date_invoice,
                               inv.amount_total,inv.residual balance,inv.payment_type,
                               inv.journal_id,crm.name,inv.date_due
                        from account_invoice inv, res_partner rp, crm_case_section crm
                        where inv.payment_type='credit' 
                        and inv.state='open' 
                        and inv.type = 'out_invoice'
                        and inv.branch_id = %s 
                        and residual > 0
                        and inv.partner_id = rp.id
                        and inv.section_id = crm.id
                        and inv.partner_id in %s
                        and inv.id NOT IN %s        
                        '''
                        , (branch_id, partner_list, invoiceList,))
                else:
                    cr.execute(''' 
                        select inv.id,inv.number,inv.partner_id,rp.name customer_name,
                               rp.customer_code customer_code,inv.origin so_no,inv.date_invoice,
                               inv.amount_total,inv.residual balance,inv.payment_type,
                               inv.journal_id,crm.name,inv.date_due
                        from account_invoice inv, res_partner rp, crm_case_section crm
                        where inv.payment_type='credit' 
                        and inv.state='open' 
                        and inv.type = 'out_invoice'
                        and inv.branch_id = %s 
                        and residual > 0
                        and inv.partner_id = rp.id
                        and inv.section_id = crm.id
                        and inv.partner_id in %s
                        '''
                        , (branch_id, partner_list,))  
            else:
                 
                if invoiceList:        
                    cr.execute(''' 
                        select inv.id,inv.number,inv.partner_id,rp.name customer_name,
                               rp.customer_code customer_code,inv.origin so_no,inv.date_invoice,
                               inv.amount_total,inv.residual balance,inv.payment_type,
                               inv.journal_id,crm.name,inv.date_due
                        from account_invoice inv, res_partner rp, crm_case_section crm
                        where inv.payment_type='credit' 
                        and inv.state='open' 
                        and inv.type = 'out_invoice'
                        and inv.branch_id = %s 
                        and residual > 0
                        and inv.partner_id = rp.id
                        and inv.section_id = crm.id
                        and inv.partner_id in %s
                        and inv.id NOT IN %s        
                        and inv.section_id = %s'''
                        , (branch_id, partner_list, invoiceList, sale_team_id,))
                else:
                    cr.execute(''' 
                        select inv.id,inv.number,inv.partner_id,rp.name customer_name,
                               rp.customer_code customer_code,inv.origin so_no,inv.date_invoice,
                               inv.amount_total,inv.residual balance,inv.payment_type,
                               inv.journal_id,crm.name,inv.date_due
                        from account_invoice inv, res_partner rp, crm_case_section crm
                        where inv.payment_type='credit' 
                        and inv.state='open' 
                        and inv.type = 'out_invoice'
                        and inv.branch_id = %s 
                        and residual > 0
                        and inv.partner_id = rp.id
                        and inv.section_id = crm.id
                        and inv.partner_id in %s
                        and inv.section_id = %s'''
                        , (branch_id, partner_list, sale_team_id,))            
            data_line = cr.fetchall()                    
        print 'data_lineeeeeeeeeeeeeee', data_line        
        return data_line
    
    def get_credit_invoice_line(self, cr, uid, partner_list, branch_id, invoiceList , context=None):    
        data_line = []
        if partner_list:
            partner_list = str(tuple(partner_list))
            partner_list = eval(partner_list)
            
            invoiceList = str(tuple(invoiceList))
            invoiceList = eval(invoiceList)
            
            if invoiceList:
                
                cr.execute(''' 
                    select  inv_line.id,inv_line.invoice_id,inv_line.product_id,pp.name_template, pp.default_code,
                            inv_line.quantity qty,inv_line.price_unit as price,inv_line.price_subtotal,
                            inv_line.discount,inv_line.discount_amt,inv_line.uos_id
                    from account_invoice inv, account_invoice_line inv_line, res_partner rp, product_product pp
                    where inv.id = inv_line.invoice_id
                    and inv.payment_type='credit' 
                    and inv.state='open' 
                    and inv.type = 'out_invoice'
                    and inv.branch_id = %s
                    and inv_line.product_id = pp.id
                    and residual > 0
                    and inv.partner_id = rp.id
                    and inv.partner_id in %s
                    and inv.id not in %s'''                       
                    , (branch_id, partner_list, invoiceList ,))
            else:
                cr.execute(''' 
                    select  inv_line.id,inv_line.invoice_id,inv_line.product_id,pp.name_template, pp.default_code,
                            inv_line.quantity qty,inv_line.price_unit as price,inv_line.price_subtotal,
                            inv_line.discount,inv_line.discount_amt,inv_line.uos_id
                    from account_invoice inv, account_invoice_line inv_line, res_partner rp, product_product pp
                    where inv.id = inv_line.invoice_id
                    and inv.payment_type='credit' 
                    and inv.state='open' 
                    and inv.type = 'out_invoice'
                    and inv.branch_id = %s
                    and inv_line.product_id = pp.id
                    and residual > 0
                    and inv.partner_id = rp.id
                    and inv.partner_id in %s
                    '''                       
                    , (branch_id, partner_list ,))
                      
            data_line = cr.fetchall()                    
        print 'data_lineeeeeeeeeeeeeee', data_line        
        return data_line
    
    def get_credit_invoice_line_withteamId(self, cr, uid, branch_id, invoiceList , sale_team_id, context=None):    
        data_line = []
        cr.execute("""select ARRAY_AGG (RP.id order by  RPS.sequence asc) partner_id
                    from sale_plan_day SPD ,outlettype_outlettype OT,
                    sale_plan_day_line RPS , res_partner RP ,res_country_state RS, res_city RC,res_township RT
                    where SPD.id = RPS.line_id 
                    and  RS.id = RP.state_id
                    and RP.township =RT.id
                    and RP.city = RC.id
                    and RP.active = true
                    and RP.outlet_type = OT.id
                    and RPS.partner_id = RP.id    
                    and SPD.sale_team = %s""",(sale_team_id,))
        partner_data = cr.fetchall()        
        if partner_data:
            partner_list = tuple(partner_data[0][0])      
            
            invoiceList = str(tuple(invoiceList))
            invoiceList = eval(invoiceList)
            
            if invoiceList:
                
                cr.execute(''' 
                    select  inv_line.id,inv_line.invoice_id,inv_line.product_id,pp.name_template, pp.default_code,
                            inv_line.quantity qty,inv_line.price_unit as price,inv_line.price_subtotal,
                            inv_line.discount,inv_line.discount_amt,inv_line.uos_id
                    from account_invoice inv, account_invoice_line inv_line, res_partner rp, product_product pp
                    where inv.id = inv_line.invoice_id
                    and inv.payment_type='credit' 
                    and inv.state='open' 
                    and inv.type = 'out_invoice'
                    and inv.branch_id = %s
                    and inv_line.product_id = pp.id
                    and residual > 0
                    and inv.partner_id = rp.id
                    and inv.partner_id in %s
                    and inv.id not in %s'''                       
                    , (branch_id, partner_list, invoiceList ,))
            else:
                cr.execute(''' 
                    select  inv_line.id,inv_line.invoice_id,inv_line.product_id,pp.name_template, pp.default_code,
                            inv_line.quantity qty,inv_line.price_unit as price,inv_line.price_subtotal,
                            inv_line.discount,inv_line.discount_amt,inv_line.uos_id
                    from account_invoice inv, account_invoice_line inv_line, res_partner rp, product_product pp
                    where inv.id = inv_line.invoice_id
                    and inv.payment_type='credit' 
                    and inv.state='open' 
                    and inv.type = 'out_invoice'
                    and inv.branch_id = %s
                    and inv_line.product_id = pp.id
                    and residual > 0
                    and inv.partner_id = rp.id
                    and inv.partner_id in %s
                    '''                       
                    , (branch_id, partner_list ,))
                      
            data_line = cr.fetchall()                    
        print 'data_lineeeeeeeeeeeeeee', data_line        
        return data_line
    
    def create_ar_collection_journal_payment(self, cursor, user, vals, context=None):
        try:
            rental_obj = self.pool.get('ar.payment')
            str = "{" + vals + "}"
            str = str.replace("'',", "',")  # null
            str = str.replace(":',", ":'',")  # due to order_id
            str = str.replace("}{", "}|{")
            str = str.replace(":'}{", ":''}")
            new_arr = str.split('|')
            result = []
            for data in new_arr:
                x = ast.literal_eval(data)
                result.append(x)
            if result:
                for ar in result:
                    ref_no = ar['payment_id'].replace('\\', "")
                    print 'Ref No', ref_no
                    cursor.execute('''select max(id) from mobile_ar_collection where ref_no = %s and write_date::date = now()::date ''', (ref_no,))
                    data = cursor.fetchall()
                    if data:
                        collection_id = data[0][0]
                    else:
                        collection_id = None                    
                    
                    rental_result = {                    
                        'collection_id':collection_id,
                        'journal_id':ar['journal_id'],
                        'amount':ar['amount'],
                        'date':ar['date'],
                        'notes':ar['notes'].replace('\\', ""),
                        'cheque_no':ar['cheque_no'].replace('\\', ""),
                        'partner_id':ar['partner_id'].replace('\\', ""),
                        'sale_team_id':ar['sale_team_id'].replace('\\', ""),
                        'payment_code':ar['payment_code'].replace('\\', ""),
                    }
                    rental_obj.create(cursor, user, rental_result, context=context)
                    cheque_no =ar['cheque_no'].replace('\\', "")
                    cursor.execute("update account_creditnote set m_status ='used' where name=%s",(cheque_no,))                      
#                     noteObj = self.pool.get('account.creditnote')
#                     note_id = noteObj.search(cursor, user,  [('name', '=',  ar['cheque_no'].replace('\\', ""))],context=None)
#                     note_data = noteObj.browse(cursor, user,  note_id, context=context)
#                     note_data.write({'m_state':'used'})
                                        
            return True
        except Exception, e:
            print 'False'
            return False 

    def product_qty_in_stock(self, cr, uid, warehouse_id , context=None, **kwargs):
            cr.execute("""
            select product_id,qty_on_hand,main_group,name_template,price,sequence from
              (    
                select product.id as product_id,sum(qty) as qty_on_hand,product_temp.main_group as main_group,
                         product.name_template as name_template,product_temp.list_price as price,product.sequence
                         from  stock_quant quant, product_product product, product_template product_temp
                         where quant.location_id = %s
                         and quant.product_id = product.id
                         and product.product_tmpl_id = product_temp.id
                         and product.active = true
                       and main_group in (select principle_id from product_sale_group_principle_rel 
                        where sale_group_id in (select sale_group_id from crm_case_section where id 
                        in (select default_section_id from res_users where id =%s)))  
                         group by quant.product_id, main_group,name_template,product.id,price,product.sequence
            )A where qty_on_hand > 0  order by name_template
            """, (warehouse_id,uid,))   
            datas = cr.fetchall()        
            return datas
    
    def create_customer_asset(self, cursor, user, vals, context=None):
        try:
            rental_obj = self.pool.get('res.partner.asset')
            str = "{" + vals + "}"
            str = str.replace("'',", "',")  # null
            str = str.replace(":',", ":'',")  # due to order_id
            str = str.replace("}{", "}|{")
            str = str.replace(":'}{", ":''}")
            new_arr = str.split('|')
            result = []
            for data in new_arr:
                x = ast.literal_eval(data)
                result.append(x)
            if result:
                for ar in result:                            
                    cursor.execute('select id from asset_type where name = %s ', (ar['asset_type'],))
                    data = cursor.fetchall()
                    if data:
                        access_type_id = data[0][0]
                    else:
                        access_type_id = None        
                    cursor.execute('select id from asset_configuration where name = %s ', (ar['name'],))
                    data = cursor.fetchall()
                    if data:
                        asset_name_id = data[0][0]
                    else:
                        asset_name_id = None                                                
                    cursor.execute('select id From res_partner where customer_code  = %s ', (ar['customer_code'],))
                    data = cursor.fetchall()                
                    if data:
                        partner_id = data[0][0]
                    else:
                        partner_id = None 
                                                
                    rental_result = {                    
                        'partner_id':partner_id,
                        'code':ar['customer_code'],
                        'qty':ar['qty'],
                        'image':ar['image'],
                        'date':ar['date'],
                        'name':ar['asset_id'],
                        'asset_name_id':asset_name_id,
                        'asset_type':access_type_id,
                        'type':ar['type'],
                        'note': ar['note'],
                    }
                    rental_obj.create(cursor, user, rental_result, context=context)
            return True
        except Exception, e:
            print 'False'
            return False         


    def create_customer_asset_check(self, cursor, user, vals, context=None):
        try:
            rental_obj = self.pool.get('res.partner.asset.check')
            str = "{" + vals + "}"
            str = str.replace("'',", "',")  # null
            str = str.replace(":',", ":'',")  # due to order_id
            str = str.replace("}{", "}|{")
            str = str.replace(":'}{", ":''}")
            new_arr = str.split('|')
            result = []
            for data in new_arr:
                x = ast.literal_eval(data)
                result.append(x)
            if result:
                for ar in result:         
                    check_date=None    
                    is_image =False               
                    if ar['check_date']:
                        date_time = ar['check_date']
                        check_date = datetime.strptime(date_time, '%Y-%m-%d %I:%M:%S %p') - timedelta(hours=6, minutes=30)
                    if ar['check_by']:
                        team_name= ar['check_by']
                        cursor.execute("select id from crm_case_section where name=%s",(team_name,))
                        team_data=cursor.fetchone()
                        if team_data:
                            team_id =team_data[0]
                        else:
                            team_id=None
                    if ar['img_ref']:
                        is_image =True
                    if ar['asset_id']:
                        cursor.execute("select id,asset_name_id from res_partner_asset where name=%s",(ar['asset_id'],))
                        asset_data=cursor.fetchone()
                        if asset_data:
                            asset_id =asset_data[0]
                            asset_name_id =asset_data[1]
                        else:
                            asset_id=None
                            asset_name_id=None
                        
                    rental_result = {                    
                        'partner_id':ar['customer_id'],
                        'status':ar['status'],
                        'date':check_date,
                        'check_by':team_id,
                        'asset_id':asset_id,
                        'asset_name':asset_name_id,
                        'image':ar['asset_image'],
                        'is_image':is_image,                                  
                        'image_reference':ar['img_ref'],
                    }
                    rental_obj.create(cursor, user, rental_result, context=context)
            return True
        except Exception, e:
            print 'False'
            return False   
        
             
    def dayplan_is_update(self, cr, uid, team_id, late_date , context=None, **kwargs):
            
            flag = False
            lastdate = datetime.strptime(late_date, "%Y-%m-%d")
            print 'DateTime', lastdate
            cr.execute('select id from sale_plan_day where write_date > %s', (lastdate,))   
            datas = cr.fetchall()
            if datas:
                flag = True
            else:
                flag = False                     
            return flag
        
    def product_is_update(self, cr, uid, team_id, late_date , context=None, **kwargs):
            
            flag = False
            lastdate = datetime.strptime(late_date, "%Y-%m-%d")
            print 'DateTime', lastdate
            cr.execute('select id from product_template where write_date > %s', (lastdate,))   
            datas = cr.fetchall()
            if datas:
                flag = True
            else:
                flag = False                     
            return flag
        
    def customer_is_update(self, cr, uid, team_id, late_date , context=None, **kwargs):
            
            flag = False
            lastdate = datetime.strptime(late_date, "%Y-%m-%d")
            print 'DateTime', lastdate
            cr.execute(''' select id from res_partner A ,sale_team_customer_rel B
                    where A.id = B.partner_id
                    And A.write_date > %s
                    And B.sale_team_id = %s
            ''', (lastdate, team_id,))   
            datas = cr.fetchall()
            if datas:
                flag = True
            else:
                flag = False                     
            return flag
    
    def tripplan_is_update(self, cr, uid, team_id, late_date , context=None, **kwargs):
            
        try:
            flag = False
            lastdate = datetime.strptime(late_date, "%Y-%m-%d")
            print 'DateTime', lastdate
            cr.execute('''
            select p.id,p.date,p.sale_team,p.name,p.principal
             from sale_plan_trip p
            ,crm_case_section c,res_partner_sale_plan_trip_rel d, res_partner e
            where  p.sale_team=c.id
            and p.sale_team= %s
            and p.active = true 
            and p.id = d.sale_plan_trip_id
            and e.id = d.partner_id
            and (e.write_date > %s or p.write_date >  %s)
                ''', (team_id , lastdate, lastdate,))   
            datas = cr.fetchall()
            if datas:
                flag = True
            else:
                flag = False                   
            return flag
        except Exception, e:
            return False
    
    def res_partners_team(self, cr, uid, section_id, late_date, context=None, **kwargs):
        
        lastdate = datetime.strptime(late_date, "%Y-%m-%d")
        print 'DateTimeTEAN', lastdate
        
        cr.execute('''                                
        select A.id,A.name,A.image,A.is_company, A.image_small,replace(A.street,',',';') street,replace(A.street2,',',';') street2,A.city,A.website,
                     replace(A.phone,',',';') phone,A.township,replace(A.mobile,',',';') mobile,A.email,A.company_id,A.customer, 
                     A.customer_code,A.mobile_customer,A.shop_name ,
                     A.address,
                     A.zip,A.state_name,A.partner_latitude,A.partner_longitude,null,A.image_medium,A.credit_limit,
                     A.credit_allow,A.sales_channel,A.branch_id,A.pricelist_id,A.payment_term_id,A.outlet_type ,
                     A.city_id,A.township_id,A.country_id,A.state_id,A.unit,A.class_id,A.chiller,A.frequency_id,A.temp_customer,
                     A.is_consignment,A.hamper,A.is_bank,A.is_cheque,A.verify,A.pricelist
                     
                     from (
                     select RP.id,RP.name,'' as image,RP.is_company,null,
                     '' as image_small,RP.street,RP.street2,RC.name as city,RP.website,
                     RP.phone,RT.name as township,RP.mobile,RP.email,RP.company_id,RP.customer, 
                     RP.customer_code,RP.mobile_customer,OT.name as shop_name,RP.address,RP.zip ,RP.partner_latitude,RP.partner_longitude,RS.name as state_name,
                     substring(replace(cast(RP.image_medium as text),'/',''),1,5) as image_medium,RP.credit_limit,RP.credit_allow,
                     RP.sales_channel,RP.branch_id,RP.pricelist_id,RP.payment_term_id,RP.outlet_type,RP.city as city_id,RP.township as township_id,
                     RP.country_id,RP.state_id,RP.unit,RP.class_id,RP.chiller,RP.frequency_id,RP.temp_customer,RP.is_consignment,RP.hamper,
                     RP.is_bank,RP.is_cheque,RP.verify,pp.name as pricelist
                     from outlettype_outlettype OT,
                                             res_partner RP ,res_country_state RS, res_city RC,res_township RT,product_pricelist pp
                                            where RS.id = RP.state_id
                                            and RP.township =RT.id
                                            and RP.city = RC.id
                                            and RP.active = true                                            
                                            and RP.outlet_type = OT.id
                                            and RP.pricelist_id = pp.id   
                                            and RP.credit_allow =True                                         
                                            and RP.collection_team=%s
                        )A 
                        where A.customer_code is not null
            ''', (section_id ,))
        datas = cr.fetchall()
        return datas

# kzo Eidt
    def res_partners_return_day(self, cr, uid, section_id, day_id, pull_date  , context=None, **kwargs):
        section = self.pool.get('crm.case.section')
        sale_team_data = section.browse(cr, uid, section_id, context=context)
        is_supervisor=sale_team_data.is_supervisor    
        lastdate = datetime.strptime(pull_date, "%Y-%m-%d")
        #print 'DateTimePARTNER', lastdate
        if is_supervisor==True:
            where ='and SPD.sale_team in (select id from crm_case_section where supervisor_team= %s)' % (section_id,)
        else:
            where ='and SPD.sale_team = %s' % (section_id,)
        cr.execute('''                    
                     select A.id,A.name,A.image,A.is_company, A.image_small,replace(A.street,',',';') street, replace(A.street2,',',';') street2,A.city,A.website,
                     replace(A.phone,',',';') phone,A.township, replace(A.mobile,',',';') mobile,A.email,A.company_id,A.customer, 
                     A.customer_code,A.mobile_customer,A.shop_name ,
                     A.address,
                     A.zip,A.state_name,A.partner_latitude,A.partner_longitude,A.sale_plan_day_id,A.image_medium,A.credit_limit,
                     A.credit_allow,A.sales_channel,A.branch_id,A.pricelist_id,A.payment_term_id,A.outlet_type ,
                     A.city_id,A.township_id,A.country_id,A.state_id,A.unit,A.class_id,A.chiller,A.frequency_id,A.temp_customer,
                     A.is_consignment,A.hamper,A.is_bank,A.is_cheque,A.verify,A.pricelist
                     from (
                     select RP.id,RP.name,'' as image,RP.is_company,RPS.line_id as sale_plan_day_id,
                     '' as image_small,RP.street,RP.street2,RC.name as city,RP.website,
                     RP.phone,RT.name as township,RP.mobile,RP.email,RP.company_id,RP.customer, 
                     RP.customer_code,RP.mobile_customer,OT.name as shop_name,RP.address,RP.zip ,RP.partner_latitude,RP.partner_longitude,RS.name as state_name,
                     substring(replace(cast(RP.image_medium as text),'/',''),1,5) as image_medium,RP.credit_limit,RP.credit_allow,
                     RP.sales_channel,RP.branch_id,RP.pricelist_id,RP.payment_term_id,RP.outlet_type,RP.city as city_id,RP.township as township_id,
                     RP.country_id,RP.state_id,RP.unit,RP.class_id,RP.chiller,RP.frequency_id,RP.temp_customer,RP.is_consignment,RP.hamper,
                     RP.is_bank,RP.is_cheque,RP.verify,pp.name as pricelist
                     from sale_plan_day SPD ,outlettype_outlettype OT,
                                            sale_plan_day_line RPS , res_partner RP ,res_country_state RS, res_city RC,res_township RT,product_pricelist pp
                                            where SPD.id = RPS.line_id 
                                            and  RS.id = RP.state_id
                                            and RP.township =RT.id
                                            and RP.city = RC.id
                                            and RP.active = true
                                            and RP.pricelist_id = pp.id
                                            and RP.outlet_type = OT.id
                                            and RPS.partner_id = RP.id 
                                            %s
                                            and RPS.line_id = %%s       
                                            order by  RPS.sequence asc                         
                                                                                                                 
                        )A 
                        where A.customer_code is not null
            '''%(where),(day_id,))
        datas = cr.fetchall()
        #print 'sale_plan_data',datas
        return datas
    
# kzo Edit add Sale Plan Trip and Day ID
    def res_partners_return_trip(self, cr, uid, section_id, day_id , pull_date, context=None, **kwargs):
        
        section = self.pool.get('crm.case.section')
        sale_team_data = section.browse(cr, uid, section_id, context=context)
        is_supervisor=sale_team_data.is_supervisor    
        lastdate = datetime.strptime(pull_date, "%Y-%m-%d")
        print 'DateTime', lastdate
        if is_supervisor==True:
            where ='and SPT.sale_team in (select id from crm_case_section where supervisor_team= %s)' % (section_id,)
        else:
            where ='and SPT.sale_team = %s' % (section_id,)
        cr.execute('''        
                    select A.id,A.name,A.image,A.is_company,
                     A.image_small,replace(A.street,',',';') street,replace(A.street2,',',';') street2,A.city,A.website,
                     replace(A.phone,',',';') phone,A.township,A.mobile,A.email,A.company_id,A.customer, 
                     A.customer_code,A.mobile_customer,A.shop_name,
                     A.address,
                     A.zip,A.state_name,A.partner_latitude,A.partner_longitude,A.sale_plan_trip_id,A.image_medium,
                     A.credit_limit,A.credit_allow,A.sales_channel,A.branch_id,A.pricelist_id,A.payment_term_id ,A.outlet_type,
                    A.city_id,A.township_id,A.country_id,A.state_id,A.unit,A.class_id,A.chiller,A.frequency_id,A.temp_customer,
                    A.is_consignment,A.hamper,A.is_bank,A.is_cheque,A.verify,A.pricelist
                      from (
                     select RP.id,RP.name,'' as image,RP.is_company,
                     '' as image_small,RP.street,RP.street2,RC.name as city,RP.website,
                     RP.phone,RT.name as township,RP.mobile,RP.email,RP.company_id,RP.customer, 
                     RP.customer_code,RP.mobile_customer,OT.name as shop_name ,RP.address,RPT.sale_plan_trip_id,
                     RP.zip ,RP.partner_latitude,RP.partner_longitude,RS.name as state_name
                      ,substring(replace(cast(RP.image_medium as text),'/',''),1,5) as image_medium ,RP.credit_limit,RP.credit_allow,
                     RP.sales_channel,RP.branch_id,RP.pricelist_id,RP.payment_term_id,RP.outlet_type,RP.city as city_id,RP.township as township_id,
                     RP.country_id,RP.state_id,RP.unit,RP.class_id,RP.chiller,RP.frequency_id,RP.temp_customer ,RP.is_consignment,RP.hamper,
                     RP.is_bank,RP.is_cheque,RP.verify,pp.name as pricelist
                     from sale_plan_trip SPT , res_partner_sale_plan_trip_rel RPT , res_partner RP ,res_country_state RS ,
                     res_city RC, res_township RT,outlettype_outlettype OT ,product_pricelist pp
                     where SPT.id = RPT.sale_plan_trip_id 
                     and RPT.partner_id = RP.id 
                     and  RS.id = RP.state_id
                     and RP.outlet_type = OT.id
                     and  RP.city = RC.id
                     and RP.pricelist_id = pp.id 
                     and RP.township = RT.id
                     and RP.active = true
                     %s
                     and RPT.sale_plan_trip_id = %%s
                        )A 
                    where A.customer_code is not null 
            ''' %(where),(day_id,))
        datas = cr.fetchall()
        return datas

    def get_promo_partner_category(self, cr, uid , context=None):        
        cr.execute('''select rel.* from promotion_rule_category_rel rel,promos_rules rule where rule.id =rel.promotion_id  and now()::date between from_date::date and to_date::date''')
        datas = cr.fetchall()        
        return datas

    def push_credit_job(self, cr, uid,date, context=None, **kwargs):
        cr.execute('''update queue_job set is_credit_invoice=False where user_id=%s and date_created::date=%s''', (uid,date,))
        return True    
        
    def get_partner_category_rel(self, cr, uid, section_id , context=None):  
        section = self.pool.get('crm.case.section')      
        sale_team_data = section.browse(cr, uid, section_id, context=context)
        is_supervisor=sale_team_data.is_supervisor    
        if is_supervisor==True:

            cr.execute('''(select distinct a.* from res_partner_res_partner_category_rel a,
                     sale_plan_day_line b
                     , sale_plan_day p
                    where a.partner_id = b.partner_id
                    and b.line_id = p.id
                    and p.sale_team in (select id from crm_case_section where supervisor_team= %s)
                    )
                    UNION ALL
                    (select distinct a.* from res_partner_res_partner_category_rel a,sale_plan_trip p,
                     res_partner_sale_plan_trip_rel b
                    where a.partner_id = b.partner_id
                    and b.sale_plan_trip_id = p.id
                    and p.sale_team in (select id from crm_case_section where supervisor_team= %s))
                    UNION ALL
                    (
                    select distinct a.* 
                    from sale_order so,res_partner_res_partner_category_rel a
                    WHERE  a.partner_id = so.partner_id
                    AND so.pre_order = TRUE 
                    AND so.delivery_id  in (select id from crm_case_section where supervisor_team= %s))
                    AND shipped = False
                    AND invoiced = False
                    AND ecommerce =TRUE)
                    
                    ''', (section_id, section_id,section_id,))
            datas = cr.fetchall()     
        else:
            cr.execute('''(select distinct a.* from res_partner_res_partner_category_rel a,
             sale_plan_day_line b
             , sale_plan_day p
            where a.partner_id = b.partner_id
            and b.line_id = p.id
            and p.sale_team = %s
            )
            UNION ALL
            (select distinct a.* from res_partner_res_partner_category_rel a,sale_plan_trip p,
             res_partner_sale_plan_trip_rel b
            where a.partner_id = b.partner_id
            and b.sale_plan_trip_id = p.id
            and p.sale_team = %s
            )
            UNION ALL
            (
            select distinct a.* 
            from sale_order so,res_partner_res_partner_category_rel a
            WHERE  a.partner_id = so.partner_id
            AND so.pre_order = TRUE 
            AND so.delivery_id =%s
            AND shipped = False
            AND invoiced = False
            AND ecommerce =TRUE)            
            ''', (section_id, section_id,section_id,))
            datas = cr.fetchall()    
        return datas
    
#     def get_monthly_promotion_history(self, cr, uid, section_id , context=None, **kwargs):
#             cr.execute("""
#             select promotion_id,date, partner_id,section_id from sales_promotion_history where section_id = %s
#             and  date between date_trunc('month', current_date)::date
#             and  DATE_TRUNC('month', CURRENT_DATE) + INTERVAL '1 month'  - INTERVAL '1 day' 
#             """, (section_id,))   
#             datas = cr.fetchall()        
#             return datas
        
    def get_monthly_promotion_history(self, cr, uid, section_id , context=None, **kwargs):
            cr.execute("""
            select promotion_id,date, partner_id,section_id from 
            sales_promotion_history h,promos_rules r where 
            h.promotion_id=r.id
            and section_id = %s and date between r.from_date and r.to_date order by promotion_id
            """, (section_id,))   
            datas = cr.fetchall()        
            return datas
    
    def create_monthly_promotion_history(self, cursor, user, vals, context=None):
                    
            promo_his_obj = self.pool.get('sales.promotion.history')
            str = "{" + vals + "}"    
            str = str.replace("'',", "',")  # null
            str = str.replace(":',", ":'',")  # due to order_id
            str = str.replace("}{", "}|{")
            str = str.replace(":'}{", ":''}")
            new_arr = str.split('|')
            result = []
            for data in new_arr:            
                x = ast.literal_eval(data)                
                result.append(x)
            month_history = []
            for r in result:                
                month_history.append(r)  
            if month_history:
                for pro in month_history:
                                                
                    pro_his = {
                        'section_id':pro['section_id'],
                        'partner_id':pro['partner_id'],
                        'promotion_id':pro['promotion_id'],
                        'date':pro['date'],
                        'user_id':pro['user_id'],
                    }
                    promo_his_obj.create(cursor, user, pro_his, context=context)
            return True
    
mobile_sale_order()

class mobile_sale_order_line(osv.osv):
    
    _name = "mobile.sale.order.line"
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
        'uom_id':fields.many2one('product.uom', 'UOM', readonly=False),
#        'uom_id':fields.function(_get_uom_from_product, type='many2one', relation='product.uom', string='UOM'),
        'price_unit':fields.float('Unit Price'),
        'discount':fields.float('Discount (%)'),
        'discount_amt':fields.float('Discount (Amt)'),
        'order_id': fields.many2one('mobile.sale.order', 'Sale Order'),
        'sub_total':fields.float('Sub Total'),
        'foc':fields.boolean('FOC'),
        'manual_foc':fields.boolean('Manual Foc'),
        'promotion_id': fields.many2one('promos.rules', 'Promotion', readonly=True)  
    }
    _defaults = {
       'product_uos_qty':1.0,
    }   
    
mobile_sale_order_line()

class sale_group(osv.osv):
    _inherit = 'res.users' 
 
    
sale_group()

class mso_promotion_line(osv.osv):
    _name = 'mso.promotion.line'
    _columns = {
              'promo_line_id':fields.many2one('mobile.sale.order', 'Promotion line'),
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
            datas = promo_pool.read(cr, uid, pro_id, ['from_date', 'to_date', 'manual'], context=context)
    
            if datas:
                result.update({'from_date':datas['from_date']})
                result.update({'to_date':datas['to_date']})
                result.update({'manual':datas['manual']})
            return {'value':result}
            
mso_promotion_line()
            
mso_promotion_line()

class mobile_product_yet_to_deliver_line(osv.osv):
    
    _name = "products.to.deliver"
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
        'sale_order_id': fields.many2one('mobile.sale.order', 'Sale Order'),
                }
mobile_product_yet_to_deliver_line()

# class account_invoice(osv.osv):
  #  _inherit = "account.invoice"
  
    # _columns = {
         #    'payment_type': fields.char('Payment Type', size=64, readonly=True),
            #   }
# account_invoice()    
 
class sale_order(osv.osv):
    _inherit = "sale.order" 
    
    def _make_invoice(self, cr, uid, order, lines, context=None):
        inv_obj = self.pool.get('account.invoice')
        obj_invoice_line = self.pool.get('account.invoice.line')
        
        if context is None:
            context = {}
        invoiced_sale_line_ids = self.pool.get('sale.order.line').search(cr, uid, [('order_id', '=', order.id), ('invoiced', '=', True)], context=context)
        from_line_invoice_ids = []
        for invoiced_sale_line_id in self.pool.get('sale.order.line').browse(cr, uid, invoiced_sale_line_ids, context=context):
            for invoice_line_id in invoiced_sale_line_id.invoice_lines:
                if invoice_line_id.invoice_id.id not in from_line_invoice_ids:
                    from_line_invoice_ids.append(invoice_line_id.invoice_id.id)
        for preinv in order.invoice_ids:
            if preinv.state not in ('cancel',) and preinv.id not in from_line_invoice_ids:
                for preline in preinv.invoice_line:
                    inv_line_id = obj_invoice_line.copy(cr, uid, preline.id, {'invoice_id': False, 'price_unit':-preline.price_unit})
                    lines.append(inv_line_id)
        inv = self._prepare_invoice(cr, uid, order, lines, context=context)

        # inv = self.prepare_invoice(cr, uid, order, lines, context=context)
        
        inv_id = inv_obj.create(cr, uid, inv, context=context)
        if order.credit_history_ids:
            for invoice_data in order.credit_history_ids:
                    credit_vals = {
                                 'invoice_id':inv_id,
                                'date':invoice_data.date,
                                'invoice_no':invoice_data.invoice_no,
                                'invoice_amt':invoice_data.invoice_amt,
                                'paid_amount':invoice_data.paid_amount,
                                'balance':invoice_data.balance,
                                'due_date':invoice_data.due_date,
                                'balance_day':invoice_data.balance_day,
                                'branch_id':invoice_data.branch_id.id,
                                'status':invoice_data.status,
                                          }             
                    self.pool.get('account.invoice.credit.history').create(cr, uid, credit_vals, context=context)        
        data = inv_obj.onchange_payment_term_date_invoice(cr, uid, [inv_id], inv['payment_term'], time.strftime(DEFAULT_SERVER_DATE_FORMAT))
        if data.get('value', False):
            inv_obj.write(cr, uid, [inv_id], data['value'], context=context)
        inv_obj.button_compute(cr, uid, [inv_id])
        # self.message_post(cr, uid, [order.id], body=_("test created"), context=context)
        # inv_obj.message_post(cr, uid, [inv_id], body=_("test created"), context=context)
                
        
        if order.payment_type == 'credit':
            self.send_message_or_not(cr, uid, order.partner_invoice_id.credit_limit, order.amount_total, inv_id, context)
                
            # self.send_message_or_not(cr, uid, order.partner_invoice_id.credit_limit, order.amount_total, inv_id, order.id, context)
        return inv_id
    
    def send_message_or_not(self, cr, uid, credit_limit, total_amt, invoice_id, context=None):
        inv_obj = self.pool.get('account.invoice')
        
        if credit_limit < total_amt and credit_limit > 0:
            inv_obj.message_post(cr, uid, [invoice_id], body=_("Total amount exceed the credit limit"), context=context)  

        return True  
          
    def _prepare_invoice(self, cr, uid, order, lines, context=None):
        """Prepare the dict of values to create the new invoice for a
           sales order. This method may be overridden to implement custom
           invoice generation (making sure to call super() to establish
           a clean extension chain).
    
           :param browse_record order: sale.order record to invoice
           :param list(int) line: list of invoice line IDs that must be
                                  attached to the invoice
           :return: dict of value to create() the invoice
        """
        
        if context is None:
            context = {}
        journal_ids = self.pool['account.invoice'].default_get(cr, uid, ['journal_id'], context=context)['journal_id']
        if journal_ids:
            try:
                journal_ids = journal_ids[0]
            except Exception, e:
                journal_ids = journal_ids
                
        if not journal_ids:
            raise osv.except_osv(_('Error!'),
                _('Please define sales journal for this company: "%s" (id:%d).') % (order.company_id.name, order.company_id.id))
        payment_type = None
        if order.payment_type == 'credit':
            payment_type = 'Credit'    
        invoice_vals = {
            'name': order.client_order_ref or '',
            'origin': order.name,
            'type': 'out_invoice',
            'reference': order.client_order_ref or order.name,
            'account_id': order.partner_invoice_id.property_account_receivable.id,
            'partner_id': order.partner_invoice_id.id,
            'journal_id': journal_ids,
            'invoice_line': [(6, 0, lines)],
            'currency_id': order.pricelist_id.currency_id.id,
            'comment': order.note,
            'payment_term': order.payment_term and order.payment_term.id or False,
            'fiscal_position': order.fiscal_position.id or order.partner_invoice_id.property_account_position.id,
            'date_invoice': context.get('date_invoice', False),
            'company_id': order.company_id.id,
            'user_id': order.user_id and order.user_id.id or False,
            'section_id' : order.section_id.id,
            'payment_type': payment_type,
        }
        
        # Care for deprecated _inv_get() hook - FIXME: to be removed after 6.1
        invoice_vals.update(self._inv_get(cr, uid, order, context=context))
        return invoice_vals           
sale_order()

class partner_photo(osv.osv):
    _name = "partner.photo"
    _description = "Patner Photo"

    _columns = {       
        'customer_id':fields.many2one('res.partner', 'Customer', domain="[('customer','=',True)]"),
        'customer_code':fields.char('Customer Code'),
        'comment':fields.char('comment'),
        'image_one':fields.binary('image_one'),
        'image_two':fields.binary('image_two'),
        'image_three':fields.binary('image_three'),
        'image_four':fields.binary('image_four'),
        'image_five':fields.binary('image_five'),
        'partner_latitude': fields.float('Geo Latitude', digits=(16, 5), readonly=True),
        'partner_longitude': fields.float('Geo Longitude', digits=(16, 5), readonly=True),
       }
partner_photo()    
