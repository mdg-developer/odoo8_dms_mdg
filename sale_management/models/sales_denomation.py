from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
from datetime import datetime
class sale_denomination(osv.osv):
    
    _name = "sales.denomination"
    _description = "Sales Denomination"         
    
    def _get_default_company(self, cr, uid, context=None):
        company_id = self.pool.get('res.users')._get_company(cr, uid, context=context)
        if not company_id:
            raise osv.except_osv(_('Error!'), _('There is no default company for the current user!'))
        return company_id        
    
    _columns = {
        'company_id':fields.many2one('res.company', 'Company'),
        'date':fields.datetime('Date'),
        'sale_team_id':fields.many2one('crm.case.section', 'Sales Team' , required=True),
        'user_id':fields.many2one('res.users', 'Salesman Name'  , required=True, select=True, track_visibility='onchange'),
        'tablet_id':fields.char('Tablet ID'),
        'name':fields.char('Txn' ,readonly=True),
        'invoice_count':fields.integer('Invoiced' , required=True),        
       'denomination_product_line':fields.one2many('sales.denomination.product.line', 'denomination_product_ids', string='Sale denomination Product Line', copy=True , required=True),
       'denomination_note_line':fields.one2many('sales.denomination.note.line', 'denomination_note_ids', string='Sale denomination Product Line', copy=True , required=True),       
       'denomination_cheque_line':fields.one2many('sales.denomination.cheque.line', 'denomination_cheque_ids', string='Sale denomination Cheque Line', copy=True , required=True),       
        'note':fields.text('Note'),
      'total_amount':fields.float('Denomination Total'),
      'product_amount':fields.float('Invoice Total'),
      'diff_amount':fields.float('Difference'),
      'partner_id':fields.many2one('res.partner', string='Partner'),

  }
    _defaults = {
        'date': fields.datetime.now,
        'company_id': _get_default_company,
        }   
    
    def on_change_date(self, cr, uid, ids, date,user_id,context=None):
        value={}
        note =[{'notes':10000,'note_qty':False},{'notes':5000,'note_qty':False},{'notes':1000,'note_qty':False},{'notes':500,'note_qty':False},{'notes':100,'note_qty':False},{'notes':50,'note_qty':False},{'notes':10,'note_qty':False},{'notes':1,'note_qty':False}]
        order_line_data=[]
        cheque_data=[]
        team_id=None
        payment_ids=None

        if date:
            date = datetime.strptime(date,'%Y-%m-%d %H:%M:%S')
            de_date=date.date()
            mobile_sale_obj = self.pool.get('mobile.sale.order')        
            mobile_sale_order_obj = self.pool.get('mobile.sale.order.line') 
            payment_obj=self.pool.get('customer.payment')
            if user_id:
                cr.execute("select default_section_id from res_users where id= %s ",(user_id,))
                team_id=cr.fetchone()[0]            
            mobile_ids = mobile_sale_obj.search(cr, uid,[('due_date', '=',de_date), ('void_flag', '!=', 'voided'),('user_id','=',user_id)], context=context)
            if team_id:
                cr.execute("select id from customer_payment where date=%s and sale_team_id=%s and cheque_no !=''  ",(de_date,team_id,))
                #payment_ids = payment_obj.search(cr, uid,[('date', '=',de_date),('sale_team_id','=',team_id),('cheque_no','!=',None)], context=context)
                payment_ids=cr.fetchall()
                print 'payyyyyyyyyyyyyyyy',payment_ids
            if  mobile_ids:
                line_ids = mobile_sale_order_obj.search(cr, uid,[('order_id', 'in',mobile_ids)], context=context)                        
                order_line_ids = mobile_sale_order_obj.browse(cr, uid, line_ids, context=context)                  
                cr.execute('select product_id,sum(product_uos_qty),sum(sub_total) from mobile_sale_order_line where id in %s group by product_id',(tuple(order_line_ids.ids),))
                order_line=cr.fetchall()
                for data in order_line:
                    product = self.pool.get('product.product').browse(cr, uid, data[0], context=context)
                    sequence=product.sequence
                    data_id={'product_id':data[0],
                                      'product_uom_qty':data[1],
                                      'sequence':sequence,
                                      'amount':data[2]}
                    order_line_data.append(data_id)
            if  payment_ids:
                for payment in payment_ids:
                    payment_data = payment_obj.browse(cr, uid, payment, context=context)                  
                    partner_id=payment_data.partner_id.id
                    journal_id=payment_data.journal_id.id
                    cheque_no=payment_data.cheque_no
                    amount=payment_data.amount
                    data_id={'partner_id':partner_id,
                                      'journal_id':journal_id,
                                      'cheque_no':cheque_no,
                                      'amount': amount,}
                    cheque_data.append(data_id)                    
                value['value'] = {
                                            'denomination_product_line': order_line_data ,
                                            'denomination_note_line':note,
                                            'denomination_cheque_line':cheque_data,
                                            } 
                
        return value      

    def create(self, cursor, user, vals, context=None):
        credit_no = self.pool.get('ir.sequence').get(cursor, user,
            'sales.denomination') or '/'
        vals['name'] = credit_no
        total_amount=False
        deno_amount=False
        denomination_note_line=vals['denomination_note_line']
        denomination_product_line=vals['denomination_product_line']
        if denomination_product_line:
            
            for p_data in denomination_product_line:
                amount=p_data[2]['amount']
                deno_amount+=amount
        vals['product_amount'] = deno_amount
        if denomination_note_line:
            for data in denomination_note_line:
                note=data[2]['notes']
                qty=data[2]['note_qty']
                total_amount+=(int(note)*int(qty))
        vals['total_amount'] = total_amount
        vals['diff_amount'] = total_amount-deno_amount
           
        return super(sale_denomination, self).create(cursor, user, vals, context=context)    
sale_denomination()               

class sale_denomination_product_line(osv.osv):    
    _name = 'sales.denomination.product.line'
    _columns = {
                'denomination_product_ids': fields.many2one('sales.denomination', 'Sales denomination'),
                'product_id':fields.many2one('product.product', 'Product', required=True),
                'product_uom_qty':fields.integer('QTY', required=True),
                'amount':fields.float('Amount',required=True, digits_compute= dp.get_precision('Product Price')), 
                'sequence':fields.integer('Sequence'),               
                }
sale_denomination_product_line()    

class sale_denomination_note_line(osv.osv):    
    _name = 'sales.denomination.note.line'
    
    def on_change_note_qty(self, cr, uid, ids, notes, note_qty, context=None):
        values = {}
        if notes and note_qty:
            values = {
                'amount':float(notes) *note_qty,
            }
        return {'value': values}   
    
    _columns = {
                'denomination_note_ids': fields.many2one('sales.denomination', 'Sales Denomination'),
                'notes':fields.char('Notes', required=True),
                'note_qty':fields.integer('Qty', required=True),
                'amount':fields.float('Total', digits_compute= dp.get_precision('Product Price')),                
                }
    _defaults = {
        'amount': 0.0,
        }   
sale_denomination_note_line()    

class sale_denomination_cheque_line(osv.osv):    
    _name = 'sales.denomination.cheque.line'
    
    _columns = {
                'denomination_cheque_ids': fields.many2one('sales.denomination', 'Sales Denomination'),
                'cheque_no':fields.char('Cheque No', required=True),
                'partner_id':fields.many2one('res.partner','Customer', required=True),
                'amount':fields.float('Total', digits_compute= dp.get_precision('Product Price')),       
                'journal_id':fields.many2one('account.journal',"Journal"),         
                }
    _defaults = {
        'amount': 0.0,
        }   
    
sale_denomination_cheque_line()    
