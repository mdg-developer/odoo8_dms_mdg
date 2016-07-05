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
        'note':fields.text('Note'),
  
  }
    _defaults = {
        'date': fields.datetime.now,
        'company_id': _get_default_company,
        }   
    
    def on_change_date(self, cr, uid, ids, date,user_id,context=None):
        value={}
        note =[{'notes':10000,'note_qty':False},{'notes':5000,'note_qty':False},{'notes':1000,'note_qty':False},{'notes':500,'note_qty':False},{'notes':100,'note_qty':False},{'notes':50,'note_qty':False},{'notes':10,'note_qty':False}]
        order_line_data=[]
        date = datetime.strptime(date,'%Y-%m-%d %H:%M:%S')        
        de_date=date.date()
        mobile_sale_obj = self.pool.get('mobile.sale.order')        
        mobile_sale_order_obj = self.pool.get('mobile.sale.order.line') 
        mobile_ids = mobile_sale_obj.search(cr, uid,[('due_date', '=',de_date), ('void_flag', '!=', 'voided'),('user_id','=',user_id)], context=context)
        if  mobile_ids:
            line_ids = mobile_sale_order_obj.search(cr, uid,[('order_id', 'in',mobile_ids)], context=context)                        
            order_line_ids = mobile_sale_order_obj.browse(cr, uid, line_ids, context=context)                  
            cr.execute('select product_id,sum(product_uos_qty),sum(sub_total) from mobile_sale_order_line where id in %s group by product_id',(tuple(order_line_ids.ids),))
            order_line=cr.fetchall()
            for data in order_line:
                data_id={'product_id':data[0],
                                  'product_uom_qty':data[1],
                                  'amount':data[2]}
                order_line_data.append(data_id)
            value['value'] = {
                                        'denomination_product_line': order_line_data ,
                                        'denomination_note_line':note,
                                        } 
        return value      

    def create(self, cursor, user, vals, context=None):
        credit_no = self.pool.get('ir.sequence').get(cursor, user,
            'sales.denomination') or '/'
        vals['name'] = credit_no
        return super(sale_denomination, self).create(cursor, user, vals, context=context)    
sale_denomination()        

class sale_denomination_product_line(osv.osv):    
    _name = 'sales.denomination.product.line'
    _columns = {
                'denomination_product_ids': fields.many2one('sales.denomination', 'Sales denomination'),
                'product_id':fields.many2one('product.product', 'Product', required=True),
                'product_uom_qty':fields.integer('Quantity', required=True),
                'amount':fields.float('Amount',required=True),                
                }
sale_denomination_product_line()    

class sale_denomination_note_line(osv.osv):    
    _name = 'sales.denomination.note.line'
    _columns = {
                'denomination_note_ids': fields.many2one('sales.denomination', 'Sales Denomination'),
                'notes':fields.char('Notes', required=True),
                'note_qty':fields.integer('Qty', required=True),
                }
sale_denomination_note_line()    