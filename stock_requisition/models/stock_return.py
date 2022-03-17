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
        team_obj = self.pool.get('crm.case.section')
        if sale_team_id:
            team = team_obj.browse(cr, uid, sale_team_id, context=context)
            values = {
                'vehicle_id': team.vehicle_id and team.vehicle_id.id or False,
                'from_location':team.location_id,
                'to_location':team.issue_location_id,
                'returner':team.receiver,
            }
        return {'value': values}
    
    def _get_default_company(self, cr, uid, context=None):
        company_id = self.pool.get('res.users')._get_company(cr, uid, context=context)
        if not company_id:
            raise osv.except_osv(_('Error!'), _('There is no default company for the current user!'))
        return company_id   
    
    
    def retrieve_data(self, cr, uid, ids, context=None):
        note_obj = self.pool.get('good.issue.note')
        note_line_obj = self.pool.get('good.issue.note.line')        
        product_trans_obj = self.pool.get('product.transactions')
        product_trans_line_obj = self.pool.get('product.transactions.line')
        mobile_obj = self.pool.get('stock.return.mobile')
        stock_return_obj = self.pool.get('stock.return.line')
        product_obj = self.pool.get('product.product')

        
        if ids:
            cr.execute('delete from stock_return_line where line_id=%s', (ids[0],))
            return_data = self.browse(cr, uid, ids, context=context)
            return_date = return_data.return_date
            to_return_date = return_data.to_return_date
            # return_from=return_data.return_from.id            
            sale_team_id = return_data.sale_team_id.id
            note_id = return_data.note_id.id
            from_location_id = return_data.from_location.id
            
            #print 'sale_team_id', sale_team_id, ids                                               
#             cr.execute("select id from good_issue_note where (issue_date+ '6 hour'::interval + '30 minutes'::interval)::date =%s and sale_team_id = %s" ,(return_date,sale_team_id,))
#             note=cr.fetchone()
#             print 'note',note
#             if note:
#                 note_id=note[0]
            print 'rereturn_date',return_date,sale_team_id
#             note_ids = note_obj.search(cr, uid, [('sale_team_id', '=', sale_team_id), ('issue_date', '>=', from_return_date), ('issue_date', '<=', return_date)])
#             if  note_ids:        
#                 cr.execute('select gin.from_location_id as location_id,product_id,sequence,sum(issue_quantity) as issue_quantity,product_uom  as small_uom_id from good_issue_note gin ,good_issue_note_line  ginl where gin.id = ginl.line_id and gin.id in %s group by product_id,from_location_id,sequence,product_uom', (tuple(note_ids),))
#                 p_line = cr.fetchall()    
#                 print 'p_line' ,p_line    
#             for note_line in p_line:
#                 product_id = note_line[1]
#                 sequence=note_line[2]
#                 small_issue_quantity = note_line[3]
#                 small_uom_id = note_line[4]
#                 location_id= note_line[0]
# 
#                 receive_qty =  small_issue_quantity
#                 cr.execute('select  SUM(COALESCE(qty,0)) qty from stock_quant where location_id=%s and product_id=%s and qty >0 group by product_id', (location_id, product_id,))
#                 qty_on_hand = cr.fetchone()
#                 if qty_on_hand:
#                     qty_on_hand=qty_on_hand[0]
#                 else:
#                     qty_on_hand=0.0
#                 stock_return_obj.create(cr, uid, {'line_id': ids[0],
#                                              'sequence':sequence,
#                                           'product_id': product_id,
#                                           'product_uom': small_uom_id,
#                                           'receive_quantity':qty_on_hand,
#                                           'return_quantity':0,
#                                           'sale_quantity':0,
#                                           'foc_quantity':0,
#                                           'rec_small_uom_id':small_uom_id,
#                                         }, context=context)
#                 
            mobile_ids = mobile_obj.search(cr, uid, [('return_date', '>=', return_date), ('return_date', '<=', to_return_date), ('sale_team_id', '=', sale_team_id)], context=context) 
            for mobile_id in mobile_ids:
                return_mobile = mobile_obj.browse(cr, uid, mobile_id, context=context)    
                for mobile_line in return_mobile.p_line:
                    product_id = mobile_line.product_id.id
                    return_quantity=0
                    if to_return_date == mobile_line.line_id.return_date:
                        return_quantity = mobile_line.return_quantity    
                    sale_quantity = mobile_line.sale_quantity 
                    foc_quantity = mobile_line.foc_quantity
                    small_uom_id = mobile_line.product_uom.id             
                    last_qty         =foc_quantity+sale_quantity
                    cr.execute('''select coalesce (sum(transfer_in.qty),0.0) - coalesce (sum(transfer_out.qty),0.0) as opening
                                    from
                                    (
                                        select distinct aa.location_id, aa.product_id 
                                        from (
                                            select s.location_id, s.product_id
                                            from stock_move s
                                            where s.state='done'        
                                            and  s.location_id=%s        
                                            and s.product_id =%s
                                            and s.origin NOT LIKE %s
                                            union
                                            select s.location_dest_id as location_id,s.product_id 
                                            from stock_move s
                                            where s.state='done'        
                                            and  s.location_dest_id=%s
                                            and s.product_id =%s
                                            and s.origin NOT LIKE %s
                                             )aa
                                     )tmp
                                    left join 
                                    (select s.product_id,s.location_dest_id,greatest(0,sum(s.product_qty)) as qty
                                    from stock_move s,
                                    stock_location fl,
                                    stock_location tl
                                    where s.state='done'
                                    and s.location_dest_id=tl.id
                                    and s.location_id=fl.id
                                    and date_trunc('day', s.date::date) >= %s
                                    and date_trunc('day', s.date::date) <= %s                                        
                                    and  s.location_dest_id=%s
                                    and s.product_id =%s
                                    and s.origin NOT LIKE %s
                                    and s.origin NOT LIKE  %s
                                    and s.origin NOT LIKE  %s
    
                                    group by s.location_dest_id, s.product_id
                                    ) transfer_in on transfer_in.product_id=tmp.product_id and transfer_in.location_dest_id=tmp.location_id
                                    left join
                                    (
                                    select s.product_id,s.location_id,greatest(0,sum(s.product_qty)) as qty
                                    from stock_move s,
                                    stock_location fl,
                                    stock_location tl
                                    where s.state='done'
                                    and s.location_dest_id=tl.id
                                    and s.location_id=fl.id
                                    and date_trunc('day', s.date::date) >= %s
                                    and date_trunc('day', s.date::date) <= %s                                        
                                    and  s.location_id=%s
                                    and s.product_id =%s
                                    and s.origin NOT LIKE %s
                                    and s.origin NOT LIKE %s
                                    and s.origin NOT LIKE %s
    
                                    group by s.location_id, s.product_id
                                    ) transfer_out on transfer_out.product_id=tmp.product_id and transfer_out.location_id=tmp.location_id'''
                      , (from_location_id, product_id, 'PD%', from_location_id, product_id, 'PD%', return_date, to_return_date, from_location_id, product_id, 'PD%', 'Reverse SO%','Reverse EC-SO%',return_date, to_return_date, from_location_id, product_id, 'PD%', 'SO%','EC-SO%',))                                
                    in_qty_data = cr.fetchone()
                    if in_qty_data:
                        if in_qty_data is not None:
                            in_stock_qty = in_qty_data[0]
                        else:
                            in_stock_qty = 0          
                                            
                    product_search = stock_return_obj.search(cr, uid, [('product_id', '=', product_id), ('line_id', '=', ids[0])], context=context) 
                    if product_search:
                        cr.execute("update stock_return_line set sale_quantity=sale_quantity + %s,foc_quantity=foc_quantity +%s where line_id=%s and product_id=%s", ( sale_quantity, foc_quantity, ids[0], product_id,))
                    else:
                        product = self.pool.get('product.product').browse(cr, uid, product_id, context=context)
                        sequence=product.sequence
                        stock_return_obj.create(cr, uid, {'line_id': ids[0],
                                                   'sequence':sequence,
                                                  'product_id': product_id,
                                                  'product_uom': small_uom_id,
                                                  'receive_quantity':in_stock_qty,
                                                  'return_quantity':return_quantity,
                                                  'sale_quantity':sale_quantity,
                                                  'foc_quantity':foc_quantity,
                                                  'rec_small_uom_id':small_uom_id,
                                                  }, context=context)
            trans_ids = product_trans_obj.search(cr, uid, [('date', '>=', return_date), ('date', '<=', to_return_date), ('void_flag', '=', 'none'), ('team_id', '=', sale_team_id)], context=context) 
            for t_id in trans_ids:
                trans_data = product_trans_obj.browse(cr, uid, t_id, context=context)
                exchange_type=trans_data.exchange_type          
                for trans_line in trans_data.item_line:
                    product_id = trans_line.product_id.id
                    return_quantity = trans_line.product_qty
                    sale_quantity = 0
                    foc_quantity = 0
                    small_uom_id = trans_line.uom_id.id     
                    product_trans_line_data=product_trans_line_obj.browse(cr, uid, trans_line.id, context=context)
                    if product_trans_line_data.trans_type == 'Out':
                        return_quantity = -1*return_quantity
#                     product_search = stock_return_obj.search(cr, uid, [('product_id', '=', product_id), ('line_id', '=', ids[0])], context=context) 
#                     if product_search:
#                         cr.execute("select exchange_quantity from stock_return_line where line_id=%s and product_id=%s", ( ids[0], product_id,))
#                         ex_qty=cr.fetchone()[0]
#                         if ex_qty !=0 and ex_qty is not None :
#                             exchange_quantity=ex_qty+exchange_quantity
#                         cr.execute("update stock_return_line set exchange_quantity=%s where line_id=%s and product_id=%s", (exchange_quantity, ids[0], product_id,))
#                     else:
                    product = self.pool.get('product.product').browse(cr, uid, product_id, context=context)
                    sequence=product.sequence
                    stock_return_obj.create(cr, uid, {'line_id': ids[0],
                                             'sequence':sequence,
                                              'product_id': product_id,
                                              'product_uom': small_uom_id,
                                              'receive_quantity':0,
                                              'return_quantity':return_quantity,
                                              'sale_quantity':0,
                                              'foc_quantity':0,
                                              'rec_small_uom_id':small_uom_id,
                                              'remark':exchange_type,
                                              'ex_return_id':t_id,
                                              }, context=context)     
            return_data = stock_return_obj.search(cr, uid, [('line_id', '=', ids[0])], context=context) 
            for data in return_data:
                return_record = stock_return_obj.browse(cr, uid, data, context=context)
                record_id= return_record.id
                product_id = return_record.product_id.id
                return_qty = return_record.return_quantity
                product = product_obj.browse(cr, uid, product_id, context=context)
                cr.execute("update stock_return_line set return_quantity=%s where product_id=%s and line_id=%s and id=%s", (return_qty, product_id, ids[0],record_id,))
                
        return True 
        
    def _get_default_branch(self, cr, uid, context=None):
        branch_id = self.pool.get('res.users')._get_branch(cr, uid, context=context)
        if not branch_id:
            raise osv.except_osv(_('Error!'), _('There is no default branch for the current user!'))
        return branch_id 
        
    _columns = {
        'sale_team_id':fields.many2one('crm.case.section', 'Sales Team' , required=True),
        'name': fields.char('SRN Ref', readonly=True),
        'note_id':fields.many2one('good.issue.note', '(GIN)Ref;No.'),
        'from_location':fields.many2one('stock.location', 'From Location'),
        'to_location':fields.many2one('stock.location', 'To Warehouse'),
        'return_from':fields.char('Return From'),
         'so_no' : fields.char('Sales Order/Inv Ref;No.'),
         'returner' : fields.char('Returned By' ),
         'wh_receiver' : fields.char('WH Receiver'),
         'return_date':fields.date('From Date of Return', required=True),
         'to_return_date':fields.date('To Date of Return', required=True),
         'vehicle_id':fields.many2one('fleet.vehicle', 'Vehicle No'),
#         'branch_id':fields.many2one('res.branch', 'Branch'),
         'state': fields.selection([
            ('draft', 'Pending'),
            ('received', 'Received'),
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
         'branch_id': _get_default_branch,
         'return_date' :fields.datetime.now,
         'to_return_date':fields.datetime.now,
    }     
    
    def create(self, cursor, user, vals, context=None):
        if vals['sale_team_id']:
            sale_team_id=vals['sale_team_id']
            sale_team = self.pool.get('crm.case.section').browse(cursor, user, sale_team_id, context=context)
            to_location_id = sale_team.issue_location_id.id            
            from_location_id=sale_team.location_id.id
        id_code = self.pool.get('ir.sequence').get(cursor, user,
                                                'stock.return.code') or '/'
        vals['name'] = id_code
        vals['to_location'] = to_location_id
        vals['from_location'] = from_location_id        
        return super(stock_return, self).create(cursor, user, vals, context=context)
    
    def confirm(self, cr, uid, ids, context=None):        
        return self.write(cr, uid, ids, {'state': 'confirm', })
    
    def cancel(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'cancel', })
    
    def received(self, cr, uid, ids, context=None):
        partner_obj=self.pool.get('res.partner')
        picking_obj = self.pool.get('stock.picking')
        move_obj = self.pool.get('stock.move')           
        note_obj = self.pool.get('good.issue.note') 
        return_obj = self.browse(cr, uid, ids, context=context)    
        origin = return_obj.name
        return_date = return_obj.to_return_date
        main_location_id = return_obj.to_location.id    
        ven_location_id = return_obj.from_location.id    
        note_id = return_obj.note_id
        cr.execute('select id from stock_picking_type where default_location_dest_id=%s and name like %s', (main_location_id, '%Internal Transfer%',))
        price_rec = cr.fetchone()
        if price_rec: 
            picking_type_id = price_rec[0] 
        else:
            raise osv.except_osv(_('Warning'),
                                 _('Picking Type has not for this transition'))
        picking_id = picking_obj.create(cr, uid, {
                                      'date': return_date,
                                      'origin':origin,
                                      'picking_type_id':picking_type_id}, context=context)
        cr.execute("select  sum(rec_small_quantity)  from stock_return_line  where line_id=%s group by line_id",(ids[0],)) 
        total_qty=cr.fetchone()[0]
        if total_qty==0.0 or total_qty is None   :
            raise osv.except_osv(_('Warning'),
                                 _('Receive Qty is Zero'))
        for line in return_obj.p_line:
            product_id = line.product_id.id
            rec_small_quantity = line.rec_small_quantity
            rec_small_uom_id = line.rec_small_uom_id.id    
            ex_return_id =    line.ex_return_id.id    
            return_quantity=line.return_quantity
            if (rec_small_quantity  > 0):
                product = self.pool.get('product.product').browse(cr, uid, product_id, context=context)       
                name = line.product_id.name_template                                                                               
                                      
                move_id = move_obj.create(cr, uid, {'picking_id': picking_id,
                                                  'picking_type_id':picking_type_id,
                                                #  'restrict_lot_id':lot_id,
                                              'product_id': product_id,
                                              'product_uom_qty': rec_small_quantity,
                                              'product_uos_qty': rec_small_quantity,
                                              'product_uom':rec_small_uom_id,
                                              'location_id':ven_location_id,
                                              'location_dest_id':main_location_id,
                                              'name':name,
                                               'origin':origin,
                                              'state':'confirmed'}, context=context)     
                move_id = move_obj.action_done(cr, uid, move_id, context=context)
            print ' ex_return_id ,return_quantity',ex_return_id ,return_quantity
            if ex_return_id and return_quantity<0:
                product = self.pool.get('product.product').browse(cr, uid, product_id, context=context)       
                name = line.product_id.name_template          
                cr.execute("select customer_id from product_transactions where  id =%s  ",(ex_return_id,))
                partner_id=cr.fetchone()[0]
                partner_data = partner_obj.browse(cr, uid, partner_id, context=context)    
                location_id = partner_data.property_stock_customer.id
                from_location_id = ven_location_id
                cr.execute('select id from stock_picking_type where default_location_dest_id=%s and default_location_src_id = %s', (location_id, from_location_id,))
                price_rec = cr.fetchone()
                if price_rec: 
                    picking_type_id = price_rec[0] 
                else:
                    raise osv.except_osv(_('Warning'),
                                         _('Picking Type has not for this transition'))
                picking_id = picking_obj.create(cr, uid, {
                                              'date': return_date,
                                              'origin':origin,
                                              'picking_type_id':picking_type_id}, context=context) 
                move_id=move_obj.create(cr, uid, {'picking_id': picking_id,
                                             'picking_type_id':picking_type_id,
                                              'product_id': product_id,
                                              'product_uom_qty': -1*return_quantity,
                                              'product_uos_qty': -1*return_quantity,
                                              'product_uom':rec_small_uom_id,
                                              'location_id':from_location_id,
                                              'location_dest_id':location_id,
                                              'name':name,
                                               'origin':origin,
                                              'state':'confirmed'}, context=context)     
                move_obj.action_done(cr, uid, move_id, context=context)             
        return self.write(cr, uid, ids, {'state':'received'})    

            
class stock_return_line(osv.osv):  # #prod_pricelist_update_line
    _name = 'stock.return.line'
    _description = 'Return Line'
        
    _columns = {                
        'line_id':fields.many2one('stock.return', 'Line', ondelete='cascade', select=True),
        'product_id': fields.many2one('product.product', 'Product', required=True),
        'product_code': fields.char(related='product_id.default_code', string="Product Code"),
        'receive_quantity' : fields.float(string='Received Qty', digits=(16, 0)),
        'return_quantity' : fields.float(string='Returned Qty', digits=(16, 0)),
        'sale_quantity' : fields.float(string='Sales Qty', digits=(16, 0)),
        'foc_quantity' : fields.float(string='FOC Qty', digits=(16, 0)),
     #   'exchange_quantity' : fields.float(string='Sale/Exchange Qty', digits=(16, 0)),
        'product_uom': fields.many2one('product.uom', 'UOM', required=True),
        'uom_ratio':fields.char('Packing Unit'),
        'expiry_date':fields.date('Expiry'),
         'remark':fields.char('Remark'),
        'rec_small_quantity' : fields.float(string='Rec Small Qty', digits=(16, 0)),
        'rec_small_uom_id': fields.many2one('product.uom', 'Rec Smaller UoM'),         
        'sequence':fields.integer('Sequence'),
        'ex_return_id':fields.many2one('product.transactions','Exchange ID'),

    }
        
   
    
