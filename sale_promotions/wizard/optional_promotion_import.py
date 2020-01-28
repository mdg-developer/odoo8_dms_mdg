from openerp.osv import orm
from openerp.osv import fields, osv
from xlrd import open_workbook
from openerp.tools.translate import _
from datetime import datetime
import base64
import logging
_logger = logging.getLogger(__name__)
CONDITION = [    
    ('>=', _('greater than or equal to')),    
    ('<=', _('less than or equal to')),
]
header_fields=['product code','quantity']
class optional_promotion_import(osv.osv):
    _name="optional.promotion.import"
    _columns={
              'import_fname':fields.char('File Name',size=128,required=True),
              'file':fields.binary('File',required=True),
              'condition': fields.selection(CONDITION, 'Condition', required=True),
              'amount':fields.float('Amount', required=True),              
              'note':fields.text('Log'),
              }
    def _check_file_ext(self, cursor, user, ids):
        for file in self.browse(cursor, user, ids):
            if '.xls' in file.import_fname:return True
            else: 
                raise osv.except_osv( _('Error!'),_("File is not correct!"))
                return False
        return True
    
    def product_import(self,cr,uid,ids,context=None):
        
        product_obj = self.pool.get('product.product')
        category_obj = self.pool.get('product.category')
        pricelist_item_obj = self.pool.get('sale.optional.promotion')
        
        data = self.browse(cr,uid,ids)[0]
        import_file = data.file
        rule_id = context['rule_id']
        condition = data.condition
        amount = data.amount
        
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
                if head_count < 1:
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
                    product_code_i = None
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
                        elif header_field == 'quantity':
                            quantity_i = i
                    for f in [(product_code_i,'product code'),(quantity_i,'quantity')]:
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
                    import_vals['quantity'] =  ln[quantity_i]
                    amls.append(import_vals)
       
        
        if err_log:
            self.write(cr, uid, ids[0], {'note': err_log})
            self.write(cr, uid, ids[0], {'state': 'error'})
        else:
            try:
                for aml in amls:
                    product_id = code = category_id = name = min_qty = category = price_list = price_type = prod = temp = None
                    quantity = 0
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
                    
                    if aml['quantity']:
                        quantity = aml['quantity']
                            
                    if code:
                        name = code
                    
                        
                    if product_id:
                        prod = self.pool.get('product.product').read(cr, uid, product_id, ['product_tmpl_id'])
                        if prod:
                            product_tmpl_id = prod['product_tmpl_id'][0]
                        temp = self.pool.get('product.template').read(cr,uid,product_tmpl_id,['list_price'])
                        if temp:
                                                  
                        
                            value = { 'rule_id':rule_id, 'product_id':product_id, 'condition':condition, 'amount':amount, 'quantity':quantity}
                            promotion_id = pricelist_item_obj.search(cr, uid, [('rule_id', '=', rule_id), ('product_id', '=', product_id), ('condition', '=', condition),('amount', '=', amount),('quantity', '=', quantity)])
                            if not promotion_id:
                                pricelist_item_obj.create(cr, uid, value, context=context)
                        
            except Exception,e:
                raise osv.except_osv(_('Warning!'),_('Something wrong with this %s .')%(e))