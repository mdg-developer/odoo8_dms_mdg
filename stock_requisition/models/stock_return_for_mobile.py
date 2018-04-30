'''
Created on Auguest 31, 2016

@author: Administrator
'''
import time

from openerp.osv import fields , osv
from openerp.tools.translate import _


class stock_return_from_mobile(osv.osv):
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _name = "stock.return.mobile"
    _description = "Stock Return From Mobile"
    _order = "id desc"    
    
    def onchange_sale_team_id(self, cr, uid, ids, section_id, context=None):
        team_obj = self.pool.get('crm.case.section')
        branch_id = False        
        vehicle_id=False
        if section_id:
            team_id = team_obj.browse(cr, uid, section_id, context=context)
            branch_id = team_id.branch_id.id         
            vehicle_id=team_id.vehicle_id.id
        return {'value': {'branch_id': branch_id,'vehicle_id':vehicle_id}}         
    
    _columns = {
        'sale_team_id':fields.many2one('crm.case.section', 'Sales Team' , required=True),
        'user_id':fields.many2one('res.users', 'Return From'  , required=True, select=True, track_visibility='onchange'),
         'return_date':fields.date('Date of Return'),
        'vehicle_id':fields.many2one('fleet.vehicle', 'Vehicle No'),
        'p_line':fields.one2many('stock.return.mobile.line', 'line_id', 'Product Lines',
                              copy=True),
               'branch_id':fields.many2one('res.branch', 'Branch'),
        'company_id':fields.many2one('res.company', 'Company'),

}
    _defaults = {
        'state' : 'draft',
    }     
    def manual_data(self, cr, uid, ids, context=None):
        note_obj = self.pool.get('good.issue.note')
        account_inv_obj = self.pool.get('account.invoice')
        stock_return_obj = self.pool.get('stock.return.mobile.line')
        if ids:
            cr.execute('delete from stock_return_mobile_line where line_id=%s', (ids[0],))
            mobile_return_data = self.browse(cr, uid, ids, context=context)
            return_date = mobile_return_data.return_date
            user_id=mobile_return_data.user_id.id
            sale_team_id = mobile_return_data.sale_team_id.id
            note_ids = note_obj.search(cr, uid, [('sale_team_id', '=', sale_team_id), ('issue_date', '=', return_date),('state','!=','cancel')])
            if  note_ids:        
                cr.execute('select gin.from_location_id as location_id,product_id,big_uom_id,sum(big_issue_quantity) as big_issue_quantity,sum(issue_quantity) as issue_quantity,product_uom  as small_uom_id from good_issue_note gin ,good_issue_note_line  ginl where gin.id = ginl.line_id and gin.id in %s group by product_id,from_location_id,big_uom_id,product_uom', (tuple(note_ids),))
                p_line = cr.fetchall()       
            else:
                raise osv.except_osv(_('Warning'),
                     _('Please Check Your GIN Record'))     
            for note_line in p_line:
                product_id = note_line[1]
                #big_uom_id = note_line[2]
                #big_issue_quantity = note_line[3]
                small_issue_quantity = note_line[4]
                small_uom_id=note_line[5]
                receive_qty=small_issue_quantity

                product = self.pool.get('product.product').browse(cr, uid, product_id, context=context)
                if small_uom_id != product.product_tmpl_id.uom_id.id:                                                                          
                    cr.execute("select floor(round(1/factor,2)) as ratio from product_uom where active = true and id=%s", (small_uom_id,))
                    bigger_qty = cr.fetchone()[0]
                    receive_qty = (small_issue_quantity * bigger_qty)
                  
                return_ids = stock_return_obj.search(cr, uid, [('product_id', '=', product_id),('line_id','=',ids[0])], context=context) 
                if return_ids:
                    cr.execute("update stock_return_mobile_line set return_quantity=return_quantity+%s where product_id=%s and line_id =%s",(receive_qty,product_id,ids[0],)) 
                else:
                    stock_return_obj.create(cr, uid, {'line_id': ids[0],
                                  'product_id': product_id,
                                  'return_quantity':receive_qty,
                                  'sale_quantity':0,
                                  'foc_quantity':0,
                                  'product_uom': small_uom_id ,
                            }, context=context)
            order_ids = account_inv_obj.search(cr, uid, [('section_id', '=', sale_team_id),('user_id','=',user_id), ('state', '=', 'open'),('date_invoice','=',return_date)], context=context) 
            order_list = str(tuple(order_ids))
            order_list = eval(order_list)
            if order_list:
                cr.execute("select avl.product_id,sum(quantity) as qty ,avl.uos_id from account_invoice_line avl where  avl.invoice_id in %s and avl.foc=False group by product_id,uos_id", (order_list,))
                account_record = cr.fetchall()             
                if account_record:
                    for sale_data in account_record:
                        product_id = int(sale_data[0])
                        sale_qty = int(sale_data[1])
                        sale_product_uom = int(sale_data[2])
                        product = self.pool.get('product.product').browse(cr, uid, product_id, context=context)
                        if sale_product_uom != product.product_tmpl_id.uom_id.id:                                                                          
                            cr.execute("select floor(round(1/factor,2)) as ratio from product_uom where active = true and id=%s", (sale_product_uom,))
                            bigger_qty = cr.fetchone()[0]
                            bigger_qty = int(bigger_qty)
                            sale_qty = bigger_qty * sale_qty
                        cr.execute('update stock_return_mobile_line set return_quantity = return_quantity - %s, sale_quantity = sale_quantity + %s where line_id= %s and product_id =%s ',(sale_qty,sale_qty,ids[0],product_id,))                
                cr.execute("select avl.product_id,sum(quantity) as qty ,avl.uos_id from account_invoice_line avl where  avl.invoice_id in %s and avl.foc=True group by product_id,uos_id", (order_list,))
                account_foc_record = cr.fetchall()             
                if account_foc_record:
                    for foc_data in account_foc_record:
                        product_id = int(foc_data[0])
                        foc_qty = int(foc_data[1])
                        foc_product_uom = int(foc_data[2])
                        product = self.pool.get('product.product').browse(cr, uid, product_id, context=context)
                        if foc_product_uom != product.product_tmpl_id.uom_id.id:                                                                          
                            cr.execute("select floor(round(1/factor,2)) as ratio from product_uom where active = true and id=%s", (foc_product_uom,))
                            bigger_qty = cr.fetchone()[0]
                            bigger_qty = int(bigger_qty)
                            foc_qty = bigger_qty * foc_qty
                        cr.execute('update stock_return_mobile_line set return_quantity = return_quantity - %s, foc_quantity = foc_quantity + %s where line_id= %s and product_id =%s ',(foc_qty,foc_qty,ids[0],product_id,))                        
        return True 
               
class stock_return_from_mobile_line(osv.osv):
    _name = 'stock.return.mobile.line'
    _description = 'Return Line From Mobile'
    _columns = {                
        'line_id':fields.many2one('stock.return.mobile', 'Line', ondelete='cascade', select=True),
        'product_id': fields.many2one('product.product', 'Product', required=True),
        'return_quantity' : fields.float(string='Returned Qty', digits=(16, 0)),
        'sale_quantity' : fields.float(string='Sales Qty', digits=(16, 0)),
        'foc_quantity' : fields.float(string='FOC Qty', digits=(16, 0)),
        'product_uom': fields.many2one('product.uom', 'UOM', required=True),
    }
        
   
    
