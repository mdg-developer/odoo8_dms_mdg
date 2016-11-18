from openerp.osv import fields, osv
from openerp.osv import orm
from xlrd import open_workbook
from openerp.tools.translate import _
from datetime import datetime
import base64
import logging

_logger = logging.getLogger(__name__)
header_fields = ['OrderReference','DueDate','Customer', 'CustomerCode', 'SalePlanName','SalemanName','SalePlanDay','SalePlanTrip', 'Warehouse', 'Location', 'Date',
                 'PaymentType','DeliverRemark','DeductionAmount', 'Paid','Void','ProductsCODE',
                 'Products', 'Quantity', 'UnitPrice', 'SubTotal','Discount', 'DiscountAmount','NetTotalAmount','VocherType','SaleTeam', 'PaymentTime']

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
            #'import_date':datetime.date.now(),
                 }
        
    def _check_file_ext(self, cursor, user, ids):
        for import_file in self.browse(cursor, user, ids):
            if '.xls' in import_file.import_fname:return True
            else: return False
        return True
    
    _constraints = [(_check_file_ext,"Please import Excel file!",['import_fname'])]
    
    
    def import_data(self, cr, uid, ids, context=None):   
        users_obj = self.pool.get('res.users')
        partner_obj=self.pool.get('res.partner') 
        product_obj = self.pool.get('product.product')
        order_obj= self.pool.get('sale.order')
        order_line_obj = self.pool.get('sale.order.line')
        warehouse_obj=self.pool.get('stock.warehouse')
        
        
#         category_obj = self.pool.get('product.category')
#         country_obj=self.pool.get('res.country')
#         tablet_obj=self.pool.get('tablets.information')
#         pricelist_obj=self.pool.get('product.pricelist')
        
#         location_obj=self.pool.get('stock.location')
#        parent_cat_id = category_obj.search(cr,uid,[('name','=','All')])
        
        data = self.browse(cr,uid,ids)[0]
        company_id = data.company_id.id
        import_file = data.import_file
        
        err_log=''
        header_line=False
        value={}
        lines= base64.decodestring(import_file)
        wb=open_workbook(file_contents=lines)
        excel_rows=[]
        
        for s in wb.sheets():
            headers=[]
            header_row=0
            for hcol in range(0,s.ncols):
                headers.append(s.cell(header_row,hcol).value)
            #add header
            excel_rows.append(headers)
            for row in range(header_row+1,s.nrows):
                values = []
                for col in range(0,s.ncols):
                    values.append(s.cell(row,col).value)
                excel_rows.append(values)
        amls = []
        
        for ln in excel_rows:
            if not ln or ln and ln[0] and ln[0][0] in ['', '#']:
                continue
            
            # process header line
            if not header_line:
                if ln[0].strip() not in header_fields:
                    raise orm.except_orm(_('Error :'), _("Error while processing the header line %s. \n\nPlease check your Excel separator as well as the column header fields") %ln)
                else:
                    header_line = True
                    OrderRefNo_i = DueDate_i = NetTotalAmount_i = DiscountAmount_i =Customer_i=CustomerCode_i=SalePlanName_i=SalemanName_i=SalePlanDay_i=SalePlanTrip_i=Warehouse_i=Location_i=Date_i=PaymentType_i=DeliverRemark_i=None
                    Discount_i=DeductionAmount_i=Paid_i=Void_i=ProductsCODE_i=Products_i=Quantity_i=UnitPrice_i=SubTotal_i=VocherType_i=SaleTeam_i=PaymentTime_i=None
                    #name_related_i = gender_i = marital_i = identification_id_i = mobile_phone_i = work_phone_i = work_email_i = birthday_i= father_name_i = finger#print_id_i = job_id_i = department_id_i = address_home_id_i = joining_date_i = salary_i = None
                    column_cnt = 0
                    for cnt in range(len(ln)):
                        if ln[cnt] == '':
                            column_cnt = cnt
                            break
                        elif cnt == len(ln)-1:
                            column_cnt = cnt + 1
                            break
                    for i in range(column_cnt):
                        # header fields
                        header_field = ln[i].strip()
                        if header_field not in header_fields:
                            err_log += '\n' + _("Invalid Excel File, Header Field '%s' is not supported !") %ln[i]
                        elif header_field == 'Customer':
                            Customer_i=i
                        elif header_field == 'CustomerCode':
                            CustomerCode_i=i
                        elif header_field == 'SalePlanName':
                            SalePlanName_i=i
                        elif header_field == 'SalemanName':
                            SalemanName_i=i
                        elif header_field == 'SalePlanDay':
                            SalePlanDay_i=i
                        elif header_field == 'SalePlanTrip':
                            SalePlanTrip_i=i
                        elif header_field == 'Warehouse':
                            Warehouse_i=i
                        elif header_field == 'Location':
                            Location_i=i
                        elif header_field == 'Date':
                            Date_i=i
                        elif header_field == 'PaymentType':
                            PaymentType_i=i
                        elif header_field == 'DeliverRemark':
                            DeliverRemark_i=i
                        elif header_field == 'Paid':
                            Paid_i=i
                        elif header_field == 'Void':
                            Void_i=i
                        elif header_field == 'ProductsCODE':
                            ProductsCODE_i=i
                        elif header_field == 'Products':
                            Products_i=i
                        elif header_field == 'Quantity':
                            Quantity_i=i
                        elif header_field == 'UnitPrice':
                            UnitPrice_i=i
                        elif header_field == 'ProductDiscount':
                            ProductDiscount_i=i
                        elif header_field == 'SubTotal':
                            SubTotal_i=i    
                        elif header_field == 'VocherType':
                            VocherType_i=i
                        elif header_field == 'SaleTeam':
                            SaleTeam_i=i
                        elif header_field == 'PaymentTime':
                            PaymentTime_i=i     
                        elif header_field == 'Discount':
                            Discount_i=i   
                        elif header_field == 'DiscountAmount':
                            DiscountAmount_i=i
                        elif header_field == 'DeductionAmount':
                            DeductionAmount_i=i
                        elif header_field == 'NetTotalAmount':
                            NetTotalAmount_i=i      
                        elif header_field == 'DueDate':
                            DueDate_i=i 
                        elif header_field == 'OrderReference':
                            OrderRefNo_i=i                              
                            
                    for f in [(OrderRefNo_i,'OrderReference'),(DueDate_i,'DueDate'),(NetTotalAmount_i,'NetTotalAmount'),(DiscountAmount_i,'DiscountAmount'),(CustomerCode_i,'CustomerCode'),(Customer_i,'Customer'),(SalePlanName_i,'SalePlanName'),
                              (SalemanName_i,'SalemanName'),(SalePlanDay_i,'SalePlanDay'),(SalePlanTrip_i,'SalePlanTrip'),(Warehouse_i,'Warehouse'),
                              (Location_i,'Location'),(Date_i,'Date'),(PaymentType_i,'PaymentType'),(DeliverRemark_i,'DeliverRemark'),
                              (Discount_i,'Discount'),(DeductionAmount_i,'DeductionAmount'),
                              (Paid_i,'Paid'),(Void_i,'Void'),(ProductsCODE_i,'ProductsCODE'),(Products_i,'Products'),(Quantity_i,'Quantity'),(UnitPrice_i,'UnitPrice'),
                              (SubTotal_i,'SubTotal'),(VocherType_i,'VocherType'),(SaleTeam_i,'SaleTeam'),(PaymentTime_i,'PaymentTime')]:
                        if not isinstance(f[0],int):
                            err_log += '\n'+ _("Invalid Excel file, Header '%s' is missing !") % f[1]                           

                        
                #process data lines   
            else:
                if ln and ln[0] and ln[0][0] not in ['#','']:
                    
                    import_vals = {}
                    
                    import_vals['CustomerCode'] = ln[CustomerCode_i]
                    import_vals['Customer'] = ln[Customer_i]
                    import_vals['SalePlanName'] = ln[SalePlanName_i]
                    import_vals['SalemanName'] = ln[SalemanName_i]
                    import_vals['SalePlanDay'] = ln[SalePlanDay_i]
                    import_vals['SalePlanTrip'] = ln[SalePlanTrip_i]
                    import_vals['Warehouse'] = ln[Warehouse_i]
                    import_vals['Location'] = ln[Location_i]
                    import_vals['Date'] = ln[Date_i]
                    import_vals['PaymentType'] = ln[PaymentType_i]
                    import_vals['DeliverRemark'] = ln[DeliverRemark_i]
                    import_vals['Paid'] = ln[Paid_i]
                    import_vals['Void'] = ln[Void_i]
                    import_vals['ProductsCODE'] = ln[ProductsCODE_i]
                    import_vals['Products'] = ln[Products_i]
                    import_vals['Quantity'] = ln[Quantity_i]
                    import_vals['UnitPrice'] = ln[UnitPrice_i]
                    import_vals['SubTotal'] = ln[SubTotal_i]
                    import_vals['VocherType'] = ln[VocherType_i]
                    import_vals['SaleTeam'] = ln[SaleTeam_i]
                    import_vals['PaymentTime'] = ln[PaymentTime_i]
                    import_vals['Discount'] = ln[Discount_i]
                    import_vals['DeductionAmount'] = ln[DeductionAmount_i]
                    import_vals['DiscountAmount'] = ln[DiscountAmount_i]
                    import_vals['NetTotalAmount'] = ln[NetTotalAmount_i]
                    import_vals['DueDate'] = ln[DueDate_i]        
                    import_vals['OrderReference'] = ln[OrderRefNo_i]          
                    amls.append(import_vals)
                    
        if err_log:
            self.write(cr, uid, ids[0], {'note': err_log})
            self.write(cr, uid, ids[0], {'state': 'failed'})
        else:
            order_id = None
            for aml in amls:
                partner_id = country_id = saleperson_id = warehouse_id = product_id = user_id = None
                
                product_code = aml['ProductsCODE']
                print 'Product_code',product_code
                products = aml['Products']
                print 'Product',aml['Products']
                products_name='['+product_code+'] '+products
                
                if products_name:
                    products=products_name.split(' ',1)
                    products_name = products[1]
                
                partner = aml['Customer']
                partner_code = str(aml['CustomerCode'])
                saleperson_name = aml['SalemanName']
                warehouse_name = aml['Warehouse']
                discount_amount=aml['DiscountAmount']
                discount = aml['Discount']
                deduct_amt=aml['DeductionAmount']
                net_total= aml['NetTotalAmount']
                if partner:
                    partner_ids = partner_obj.search(cr,uid,['&',
                                                                 ('name','=',partner),
                                                                 ('customer_code','=',partner_code)])
                    if not partner_ids:
                        partner_value={
                                  'name':partner,
                                  'country_id':country_id,

                                  }
                        partner_id = partner_obj.create(cr,uid,partner_value, context)
                    else:
                        partner_id = partner_ids[0]
                        
                   
                if saleperson_name:
                    saleperson_ids = partner_obj.search(cr,uid,[('name','=',saleperson_name)])
                    if saleperson_ids:
                        saleperson_id = saleperson_ids[0]
                        user_ids = users_obj.search(cr,uid,[('partner_id','=',saleperson_id)])
                        if user_ids:
                            user_id=user_ids[0]
                
                
                if warehouse_name:
                    warehouse_ids = warehouse_obj.search(cr,uid,[('name','=',warehouse_name)])
                    if warehouse_ids:
                        warehouse_id = warehouse_ids[0]
                
                
                if products_name:
                    product_ids = product_obj.search(cr,uid,[('name','=',products_name)])
                    if product_ids:
                        product_id = product_ids[0]
                #Sale Plan Name, Sale Plan Day,Sale Plan Trip, Deliver Remark, Discount, Deduction Amount,Paid Amount, Paid,Void
                order_value={
                              'partner_id':partner_id,
                              'company_id':1, #company_id,
                              'user_id':user_id,
                              'warehouse_id':warehouse_id,
                              'date_order':aml['Date'],
                              'date_confirm':aml['Date'],
                              'payment_type':'cash', #aml['PaymentType'],
#                                   'amount_total':aml['TotalAmount'],
                              'state':'draft',
                              'deduct_amt':deduct_amt,
                              'tb_ref_no':aml['OrderReference']
                              }
                order_ids = order_obj.search(cr,uid,[('tb_ref_no','=',aml['OrderReference'])],context=context)
                if order_ids:
                    order_id=order_ids[0]
                else:
                    order_id = order_obj.create(cr,uid,order_value, context)
                print 'order id',order_id            
                if products_name:
                    order_line_value={
                                  'order_id':order_id,
                                  'product_id':product_id,
                                  'name':products_name,
                                  'price_unit':aml['UnitPrice'],   
                                  'product_uom':1,      
                                  'product_uom_qty':aml['Quantity'],   
                                  'discount':discount,
                                  'discount_amt':discount_amount,
                                  'company_id':1,#company_id,
                                  'state':'confirmed',
                                  'net_total':net_total
                                  #'invoiced':'TRUE',
                
                                }
          
                    
                    order_line_id=order_line_obj.create(cr,uid,order_line_value, context)
                    ##print 'order_line_id',order_line_id        
                self.write(cr, uid, ids[0], {'state': 'completed'})
                #print amls               
#            COPY mobile_sale_order_temp FROM '/Users/iMac/akdata/order.csv' WITH CSV header
        
        
    
#mobile_sale_import()
