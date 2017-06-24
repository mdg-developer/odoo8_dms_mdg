from openerp.osv import orm
from openerp.osv import fields, osv
from xlrd import open_workbook
from openerp.tools.translate import _
from datetime import datetime
import base64
import logging
_logger = logging.getLogger(__name__)

header_fields=['product code','minimum quantity','pricelist','product category','discount amount']
class product_pricelist_import(osv.osv):
    _name="product.pricelist.import"
    _columns={
              'import_fname':fields.char('File Name',size=128,required=True),
              'file':fields.binary('File',required=True),
            'note':fields.text('Log'),
              }
    
    def _check_file_ext(self, cursor, user, ids):
        for file in self.browse(cursor, user, ids):
            if '.xls' in file.import_fname:return True
            else: 
                raise osv.except_osv( _('Error!'),_("File is not correct!"))
                return False
        return True
    
    
    def price_dis_change(self, cr, uid, ids,product_id,price_discount,new_price,price_surcharge, context=None):
        
        if not product_id:
            return {}
        prod = self.pool.get('product.product').read(cr, uid, [product_id], ['code','name','product_tmpl_id'])
        product_tmpl_id = prod[0]['product_tmpl_id'][0]
        temp = self.pool.get('product.template').read(cr,uid,[product_tmpl_id],['list_price'])
        product_price = temp[0]['list_price']
        
        if price_discount:
            new_price = (product_price * (1+price_discount))+price_surcharge
            return {'value':{'new_price':new_price}}
        return {}

    
    def product_import(self,cr,uid,ids,context=None):
        
        product_obj = self.pool.get('product.product')
        category_obj = self.pool.get('product.category')
        pricelist_item_obj = self.pool.get('product.pricelist.item')
        
        data = self.browse(cr,uid,ids)[0]
        import_file = data.file
        pricelist_id = context['pricelist_id']
        version_id = context['version_id']
        err_log = ''
        header_line = False
        lines = base64.decodestring(import_file)
        wb = open_workbook(file_contents = lines)
        excel_rows=[]
        for s in wb.sheets():
            #header
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
        count = val = head_count = 0
        for ln in excel_rows:
            #ln = [str(x).strip() for x in ln]
            if not ln or ln and ln[0] and ln[0][0] in ['', '#']:
                continue
            # process header line
            if not header_line:
                for l in header_fields:
                    if str(l).strip().lower() in [str(x).strip().lower() for x in ln]:
                        head_count = head_count + 1
                if head_count < 2:
                    print 'Illegal Header Fields'
                
                else:
                    
                    if ln:
                        for l in header_fields:
                            if str(l).strip() in [str(x).strip().lower() for x in ln]:
                                print 'same fields', l
                            else:
                                #check the columns without contained the header fields
                                ln.append(str(l))
                                count = count + 1
                                val = count
                    header_line = True
                    product_code_i = minimum_quantity_i = pricelist_i = product_category_i = discount_amount_i = None
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
                            err_log += '\n' + _("Invalid CSV File, Header Field '%s' is not supported !") %ln[i]
                        # required header fields : account, debit, credit
                        elif header_field == 'product code':
                            product_code_i = i
                        elif header_field == 'minimum quantity':
                            minimum_quantity_i = i
                        elif header_field == 'pricelist':
                            pricelist_i = i
                        elif header_field == 'product category':
                            product_category_i = i
                        elif header_field =='discount amount':
                            discount_amount_i = i
                    for f in [(product_code_i,'product code'),(minimum_quantity_i,'minimum quantity'),(pricelist_i,'pricelist'),(product_category_i,'product category'),(discount_amount_i,'discount amount')]:
                        if not isinstance(f[0],int):
                            err_log += '\n'+ _("Invalid Excel file, Header '%s' is missing !") % f[1]
                         
                #process data lines   
            else:
                #add the without value for without header fields columns
                for i in range(0, val):
                    ln.append('')
                if ln and ln[0] and ln[0][0] not in ['#','']:
                    import_vals = {}
                    import_vals['product code'] =  ln[product_code_i]
                    import_vals['minimum quantity'] = ln[minimum_quantity_i]
                    import_vals['pricelist'] = ln[pricelist_i]
                    import_vals['product category'] = ln[product_category_i]
                    import_vals['discount amount'] = ln[discount_amount_i]
                    amls.append(import_vals)
       
        
        if err_log:
            self.write(cr, uid, ids[0], {'note': err_log})
            self.write(cr, uid, ids[0], {'state': 'error'})
        else:
            try:
                for aml in amls:
                    product_id = code = category_id = name = min_qty = category = price_list = price_type = prod = temp = None
                    discount_amount = new_price =0.0
                    if aml['product code']:
                        code = str(aml['product code'])
                        cr.execute('select id from product_product where lower(default_code) like %s',(code.lower(),))
                        product_ids = cr.fetchall()
                        if product_ids:
                            product_id = product_ids[0]
                        else:
                            product_id = None
                    else:
                        code = ''
                        
                    if code:
                        name = code
                    if aml['product category']:
                        category = str(aml['product category'])
                        cr.execute('select id from product_category where lower(name) like %s',(category.lower(),))
                        category_ids = cr.fetchall()
                        if category_ids:
                            category_id =category_ids[0]
                        else:
                            category_id = None
                    else:
                        category = ''
                        category_id = None
                        
                    if aml['minimum quantity']:
                        min_qty = float(aml['minimum quantity'])
                    
                    if aml['pricelist']:
                        price_list = str(aml['pricelist'])
                        if price_list.lower() =='public price':
                            price_type = int(1)
                        elif price_list.lower() =='cost price':
                            price_type = int(2)
                        elif price_list.lower() =='other price':
                            price_type = int(-1)
                        elif price_list.lower() =='supplier price':
                            price_type = int(-2)
                    if aml['discount amount']:
                        discount_amount = float(aml['discount amount'])
                        
                    if product_id:
                        prod = self.pool.get('product.product').read(cr, uid, product_id, ['product_tmpl_id'])
                        if prod:
                            product_tmpl_id = prod['product_tmpl_id'][0]
                        temp = self.pool.get('product.template').read(cr,uid,product_tmpl_id,['list_price'])
                        if temp:
                            product_price = temp['list_price']
                        
                        if discount_amount:
                            new_price = (product_price * (1 + 0.0)) + discount_amount
                            pricelist_res_discount = {'name':name, 'price_version_id':version_id, 'product_id':product_id, 'categ_id':category_id, 'min_quantity':min_qty, 'base':price_type, 'base_pricelist_id':None, 'price_surcharge':discount_amount, 'new_price':new_price}
                            pricelist_item_obj.create(cr,uid,pricelist_res_discount,context=context)
                        
                        if discount_amount == 0:
                            new_price = (product_price * (1 + 0.0)) + discount_amount
                            pricelist_res_nodiscount = {'name':name, 'price_version_id':version_id, 'product_id':product_id, 'categ_id':category_id, 'min_quantity':min_qty, 'base':price_type, 'base_pricelist_id':None, 'price_surcharge':product_price, 'new_price':new_price}
                            pricelist_item_obj.create(cr, uid, pricelist_res_nodiscount, context=context)
                        
            except Exception,e:
                raise osv.except_osv(_('Warning!'),_('Something wrong with this %s .')%(e))    