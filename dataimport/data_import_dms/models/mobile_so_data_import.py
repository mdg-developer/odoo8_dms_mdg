from openerp.osv import fields, osv
from openerp.osv import orm
from xlrd import open_workbook
from openerp.tools.translate import _
from datetime import datetime
import base64
import logging


_logger = logging.getLogger(__name__)
header_fields = ['orderreference', 'voucherno', 'duedate', 'customercode', 'saleplanname', 'salemanname', 'saleplanday', 'saleplantrip', 'warehouse', 'location', 'date',
                 'paymenttype', 'deliverremark', 'deductionamount', 'paid', 'void', 'productscode', 'foc', 'tax', 'pricelist',
                 'product', 'quantity(pcs)', 'unitprice', 'subtotal', 'discount(%)', 'discountamount', 'nettotalamount', 'saleteam', 'paymentterm']

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
        value = {}
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
                if head_count < 5:
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
                        header_field = ln[i].strip()
                        if header_field not in header_fields:
                            err_log += '\n' + _("Invalid Excel File, Header Field '%s' is not supported !") % ln[i]
                        
                        elif header_field == 'CustomerCode':
                            CustomerCode_i = i
                        elif header_field == 'SalePlanName':
                            SalePlanName_i = i
                        elif header_field == 'SalemanName':
                            SalemanName_i = i
                        elif header_field == 'SalePlanDay':
                            SalePlanDay_i = i
                        elif header_field == 'SalePlanTrip':
                            SalePlanTrip_i = i
                        elif header_field == 'Warehouse':
                            Warehouse_i = i
                        elif header_field == 'PriceList':
                            PriceList_i = i
                        elif header_field == 'Location':
                            Location_i = i
                        elif header_field == 'Date':
                            Date_i = i
                        elif header_field == 'PaymentType':
                            PaymentType_i = i
                        elif header_field == 'DeliverRemark':
                            DeliverRemark_i = i
                        elif header_field == 'Paid':
                            Paid_i = i
                        elif header_field == 'Void':
                            Void_i = i
                        elif header_field == 'FOC':
                            FOC_i = i
                        elif header_field == 'ProductsCODE':
                            ProductsCODE_i = i
                        elif header_field == 'Product':
                            Products_i = i
                        elif header_field == 'Quantity(PCS)':
                            Quantity_i = i
                        elif header_field == 'UnitPrice':
                            UnitPrice_i = i
                        elif header_field == 'ProductDiscount':
                            ProductDiscount_i = i
                        elif header_field == 'SubTotal':
                            SubTotal_i = i    
                       
                        elif header_field == 'SaleTeam':
                            SaleTeam_i = i
                        elif header_field == 'PaymentTerm':
                            PaymentTerm_i = i     
                        elif header_field == 'Discount(%)':
                            Discount_i = i   
                        elif header_field == 'DiscountAmount':
                            DiscountAmount_i = i
                        elif header_field == 'DeductionAmount':
                            DeductionAmount_i = i
                        elif header_field == 'NetTotalAmount':
                            NetTotalAmount_i = i      
                        elif header_field == 'DueDate':
                            DueDate_i = i 
                        elif header_field == 'OrderReference':
                            OrderRefNo_i = i
                        elif header_field == 'Tax':
                            Tax_i = i                               
                      
                    for f in [(OrderRefNo_i, 'OrderReference'), (DueDate_i, 'DueDate'), (NetTotalAmount_i, 'NetTotalAmount'), (DiscountAmount_i, 'DiscountAmount'), (CustomerCode_i, 'CustomerCode'), (SalePlanName_i, 'SalePlanName'),
                              (SalemanName_i, 'SalemanName'), (SalePlanDay_i, 'SalePlanDay'), (SalePlanTrip_i, 'SalePlanTrip'), (Warehouse_i, 'Warehouse'),
                              (Location_i, 'Location'), (Date_i, 'Date'), (PaymentType_i, 'PaymentType'), (DeliverRemark_i, 'DeliverRemark'),
                              (Discount_i, 'Discount(%)'), (DeductionAmount_i, 'DeductionAmount'), (Tax_i, 'Tax'), (PriceList_i, 'PriceList'),
                              (Paid_i, 'Paid'), (Void_i, 'Void'), (FOC_i, 'FOC'), (ProductsCODE_i, 'ProductsCODE'), (Products_i, 'Product'), (Quantity_i, 'Quantity(PCS)'), (UnitPrice_i, 'UnitPrice'),
                              (SubTotal_i, 'SubTotal'), (SaleTeam_i, 'SaleTeam'), (PaymentTerm_i, 'PaymentTerm')]:
                        if not isinstance(f[0], int):
                            err_log += '\n' + _("Invalid Excel file, Header '%s' is missing !") % f[1]                           

                        
                # process data lines   
            else:
                # add the without value for without header fields columns
                for i in range(0, val):
                    ln.append('')
                if ln and ln[0] and ln[0][0] not in ['#', '']:
                    
                    import_vals = {}
                    
                    import_vals['CustomerCode'] = ln[CustomerCode_i].strip()
                    import_vals['Tax'] = ln[Tax_i].strip()
                    import_vals['SalePlanName'] = ln[SalePlanName_i].strip()
                    import_vals['SalemanName'] = ln[SalemanName_i].strip()
                    import_vals['SalePlanDay'] = ln[SalePlanDay_i].strip()
                    import_vals['SalePlanTrip'] = ln[SalePlanTrip_i].strip()
                    import_vals['Warehouse'] = ln[Warehouse_i].strip()
                    import_vals['PriceList'] = ln[PriceList_i].strip()
                    import_vals['Location'] = ln[Location_i].strip()
                    import_vals['Date'] = ln[Date_i]
                    import_vals['PaymentType'] = ln[PaymentType_i].strip()
                    import_vals['DeliverRemark'] = ln[DeliverRemark_i].strip()
                    import_vals['Paid'] = ln[Paid_i].strip()
                    import_vals['Void'] = ln[Void_i].strip()
                    import_vals['FOC'] = ln[FOC_i].strip()
                    import_vals['ProductsCODE'] = ln[ProductsCODE_i].strip()
                    import_vals['Product'] = ln[Products_i].strip()
                    import_vals['Quantity(PCS)'] = ln[Quantity_i]
                    import_vals['UnitPrice'] = ln[UnitPrice_i]
                    import_vals['SubTotal'] = ln[SubTotal_i]
                    
                    import_vals['SaleTeam'] = ln[SaleTeam_i].strip()
                    import_vals['PaymentTerm'] = ln[PaymentTerm_i].strip()
                    import_vals['Discount(%)'] = ln[Discount_i]
                    import_vals['DeductionAmount'] = ln[DeductionAmount_i]
                    import_vals['DiscountAmount'] = ln[DiscountAmount_i]
                    import_vals['NetTotalAmount'] = ln[NetTotalAmount_i]
                    import_vals['DueDate'] = ln[DueDate_i]        
                    import_vals['OrderReference'] = ln[OrderRefNo_i].strip()    
                    amls.append(import_vals)
                    
        if err_log:
            self.write(cr, uid, ids[0], {'note': err_log})
            self.write(cr, uid, ids[0], {'state': 'failed'})
        else:
            order_id = None
            for aml in amls:
                print 'aml', aml
                _tax = _foc = _state = analytic_id = pricelist_id = partner_id = country_id = saleperson_id = warehouse_id = product_id = user_id = sale_plan_day_id = sale_plan_trip_id = section_id = payment_term_id = _duedate = None
                
                product_code = aml['ProductsCODE']
               
                products = aml['Product']
                
                products_name = '[' + product_code + '] ' + products
                
                if products_name:
                    products = products_name.split(' ', 1)
                    products_name = products[1]
                
                partner_code = str(aml['CustomerCode'])
                sale_plan_name = str(aml['SalePlanName'])
                payment_type = str(aml['PaymentType'])
                delivery_remark = str(aml['DeliverRemark'])
                saleperson_name = aml['SalemanName']
                warehouse_name = aml['Warehouse']
                sale_plan_day_name = aml['SalePlanDay']
                sale_plan_trip_name = aml['SalePlanTrip']
                section_name = aml['SaleTeam']
                payment_term_name = aml['PaymentTerm']
                discount_amount = aml['DiscountAmount']
                qty_pcs = aml['Quantity(PCS)']
                unit_price = aml['UnitPrice']
                discount = aml['Discount(%)']
                deduct_amt = aml['DeductionAmount']
                pricelist_name = aml['PriceList']                            
                net_total = aml['NetTotalAmount']
               
                        
                   
                if saleperson_name:
                    saleperson_ids = partner_obj.search(cr, uid, [('name', '=', saleperson_name)])
                    if saleperson_ids:
                        saleperson_id = saleperson_ids[0]
                        user_ids = users_obj.search(cr, uid, [('partner_id', '=', saleperson_id)])
                        if user_ids:
                            user_id = user_ids[0]
                            
                if pricelist_name:
                    pricelist_ids = product_pricelist_obj.search(cr, uid, [('name', '=', pricelist_name)])
                    print 'pricelist_ids', pricelist_ids
                    if pricelist_ids:
                        pricelist_id = pricelist_ids[0]
                        
                print 'pricelist_name', pricelist_name
                if warehouse_name:
                    warehouse_ids = warehouse_obj.search(cr, uid, [('name', '=', warehouse_name)])
                    if warehouse_ids:
                        warehouse_id = warehouse_ids[0]
                        
                if sale_plan_day_name:
                    sale_plan_day_ids = sale_plan_day_obj.search(cr, uid, [('name', '=', sale_plan_day_name)])
                    if sale_plan_day_ids:
                        sale_plan_day_id = sale_plan_day_ids[0]
                        
                if sale_plan_trip_name:
                    sale_plan_trip_ids = sale_plan_trip_obj.search(cr, uid, [('name', '=', sale_plan_trip_name)])
                    if sale_plan_trip_ids:
                        sale_plan_trip_id = sale_plan_trip_ids[0]
                        
                if section_name:
                    section_ids = section_obj.search(cr, uid, [('name', '=', section_name)])
                    if section_ids:
                        section_id = section_ids[0]
                        
                if payment_term_name:
                    payment_term_ids = payment_term_obj.search(cr, uid, [('name', '=', payment_term_name)])
                    if payment_term_ids:
                        payment_term_id = payment_term_ids[0]
                
                if products_name:
                    product_ids = product_obj.search(cr, uid, [('name', '=', products_name)])
                    if product_ids:
                        product_id = product_ids[0]
                        
                if aml['DueDate'] == "":
                   
                    _duedate = aml['Date'] 
                elif aml['DueDate'] is not  None:
                  
                    _duedate = aml['DueDate'] 
                elif aml['DueDate'] is  None:
                    _duedate = aml['Date']
                    
                if aml['Void'] == "" and aml['Void'] == "Unvoid": 
                    _state = "draft"
                elif aml['Void'] == "Void":
                    _state = "cancel"
                else:
                    _state = "draft"
                 
                if aml['FOC'] == "":
                    _foc = False
                   
                elif aml['FOC'] == "Yes":
                    _foc = True
                    unit_price = 0
                    discount = 0
                    discount_amount = 0
                    net_total = 0
                else:
                    _foc = False
                   
                    
                if deduct_amt == "":
                    deduct_amt = 0
                elif deduct_amt is None:
                    deduct_amt = 0
                                                      
                if section_id:
                    crm_ids = section_obj.search(cr, uid, [('id', '=', section_id)], context=None)
                    if crm_ids:
                        for line in crm_ids:
                            val = section_obj.browse(cr, uid, line, context=context)
                            analytic_id = val.analytic_account_id.id
                            
                if partner_code:
                   va = partner_obj.search(cr, uid, [('customer_code', '=', partner_code)], context=None)
                   partner_id = va[0]
                
                # Calculate the Discount Amount
                if discount != "":
                    discount_amount = (qty_pcs * unit_price) * (discount / 100.00)
      
                
                # Sale Plan Name, Sale Plan Day,Sale Plan Trip, Deliver Remark, Discount, Deduction Amount,Paid Amount, Paid,Void
                order_value = {
                              'partner_id':partner_id,
                              'company_id':1,  # company_id,
                              'user_id':user_id,
                              'warehouse_id':warehouse_id,
                              'customer_code':partner_code,
                              'sale_plan_name':sale_plan_name,
                              'sale_plan_day_id':sale_plan_day_id,
                              'sale_plan_trip_id':sale_plan_trip_id,
                              'section_id':section_id,
                              'payment_term':payment_term_id,
                              'date_order':aml['Date'],
                              'due_date':_duedate,
                              'date_confirm':aml['Date'],
                              'payment_type':payment_type.lower(),
                              'delivery_remark':delivery_remark.lower(),
                              'project_id':analytic_id,
                              'pricelist_id':pricelist_id,
#                                   'amount_total':aml['TotalAmount'],
                              'state':_state,
                              
                              'deduct_amt':deduct_amt,
                              'tb_ref_no':aml['OrderReference']
                              }
             
                order_ids = order_obj.search(cr, uid, [('tb_ref_no', '=', aml['OrderReference'])], context=context)
                if order_ids:
                    order_id = order_ids[0]
                else:
                    order_id = order_obj.create(cr, uid, order_value, context)
                # print 'order id',order_id            
                if products_name:
                    order_line_value = {
                                  'order_id':order_id,
                                  'product_id':product_id,
                                  'name':products_name,
                                  'price_unit':unit_price,
                                  'product_uom':1,
                                  'product_uom_qty':qty_pcs,
                                  'discount':discount,
                                  'discount_amt':discount_amount,
                                  'company_id':1,  # company_id,
                                  'state':'draft',
                                  'net_total':net_total,
                                  'sale_foc':_foc
                                  # 'invoiced':'TRUE',
                
                                }
          
                    
                    order_line_id = order_line_obj.create(cr, uid, order_line_value, context)
                  
                    # Tax Filed is inserted into the sale_order_tax table
                    cr.execute('select id,name,description  from account_tax where parent_id is null')
                    tax_rec = cr.fetchall() 
                
#                     for  k in tax_rec:
#                             
#                         if k[2]==  aml['Tax']:
#                             print 'Description', k[2]
#                             _tax= k[0]
#                         elif k[1]==  aml['Tax']:
#                             print 'Name Tax', k[1]
#                             _tax= k[0]
                   
                    if aml['Tax']:
                        val_tax = aml['Tax'].split(',')
                        for num in val_tax:
                            for  k in tax_rec:
                                if k[2] == num:
                                    print 'Description', k[2]
                                    _tax = k[0]
                                elif k[1] == num:
                                    print 'Name Tax', k[1]
                                    _tax = k[0]
                                
                            if _tax != None:
                                print '_tax_', _tax
                                print 'order_line_id', order_line_id
                                cr.execute("insert into sale_order_tax (order_line_id,tax_id) values(%s,%s)", (order_line_id, _tax,))
                          

                   
                self.write(cr, uid, ids[0], {'state': 'completed'})
                         
#            COPY mobile_sale_order_temp FROM '/Users/iMac/akdata/order.csv' WITH CSV header
        
        
    
# mobile_sale_import()
