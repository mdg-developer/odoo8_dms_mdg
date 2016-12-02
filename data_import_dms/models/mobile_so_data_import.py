from openerp.osv import fields, osv
from openerp.osv import orm
from xlrd import open_workbook
from openerp.tools.translate import _
from datetime import datetime
import base64
import logging


_logger = logging.getLogger(__name__)
header_fields = ['orderreference', 'voucherno', 'duedate', 'customercode', 'saleplanname', 'salemanname', 'saleplanday', 'saleplantrip', 'warehouse', 'location', 'date', 'orderid', 'customer', 'totalamount', 'paidamount', 'quantity',
                 'discount', 'vochertype', 'paymenttime', 'paymenttype', 'deliverremark', 'deductionamount', 'paid', 'void', 'productscode', 'foc', 'tax', 'pricelist',
                 'products', 'quantity(pcs)', 'unitprice', 'subtotal', 'discount(%)', 'discountamount', 'nettotalamount', 'saleteam', 'paymentterm']

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
                    print 's.cell(row, col).value',s.cell(row, col).value
                    values.append(s.cell(row, col).value)
                    print 'values',values
                excel_rows.append(values)
        con_ls = []
        amls = []
        count = val = head_count = 0
        print 'excel_rows',excel_rows
        for ln in excel_rows:
            print 'ln',ln
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
                    pricelist_i = orderid_i = paymenttime_i = customer_i = totalamount_i = paidamount_i = quantity_i = discount_i = vochertype_i = tax_i = orderreference_i = duedate_i = nettotalamount_i = discountamount_i = saleplanname_i = salemanname_i = saleplanday_i = saleplantrip_i = warehouse_i = location_i = date_i = paymenttype_i = deliverremark_i = None
                    foc_i = discount_i = deductionamount_i = paid_i = void_i = products_i = quantity_i = unitprice_i = subtotal_i = saleteam_i = paymentterm_i = None
                    customercode_i = None
                    productscode_i = None
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
                            customercode_i = i
                        elif header_field == 'saleplanname':
                            saleplanname_i = i
                        elif header_field == 'salemanname':
                            salemanname_i = i
                        elif header_field == 'saleplanday':
                            saleplanday_i = i
                        elif header_field == 'saleplantrip':
                            saleplantrip_i = i
                        elif header_field == 'warehouse':
                            warehouse_i = i
                        elif header_field == 'pricelist':
                            pricelist_i = i
                        elif header_field == 'location':
                            location_i = i
                        elif header_field == 'date':
                            date_i = i
                            print 'date_i',date_i
                        elif header_field == 'paymenttype':
                            paymenttype_i = i
                        elif header_field == 'deliverremark':
                            deliverremark_i = i
                        elif header_field == 'paid':
                            paid_i = i
                        elif header_field == 'void':
                            void_i = i
                        elif header_field == 'foc':
                            foc_i = i
                        elif header_field == 'productscode':
                            productscode_i = i
                        elif header_field == 'products':
                            products_i = i
                        elif header_field == 'quantity(pcs)':
                            quantity_i = i
                        elif header_field == 'unitprice':
                            unitprice_i = i
                        elif header_field == 'productdiscount':
                            productdiscount_i = i
                        elif header_field == 'subtotal':
                            subtotal_i = i    
                        elif header_field == 'saleteam':
                            saleteam_i = i
                        elif header_field == 'paymentterm':
                            paymentterm_i = i     
                        elif header_field == 'discount(%)':
                            discount_i = i   
                        elif header_field == 'discountamount':
                            discountamount_i = i
                        elif header_field == 'deductionamount':
                            deductionamount_i = i
                        elif header_field == 'nettotalamount':
                            nettotalamount_i = i      
                        elif header_field == 'duedate':
                            duedate_i = i 
                        elif header_field == 'orderreference':
                            orderreference_i = i
                        elif header_field == 'tax':
                            tax_i = i              
                        elif header_field == 'orderid':
                            orderid_i = i
                        elif header_field == 'customer':
                            customer_i = i
                        elif header_field == 'totalamount':
                            totalamount_i = i
                        elif header_field == 'paidamount':
                            paidamount_i = i
                        elif header_field == 'quantity':
                            quantity_i = i
                        elif header_field == 'discount':
                            discount_i = i
                        elif header_field == 'vochertype':
                            vochertype_i = i
                        elif header_field == 'paymenttime':
                            paymenttime_i = i                 
                      
                    for f in [(orderid_i, 'orderid'), (customer_i, 'customer'), (totalamount_i, 'totalamount'), (paidamount_i, 'paidamount'), (quantity_i, 'quantity'), (discount_i, 'discount'), (vochertype_i, 'vochertype'),
                              (paymenttime_i, 'paymenttime'), (orderreference_i, 'orderreference'), (duedate_i, 'duedate'), (nettotalamount_i, 'nettotalamount'), (discountamount_i, 'discountamount'),
                               (customercode_i, 'customercode'), (saleplanname_i, 'saleplanname'),
                              (salemanname_i, 'salemanname'), (saleplanday_i, 'saleplanday'), (saleplantrip_i, 'saleplantrip'), (warehouse_i, 'warehouse'),
                              (location_i, 'location'), (date_i, 'date'), (paymenttype_i, 'paymenttype'), (deliverremark_i, 'deliverremark'),
                              (discount_i, 'discount(%)'), (deductionamount_i, 'deductionamount'), (tax_i, 'tax'), (pricelist_i, 'pricelist'),
                              (paid_i, 'paid'), (void_i, 'void'), (foc_i, 'foc'), (productscode_i, 'productscode'), (products_i, 'products'), (quantity_i, 'quantity(pcs)'), (unitprice_i, 'unitprice'),
                              (subtotal_i, 'subtotal'), (saleteam_i, 'saleteam'), (paymentterm_i, 'paymentterm')]:
                        if not isinstance(f[0], int):
                            err_log += '\n' + _("Invalid Excel file, Header '%s' is missing !") % f[1]                           

                        
                # process data lines   
            else:
                # add the without value for without header fields columns
                for i in range(0, val):
                    ln.append('')
                if ln and ln[0] and ln[0][0] not in ['#', '']:
                    import_vals = {}
                    import_vals['customercode'] = ln[customercode_i]
                    import_vals['tax'] = ln[tax_i]
                    import_vals['saleplanname'] = ln[saleplanname_i]
                    import_vals['salemanname'] = ln[salemanname_i]
                    import_vals['saleplanday'] = ln[saleplanday_i]
                    import_vals['saleplantrip'] = ln[saleplantrip_i]
                    import_vals['warehouse'] = ln[warehouse_i]
                    import_vals['pricelist'] = ln[pricelist_i]
                    import_vals['location'] = ln[location_i]
                    print 'ln[date_i]',ln[date_i]
                    import_vals['date'] = ln[date_i]
                    import_vals['paymenttype'] = ln[paymenttype_i]
                    import_vals['deliverremark'] = ln[deliverremark_i]
                    import_vals['paid'] = ln[paid_i]
                    import_vals['void'] = ln[void_i]
                    import_vals['foc'] = ln[foc_i]
                    import_vals['products'] = ln[products_i]
                    import_vals['productscode'] = ln[productscode_i]
                    import_vals['quantity(pcs)'] = ln[quantity_i]
                    import_vals['unitprice'] = ln[unitprice_i]
                    import_vals['subtotal'] = ln[subtotal_i]
                    import_vals['saleteam'] = ln[saleteam_i]
                    import_vals['paymentterm'] = ln[paymentterm_i]
                    import_vals['discount(%)'] = ln[discount_i]
                    import_vals['deductionamount'] = ln[deductionamount_i]
                    import_vals['discountamount'] = ln[discountamount_i]
                    import_vals['nettotalamount'] = ln[nettotalamount_i]
                    import_vals['duedate'] = ln[duedate_i]        
                    import_vals['orderreference'] = ln[orderreference_i]    
                    import_vals['orderid'] = ln[orderid_i]
                    import_vals['customer'] = ln[customer_i]
                    import_vals['totalamount'] = ln[totalamount_i]
                    import_vals['paidamount'] = ln[paidamount_i]
                    import_vals['quantity'] = ln[quantity_i]
                    import_vals['discount'] = ln[discount_i]
                    import_vals['vochertype'] = ln[vochertype_i]
                    import_vals['paymenttime'] = ln[paymenttime_i]   
                    print 'import_vals',import_vals      
                    amls.append(import_vals)
                    
        if err_log:
            self.write(cr, uid, ids[0], {'note': err_log})
            self.write(cr, uid, ids[0], {'state': 'error'})
        else:
            order_id = None
            for aml in amls:
                print 'aml', aml
                _tax = _foc = _state = analytic_id = pricelist_id = partner_id = country_id = saleperson_id = warehouse_id = product_id = user_id = sale_plan_day_id = sale_plan_trip_id = section_id = payment_term_id = _duedate = None
                
                product_code = aml['productscode']
               
                products = aml['products']
                
                products_name = '[' + product_code + '] ' + products
                
                if products_name:
                    products = products_name.split(' ', 1)
                    products_name = products[1]
                
                partner_code = str(aml['customercode'])
                sale_plan_name = str(aml['saleplanname'])
                payment_type = str(aml['paymenttype'])
                delivery_remark = str(aml['deliverremark'])
                saleperson_name = aml['salemanname']
                warehouse_name = aml['warehouse']
                sale_plan_day_name = aml['saleplanday']
                sale_plan_trip_name = aml['saleplantrip']
                section_name = aml['saleteam']
                payment_term_name = aml['paymentterm']
                discount_amount = aml['discountamount']
                qty_pcs = aml['quantity(pcs)']
                unit_price = aml['unitprice']
                discount = aml['discount(%)']
                deduct_amt = aml['deductionamount']
                pricelist_name = aml['pricelist']                            
                net_total = aml['nettotalamount']
               
                        
                   
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
                        
                if aml['duedate'] == "":
                   
                    _duedate = aml['date'] 
                elif aml['duedate'] is not  None:
                  
                    _duedate = aml['duedate'] 
                elif aml['duedate'] is  None:
                    _duedate = aml['date']
                    
                if aml['void'] == "" and aml['void'] == "Unvoid": 
                    _state = "draft"
                elif aml['void'] == "void":
                    _state = "cancel"
                else:
                    _state = "draft"
                 
                if aml['foc'] == "":
                    _foc = False
                   
                elif aml['foc'] == "Yes":
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
      
                print 'aml[date]',aml['date']
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
                              'date_order':aml['date'],
                              'due_date':_duedate,
                              'date_confirm':aml['date'],
                              'payment_type':payment_type.lower(),
                              'delivery_remark':delivery_remark.lower(),
                              'project_id':analytic_id,
                              'pricelist_id':pricelist_id,
#                                   'amount_total':aml['TotalAmount'],
                              'state':_state,
                              
                              'deduct_amt':deduct_amt,
#                               'tb_ref_no':aml['OrderReference']
                              'tb_ref_no':aml['orderreference']
                              }
             
                order_ids = order_obj.search(cr, uid, [('tb_ref_no', '=', aml['orderreference'])], context=context)
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
                                  'product_uom':20,
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
                   
                    if aml['tax']:
                        val_tax = aml['tax'].split(',')
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
