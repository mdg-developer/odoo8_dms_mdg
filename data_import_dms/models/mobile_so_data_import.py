from openerp.osv import fields, osv
from openerp.osv import orm
from xlrd import open_workbook
import xlrd
from openerp.tools.translate import _
from datetime import datetime
from datetime import timedelta  
import base64
import logging

_logger = logging.getLogger(__name__)
header_fields = ['orderreference', 'voucherno', 'customercode', 'salemanname', 'saleplanday', 'saleplantrip', 'date',
                 'paymenttype', 'deliverremark', 'deductionamount', 'paid', 'void', 'tax', 'pricelist',
                 'product', 'quantity(pcs)', 'unitprice', 'discount(%)', 'discountamount', 'saleteam', 'paymentterm']

class mobile_sale_import(osv.osv):
    
    _name = 'mobile.so_import'
    _description = 'Sales Order Import'
    _columns = {
              'name':fields.char('Description'),
              'import_date':fields.date('Import Date', readonly=True),
              'import_fname': fields.char('Filename', size=128),
              'import_file':fields.binary('File', required=True),
              'note':fields.text('Log'),
              'company_id': fields.many2one('res.company', 'Company', required=False),
              'state':fields.selection([
                ('draft', 'Draft'),
                ('completed', 'Completed'),
                ('error', 'Error'),
            ], 'States'),
        }
    
    _defaults = {
            'state':'draft',
            # 'import_date':datetime.date.now(),
                 }
        
    def _check_file_ext(self, cursor, user, ids):
        for import_file in self.browse(cursor, user, ids):
            if '.xls' in import_file.import_fname:return True
            else: return False
        return True
    
    _constraints = [(_check_file_ext, "Please import Excel file!", ['import_fname'])]
    
    
    def import_data(self, cr, uid, ids, context=None):   
        users_obj = self.pool.get('res.users')
        partner_obj = self.pool.get('res.partner') 
        product_obj = self.pool.get('product.product')
        order_obj = self.pool.get('sale.order')
        order_line_obj = self.pool.get('sale.order.line')
        warehouse_obj = self.pool.get('stock.warehouse')
        sale_plan_day_obj = self.pool.get('sale.plan.day')
        sale_plan_trip_obj = self.pool.get('sale.plan.trip')
        section_obj = self.pool.get('crm.case.section')
        payment_term_obj = self.pool.get('account.payment.term')
        sale_order_tax_obj = self.pool.get('sale.order.tax')
        sale_order_tax_obj = self.pool.get('sale.order.tax')
        product_pricelist_obj = self.pool.get('product.pricelist')
      
        
        
#         category_obj = self.pool.get('product.category')
#         country_obj=self.pool.get('res.country')
#         tablet_obj=self.pool.get('tablets.information')
#         pricelist_obj=self.pool.get('product.pricelist')
        
#         location_obj=self.pool.get('stock.location')
#        parent_cat_id = category_obj.search(cr,uid,[('name','=','All')])
        
        data = self.browse(cr, uid, ids)[0]
        company_id = data.company_id.id
        import_file = data.import_file

        err_log = ''
        header_line = False

        lines = base64.decodestring(import_file)
        wb = open_workbook(file_contents=lines)
        excel_rows = []
        
        for s in wb.sheets():
            headers = []
            header_row = 0
            for hcol in range(0, s.ncols):
                headers.append(s.cell(header_row, hcol).value)
            # add header
            excel_rows.append(headers)
            for row in range(header_row + 1, s.nrows):
                values = []
                for col in range(0, s.ncols):
                    values.append(s.cell(row, col).value)
                excel_rows.append(values)
        con_ls = []
        amls = []
        count = val = head_count = 0
        for ln in excel_rows:
            # ln = [str(x).strip() for x in ln]
            if not ln or ln and ln in ['', '#']:
                continue
            # process header line
            
            if not header_line:
                for x in ln:
                    x = str(x).strip().lower()
                    if x in header_fields:
                        con_ls.append(x)
                        head_count = head_count + 1
                if head_count < 3:
                    head_count = 0
                    con_ls = []
                else:
                    if ln:
                        b3 = set(header_fields).difference(con_ls)
                        # check the columns without contained the header fields
                        if b3:
                            for l in b3:
                                ln.append(str(l))
                            val = len(b3)
                    header_line = True
                    PriceList_i = Tax_i = OrderRefNo_i = DueDate_i = NetTotalAmount_i = DiscountAmount_i = CustomerCode_i = SalePlanName_i = SalemanName_i = SalePlanDay_i = SalePlanTrip_i = Warehouse_i = Location_i = Date_i = PaymentType_i = DeliverRemark_i = None
                    FOC_i = Discount_i = DeductionAmount_i = Paid_i = Void_i = ProductsCODE_i = Products_i = Quantity_i = UnitPrice_i = SubTotal_i = SaleTeam_i = PaymentTerm_i = None
                    # name_related_i = gender_i = marital_i = identification_id_i = mobile_phone_i = work_phone_i = work_email_i = birthday_i= father_name_i = finger#print_id_i = job_id_i = department_id_i = address_home_id_i = joining_date_i = salary_i = None
                    column_cnt = 0
                    for cnt in range(len(ln)):
                        if ln[cnt] == '':
                            column_cnt = cnt
                            break
                        elif cnt == len(ln) - 1:
                            column_cnt = cnt + 1
                            break
                    for i in range(column_cnt):
                        # header fields
                        header_field = ln[i].strip().lower()
                        if header_field not in header_fields:
                            err_log += '\n' + _("Invalid Excel File, Header Field '%s' is not supported !") % ln[i]
                        
                        elif header_field == 'customercode':
                            CustomerCode_i = i
                        elif header_field == 'salemanname':
                            SalemanName_i = i
                        elif header_field == 'saleplanday':
                            SalePlanDay_i = i
                        elif header_field == 'saleplantrip':
                            SalePlanTrip_i = i
#                         elif header_field == 'Warehouse':
#                             Warehouse_i=i
                        elif header_field == 'pricelist':
                            PriceList_i = i
#                         elif header_field == 'Location':
#                             Location_i=i
                        elif header_field == 'date':
                            Date_i = i
                        elif header_field == 'paymenttype':
                            PaymentType_i = i
                        elif header_field == 'deliverremark':
                            DeliverRemark_i = i
                        elif header_field == 'paid':
                            Paid_i = i
                        elif header_field == 'void':
                            Void_i = i
                        elif header_field == 'product':
                            Products_i = i
                        elif header_field == 'quantity(pcs)':
                            Quantity_i = i
                        elif header_field == 'unitprice':
                            UnitPrice_i = i
                    
                        elif header_field == 'saleteam':
                            SaleTeam_i = i
                        elif header_field == 'paymentterm':
                            PaymentTerm_i = i     
                        elif header_field == 'discount(%)':
                            Discount_i = i   
                        elif header_field == 'discountamount':
                            DiscountAmount_i = i
                        elif header_field == 'deductionamount':
                            DeductionAmount_i = i
                        elif header_field == 'orderreference':
                            OrderRefNo_i = i
                        elif header_field == 'tax':
                            Tax_i=i                               
                      
                    for f in [(OrderRefNo_i, 'orderreference'), (DiscountAmount_i, 'discountamount'), (CustomerCode_i, 'customercode'),
                              (SalemanName_i, 'salemanname'), (SalePlanDay_i, 'saleplanday'), (SalePlanTrip_i, 'saleplantrip'),
                              (Date_i, 'date'), (PaymentType_i, 'paymenttype'), (DeliverRemark_i, 'deliverremark'),
                              (Discount_i, 'discount(%)'), (DeductionAmount_i, 'deductionamount'), (PriceList_i, 'pricelist'),
                              (Paid_i, 'paid'), (Void_i, 'void'), (Products_i, 'product'), (Quantity_i, 'quantity(pcs)'), (UnitPrice_i, 'unitprice'),
                              (SaleTeam_i, 'saleteam'), (Tax_i, 'Tax'),(PaymentTerm_i, 'paymentterm')]:
                        if not isinstance(f[0], int):
                            err_log += '\n' + _("Invalid Excel file, Header '%s' is missing !") % f[1]                           

                        
                # process data lines   
            else:
                # add the without value for without header fields columns
                for i in range(0, val):
                    ln.append('')
                if ln and ln[0] and ln[0][0] not in ['#', '']:
                    
                    import_vals = {}
                    
                    import_vals['customercode'] = ln[CustomerCode_i]
                    import_vals['salemanname'] = ln[SalemanName_i]
                    import_vals['saleplanday'] = ln[SalePlanDay_i]
                    import_vals['saleplantrip'] = ln[SalePlanTrip_i]
                    import_vals['pricelist'] = ln[PriceList_i]
                    import_vals['date'] = ln[Date_i]
                    import_vals['paymenttype'] = ln[PaymentType_i]
                    import_vals['deliverremark'] = ln[DeliverRemark_i]
                    import_vals['paid'] = ln[Paid_i]
                    import_vals['void'] = ln[Void_i]
                    import_vals['product'] = ln[Products_i]
                    import_vals['quantity(pcs)'] = ln[Quantity_i]
                    import_vals['unitprice'] = ln[UnitPrice_i]

                    
                    import_vals['saleteam'] = ln[SaleTeam_i]
                    import_vals['paymentterm'] = ln[PaymentTerm_i]
                    import_vals['discount(%)'] = ln[Discount_i]
                    import_vals['deductionamount'] = ln[DeductionAmount_i]
                    import_vals['discountamount'] = ln[DiscountAmount_i]
      
                    import_vals['orderreference'] = ln[OrderRefNo_i]
                    import_vals['Tax']=ln[Tax_i]
                    amls.append(import_vals)
                    
        if err_log:
            self.write(cr, uid, ids[0], {'note': err_log})
            self.write(cr, uid, ids[0], {'state': 'error'})
        else:
            order_id = None
            
            try : 
                #fordelete
                for aml in amls:
                    deleteorderRef=orderRef=order_ids=None
                    if aml['orderreference']:
                        deleteorderRef = str(aml['orderreference']).strip()       
                    cr.execute(""" select id,tb_ref_no,state from sale_order where tb_ref_no =%s""", (deleteorderRef,))
                    data = cr.fetchall()
                    if data:
                        order_ids = data[0]
                    if order_ids:
                        order_id = order_ids[0] 
                        so_ref = str(order_ids[1]).strip()
                        state =order_ids[2]
                        if state!='draft':
                            raise osv.except_osv(_('Warning!'), _("Please Check Your Sale Order State '%s'!") % (so_ref,))                                      

                        if so_ref==deleteorderRef:
                            cr.execute("""delete from sale_order_line where order_id=%s""", (order_id,))     
                #forinsert                                
                for aml in amls:
                    order_ids = pricelist_ids = payment_term_ids = uom_ids = partner_ids = tax = _foc = _state = analytic_id = pricelist_id = partner_id = country_id = saleperson_id = warehouse_id = product_id = user_id = sale_plan_day_id = sale_plan_trip_id = section_id = payment_term_id = _duedate = None
                    void = secObj = products_name=product_ids =orderRef = partner_code = branch_id=payment_type = delivery_remark = saleperson_name = sale_plan_day_name = sale_plan_trip_name = section_name = payment_term_name = pricelist_name = date = pricelist_name = so_partner_id=so_date=so_ref=None
                   # product_code = aml['ProductsCODE']
                    discount_amount = qty_pcs = unit_price = discount = deduct_amt = numberOfDays = 0
                    if aml['product']: 
                        products = str(aml['product']).strip()
                    if products:
                        products_name = products  # '['+product_code+'] '+ 
                    
                    if aml['orderreference']:
                        orderRef = str(aml['orderreference']).strip()
                    if aml['Tax']:
                        tax=str(aml['Tax']).strip()
                    if aml['customercode']:
                        partner_code = str(aml['customercode']).strip()
                        
                    if aml['paymenttype']:
                        payment_type = str(aml['paymenttype']).strip()
                        
                        
                    if aml['deliverremark']:
                        delivery_remark = str(aml['deliverremark']).strip()
        
                        
                    if aml['salemanname']:
                        saleperson_name = str(aml['salemanname']).strip()
        
                        
                    if aml['saleplanday']:
                        sale_plan_day_name = str(aml['saleplanday']).strip()
        
                    
                    if aml['saleplantrip']:
                        sale_plan_trip_name = str(aml['saleplantrip']).strip()
        
                        
                    if aml['saleteam']:
                        section_name = str(aml['saleteam']).strip()
        
                        
                    if aml['paymentterm']:
                        payment_term_name = str(aml['paymentterm']).strip()
        
                        
                    if aml['discountamount']:
                        discount_amount = float(aml['discountamount'])
                        
                    if aml['quantity(pcs)']:
                        qty_pcs = float(aml['quantity(pcs)'])
                    
                    if aml['unitprice']:
                        unit_price = float(aml['unitprice'])
                        
                    if aml['discount(%)']:
                        discount = float(aml['discount(%)'])
                        
                    if aml['deductionamount']:
                        deduct_amt = float(aml['deductionamount'])
                        
                    if aml['pricelist']:
                        pricelist_name = str(aml['pricelist']).strip()             
                        
                    if aml['void']:
                        void = str(aml['void']).strip()
                        
                    if aml['date']:
                        try:
                            data_time = float(aml['date'])
                            result = xlrd.xldate.xldate_as_tuple(data_time, 0)
                            a = str(result[1]) + '/' + str(result[2]) + '/' + str(result[0]) + ' ' + str(result[3]) + ':' + str(result[4]) + ':' + str(result[5])
                            date = datetime.strptime(a, '%m/%d/%Y %H:%M:%S').date()
                        except Exception , e:
                            try:
                                str_date = str(aml['date']).strip() + ' 00:00:00'
                                date = datetime.strptime(str_date, '%m/%d/%Y %H:%M:%S').date()
                            except Exception, e:
                                try:
                                    str_date = str(aml['date']).strip() + ' 00:00:00'
                                    date = datetime.strptime(str_date, '%Y/%m/%d %H:%M:%S').date()
                                except Exception, e:
                                    try:
                                        str_date = str(aml['date']).strip() + ' 00:00:00'
                                        date = datetime.strptime(str_date, '%d/%m/%Y %H:%M:%S').date()
                                    except Exception, e:
                                        try:
                                            date = None
                                        except Exception, e:
                                            raise orm.except_orm(_('Error :'), _("Error while processing Excel Columns. \n\nPlease check your Date!"))                        
                       
                    if saleperson_name:
                        cr.execute(""" select id from res_partner where lower(name) = %s""", (saleperson_name.lower(),))
                        data = cr.fetchall()
                        if data:
                            saleperson_ids = data[0]
        #                     saleperson_ids = partner_obj.search(cr, uid, [('name', '=', saleperson_name)])
                        if saleperson_ids:
                            saleperson_id = saleperson_ids[0]
                            user_ids = users_obj.search(cr, uid, [('partner_id', '=', saleperson_id)])
                            if user_ids:
                                user_id = user_ids[0]
                                
                    if pricelist_name:
                        cr.execute(""" select id from product_pricelist where lower(name) = %s """, (pricelist_name.lower(),))
                        data = cr.fetchall()
                        if data:
                            pricelist_ids = data[0]
        #                     pricelist_ids = product_pricelist_obj.search(cr, uid, [('name', '=', pricelist_name)])
                        if pricelist_ids:
                            pricelist_id = pricelist_ids[0]
                            
        #                 if warehouse_name:
        #                     warehouse_ids = warehouse_obj.search(cr,uid,[('name','=',warehouse_name)])
        #                     if warehouse_ids:
        #                         warehouse_id = warehouse_ids[0]
                            
                    if sale_plan_day_name:
                        cr.execute(""" select id from sale_plan_day where lower(name) = %s""", (sale_plan_day_name.lower(),))
                        data = cr.fetchall()
                        if data:
                            sale_plan_day_ids = data[0]
        #                     sale_plan_day_ids = sale_plan_day_obj.search(cr, uid, [('name', '=', sale_plan_day_name)])
                        if sale_plan_day_ids:
                            sale_plan_day_id = sale_plan_day_ids[0]
                            
                    if sale_plan_trip_name:
                        cr.execute(""" select id from sale_plan_trip where lower(name) = %s""", (sale_plan_trip_name.lower(),))
                        data = cr.fetchall()
                        if data:
                            sale_plan_trip_ids = data[0]
        #                     sale_plan_trip_ids = sale_plan_trip_obj.search(cr, uid, [('name', '=', sale_plan_trip_name)])
                        if sale_plan_trip_ids:
                            sale_plan_trip_id = sale_plan_trip_ids[0]
                            
                    if section_name:
                        cr.execute(""" select id from crm_case_section where lower(name) =%s """, (section_name.lower(),))
                        data = cr.fetchall()
                        if data:
                            section_ids = data[0]
        #                     section_ids = section_obj.search(cr, uid, [('name', '=', section_name)])
                        if section_ids:
                            section_id = section_ids[0]
                            secObj = section_obj.browse(cr, uid, section_id, context=None)
                    if secObj:
                        warehouse_id = secObj.warehouse_id.id
                        branch_id=secObj.branch_id.id
                    if payment_term_name:
                        cr.execute(""" select id from account_payment_term where lower(name) = %s """, (payment_term_name.lower(),))
                        data = cr.fetchall()
                        if data:
                            payment_term_ids = data[0]
        #                     payment_term_ids = payment_term_obj.search(cr, uid, [('name', '=', payment_term_name)])
                        if payment_term_ids:
                            payment_term_id = payment_term_ids[0]
                                                                  
                    if payment_term_id:
                        cr.execute(""" select days from account_payment_term_line where payment_id=%s""", (payment_term_id,))
                        data = cr.fetchall()
                        if data:
                            numberOfDays = data[0][0]
                    if products_name:
                        cr.execute(""" select id from product_product where lower(name_template) = %s """, (products_name.lower(),))
                        data = cr.fetchall()
                        if data:
                            product_ids = data[0]
        #                     product_ids = product_obj.search(cr, uid, [('name', '=', products_name)])
                        if product_ids:
                            product_id = product_ids[0]
                            productObj = product_obj.browse(cr, uid, product_id, context=None)
                            uom_ids = productObj.uom_id.id
                        else:
                            raise osv.except_osv(_('Warning!'), _("Please Check Your Product Name '%s'!") % (products_name,))                                      
                        

                    if void.lower() == "" and void.lower() == "unvoid": 
                        _state = "draft"
                    elif void.lower() == "void":
                        _state = "cancel"
                    else:
                        _state = "draft"
                     
                     
#                 print 'section_namesection_namesection_namesection_name',section_name
#                 if section_name:
#                     cr.execute(""" select id from crm_case_section where lower(name) =%s """, (section_name.lower(),))
#                     data = cr.fetchall()
#                     if data:
#                         section_ids = data[0]
# #                     section_ids = section_obj.search(cr, uid, [('name', '=', section_name)])
#                     if section_ids:
#                         section_id = section_ids[0]
#                         secObj = section_obj.browse(cr, uid, section_id, context=None)
#                 if secObj:
#                     warehouse_id = secObj.warehouse_id.id   
#                     branch_id=secObj.branch_id.id    
#                 if payment_term_name:
#                     cr.execute(""" select id from account_payment_term where lower(name) = %s """, (payment_term_name.lower(),))
#                     data = cr.fetchall()
#                     if data:
#                         payment_term_ids = data[0]
# #                     payment_term_ids = payment_term_obj.search(cr, uid, [('name', '=', payment_term_name)])
#                     if payment_term_ids:
#                         payment_term_id = payment_term_ids[0]
#                 if payment_term_id:
#                     cr.execute(""" select days from account_payment_term_line where payment_id=%s""", (payment_term_id,))
#                     data = cr.fetchall()
#                     if data:
#                         numberOfDays = data[0][0]
#                 print 'products_nameproducts_nameproducts_name',products_name
#                 if products_name:
#                     cr.execute(""" select id from product_product where lower(name_template) = %s """, (products_name.lower(),))
#                     data = cr.fetchall()
#                     if data:
#                         product_ids = data[0]
#                     else:
#                         raise osv.except_osv(_('Warning!'), _("Please Check Your Product Name '%s'!") % (products_name,))
# #                     product_ids = product_obj.search(cr, uid, [('name', '=', products_name)])
#                     if product_ids:
#                         product_id = product_ids[0]
#                         productObj = product_obj.browse(cr, uid, product_id, context=None)
#                         uom_ids = productObj.uom_id.id
#                                   
#                     if deduct_amt == "":
#                         deduct_amt = 0
#                     elif deduct_amt is None:
#                         deduct_amt = 0
                                                          
                    if section_id:
                        crm_ids = section_obj.search(cr, uid, [('id', '=', section_id)], context=None)
                        if crm_ids:
                            for line in crm_ids:
                                val = section_obj.browse(cr, uid, line, context=context)
                                analytic_id = val.analytic_account_id.id
                                
                    if partner_code:
                        cr.execute(""" select id from res_partner where lower(customer_code) =%s""", (partner_code.lower(),))
                        data = cr.fetchall()
                        if data:
                            print 'data', data
                            partner_ids = data[0]
        #                     va = partner_obj.search(cr, uid, [('customer_code', '=', partner_code)], context=None)
                        print 'partner_ids .>> ', partner_ids
                        if partner_ids:
                            partner_id = partner_ids[0]
                    
        #                 Calculate the Discount Amount
                    if discount_amount!=0:
                        discount_amount=discount_amount
                        
                    if discount != 0:
                        if discount_amount >0:
                            discount_amount = discount_amount + (qty_pcs * unit_price) * (discount / 100)
                        else:
                            
                            discount_amount = (qty_pcs * unit_price) * (discount / 100)
                        
          
                    if tax:
                        cr.execute(""" select id from account_tax where description = %s """, (tax,))
                        tax_record = cr.fetchall()     
                        if tax_record:
                            taxs = tax_record[0][0]
                            if taxs and partner_id:
                                partner=partner_obj.browse(cr, uid, partner_id, context=context)
                                taxs=self.pool.get('account.tax').browse(cr, uid, taxs, context=context)
                                fpos = partner.property_account_position or False
                                tax_id = self.pool.get('account.fiscal.position').map_tax(cr, uid, fpos, taxs, context=context)
                                tax_data=[[6, 0, tax_id]]
                        else:
                            tax_data=False
                            raise osv.except_osv(_('Warning!'), _("Please Check Your Tax Name '%s'!") % (tax.lower(),))                                      
                    else:
                        tax_data=False                    
                    # Sale Plan Name, Sale Plan Day,Sale Plan Trip, Deliver Remark, Discount, Deduction Amount,Paid Amount, Paid,Void

                    order_value = {
                                  'partner_id':partner_id,
                                  'branch_id':branch_id,
                                  'company_id':1,  # company_id,
                                  'user_id':user_id,
                                  'customer_code':partner_code,
                                  'sale_plan_day_id':sale_plan_day_id,
                                  'sale_plan_trip_id':sale_plan_trip_id,
                                  'section_id':section_id,
                                  'payment_term':payment_term_id,
                                  'date_order':date,
                                  
        #                               'date_confirm':date + timedelta(days=numberOfDays),
                                  'due_date':date + timedelta(days=numberOfDays),
                                  'payment_type':payment_type.lower(),
                                  'delivery_remark':delivery_remark.lower(),
                                  'project_id':analytic_id,
                                  'pricelist_id':pricelist_id,
                                  'state':_state,
                                  'warehouse_id':warehouse_id,
                                  'deduct_amt':deduct_amt,
                                  'tb_ref_no':orderRef
                                  
                                  }

                    cr.execute(""" select id,tb_ref_no,state from sale_order where tb_ref_no =%s""", (orderRef,))
                    data = cr.fetchall()
                    order_line_flg = False
                    if data:
                        order_ids = data[0]
        #                 order_ids = order_obj.search(cr, uid, [('tb_ref_no', '=', orderRef)], context=context)
                    if order_ids:
                        order_id = order_ids[0] 
                        so_ref = str(order_ids[1]).strip()
                        state =order_ids[2]
                        if state!='draft':
                            raise osv.except_osv(_('Warning!'), _("Please Check Your Sale Order State '%s'!") % (so_ref,))                                      
 
#                         if so_ref==orderRef:
#                             cr.execute("""delete from sale_order_line where order_id=%s""", (order_id,))
                    else:
                        order_id = order_obj.create(cr, uid, order_value, context)

                #forinsert
#                 for aml in amls:
#                     order_ids = pricelist_ids = payment_term_ids = uom_ids = partner_ids = tax = _foc = _state = analytic_id = pricelist_id = partner_id = country_id = saleperson_id = warehouse_id = product_id = user_id = sale_plan_day_id = sale_plan_trip_id = section_id = payment_term_id = _duedate = None
#                     void = secObj = orderRef = partner_code = payment_type =branch_id= delivery_remark = saleperson_name = sale_plan_day_name = sale_plan_trip_name = section_name = payment_term_name = pricelist_name = date = pricelist_name = so_partner_id=so_date=so_ref=None
#                    # product_code = aml['ProductsCODE']
#                     discount_amount = qty_pcs = unit_price = discount = deduct_amt = numberOfDays = 0
#                     if aml['product']: 
#                         products = str(aml['product']).strip()
#                     if products:
#                         products_name = products  # '['+product_code+'] '+ 
#                     
#                     if aml['orderreference']:
#                         orderRef = str(aml['orderreference']).strip()
#                     if aml['customercode']:
#                         partner_code = str(aml['customercode']).strip()
#                         
#                     if aml['paymenttype']:
#                         payment_type = str(aml['paymenttype']).strip()
#                         
#                         
#                     if aml['deliverremark']:
#                         delivery_remark = str(aml['deliverremark']).strip()
#         
#                         
#                     if aml['salemanname']:
#                         saleperson_name = str(aml['salemanname']).strip()
#         
#                         
#                     if aml['saleplanday']:
#                         sale_plan_day_name = str(aml['saleplanday']).strip()
#         
#                     
#                     if aml['saleplantrip']:
#                         sale_plan_trip_name = str(aml['saleplantrip']).strip()
#         
#                         
#                     if aml['saleteam']:
#                         section_name = str(aml['saleteam']).strip()
#         
#                         
#                     if aml['paymentterm']:
#                         payment_term_name = str(aml['paymentterm']).strip()
#         
#                         
#                     if aml['discountamount']:
#                         discount_amount = float(aml['discountamount'])
#                         
#                     if aml['quantity(pcs)']:
#                         qty_pcs = float(aml['quantity(pcs)'])
#                     
#                     if aml['unitprice']:
#                         unit_price = float(aml['unitprice'])
#                         
#                     if aml['discount(%)']:
#                         discount = float(aml['discount(%)'])
#                         
#                     if aml['deductionamount']:
#                         deduct_amt = float(aml['deductionamount'])
#                         
#                     if aml['pricelist']:
#                         pricelist_name = str(aml['pricelist']).strip()             
#                         
#                     if aml['void']:
#                         void = str(aml['void']).strip()
#                     if aml['Tax']:
#                         tax = str(aml['Tax']).strip()                        
#                         
#                     if aml['date']:
#                         try:
#                             data_time = float(aml['date'])
#                             result = xlrd.xldate.xldate_as_tuple(data_time, 0)
#                             a = str(result[1]) + '/' + str(result[2]) + '/' + str(result[0]) + ' ' + str(result[3]) + ':' + str(result[4]) + ':' + str(result[5])
#                             date = datetime.strptime(a, '%m/%d/%Y %H:%M:%S').date()
#                         except Exception , e:
#                             try:
#                                 str_date = str(aml['date']).strip() + ' 00:00:00'
#                                 date = datetime.strptime(str_date, '%m/%d/%Y %H:%M:%S').date()
#                             except Exception, e:
#                                 try:
#                                     str_date = str(aml['date']).strip() + ' 00:00:00'
#                                     date = datetime.strptime(str_date, '%Y/%m/%d %H:%M:%S').date()
#                                 except Exception, e:
#                                     try:
#                                         str_date = str(aml['date']).strip() + ' 00:00:00'
#                                         date = datetime.strptime(str_date, '%d/%m/%Y %H:%M:%S').date()
#                                     except Exception, e:
#                                         try:
#                                             date = None
#                                         except Exception, e:
#                                             raise orm.except_orm(_('Error :'), _("Error while processing Excel Columns. \n\nPlease check your Date!"))                        
#                        
#                     if saleperson_name:
#                         cr.execute(""" select id from res_partner where lower(name) = %s""", (saleperson_name.lower(),))
#                         data = cr.fetchall()
#                         if data:
#                             saleperson_ids = data[0]
#         #                     saleperson_ids = partner_obj.search(cr, uid, [('name', '=', saleperson_name)])
#                         if saleperson_ids:
#                             saleperson_id = saleperson_ids[0]
#                             user_ids = users_obj.search(cr, uid, [('partner_id', '=', saleperson_id)])
#                             if user_ids:
#                                 user_id = user_ids[0]
#                                 
#                     if pricelist_name:
#                         cr.execute(""" select id from product_pricelist where lower(name) = %s """, (pricelist_name.lower(),))
#                         data = cr.fetchall()
#                         if data:
#                             pricelist_ids = data[0]
#         #                     pricelist_ids = product_pricelist_obj.search(cr, uid, [('name', '=', pricelist_name)])
#                         print 'pricelist_ids', pricelist_ids
#                         if pricelist_ids:
#                             pricelist_id = pricelist_ids[0]
#                             
#                     print 'pricelist_name', pricelist_name
#         #                 if warehouse_name:
#         #                     warehouse_ids = warehouse_obj.search(cr,uid,[('name','=',warehouse_name)])
#         #                     if warehouse_ids:
#         #                         warehouse_id = warehouse_ids[0]
#                             
#                     if sale_plan_day_name:
#                         cr.execute(""" select id from sale_plan_day where lower(name) = %s""", (sale_plan_day_name.lower(),))
#                         data = cr.fetchall()
#                         if data:
#                             sale_plan_day_ids = data[0]
#         #                     sale_plan_day_ids = sale_plan_day_obj.search(cr, uid, [('name', '=', sale_plan_day_name)])
#                         if sale_plan_day_ids:
#                             sale_plan_day_id = sale_plan_day_ids[0]
#                             
#                     if sale_plan_trip_name:
#                         cr.execute(""" select id from sale_plan_trip where lower(name) = %s""", (sale_plan_trip_name.lower(),))
#                         data = cr.fetchall()
#                         if data:
#                             sale_plan_trip_ids = data[0]
#         #                     sale_plan_trip_ids = sale_plan_trip_obj.search(cr, uid, [('name', '=', sale_plan_trip_name)])
#                         if sale_plan_trip_ids:
#                             sale_plan_trip_id = sale_plan_trip_ids[0]
#                             
#                     if section_name:
#                         cr.execute(""" select id from crm_case_section where lower(name) =%s """, (section_name.lower(),))
#                         data = cr.fetchall()
#                         if data:
#                             section_ids = data[0]
#         #                     section_ids = section_obj.search(cr, uid, [('name', '=', section_name)])
#                         if section_ids:
#                             section_id = section_ids[0]
#                             secObj = section_obj.browse(cr, uid, section_id, context=None)
#                     if secObj:
#                         warehouse_id = secObj.warehouse_id.id     
#                         branch_id=secObj.branch_id.id  
#                     if payment_term_name:
#                         cr.execute(""" select id from account_payment_term where lower(name) = %s """, (payment_term_name.lower(),))
#                         data = cr.fetchall()
#                         if data:
#                             payment_term_ids = data[0]
#         #                     payment_term_ids = payment_term_obj.search(cr, uid, [('name', '=', payment_term_name)])
#                         if payment_term_ids:
#                             payment_term_id = payment_term_ids[0]
#                     if payment_term_id:
#                         cr.execute(""" select days from account_payment_term_line where payment_id=%s""", (payment_term_id,))
#                         data = cr.fetchall()
#                         if data:
#                             numberOfDays = data[0][0]
#                     if products_name:
#                         cr.execute(""" select id from product_product where lower(name_template) = %s """, (products_name.lower(),))
#                         data = cr.fetchall()
#                         if data:
#                             product_ids = data[0]
#         #                     product_ids = product_obj.search(cr, uid, [('name', '=', products_name)])
#                         if product_ids:
#                             product_id = product_ids[0]
#                             productObj = product_obj.browse(cr, uid, product_id, context=None)
#                             uom_ids = productObj.uom_id.id
#                             
#                         
#                     if void.lower() == "" and void.lower() == "unvoid": 
#                         _state = "draft"
#                     elif void.lower() == "void":
#                         _state = "cancel"
#                     else:
#                         _state = "draft"
#                      
#                      
#                         
#                     if deduct_amt == "":
#                         deduct_amt = 0
#                     elif deduct_amt is None:
#                         deduct_amt = 0
#                                                           
#                     if section_id:
#                         crm_ids = section_obj.search(cr, uid, [('id', '=', section_id)], context=None)
#                         if crm_ids:
#                             for line in crm_ids:
#                                 val = section_obj.browse(cr, uid, line, context=context)
#                                 analytic_id = val.analytic_account_id.id
#                                 
#                     if partner_code:
#                         print 'partner_code .>> ', partner_code
#                         cr.execute(""" select id from res_partner where lower(customer_code) =%s""", (partner_code.lower(),))
#                         data = cr.fetchall()
#                         if data:
#                             print 'data', data
#                             partner_ids = data[0]
#         #                     va = partner_obj.search(cr, uid, [('customer_code', '=', partner_code)], context=None)
#                         print 'partner_ids .>> ', partner_ids
#                         if partner_ids:
#                             partner_id = partner_ids[0]
#                     
#                     # Calculate the Discount Amount
#                     if discount != 0:
#                         discount_amount = (qty_pcs * unit_price) * (discount / 100)
#           
#                     if tax:
#                         cr.execute(""" select id from account_tax where description = %s """, (tax,))
#                         tax_record = cr.fetchall()     
#                         if tax_record:
#                             taxs = tax_record[0][0]
#                             if taxs and partner_id:
#                                 partner=partner_obj.browse(cr, uid, partner_id, context=context)
#                                 taxs=self.pool.get('account.tax').browse(cr, uid, taxs, context=context)
#                                 fpos = partner.property_account_position or False
#                                 tax_id = self.pool.get('account.fiscal.position').map_tax(cr, uid, fpos, taxs, context=context)
#                                 tax_data=[[6, 0, tax_id]]
#                         else:
#                             tax_data=False
#                             raise osv.except_osv(_('Warning!'), _("Please Check Your Tax Name '%s'!") % (tax.lower(),))                        
#                     else:
#                         tax_data=False
#                     # Sale Plan Name, Sale Plan Day,Sale Plan Trip, Deliver Remark, Discount, Deduction Amount,Paid Amount, Paid,Void
#                     order_value = {
#                                   'partner_id':partner_id,
#                                   'branch_id':branch_id,
#                                   'company_id':1,  # company_id,
#                                   'user_id':user_id,
#                                   'customer_code':partner_code,
#                                   'sale_plan_day_id':sale_plan_day_id,
#                                   'sale_plan_trip_id':sale_plan_trip_id,
#                                   'section_id':section_id,
#                                   'payment_term':payment_term_id,
#                                   'date_order':date,
#         #                               'date_confirm':date + timedelta(days=numberOfDays),
#                                   'due_date':date + timedelta(days=numberOfDays),
#                                   'payment_type':payment_type.lower(),
#                                   'delivery_remark':delivery_remark.lower(),
#                                   'project_id':analytic_id,
#                                   'pricelist_id':pricelist_id,
#                                   'state':_state,
#                                   'warehouse_id':warehouse_id,
#                                   'deduct_amt':deduct_amt,
#                                   'tb_ref_no':orderRef
#                                   }
#                     cr.execute(""" select id,date_order::date,partner_id,tb_ref_no from sale_order where lower(tb_ref_no) =%s""", (orderRef.lower(),))
#                     data = cr.fetchall()
#                     order_line_flg = False
#                     if data:
#                         order_ids = data[0]
#         #                 order_ids = order_obj.search(cr, uid, [('tb_ref_no', '=', orderRef)], context=context)
#                     if order_ids:
#                         order_id = order_ids[0] 
#                     else:
#                         order_id = order_obj.create(cr, uid, order_value, context)
#                     
#                     # print 'order id',order_id            
                    if products_name:
                        order_line_value = {
                                      'order_id':order_id,
                                      'product_id':product_id,
                                      'name':products_name,
                                      'price_unit':unit_price,
                                      'product_uom':uom_ids,
                                      'product_uom_qty':qty_pcs,
                                      'discount':discount,
                                      'discount_amt':discount_amount,
                                      'company_id':1,  # company_id,
                                      'state':'draft',
                                      'tax_id': tax_data,
                                      # 'invoiced':'TRUE',
                     
                                    }
              
#                             order_line_flg = order_line_obj.search(cr,uid,[('order_id', '=', order_id),('product_id','=',product_id),
#                                                                            ('product_uom', '=', uom_ids),('price_unit','=',unit_price),
#                                                                            ('product_uom_qty', '=', qty_pcs),('discount','=',discount),('discount_amt','=',discount_amount)])
#                             if len(order_line_flg) > 0:
#                                 order_line_id = order_line_obj.write(cr, uid,order_line_flg, order_line_value, context)
#                             else:    
                        order_line_id = order_line_obj.create(cr, uid, order_line_value, context)
                        self.button_dummy(cr, uid, order_id, context=None)
                        # Tax Filed is inserted into the sale_order_tax table
                        cr.execute('select id,name,description  from account_tax where parent_id is null')
                        tax_rec = cr.fetchall() 
                    
        
                       
                    self.write(cr, uid, ids[0], {'state': 'completed'})
            except Exception, e:
                print e
                raise osv.except_osv(_('Warning!'), _('Reference No "%s" (Product:%s).(error:%s)') % (orderRef,str(aml['product']).strip(),e))                         
#            COPY mobile_sale_order_temp FROM '/Users/iMac/akdata/order.csv' WITH CSV header
        
    def button_dummy(self, cr, uid, order_id, context=None):
        res=result={}
        cur_obj = self.pool.get('res.currency')
        deduct=untax=total=0.0        
        if order_id:
            if (type(order_id)==int):
                cr.execute('select sum(discount_amt) from sale_order_line where order_id=%s',(order_id,))
                total_dis_amt=cr.fetchall()[0]
                cr.execute('select deduct_amt,amount_untaxed,amount_tax,additional_discount from sale_order where id=%s',(order_id,))
                result=cr.fetchall()[0]
                deduct=result[0]
                untax=result[1]
                amount_tax=result[2]
                additional_discount=result[3]
                print result,'result and deduction',deduct,total_dis_amt
                if additional_discount is None:
                    additional_discount=0.0
                if deduct is None:
                    deduct=0.0
                if amount_tax is None:
                    amount_tax=0.0           
                total=untax+amount_tax-deduct-(untax*(additional_discount/100))
                cr.execute('update sale_order so set amount_total=%s,total_dis=%s,deduct_amt=%s,additional_discount=%s where so.id=%s',(total,total_dis_amt,deduct,additional_discount,order_id))
            else:
                cr.execute('select sum(discount_amt) from sale_order_line where order_id=%s',(order_id[0],))
                total_dis_amt=cr.fetchall()[0]
                cr.execute('select deduct_amt,amount_untaxed,amount_tax,additional_discount from sale_order where id=%s',(order_id[0],))
                result=cr.fetchall()[0]
                deduct=result[0]
                untax=result[1]
                amount_tax=result[2]
                additional_discount=result[3]
                print result,'result and deduction',deduct,total_dis_amt,additional_discount
                if deduct is None:
                    deduct=0.0
                if amount_tax is None:
                    amount_tax=0.0           
                print    '(untax*additional_discount)',untax,additional_discount,(additional_discount/100),amount_tax
                total=untax+amount_tax-deduct-(untax*(additional_discount/100))
                print 'total',total
                cr.execute('update sale_order so set amount_total=%s,total_dis=%s,deduct_amt=%s,additional_discount=%s where so.id=%s',(total,total_dis_amt,deduct,additional_discount,order_id[0]))
        return True
# mobile_sale_import()
