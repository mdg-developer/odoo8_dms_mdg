'''
Created on Auguest 31, 2016

@author: Administrator
'''
import time

import os
from datetime import datetime
from datetime import timedelta  
from dateutil.relativedelta import relativedelta
from dateutil import parser
import time
from openerp.osv import fields , osv
from openerp.tools.translate import _
import datetime


class stock_return(osv.osv):
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _name = "stock.return"
    _description = "Stock Return"
    _order = "id desc"    
    _track = {
        'state': {
            'stock_return.mt_return_confirm': lambda self, cr, uid, obj, ctx = None: obj.state in ['confirm'],
            'stock_return.mt_return_approve': lambda self, cr, uid, obj, ctx = None: obj.state in ['approve']
        },
    }    
    
    def on_change_sale_team_id(self, cr, uid, ids, sale_team_id, context=None):
        values = {}
        team_obj= self.pool.get('crm.case.section')
        if sale_team_id:
            team =team_obj.browse(cr, uid, sale_team_id, context=context)
            values = {
                'vehicle_id': team.vehicle_id and team.vehicle_id.id or False,
            }
        return {'value': values}
    
    def _get_default_company(self, cr, uid, context=None):
        company_id = self.pool.get('res.users')._get_company(cr, uid, context=context)
        if not company_id:
            raise osv.except_osv(_('Error!'), _('There is no default company for the current user!'))
        return company_id   
    
    
    def retrieve_data(self, cr, uid,ids, context=None):
        note_obj=self.pool.get('good.issue.note')
        product_trans_obj=self.pool.get('product.transactions')
        product_trans_line_obj=self.pool.get('product.transactions.line')
        mobile_obj=self.pool.get('stock.return.mobile')
        stock_return_obj=self.pool.get('stock.return.line')
        product_obj=self.pool.get('product.product')

        
        if ids:
            cr.execute('delete from stock_return_line where line_id=%s',(ids[0],))
            return_data=self.browse(cr, uid, ids, context=context)
            return_date=return_data.return_date
            return_from=return_data.return_from.id            
            sale_team_id=return_data.sale_team_id.id
            note_id=return_data.note_id.id
            print 'sale_team_id',sale_team_id,ids                                               
#             cr.execute("select id from good_issue_note where (issue_date+ '6 hour'::interval + '30 minutes'::interval)::date =%s and sale_team_id = %s" ,(return_date,sale_team_id,))
#             note=cr.fetchone()
#             print 'note',note
#             if note:
#                 note_id=note[0]
            note_data=note_obj.browse(cr, uid, note_id,context=context)
            for note_line in note_data.p_line:
                product_id=note_line.product_id.id
                big_uom_id=note_line.big_uom_id.id
                big_issue_quantity=note_line.big_issue_quantity
                small_issue_quantity=note_line.issue_quantity
                small_uom_id=note_line.product_uom.id
                cr.execute("select floor(1/factor) as ratio from product_uom where active = true and id=%s",(big_uom_id,))
                bigger_qty=cr.fetchone()[0]
                receive_qty=  (big_issue_quantity* bigger_qty )  + small_issue_quantity
                stock_return_obj.create(cr, uid, {'line_id': ids[0],
                                          'product_id': product_id,
                                          'product_uom': small_uom_id,
                                          'receive_quantity':receive_qty,
                                          'return_quantity':0,
                                          'sale_quantity':0,
                                          'foc_quantity':0,
                                          'rec_small_uom_id':small_uom_id,
                                          'rec_big_uom_id':big_uom_id,
                                        }, context=context)
                                        
            mobile_ids = mobile_obj.search(cr, uid, [('return_date', '=', return_date), ('user_id', '=', return_from)], context=context) 
            return_mobile=mobile_obj.browse(cr, uid, mobile_ids,context=context)            
            for mobile_line in return_mobile.p_line:
                product_id= mobile_line.product_id.id
                return_quantity=mobile_line.return_quantity
                sale_quantity= mobile_line.sale_quantity
                foc_quantity=mobile_line.foc_quantity
                small_uom_id= mobile_line.product_uom.id             
                product_search = stock_return_obj.search(cr, uid, [('product_id', '=', product_id), ('line_id', '=', ids[0])], context=context) 
                if product_search:
                    cr.execute("update stock_return_line set return_quantity=%s,sale_quantity=%s,foc_quantity=%s where line_id=%s and product_id=%s",(return_quantity,sale_quantity,foc_quantity,ids[0],product_id,))
                else:
                    product=self.pool.get('product.product').browse(cr,uid,product_id,context=context)
                    big_uom=product.product_tmpl_id.big_uom_id and product.product_tmpl_id.big_uom_id.id or False,                    
                    stock_return_obj.create(cr, uid, {'line_id': ids[0],
                                              'product_id': product_id,
                                              'product_uom': small_uom_id,
                                              'receive_quantity':0,
                                              'return_quantity':return_quantity,
                                              'sale_quantity':sale_quantity,
                                              'foc_quantity':foc_quantity,
                                              'rec_small_uom_id':small_uom_id,
                                              'rec_big_uom_id':big_uom,                                              
                                              }, context=context)
            trans_ids = product_trans_obj.search(cr, uid, [('date', '=', return_date), ('exchange_type','!=','Exchange'),('void_flag','=','none'),('team_id', '=', sale_team_id)], context=context) 
            for t_id in trans_ids:
                trans_data=product_trans_obj.browse(cr, uid, t_id,context=context)          
                for trans_line in trans_data.item_line:
                    product_id= trans_line.product_id.id
                    return_quantity=trans_line.product_qty
                    sale_quantity= 0
                    foc_quantity=0
                    small_uom_id= trans_line.uom_id.id                          
                    product_search = stock_return_obj.search(cr, uid, [('product_id', '=', product_id), ('line_id', '=', ids[0])], context=context) 
                    if product_search:
                        cr.execute("update stock_return_line set return_quantity=return_quantity + %s where line_id=%s and product_id=%s",(return_quantity,ids[0],product_id,))
                    else:
                        product=self.pool.get('product.product').browse(cr,uid,product_id,context=context)
                        big_uom=product.product_tmpl_id.big_uom_id and product.product_tmpl_id.big_uom_id.id or False,                    
                        stock_return_obj.create(cr, uid, {'line_id': ids[0],
                                                  'product_id': product_id,
                                                  'product_uom': small_uom_id,
                                                  'receive_quantity':0,
                                                  'return_quantity':return_quantity,
                                                  'sale_quantity':sale_quantity,
                                                  'foc_quantity':foc_quantity,
                                                  'rec_small_uom_id':small_uom_id,
                                                  'rec_big_uom_id':big_uom,                                              
                                                  }, context=context)     
            return_data = stock_return_obj.search(cr, uid, [('line_id', '=', ids[0])], context=context) 
            for data in return_data:
                return_record=stock_return_obj.browse(cr,uid,data,context=context)
                product_id=return_record.product_id.id
                return_qty=return_record.return_quantity
                product = product_obj.browse(cr, uid, product_id, context=context)                                                                          
                cr.execute("select floor(1/factor) as ratio from product_uom where active = true and id=%s",(product.product_tmpl_id.big_uom_id.id,))
                bigger_qty=cr.fetchone()[0]
                bigger_qty=int(bigger_qty)
                #print ' bigger_qty',sale_qty,bigger_qty,type(sale_qty),type(bigger_qty)                        
                big_uom_qty=divmod(return_qty,bigger_qty)
                #print 'big_uom_qty',big_uom_qty
                if  big_uom_qty:
                    big_quantity=big_uom_qty[0]
                    small_quantity=big_uom_qty[1]
                    cr.execute("update stock_return_line set rec_big_quantity=%s,rec_small_quantity=%s where product_id=%s and line_id=%s",(big_quantity,small_quantity,product_id, ids[0],))
                
                                   
        return True          
    _columns = {
        'sale_team_id':fields.many2one('crm.case.section', 'Sales Team' , required=True),
        'name': fields.char('(SRN)Ref;No.', readonly=True),
        'note_id':fields.many2one('good.issue.note', '(GIN)Ref;No.', required=True),
        'return_from':fields.many2one('res.users', 'Return From', required=True),
         'so_no' : fields.char('Sales Order/Inv Ref;No.'),
         'return_date':fields.date('Date of Return',required=True),
        'vehicle_id':fields.many2one('fleet.vehicle', 'Vehicle No'),
        'state': fields.selection([
            ('draft', 'Draft'),
            ('confirm', 'Confirmed'),
            ('approve', 'Approved'),
            ('cancel', 'Cancel')
            ], 'Status', readonly=True, copy=False, help="Gives the status of the quotation or sales order.\
              \nThe exception status is automatically set when a cancel operation occurs \
              in the invoice validation (Invoice Exception) or in the picking list process (Shipping Exception).\nThe 'Waiting Schedule' status is set when the invoice is confirmed\
               but waiting for the scheduler to run on the order date.", select=True),
        'p_line':fields.one2many('stock.return.line', 'line_id', 'Product Lines',
                              copy=True),
                'company_id':fields.many2one('res.company', 'Company'),
				'partner_id':fields.many2one('res.partner', 'Customer'), 
}		
    
    _defaults = {
        'state' : 'draft',
         'company_id': _get_default_company,
    }     
    
    def create(self, cursor, user, vals, context=None):
        id_code = self.pool.get('ir.sequence').get(cursor, user,
                                                'stock.return.code') or '/'
        vals['name'] = id_code
        return super(stock_return, self).create(cursor, user, vals, context=context)
    
    def confirm(self, cr, uid, ids, context=None):        
        return self.write(cr, uid, ids, {'state': 'confirm', })
    def cancel(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'cancel', })
    def approve(self, cr, uid, ids, context=None):
        picking_obj = self.pool.get('stock.picking')
        move_obj = self.pool.get('stock.move')            
        return_obj=self.browse(cr, uid,ids,context=context )    
        origin=return_obj.name
        return_date=return_obj.return_date   
        main_location_id=return_obj.note_id.to_location_id.id    
        ven_location_id=return_obj.note_id.from_location_id.id    
        
        cr.execute('select id from stock_picking_type where default_location_dest_id=%s and name like %s', (main_location_id, '%Internal Transfer%',))
        price_rec = cr.fetchone()
        print 'price_rec',price_rec
        if price_rec: 
            picking_type_id = price_rec[0] 
        else:
            raise osv.except_osv(_('Warning'),
                                 _('Picking Type has not for this transition'))
        picking_id = picking_obj.create(cr, uid, {
                                      'date': return_date,
                                      'origin':origin,
                                      'picking_type_id':picking_type_id}, context=context)        
        for line in return_obj.p_line:
            product_id=line.product_id.id
            rec_big_uom_id=line.rec_big_uom_id.id
            rec_big_quantity=line.rec_big_quantity
            rec_small_quantity=line.rec_small_quantity
            rec_small_uom_id=line.rec_small_uom_id.id             
            if (rec_small_quantity+rec_big_quantity>0):
                product = self.pool.get('product.product').browse(cr, uid, product_id, context=context)       
                name = line.product_id.name_template                                                                               
                cr.execute("select floor(1/factor) as ratio from product_uom where active = true and id=%s",(rec_big_uom_id,))
                big_qty=cr.fetchone()
                if big_qty:
                        bigger_qty=big_qty[0]*rec_big_quantity                        
                        move_id=move_obj.create(cr, uid, {'picking_id': picking_id,
                                                  'picking_type_id':picking_type_id,
                                                #  'restrict_lot_id':lot_id,
                                              'product_id': product_id,
                                              'product_uom_qty': rec_small_quantity+bigger_qty,
                                              'product_uos_qty': rec_small_quantity+bigger_qty,
                                              'product_uom':rec_small_uom_id,
                                              'location_id':ven_location_id,
                                              'location_dest_id':main_location_id,
                                              'name':name,
                                               'origin':origin,
                                              'state':'confirmed'}, context=context)     
                        move_id=move_obj.action_done(cr, uid, move_id, context=context)
                        print 'doned',move_id                         
        return self.write(cr, uid, ids, {'state':'approve'})    

            
class stock_return_line(osv.osv):  # #prod_pricelist_update_line
    _name = 'stock.return.line'
    _description = 'Return Line'
        
    _columns = {                
        'line_id':fields.many2one('stock.return', 'Line', ondelete='cascade', select=True),
        'product_id': fields.many2one('product.product', 'Product', required=True),
        'receive_quantity' : fields.float(string='Received Qty', digits=(16, 0)),
        'return_quantity' : fields.float(string='Returned Qty', digits=(16, 0)),
        'sale_quantity' : fields.float(string='Sales Qty', digits=(16, 0)),
        'foc_quantity' : fields.float(string='FOC Qty', digits=(16, 0)),
        'product_uom': fields.many2one('product.uom', 'UOM', required=True),
        'uom_ratio':fields.char('Packing Unit'),
   #     'qty_by_wh':fields.char('Received Qty by WH'),
        'expiry_date':fields.date('Expiry'),
         'remark':fields.char('Remark'),
        'rec_big_uom_id': fields.many2one('product.uom', 'Rec Bigger UoM',help="Default Unit of Measure used for all stock operation."),
        'rec_big_quantity' : fields.float(string='Rec Qty', digits=(16, 0)),        
        'rec_small_quantity' : fields.float(string='Rec Qty', digits=(16, 0)),
        'rec_small_uom_id': fields.many2one('product.uom', 'Rec Smaller UoM'),         
         
    }
        
   
    
