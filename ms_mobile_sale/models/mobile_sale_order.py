from openerp.osv import fields, osv
from openerp.osv import orm
from datetime import datetime
import ast
import time
DEFAULT_SERVER_DATE_FORMAT = "%Y-%m-%d"
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
       'promos_line_ids':fields.one2many('mso.promotion.line', 'promo_line_id', 'Promotion Lines')                
    }
    _order = 'id desc'
    _defaults = {
        'date': datetime.now(),
        'm_status' : 'draft',
       
    } 
    
    def create_massive(self, cursor, user, vals, context=None):
        print 'vals', vals
        sale_order_name_list = []
        try : 
            mobile_sale_order_obj = self.pool.get('mobile.sale.order')
            mobile_sale_order_line_obj = self.pool.get('mobile.sale.order.line')
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
                if len(r) >= 28:
                    sale_order.append(r)
                else:
                    sale_order_line.append(r)
            
            if sale_order:
                for so in sale_order:
                   # print 'Sale Man Id', so['user_id']
                   # print 'Sale Void', so['void_flag']
                   # cursor.execute('select id From res_users where partner_id  = %s ', (so['user_id'],))
                   # data = cursor.fetchall()
                    # if data:
                    #    saleManId = data[0][0]
                  #  else:
                     #   saleManId = None
                    
                    cursor.execute('select id From outlettype_outlettype where name  = %s ', (so['outlet_type'],))
                    data = cursor.fetchall()
                    print 'outlet type data', data
                    if data:
                        outlet_type = data[0][0]
                    else:
                        outlet_type = None

                    mso_result = {
                        'customer_code':so['customer_code'],
                        'sale_plan_day_id':so['sale_plan_day_id'],
                        'sale_plan_trip_id':so['sale_plan_trip_id'] ,
                        'paid': True,
                        'warehouse_id':so['warehouse_id'],
                        'tablet_id':so['tablet_id'],
                        'delivery_remark':so['delivery_remark'],
                        'location_id':so['location_id'],
                        'deduction_amount':so['deduction_amount'],
                        'user_id':so['user_id'],
                        'name':so['name'],
                        'paid_amount':so['paid_amount'],
                        'partner_id':so['partner_id'],
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
                        'outlet_type':outlet_type
                    }
                    s_order_id = mobile_sale_order_obj.create(cursor, user, mso_result, context=context)
                    print "Create Sale Order", so['name']
                    for sol in sale_order_line:
                        if sol['so_name'] == so['name']:
                                cursor.execute('select id From product_product where product_tmpl_id  = %s ', (sol['product_id'],))
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
                                  'product_uos_qty':sol['product_uos_qty'],
                                  'foc': foc_val,
                                  'discount':sol['discount'],
                                  'discount_amt':sol['discount_amt'],
                                  'sub_total':sol['sub_total'],
                                }
                                mobile_sale_order_line_obj.create(cursor, user, mso_line_res, context=context) 
                                print 'Create Order line', sol['so_name']                     
                    sale_order_name_list.append(so['name'])
            print 'True'
            return True       
        except Exception, e:
            print 'False'
            return False 
    
# NZO
    def create_exchange_product(self, cursor, user, vals, context=None):
        print 'vals', vals
        try : 
            product_trans_obj = self.pool.get('product.transactions')
            product_trans_line_obj = self.pool.get('product.transactions.line')
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
                if len(r) >= 13:
                    product_trans_line.append(r)                   
                else:
                    product_trans.append(r)
            
            if product_trans:
                for pt in product_trans:
#                     print 'Sale Man Id',so['user_id']
#                     print 'Sale Void', so['void_flag']
#                     cursor.execute('select id From res_users where partner_id  = %s ',(so['user_id'],))
#                     data = cursor.fetchall()
#                     if data:
#                         saleManId = data[0][0]
#                     else:
#                         saleManId = None
                    mso_result = {
                        'transaction_id':pt['transaction_id'],
                        'customer_id':pt['customer_id'],
                        'customer_code':pt['customer_code'] ,
                        'team_id':pt['team_id'],
                        'date':pt['date'],
                        'exchange_type':pt['exchange_type'],
                        'void_flag':pt['void_flag'],
                        'location_id':pt['location_id'],
                    }
                    s_order_id = product_trans_obj.create(cursor, user, mso_result, context=context)
                    
                    for ptl in product_trans_line:
                        if ptl['transaction_id'] == pt['transaction_id']:
                                mso_line_res = {                                                            
                                  'transaction_id':s_order_id,
                                  'product_id':ptl['product_id'],
                                  'product_qty':ptl['product_qty'],
                                  'so_No':ptl['so_No'],
                                  'trans_type':ptl['trans_type'],
                                  'transaction_name':ptl['transaction_name'],
                                  'note':ptl['note'],
                                  'exp_date':ptl['exp_date'],
                                  'batchno':ptl['batchno'],
                                }
                                product_trans_line_obj.create(cursor, user, mso_line_res, context=context)
            print 'True'
            return True       
        except Exception, e:
            print 'False'
            return False     
    
    def create_visit(self, cursor, user, vals, context=None):
        print 'vals', vals
        customer_visit_obj = self.pool.get('customer.visit')
        str = "{" + vals + "}"
#             str = str.replace(":''",":'")#change Order_id
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
            print "length", len(r)
            customer_visit.append(r)  
        if customer_visit:
            for vs in customer_visit:
                visit_result = {
                    'customer_code':vs['customer_code'],
                    'customer_id':vs['customer_id'],
                    'sale_plan_day_id':vs['sale_plan_day_id'],
                    'sale_plan_trip_id':vs['sale_plan_trip_id'] ,
                    'sale_plan_name':vs['sale_plan_name'],
                    'sale_team':vs['sale_team'],
                    'sale_team_id':vs['sale_team_id'],
                    'user_id':vs['user_id'],
                    'date':vs['date'],
                    'user_id':vs['visit_reason'],
                    'tablet_id':vs['tablet_id'],
                    'other_reason':vs['other_reason'],
                    'visit_reason':vs['visit_reason'],
                    'latitude':vs['latitude'],
                    'longitude':vs['longitude'],
                }
                customer_visit_obj.create(cursor, user, visit_result, context=context)
        return True
    
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
  #  def action_convert_so(self, cr, uid, ids, context=None):
  #      for saleorder in self.browse(cr, uid, ids, context=context):            
   #         cr.execute('SELECT import_data_from_mobile_to_server(%s,%s)', (saleorder['id'], saleorder['name']))
  #          cr.execute("update mobile_sale_order set m_status='done' where id = %s and name = %s ", (saleorder['id'], saleorder['name'],))
    # MMK   
    def action_convert_so(self, cr, uid, ids, context=None):
        msoObj = self.pool.get('mobile.sale.order')
        soObj = self.pool.get('sale.order')
        solObj = self.pool.get('sale.order.line')
        invObj = self.pool.get("sale.advance.payment.inv")
        invoiceObj = self.pool.get('account.invoice')
        voucherObj = self.pool.get('account.voucher')
        voucherLineObj = self.pool.get('account.voucher.line')
        stockPickingObj = self.pool.get('stock.picking')
        stockDetailObj = self.pool.get('stock.transfer_details')
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
            try:
                # default price list need in sale order form
                cr.execute("""select id from product_pricelist where type = 'sale' """)
                data = cr.fetchall()
                if data:
                    pricelist_id = data[0][0]
    
                cr.execute("select TI.sale_team_id from  mobile_sale_order msol,tablets_information TI where msol.tablet_id=TI.id and msol.id=%s", (ids[0],))
                sale_team_id = cr.fetchone()
                if sale_team_id:
                    sale_team_id = sale_team_id[0]
                cr.execute("select cc.analytic_account_id from crm_case_section cc,mobile_sale_order mso where mso.sale_team=cc.id and mso.id=%s", (ids[0],))
                analytic_id = cr.fetchone()
                if analytic_id:
                    analytic_id = analytic_id[0]
                else:
                    analytic_id = False
    
                for ms_ids in msoObj.browse(cr, uid, ids[0], context=context):
                    if ms_ids:
                        if ms_ids.void_flag == 'voided':  # they work while payment type not 'cash' and 'credit'
                            so_state = 'cancel'
                        elif ms_ids.void_flag == 'none':
                            so_state = 'draft'
                        soResult = {
                                              'date_order':ms_ids.date,
                           'partner_id':ms_ids.partner_id.id,
                           'amount_untaxed':ms_ids.amount_total ,
                           'partner_invoice_id':ms_ids.partner_id.id,
                           'user_id':ms_ids.user_id.id,
                           'date_confirm':ms_ids.date,
                           'amount_total':ms_ids.amount_total,
                           'order_policy':'manual',
                           'company_id':1,
                           'payment_term':ms_ids.payment_term.id,
                            'state':so_state,
                            'pricelist_id':pricelist_id,
                            'picking_policy':'direct',
                            'warehouse_id':ms_ids.warehouse_id.id,
                            'project_id':analytic_id,
                            'partner_shipping_id':ms_ids.partner_id.id,
                            # 'shipped':'f',
                            'tb_ref_no':ms_ids.name,
                            'sale_plan_name':ms_ids.sale_plan_name,
                            'payment_type':ms_ids.type,
                            'section_id':sale_team_id,
                            'due_date':ms_ids.due_date,
                            'so_latitude':ms_ids.mso_latitude,
                            'so_longitude':ms_ids.mso_longitude,
                            # 'total_dis':additional_discount,
                            'deduct_amt':ms_ids.deduction_amount,
                            'delivery_remark':ms_ids.delivery_remark,
                            'sale_plan_day_id':ms_ids.sale_plan_day_id.id,
                            'sale_plan_trip_id':ms_ids.sale_plan_trip_id.id,
                            'customer_code':ms_ids.customer_code 
                                            }
                        soId = soObj.create(cr, uid, soResult, context=context)
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
                                                product_name = '[' + default_code + ']' + line_id.product_id.name
                                            else:
                                                product_name = line_id.product_id.name
                                            # FOC with price_unit or foc true, false
                                        if line_id.price_unit == 0.0 or line_id.foc:
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
                                                  'product_uom':1,
                                                  'product_uom_qty':line_id.product_uos_qty,
                                                  'discount':line_id.discount,
                                                  'discount_amt':line_id.discount_amt,
                                                  'company_id':1,  # company_id,
                                                  'state':'draft',
                                                  'net_total':line_id.sub_total,
                                                  'sale_foc':foc
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
                                soObj.action_button_confirm(cr, uid, solist, context=context)
                                # Create Invoice
                                invoice_id = self.create_invoices(cr, uid, solist, context=context)
                                invoiceObj.button_reset_taxes(cr, uid, [invoice_id], context=context)
                                if invoice_id and ms_ids.paid == True:
                                    invlist = []
                                    invlist.append(invoice_id)
                                    # call the api function
                                    # invObj contain => account.invoice(1,) like that
                                    invObj = invoiceObj.browse(cr, uid, invoice_id, context=context)
                                    invObj.action_date_assign()
                                    invObj.action_move_create()
                                    invObj.action_number()
                                    # validate invoice
                                    invObj.invoice_validate()
                                    
                                    # register Payment
                                    # calling the register payment pop-up
                                    invoiceObj.invoice_pay_customer(cr, uid, invlist, context=context)
                                    cr.execute('select id from account_journal where type=%s', ('cash',))
                                    data = cr.fetchall()
                                    if data:
                                        journal_id = data[0]
                                    cr.execute('select id from account_account where lower(name)=%s and active= %s', ('cash', True,))  # which account shall I choose. It is needed.
                                    data = cr.fetchall()
                                    if data:
                                        accountId = data[0]
                                    if journal_id and accountId:  # cash journal and cash account. If there no journal id or no account id, account invoice is not make payment.
                                        accountVResult = {
                                                        'partner_id':invObj.partner_id.id,
                                                        'amount':invObj.amount_total,
                                                        'journal_id':journal_id,
                                                        'date':invObj.date_invoice,
                                                        'period_id':invObj.period_id.id,
                                                        'account_id':accountId,
                                                        'pre_line':True,
                                                        'type':'receipt'
                                                        }
                                        # create register payment voucher
                                        voucherId = voucherObj.create(cr, uid, accountVResult, context=context)
                                        
                                    if voucherId:
                                        vlist = []
                                        vlist.append(voucherId)
                                        # get the voucher lines
                                        vlresult = voucherObj.recompute_voucher_lines(cr, uid, vlist, invObj.partner_id.id, journal_id, invObj.amount_total, 120, 'receipt', invObj.date_invoice, context=None)
                                        if vlresult:
                                            result = vlresult['value']['line_cr_ids'][0]
                                            result['voucher_id'] = voucherId
                                            # create the voucher lines
                                            voucherLineObj.create(cr, uid, result, context=context)
                                        # invoice register payment done
                                        voucherObj.button_proforma_voucher(cr, uid, vlist , context=context)
                                        # invoice paid status is true
                                        invFlag = True
                                # clicking the delivery order view button
                                stockViewResult = soObj.action_view_delivery(cr, uid, solist, context=context)    
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
                                        
                            if ms_ids.type == 'cash' and ms_ids.delivery_remark == 'none':  # Payment Type=>Cash and Delivery Remark=>None
                                # SO Confirm 
                                soObj.action_button_confirm(cr, uid, solist, context=context)
                                # Create Invoice
                                invoice_id = self.create_invoices(cr, uid, solist, context=context)
                                invoiceObj.button_reset_taxes(cr, uid, [invoice_id], context=context)
                                if invoice_id and ms_ids.paid == True:
                                    invlist = []
                                    invlist.append(invoice_id)
                                    # call the api function
                                    # invObj contain => account.invoice(1,) like that
                                    invObj = invoiceObj.browse(cr, uid, invoice_id, context=context)
                                    invObj.action_date_assign()
                                    invObj.action_move_create()
                                    invObj.action_number()
                                    # validate invoice
                                    invObj.invoice_validate()
                                    
                                    # register Payment
                                    # calling the register payment pop-up
                                    invoiceObj.invoice_pay_customer(cr, uid, invlist, context=context)
                                    cr.execute('select id from account_journal where type=%s', ('cash',))
                                    data = cr.fetchall()
                                    if data:
                                        journal_id = data[0]
                                    cr.execute('select id from account_account where lower(name)=%s and active= %s', ('cash', True,))  # which account shall I choose. It is needed.
                                    data = cr.fetchall()
                                    if data:
                                        accountId = data[0]
                                    if journal_id and accountId:  # cash journal and cash account. If there no journal id or no account id, account invoice is not make payment.
                                        accountVResult = {
                                                        'partner_id':invObj.partner_id.id,
                                                        'amount':invObj.amount_total,
                                                        'journal_id':journal_id,
                                                        'date':invObj.date_invoice,
                                                        'period_id':invObj.period_id.id,
                                                        'account_id':accountId,
                                                        'pre_line':True,
                                                        'type':'receipt'
                                                        }
                                        # create register payment voucher
                                        voucherId = voucherObj.create(cr, uid, accountVResult, context=context)
                                        
                                    if voucherId:
                                        vlist = []
                                        vlist.append(voucherId)
                                        # get the voucher lines
                                        vlresult = voucherObj.recompute_voucher_lines(cr, uid, vlist, invObj.partner_id.id, journal_id, invObj.amount_total, 120, 'receipt', invObj.date_invoice, context=None)
                                        if vlresult:
                                            result = vlresult['value']['line_cr_ids'][0]
                                            result['voucher_id'] = voucherId
                                            # create the voucher lines
                                            voucherLineObj.create(cr, uid, result, context=context)
                                        # invoice register payment done
                                        voucherObj.button_proforma_voucher(cr, uid, vlist , context=context)
                                        # invoice paid status is true
                                        invFlag = True
                                # clicking the delivery order view button
                                soObj.action_view_delivery(cr, uid, solist, context=context)  # create the delivery with draft state
                                        
                            if ms_ids.type == 'cash' and ms_ids.delivery_remark == 'partial':  # Payment Type=>Cash and Delivery Remark=>None
                                # SO Confirm 
                                soObj.action_button_confirm(cr, uid, solist, context=context)
                                # Create Invoice
                                invoice_id = self.create_invoices(cr, uid, solist, context=context)
                                invoiceObj.button_reset_taxes(cr, uid, [invoice_id], context=context)
                                if invoice_id and ms_ids.paid == True:
                                    invlist = []
                                    invlist.append(invoice_id)
                                    # call the api function
                                    # invObj contain => account.invoice(1,) like that
                                    invObj = invoiceObj.browse(cr, uid, invoice_id, context=context)
                                    invObj.action_date_assign()
                                    invObj.action_move_create()
                                    invObj.action_number()
                                    # validate invoice
                                    invObj.invoice_validate()
                                    
                                    # register Payment
                                    # calling the register payment pop-up
                                    invoiceObj.invoice_pay_customer(cr, uid, invlist, context=context)
                                    cr.execute('select id from account_journal where type=%s', ('cash',))
                                    data = cr.fetchall()
                                    if data:
                                        journal_id = data[0]
                                    cr.execute('select id from account_account where lower(name)=%s and active= %s and type=%s ', ('cash', True, 'liquidity',))  # which account shall I choose. It is needed.
                                    data = cr.fetchall()
                                    if data:
                                        accountId = data[0]
                                    if journal_id and accountId:  # cash journal and cash account. If there no journal id or no account id, account invoice is not make payment.
                                        accountVResult = {
                                                        'partner_id':invObj.partner_id.id,
                                                        'amount':invObj.amount_total,
                                                        'journal_id':journal_id,
                                                        'date':invObj.date_invoice,
                                                        'period_id':invObj.period_id.id,
                                                        'account_id':accountId,
                                                        'pre_line':True,
                                                        'type':'receipt'
                                                        }
                                        # create register payment voucher
                                        voucherId = voucherObj.create(cr, uid, accountVResult, context=context)
                                        
                                    if voucherId:
                                        vlist = []
                                        vlist.append(voucherId)
                                        # get the voucher lines
                                        vlresult = voucherObj.recompute_voucher_lines(cr, uid, vlist, invObj.partner_id.id, journal_id, invObj.amount_total, 120, 'receipt', invObj.date_invoice, context=None)
                                        if vlresult:
                                            result = vlresult['value']['line_cr_ids'][0]
                                            result['voucher_id'] = voucherId
                                            # create the voucher lines
                                            voucherLineObj.create(cr, uid, result, context=context)
                                        # invoice register payment done
                                        voucherObj.button_proforma_voucher(cr, uid, vlist , context=context)
                                        # invoice paid status is true
                                        invFlag = True
                                # clicking the delivery order view button
                                soObj.action_view_delivery(cr, uid, solist, context=context)  # create the delivery with draft state
                                
                            if ms_ids.type == 'credit' and ms_ids.delivery_remark == 'delivered':  # Payment Type=>Credit and Delivery Remark=>Delivered
                                # so Confirm
                                soObj.action_button_confirm(cr, uid, solist, context=context)
                                # invoice create at draft state
                                invoice_id = self.create_invoices(cr, uid, solist, context=context)
                                invoiceObj.button_reset_taxes(cr, uid, [invoice_id], context=context)
                                # clicking the delivery order view button
                                stockViewResult = soObj.action_view_delivery(cr, uid, solist, context=context)    
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

                            if ms_ids.type == 'credit' and ms_ids.delivery_remark == 'none':  # Payment Type=>Credit and Delivery Remark=>None
                                # so Confirm
                                soObj.action_button_confirm(cr, uid, solist, context=context)
                                # invoice create at draft state
                                invoice_id = self.create_invoices(cr, uid, solist, context=context)
                                invoiceObj.button_reset_taxes(cr, uid, [invoice_id], context=context)
                                # clicking the delivery order view button
                                stockViewResult = soObj.action_view_delivery(cr, uid, solist, context=context)  # create delivery order with draft state
                                
                            if ms_ids.type == 'credit' and ms_ids.delivery_remark == 'partial':  # Payment Type=>Credit and Delivery Remark=>Partial
                                # so Confirm
                                soObj.action_button_confirm(cr, uid, solist, context=context)
                                # invoice create at draft state
                                invoice_id = self.create_invoices(cr, uid, solist, context=context)
                                invoiceObj.button_reset_taxes(cr, uid, [invoice_id], context=context)
                                # clicking the delivery order view button
                                stockViewResult = soObj.action_view_delivery(cr, uid, solist, context=context)  # create delivery order with draft state
            except Exception, e:
                raise orm.except_orm(_('Error :'), _("Error Occured while Convert Mobile Sale Order! \n [ %s ]") % (e))
            self.write(cr, uid, ids[0], {'m_status':'done'}, context=context)
            if invFlag == True:
                invoiceObj.write(cr, uid, invlist[0], {'state':'paid'}, context=context)
        return True   
    # MMK
    def create_invoices(self, cr, uid, ids, context=None):
        """ create invoices for the active sales orders """
        sale_obj = self.pool.get('sale.order')
        sale_ids = ids
        if sale_ids:
            # create the final invoices of the active sales orders
            print 'YOOOOOOOOOOOOO'
            res = sale_obj.manual_invoice(cr, uid, sale_ids, context)
            if context.get('open_invoices', False):
                return res
            return res['res_id']
    # kzo Edit
    def get_products_by_sale_team(self, cr, uid, section_id , context=None, **kwargs):
        cr.execute('''select  pp.product_tmpl_id,pt.list_price , pt.description,pt.categ_id,pc.name as categ_name,pp.default_code, 
                         pt.name,substring(replace(cast(pt.image_small as text),'/',''),1,5) as image_small,pt.main_group,pt.uom_ratio
                        from crm_case_section_product_product_rel crm_real ,
                        crm_case_section ccs ,product_template pt, product_product pp , product_category pc
                        where pp.id = crm_real.product_product_id
                        and pt.id = pp.product_tmpl_id
                        and ccs.id = crm_real.crm_case_section_id
                        and pc.id = pt.categ_id           
                        and ccs.id = %s ''', (section_id,))
        datas = cr.fetchall()
        return datas
    
    def get_salePlanDays_by_sale_team(self, cr, uid, section_id , context=None, **kwargs):
        cr.execute('''select id,name,date,sale_team from sale_plan_day where sale_team=%s ''', (section_id,))
        datas = cr.fetchall()
        cr.execute
        return datas
    
    # get promotion datas from database
    def get_products_categ_by_sale_team(self, cr, uid, section_id , context=None, **kwargs):
        cr.execute('''select distinct categ_id,categ_name from (
                        select pp.product_tmpl_id,pt.list_price , pt.description,pt.categ_id,pc.name as categ_name from crm_case_section_product_product_rel crm_real ,
                        crm_case_section ccs ,product_template pt, product_product pp , product_category pc
                        where pp.id = crm_real.product_product_id
                        and pt.id = pp.product_tmpl_id
                        and ccs.id = crm_real.crm_case_section_id
                        and pc.id = pt.categ_id
                        and ccs.id = %s
                        )A ''', (section_id,))
        datas = cr.fetchall()
        cr.execute
        return datas
    # get promotion datas from database
    
    def get_promos_datas(self, cr, uid , section_id , branch_id, context=None, **kwargs):
        cr.execute('''select id,sequence as seq,from_date ,to_date,active,name as p_name,
                        logic ,expected_logic_result ,special, special1, special2, special3 ,branch_id 
                        from promos_rules pr where pr.active = true and main_group in 
                        (select product_maingroup_id 
                        from crm_case_section_product_maingroup_rel mg,crm_case_section cs 
                        where cs.id = mg.crm_case_section_id and cs.id = %s)
                        and pr.branch_id = %s                        
                        ''', (section_id,branch_id,))
        datas = cr.fetchall()
        cr.execute
        return datas
    def get_promos_act_datas(self, cr, uid , section_id , branch_id, context=None, **kwargs):
        cr.execute('''select act.id,act.promotion,act.sequence as act_seq ,act.arguments,act.action_type,act.product_code
                            from promos_rules r ,promos_rules_actions act
                            where r.id = act.promotion
                            and r.active = 't'
                            and r.main_group in
                            (select product_maingroup_id 
                            from crm_case_section_product_maingroup_rel mg,crm_case_section cs 
                            where cs.id = mg.crm_case_section_id and cs.id = %s)
                            and r.branch_id = %s
                    ''', (section_id,branch_id,))
        datas = cr.fetchall()
        cr.execute
        return datas
    def get_promos_cond_datas(self, cr, uid , section_id ,branch_id, context=None, **kwargs):
        cr.execute('''select cond.id,cond.promotion,cond.sequence as cond_seq,
                            cond.attribute as cond_attr,cond.comparator as cond_comparator,
                            cond.value as comp_value
                            from promos_rules r ,promos_rules_conditions_exps cond
                            where r.id = cond.promotion
                            and r.active = 't'
                            and r.main_group in
                            (select product_maingroup_id 
                            from crm_case_section_product_maingroup_rel mg,crm_case_section cs 
                            where cs.id = mg.crm_case_section_id and cs.id = %s)
                            and r.branch_id = %s
                    ''', (section_id,branch_id,))
        datas = cr.fetchall()
        cr.execute
        return datas
    def get_promos_rule_partner_datas(self, cr, uid , section_id , context=None, **kwargs):
        cr.execute('''select category_id,rule_id from rule_partner_cat_rel''')
        datas = cr.fetchall()
        cr.execute
        return datas
    def get_promos_category_datas(self, cr, uid , section_id , context=None, **kwargs):
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
#         cr.execute("select id,product_id,product_uos_qty,price_unit,discount,sub_total,order_id from mobile_sale_order_line where create_date > %s and order_id in(%s)",(todayDateNormal,order_ids,))
# #                             where due_date > %s''',(todayDateNormal,))
#         datas = cr.fetchall()
#         cr.execute
#         return datas
    
    # get pricelsit datas
    def get_pricelist_datas(self, cr, uid , section_id, context=None, **kwargs):
        cr.execute('''select id,name,type,active from product_pricelist where active = 't' and main_group_id in (select product_maingroup_id 
                        from crm_case_section_product_maingroup_rel mg,crm_case_section cs 
                        where cs.id = mg.crm_case_section_id and cs.id = %s) or main_group_id is null''', (section_id,))
        datas = cr.fetchall()
        cr.execute
        return datas
    def get_pricelist_version_datas(self, cr, uid, section_id , context=None, **kwargs):
        cr.execute('''select pv.id,date_end,date_start,pv.active,pv.name,pv.pricelist_id 
                        from product_pricelist_version pv, product_pricelist pp where pv.pricelist_id = pp.id 
                        and (pp.main_group_id in (select product_maingroup_id 
                        from crm_case_section_product_maingroup_rel mg,crm_case_section cs 
                        where cs.id = mg.crm_case_section_id and cs.id =%s) or pp.main_group_id is null)''', (section_id,))
        datas = cr.fetchall()
        cr.execute
        return datas
    def get_pricelist_item_datas(self, cr, uid, section_id , context=None, **kwargs):
        cr.execute('''select pi.id,pi.price_discount,pi.sequence,pi.product_tmpl_id,pi.name,pi.base_pricelist_id,
                    pi.product_id,pi.base,pi.price_version_id,pi.min_quantity,
                    pi.categ_id,pi.price_surcharge from product_pricelist_item pi, product_pricelist_version pv, product_pricelist pp where pv.pricelist_id = pp.id 
                    and pv.id = pi.price_version_id and (pp.main_group_id in (select product_maingroup_id 
                    from crm_case_section_product_maingroup_rel mg,crm_case_section cs 
                    where cs.id = mg.crm_case_section_id and cs.id = %s) or pp.main_group_id is null)''', (section_id,))
        datas = cr.fetchall()
        cr.execute
        return datas
    
   # def get_product_uoms(self, cr, uid , context=None, **kwargs):
    #    cr.execute('''
     #               select distinct pu.id as uom_id,pu.name as uom_name ,1/pu.factor as ratio,pur.product_template_id as  product_template_id
      #          from product_uom pu , product_template_product_uom_rel pur , product_template pt,product_product pp
       #         where pt.id = pur.product_template_id
        #        and pu.id = pur.product_uom_id''')
        # datas = cr.fetchall()
        # cr.execute
        # return datas
    def get_product_uoms(self, cr, uid , saleteam_id, context=None, **kwargs):
        cr.execute('''     
                select distinct uom_id,uom_name,ratio,product_template_id from(
                select  pu.id as uom_id,pu.name as uom_name ,1/pu.factor as ratio,
                pur.product_template_id as  product_template_id
                from product_uom pu , product_template_product_uom_rel pur , product_template pt,
                product_product pp,
                crm_case_section_product_product_rel crm
                where pt.id = pur.product_template_id
                and crm.product_product_id = pp.id
                and pu.id = pur.product_uom_id
                and crm.crm_case_section_id = %s
                )A''' , (saleteam_id,))
        datas = cr.fetchall()
        cr.execute
        return datas

    # Get Res Partner and Res Partner Category res_partner_res_partner_category_rel
    def get_res_partner_category_datas(self, cr, uid , context=None, **kwargs):
        cr.execute('''
        select a.category_id, a.partner_id ,b.name
        from res_partner_res_partner_category_rel a , res_partner_category b
        where a.category_id = b.id
        ''')
        datas = cr.fetchall()
        return datas
    
    def get_sale_team_members_datas(self, cr, uid , member_id, saleteam_id, context=None, **kwargs):
        cr.execute('''select u.id as id,u.active as active,u.login as login,u.password as password,u.partner_id as partner_id,p.name as name from res_users u, res_partner p
                   where u.partner_id = p.id and u.id in(select member_id from crm_case_section cr, sale_member_rel sm where sm.section_id = cr.id and cr.id =%s)''', (saleteam_id,)) 
        datas = cr.fetchall()
        cr.execute
        return datas
    def sale_team_return(self, cr, uid, section_id , saleTeamId, context=None, **kwargs):
        cr.execute('''select DISTINCT cr.id,cr.complete_name,cr.warehouse_id,cr.name,sm.member_id,cr.code,pr.product_product_id,cr.location_id
                    from crm_case_section cr, sale_member_rel sm,crm_case_section_product_product_rel pr where sm.section_id = cr.id and cr.id=pr.crm_case_section_id  
                    and sm.member_id =%s 
                    and cr.id = %s
            ''', (section_id, saleTeamId,))
        datas = cr.fetchall()
        cr.execute
        return datas

    def sale_plan_day_return(self, cr, uid, section_id , context=None, **kwargs):
     
#         cr.execute('''            
#             select p.id,p.date,p.sale_team,p.name,p.main_group from sale_plan_day p
#             join  crm_case_section c on p.sale_team=c.id
#             where p.sale_team=%s and p.active = true
#             ''', (section_id, ))        
        cr.execute('''            
            select p.id,p.date,p.sale_team,p.name,p.principal from sale_plan_day p
            join  crm_case_section c on p.sale_team=c.id
            where p.sale_team=%s and p.active = true
            ''', (section_id,))
        datas = cr.fetchall()
        cr.execute      
        return datas    
    def sale_plan_trip_return(self, cr, uid, section_id , context=None, **kwargs):
     
        cr.execute('''            
            select p.id,p.date,p.sale_team,p.name,p.principal from sale_plan_trip p
            join  crm_case_section c on p.sale_team=c.id
            where p.sale_team=%s and p.active = true
            ''', (section_id,))
        datas = cr.fetchall()
        cr.execute
      
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
            ,hotline,sale_team_id,notification_time
            from tablets_information 
            where name = %s
            ''', (tabetId,))
        datas = cr.fetchall()
        return datas
    
    def get_company_datas(self, cr, uid , context=None):        
        cr.execute('''select id,name from res_company''')
        datas = cr.fetchall()        
        return datas
    
    def get_res_users(self, cr, uid, sale_team_id , context=None, **kwargs):
        cr.execute('''
            select id,active,login,password,partner_id,branch_id from res_users where id = %s
            ''', (sale_team_id,))
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
                    from crm_case_section cr, sale_member_rel sm,crm_case_section_product_product_rel pr
                    where sm.section_id = cr.id and cr.id=pr.crm_case_section_id
            ) B on A.userid = B.member_id
            )D on c.sale_team_id = D.saleTeamId
            where c.name = %s
            and D.login= %s
            and d.login_password = crypt(%s, login_password)
            ''', (sale_team_id, login, pwd,))
        datas = cr.fetchall()            
        return datas  
       
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
    
    def create_dsr_notes(self, cursor, user, vals, context=None):
        print 'vals',vals
        try : 
            history_obj=self.pool.get('sales.denomination')
            notes_line_obj=self.pool.get('sales.denomination.note.line')
            deno_product_obj= self.pool.get('sales.denomination.product.line')
            
            str ="{"+vals+"}"
            str = str.replace(":''",":'")
            str = str.replace("'',","',")
            str = str.replace(":',",":'',")
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
                print "length", len(r)
                if len(r)>=7:
                    history.append(r)                   
                else:
                    notes_line.append(r)
            
            if history:
                for pt in history:
                    deno_result={
                        'invoice_count':pt['invoice_count'],
                        'sale_team_id':pt['sale_team_id'],
                        'company_id':pt['company_id'] ,
                        'note':pt['note'],
                        'date':pt['date'],
                        'tablet_id':pt['tablet_id'],
                        'user_id':pt['user_id'],
                    }
                    deno_id = history_obj.create(cursor, user, deno_result, context=context)
                    
                    for ptl in notes_line:
                                note_line_res={                                                            
                                  'denomination_note_ids':deno_id,
                                  'note_qty':ptl['note_qty'],
                                  'notes':ptl['notes'],                     
                                }
                                notes_line_obj.create(cursor, user, note_line_res, context=context)
                    
                        
                de_date= pt['date']
                user_id = pt['user_id']
                mobile_sale_obj = self.pool.get('mobile.sale.order')        
                mobile_sale_order_obj = self.pool.get('mobile.sale.order.line')
                cursor.execute("select id from mobile_sale_order where due_date=%s and user_id=%s and void_flag != 'voided'",(de_date,user_id))
                mobile_ids = cursor.fetchall()
                if  mobile_ids:
                    line_ids = mobile_sale_order_obj.search(cursor, user,[('order_id', 'in',mobile_ids)], context=context)                        
                    order_line_ids = mobile_sale_order_obj.browse(cursor, user, line_ids, context=context)                  
                    cursor.execute('select product_id,sum(product_uos_qty),sum(sub_total) from mobile_sale_order_line where id in %s group by product_id',(tuple(order_line_ids.ids),))
                    order_line=cursor.fetchall()
                    for data in order_line:
                        data_id={'product_id':data[0],
                                          'product_uom_qty':data[1],
                                          'denomination_product_ids':deno_id,
                                          'amount':data[2]}
                        deno_product_obj.create(cursor, user, data_id, context=context)
            print 'True'
            return True       
        except Exception, e:
            print 'False'
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
                cursor.execute('select id From res_partner where customer_code = %s ',(ar['customer_code'],))
                data = cursor.fetchall()
                if data:
                    partner_id = data[0][0]
                else:
                    partner_id = None
                
                ar_result = {
                    'customer_code':ar['customer_code'],
                    'partner_id':partner_id,
                    'credit_limit':ar['credit_limit'],
                    'date':ar['date'] ,                    
                    'tablet_id':ar['tablet_id'],
                    'void_flag':ar['void_flag'],
                    'payment_amount':ar['payment_amount'],                
                    'so_amount':ar['so_amount'],
                    'balance':ar['balance'],
                    'ref_no':ar['ref_no'],
                    'so_ref':ar['so_ref'],
                    'sale_team_id':ar['sale_team_id'],
                    'user_id':ar['user_id'],
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
                    cursor.execute('select id From res_partner where customer_code = %s ',(ar['partner_id'],))
                    data = cursor.fetchall()
                    if data:
                        partner_id = data[0][0]
                    else:
                        partner_id = None
                    
                    rental_result = {
                    
                        'partner_id':partner_id,
                        'from_date':ar['from_date'],
                        'date':ar['date'] ,                    
                        'to_date':ar['to_date'],
                        'image':ar['image'],
                        'company_id':ar['company_id'],                
                        'monthy_amt':ar['monthy_amt'],
                        'month':'month',
                        'latitude':ar['latitude'],
                        'longitude':ar['longitude'],
                        'address':ar['address'],
                        'month':ar['month'],
                        'name':ar['name'],
                        'total_amt':ar['total_amt'],
                    }
                    rental_obj.create(cursor, user, rental_result, context=context)
            return True
         except Exception, e:
            print 'False'
            return False
    def get_credit_notes(self, cr, uid, sale_team_id , context=None, **kwargs):
        cr.execute('''            
                  select ac.id,ac.description,ac.name,ac.used_date,
                    ac.issued_date,ac.terms_and_conditions,ac.amount,ac.so_no,
                    ac.m_status,ac.customer_id,ac.type,ac.sale_team_id,res.name,res.customer_code,ac.ref_no
                 from account_creditnote ac,res_partner res
                   where ac.customer_id = res.id
                   and ac.m_status = 'new'
                   and  ac.sale_team_id = %s
         ''', (sale_team_id,))
        datas = cr.fetchall()
        cr.execute
        return datas
    
    def udpate_credit_notes_issue_status(self, cr, uid, sale_team_id , context=None, **kwargs):
        try:
            cr.execute('''update account_creditnote set m_Status='issued' where
                        sale_team_id = %s and m_status ='new'
             ''', (sale_team_id,))
            return True
        except Exception, e:
            return False
        
    def udpate_credit_notes_used_status(self, cr, uid, sale_team_id ,usedList, context=None, **kwargs):
        try:
            crnote = tuple(usedList)
            note_order_obj = self.pool.get('account.creditnote')
            list_val = None
            list_val = note_order_obj.search(cr,uid, [('sale_team_id', '=', sale_team_id), ('m_status', '=', 'issued'),('name','in', usedList)])            
            print'credit id', list_val
            for note_id in list_val:
                print'Note id', note_id
                cr.execute("""update account_creditnote set m_status ='used' where id = %s""",(note_id,))
            return True
        except Exception, e:
            return False
    
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
        cr.execute('''select promo_id,sale_channel_id from promo_sale_channel_rel''')
        datas = cr.fetchall()        
        return datas    
    
	def get_product_qty_in_hand(self, cr, uid, warehouse_id , context=None, **kwargs):
         cr.execute("""
               select product_id,qty_on_hand + qty as qty_on_hand,main_group,name_template from (
                select sm.product_id  ,sum(sm.product_uos_qty) as qty_on_hand ,0 as qty, pt.main_group, pp.name_template
                                      from stock_move sm , stock_picking sp , stock_picking_type spt,product_template pt, product_product pp
                                      where sm.picking_id = sp.id
                          and sm.state = 'done'                     
                          and spt.id = sm.picking_type_id
                          and sp.picking_type_id = sm.picking_type_id
                          and spt.code = 'internal'
                          and pp.active = true
                          and sm.location_dest_id = %s
                          and sm.date::date = now()::date
                          and sm.product_id = pp.id
                          and pp.product_tmpl_id = pt.id
                          group by product_id, pt.main_group, pp.name_template)A
                """, (warehouse_id,))
        datas = cr.fetchall()
        return datas
	
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
        'product_id':fields.many2one('product.product', 'Products'),
        'product_uos_qty':fields.float('Quantity'),
        'uom_id':fields.function(_get_uom_from_product, type='many2one', relation='product.uom', string='UOM'),
        'price_unit':fields.float('Unit Price'),
        'discount':fields.float('Discount (%)'),
        'discount_amt':fields.float('Discount (Amt)'),
        'order_id': fields.many2one('mobile.sale.order', 'Sale Order'),
        'sub_total':fields.float('Sub Total'),
        'foc':fields.boolean('FOC'),
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

class account_invoice(osv.osv):
    _inherit = "account.invoice"
  
    _columns = {
             'payment_type': fields.char('Payment Type', size=64, readonly=True),
               }
account_invoice()    
 
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
            except Exception,e:
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