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
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP


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
        warehouse_obj = self.pool.get('stock.warehouse')
        
        if sale_team_id:
            team = team_obj.browse(cr, uid, sale_team_id, context=context)
            warehouse_id = self.pool.get('stock.warehouse').browse(cr, uid, team.issue_warehouse_id.id, context=context)

            values = {
                'vehicle_id': team.vehicle_id and team.vehicle_id.id or False,
                'from_location':team.location_id,
                'from_wh_normal_return_location_id':team.normal_return_location_id,
                'from_wh_exp_location_id':team.exp_location_id,
                'from_wh_near_exp_location_id':team.near_exp_location_id,
                'from_wh_damage_location_id':team.damage_location_id,
                'from_wh_fresh_stock_not_good_location_id':team.fresh_stock_not_good_location_id,
                'to_location':team.issue_location_id,
                'to_wh_normal_return_location_id':warehouse_id.wh_normal_return_location_id,
                'to_wh_exp_location_id':warehouse_id.wh_exp_location_id,
                'to_wh_near_exp_location_id':warehouse_id.wh_near_exp_location_id,
                'to_wh_damage_location_id':warehouse_id.wh_damage_location_id,
                'to_wh_fresh_stock_not_good_location_id':warehouse_id.wh_fresh_stock_not_good_location_id,
                'vehicle_id':team.vehicle_id,
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
        product_disassembly_obj = self.pool.get('product.disassembly')
        product_disassembly_line_obj = self.pool.get('product.disassembly.line')
        
        product_trans_line_obj = self.pool.get('product.transactions.line')
        
        mobile_obj = self.pool.get('stock.return.mobile')
        stock_return_obj = self.pool.get('stock.return.line')
        product_obj = self.pool.get('product.product')
        quant_obj = self.pool.get('stock.quant')
        move_obj = self.pool.get('stock.move')
        if ids:
            cr.execute('delete from stock_return_line where line_id=%s', (ids[0],))
            return_data = self.browse(cr, uid, ids, context=context)
            return_date = return_data.return_date
            to_return_date = return_data.to_return_date
            from_location_id = return_data.from_location.id
            to_location_id = return_data.sale_team_id.issue_location_id.id            

            # return_from=return_data.return_from.id            
            optional_issue_location_id = return_data.sale_team_id.optional_issue_location_id.id
            issue_from_optional_location = return_data.issue_from_optional_location
            is_separate_srn =return_data.is_separate_srn
            
            if  issue_from_optional_location == True:
                to_location_id = optional_issue_location_id
                cr.execute("update stock_return set to_location=%s where id =%s ", (to_location_id, return_data.id,))
            else:
                issue_from_optional_location = False
                to_location_id = to_location_id
                cr.execute("update stock_return set to_location=%s where id =%s ", (to_location_id, return_data.id,))

            sale_team_id = return_data.sale_team_id.id
            branch_id =return_data.branch_id.id
            team_location_id = return_data.sale_team_id.location_id.id
            if  from_location_id != team_location_id :
                raise osv.except_osv(_('Warning'),
                                 _('Please Check Your Sales Team Location'))
            note_id = return_data.note_id.id
            # print 'sale_team_id', sale_team_id, ids                                               
#             cr.execute("select id from good_issue_note where (issue_date+ '6 hour'::interval + '30 minutes'::interval)::date =%s and sale_team_id = %s" ,(return_date,sale_team_id,))
#             note=cr.fetchone()
#             print 'note',note
#             if note:
#                 note_id=note[0]
#            print 'rereturn_date',return_date,sale_team_id
             # note_ids = note_obj.search(cr, uid, [('sale_team_id', '=', sale_team_id), ('issue_date', '=', return_date),('state','=','issue')])
            mobile_ids = mobile_obj.search(cr, uid, [('return_date', '>=', return_date), ('return_date', '<=', to_return_date) , ('sale_team_id', '=', sale_team_id)], context=context)
#             if  mobile_ids:        
#                 #cr.execute('select gin.from_location_id as location_id,product_id,big_uom_id,sum(big_issue_quantity) as big_issue_quantity,sum(issue_quantity) as issue_quantity,product_uom  as small_uom_id from good_issue_note gin ,good_issue_note_line  ginl where gin.id = ginl.line_id and gin.id in %s group by product_id,from_location_id,big_uom_id,product_uom', (tuple(note_ids),))
#                 cr.execute('select product_id,product_uom,sum(return_quantity) as return_quantity,sum(sale_quantity) as sale_quantity from stock_return_mobile srm, stock_return_mobile_line srml where srm.id=srml.line_id and srm.id in %s group by product_id,product_uom', (tuple(mobile_ids),))
#                 p_line = cr.fetchall()            
#             for note_line in p_line:
#                 product_id = note_line[0]
#                 pro_data = product_obj.browse(cr, uid, product_id, context=context)
#                 sequence=pro_data.sequence
#                 uom_id = note_line[1]
#                 return_quantity = note_line[2]
#                 sale_quantity = note_line[3]
#                 #big_uom_id = note_line[2]
#                 #big_issue_quantity = note_line[3]
#                 #small_issue_quantity = note_line[4]
#                 #small_uom_id = note_line[5]
#                 #location_id= note_line[0]
#                 #cr.execute("select floor(round(1/factor,2)) as ratio from product_uom where active = true and id=%s", (big_uom_id,))
#                 #cr.execute("select floor(round(1/factor,2)) as ratio from product_uom where active = true and id=%s", (uom_id,))
#                 #bigger_qty = cr.fetchone()[0]
#                 #receive_qty = (big_issue_quantity * bigger_qty) + small_issue_quantity
#                 #receive_qty = (issue_quantity * bigger_qty)
#                 #cr.execute('select  SUM(COALESCE(qty,0)) qty from stock_quant where location_id=%s and product_id=%s and qty >0 group by product_id', (location_id, product_id,))
#                 #qty_on_hand = cr.fetchone()
#                 #if qty_on_hand:
#                     #qty_on_hand=qty_on_hand[0]
#                # else:
#                     #qty_on_hand=0.0
#                 stock_return_obj.create(cr, uid, {'line_id': ids[0],
#                                              'sequence':sequence,
#                                           'product_id': product_id,
#                                           #'product_uom': small_uom_id,
#                                           'product_uom': uom_id,
#                                           'receive_quantity':0,
#                                           'return_quantity':0,
#                                           'sale_quantity':0,
#                                           'foc_quantity':0,
#                                           'rec_small_uom_id':0,
#                                           'rec_big_uom_id':0,
#                                           #'rec_small_uom_id':small_uom_id,
#                                           #'rec_big_uom_id':big_uom_id,
#                                         }, context=context)
#             if not mobile_ids:
#                 mobile_create_id=mobile_obj.create(cr, uid, {
#                                                         'sale_team_id':sale_team_id,
#                                                         'user_id':uid,
#                                                        'branch_id':branch_id,
#                                                       'return_date': to_return_date,
#                                                       }, context=context) 
#                 mobile_obj.manual_data(cr, uid, [mobile_create_id], context=context)
#                 mobile_ids=[mobile_create_id]
            for mobile_id in mobile_ids:
                return_mobile = mobile_obj.browse(cr, uid, mobile_id, context=context)    
                return_quantity = 0
                manual = return_mobile.manual
                for mobile_line in return_mobile.p_line:
                    product_id = mobile_line.product_id.id
                    product_cat = self.pool.get('product.product').browse(cr, uid, product_id, context=context)
                    categ_issue_from_optional_location = product_cat.product_tmpl_id.categ_id.issue_from_optional_location
                    principle_is_separate_srn=product_cat.product_tmpl_id.main_group.is_separate_transition
                    if issue_from_optional_location == categ_issue_from_optional_location and principle_is_separate_srn==is_separate_srn:
                        if to_return_date == mobile_line.line_id.return_date:
                            return_quantity = mobile_line.return_quantity      
                        # if return_quantity<0:
                            # substract_qty=return_quantity
                        # else:
                            # substract_qty=0
        
                        sale_quantity = mobile_line.sale_quantity + mobile_line.foc_quantity
                        # foc_quantity = mobile_line.foc_quantity
                        small_uom_id = mobile_line.product_uom.id             
                        # last_qty         = foc_quantity + sale_quantity
                        # openingQTY
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
                                                union
                                                select s.location_dest_id as location_id,s.product_id 
                                                from stock_move s
                                                where s.state='done'        
                                                and  s.location_dest_id=%s
                                                and s.product_id =%s
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
                                        and date_trunc('day', s.date::date) < %s
                                        and  s.location_dest_id=%s
                                        and s.product_id =%s
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
                                        and date_trunc('day', s.date::date) < %s
                                        and  s.location_id=%s
                                        and s.product_id =%s
                                        group by s.location_id, s.product_id
                                        ) transfer_out on transfer_out.product_id=tmp.product_id and transfer_out.location_id=tmp.location_id'''
                          , (from_location_id, product_id, from_location_id, product_id, return_date, from_location_id, product_id, return_date, from_location_id, product_id,))                
                        opening_data = cr.fetchone()
                        if opening_data:
                            if opening_data is not None:
                                opening_qty = opening_data[0]
                            else:
                                opening_qty = 0
                        # Stock In QTY
#                         cr.execute('''select coalesce (sum(transfer_in.qty),0.0) as opening
#                                         from
#                                         (select s.product_id,s.location_dest_id,greatest(0,sum(s.product_qty)) as qty
#                                         from stock_move s,
#                                         stock_location fl,
#                                         stock_location tl
#                                         where s.state='done'
#                                         and s.location_dest_id=tl.id
#                                         and s.location_id=fl.id
#                                         and date_trunc('day', s.date::date) >= %s
#                                         and date_trunc('day', s.date::date) <= %s
#                                         and  s.location_dest_id=%s
#                                         and s.product_id =%s
#                                         and s.origin NOT LIKE %s
#                                         group by s.location_dest_id, s.product_id
#                                         ) transfer_in '''
#                           , (return_date,to_return_date, from_location_id, product_id,'PD%',))    
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
                                        and s.is_exchange !=True
                                        and s.origin NOT LIKE %s
                                        and s.origin NOT LIKE %s
                                        and s.origin NOT LIKE %s

                                        group by s.location_id, s.product_id
                                        ) transfer_out on transfer_out.product_id=tmp.product_id and transfer_out.location_id=tmp.location_id'''
                          , (from_location_id, product_id, 'PD%', from_location_id, product_id, 'PD%', return_date, to_return_date, from_location_id, product_id, 'PD%', 'Reverse SO%','Reverse EC-SO%',return_date, to_return_date, from_location_id, product_id, 'PD%', 'SO%','EC-SO%',))                
                        # opening_data = cr.fetchone()                        
                        
                                    
                        in_qty_data = cr.fetchone()
                        if in_qty_data:
                            if in_qty_data is not None:
                                in_stock_qty = in_qty_data[0]
                            else:
                                in_stock_qty = 0                
                        product_search = stock_return_obj.search(cr, uid, [('product_id', '=', product_id), ('line_id', '=', ids[0])], context=context) 
                        actual_return_quantity = 0
                        onground_quantity = 0
                        if manual == True:
                            onground_quantity = return_quantity
                            actual_return_quantity = return_quantity  
                        if product_search:                                                                                         
                            # cr.execute("update stock_return_line set receive_quantity=receive_quantity+%s + %s ,return_quantity=%s,sale_quantity=%s,foc_quantity=%s where line_id=%s and product_id=%s", (last_qty,substract_qty,return_quantity, sale_quantity, foc_quantity, ids[0], product_id,))
                            cr.execute("update stock_return_line set return_quantity=return_quantity + %s,onground_quantity=onground_quantity + %s,actual_return_quantity=actual_return_quantity + %s,sale_quantity=sale_quantity - %s where line_id=%s and product_id=%s", (return_quantity, onground_quantity, actual_return_quantity, sale_quantity, ids[0], product_id,))
                        else:
                            product = self.pool.get('product.product').browse(cr, uid, product_id, context=context)
                            sequence = product.sequence
                            big_uom = product.product_tmpl_id.big_uom_id and product.product_tmpl_id.big_uom_id.id or False,
                            stock_return_obj.create(cr, uid, {'line_id': ids[0],
                                                        'opening_stock_qty':opening_qty,
                                                        'in_stock_qty':in_stock_qty,
                                                       'sequence':sequence,
                                                      'product_id': product_id,
                                                      'product_uom': product.product_tmpl_id.uom_id.id,
                                                      'assembly_qty':0,
                                                      'return_quantity':return_quantity,
                                                       'onground_quantity':onground_quantity,
                                                       'actual_return_quantity':actual_return_quantity,
                                                      'sale_quantity':-1 * sale_quantity,
                                                      'status':'Stock Return',
                                                      'miss_qty':0,
                                                      # 'foc_quantity':foc_quantity,
                                                      'from_location_id':from_location_id ,
                                                      'to_location_id': to_location_id,
                                                     # 'rec_small_uom_id':small_uom_id,
                                                    #  'rec_big_uom_id':big_uom,
                                                      }, context=context)


            cr.execute('''
                select sol.product_id,sum(product_uom_qty *(select floor(round(1/factor,2)) as ratio from product_uom where active = true and id=sol.product_uom)) as total_qty from pending_delivery delivery ,
                sale_order so,sale_order_line sol,product_product pp,
                product_template pt,product_category pc 
                where so.id=sol.order_id  
                and delivery.order_id=so.id and pp.id=sol.product_id and pp.product_tmpl_id =pt.id and pc.id=pt.categ_id  
                and delivery.delivery_team_id = %s
                and pt.type!='service'
                and delivery.miss=True
                and delivery.state='done'
                and delivery.delivery_date between %s and %s 
                group by product_id''', (sale_team_id,return_date,to_return_date,))
            sale_record = cr.fetchall()             
            if sale_record:
                for sale_data in sale_record:
                    sale_product_id = int(sale_data[0])
                    miss_qty = int(sale_data[1])
                    #product = self.pool.get('product.product').browse(cr, uid, sale_product_id, context=context)
                    miss_stock_id = stock_return_obj.search(cr, uid , [('line_id', '=', ids[0]) , ('product_id', '=', sale_product_id), ('status', '=', 'Stock Return')])
                    if miss_stock_id:
                        cr.execute("update stock_return_line set miss_qty=miss_qty+%s where status ='Stock Return' and product_id=%s and line_id=%s", (miss_qty,sale_product_id, ids[0],))                        
#                     else:
#                         location_type='Missed Order'
#                         stock_return_obj.create(cr, uid, {'line_id': ids[0],
#                                                    'sequence':product.sequence,
#                                                   'product_id': sale_product_id,
#                                                   'product_uom': product.product_tmpl_id.uom_id.id,
#                                                   'assembly_qty':0,
#                                                   'return_quantity':0,
#                                                   'exchange_qty':0,
#                                                   'sale_quantity':0,
#                                                   'miss_qty':miss_qty,
#                                                   'status':location_type,
#                                                   'from_location_id':from_location_id,
#                                                   'to_location_id': to_location_id,
#                                                   }, context=context)                   
            disassembly_ids = product_disassembly_obj.search(cr, uid, [('date', '>=', return_date), ('date', '<=', to_return_date), ('section_id', '=', sale_team_id)], context=context),
            for d_list in disassembly_ids:
                for d_id in d_list:
                    dis_data = product_disassembly_obj.browse(cr, uid, d_id, context=context)
                    location_type = 'Disassembly'
                    location_id = dis_data.location_id.id
                    for product_line in dis_data.product_lines:   
                        dis_data = product_disassembly_line_obj.browse(cr, uid, product_line.id, context=context)
                        first_product_id = dis_data.product_id.id
                        product_data = product_obj.browse(cr, uid, first_product_id, context=context)
                        categ_issue_from_optional_location = product_data.product_tmpl_id.categ_id.issue_from_optional_location
                        principle_is_separate_srn=product_data.product_tmpl_id.main_group.is_separate_transition

                        if issue_from_optional_location == categ_issue_from_optional_location and principle_is_separate_srn==is_separate_srn:
                            sequence = product_data.sequence
                            first_uom_id = dis_data.big_uom_id.id
                            first_big_quantity = dis_data.big_quantity
                            sec_to_product_id = dis_data.to_product_id.id
                            sec_uom_id = dis_data.uom_id.id
                            sec_quantity = dis_data.quantity
                            first_normal_stock_id = stock_return_obj.search(cr, uid , [('line_id', '=', ids[0]) , ('product_id', '=', first_product_id), ('status', '=', 'Stock Return')])
                            if first_normal_stock_id:
                                cr.execute('update stock_return_line set assembly_qty = assembly_qty - %s where id=%s ', (first_big_quantity, first_normal_stock_id[0],))                        
                            else:
                                stock_return_obj.create(cr, uid, {'line_id': ids[0],
                                                           'sequence':sequence,
                                                          'product_id': first_product_id,
                                                          'product_uom': first_uom_id,
                                                          'assembly_qty':-1 * first_big_quantity,
                                                          'return_quantity':0,
                                                          'exchange_qty':0,
                                                          'sale_quantity':0,
                                                          'status':location_type,
                                                          'from_location_id':location_id ,
                                                          'to_location_id': False,
                                                          }, context=context)           
                            sec_normal_stock_id = stock_return_obj.search(cr, uid , [('line_id', '=', ids[0]) , ('product_id', '=', sec_to_product_id), ('status', '=', 'Stock Return')])
                            if sec_normal_stock_id:                           
                                cr.execute('update stock_return_line set assembly_qty = assembly_qty +%s where id=%s ', (sec_quantity, sec_normal_stock_id[0],))   
                            else:
                                stock_return_obj.create(cr, uid, {'line_id': ids[0],
                                                           'sequence':sequence,
                                                          'product_id': sec_to_product_id,
                                                          'product_uom': sec_uom_id,
                                                          'assembly_qty': sec_quantity,
                                                          'return_quantity':0,
                                                          'exchange_qty':0,
                                                          'sale_quantity':0,
                                                          'status':location_type,
                                                          'from_location_id':location_id ,
                                                          'to_location_id': False,
                                                          }, context=context)                                       
                                                 
            trans_ids = product_trans_obj.search(cr, uid, [('date', '>=', return_date), ('date', '<=', to_return_date), ('void_flag', '=', 'none'), ('team_id', '=', sale_team_id)], context=context),
            for t_list in trans_ids:
                for t_id in t_list:
                    exchange_data = product_trans_obj.browse(cr, uid, t_id, context=context)
                    location_type = exchange_data.location_type
                    exchange_name = exchange_data.transaction_id
                    from datetime import datetime
                    exchange_date = datetime.strptime(exchange_data.date, DEFAULT_SERVER_DATETIME_FORMAT).strftime(DEFAULT_SERVER_DATE_FORMAT)
                    customer_location_id = exchange_data.customer_id.property_stock_customer.id
                    out_quant_ids = move_obj.search(cr, uid, [('origin', '=', exchange_name), ('location_dest_id', '=', customer_location_id)])
                    if  out_quant_ids:        
                        for move_id in out_quant_ids:
                            move_data = move_obj.browse(cr, uid, move_id, context=context)
                            product_id = move_data.product_id.id
                            product_data = product_obj.browse(cr, uid, product_id, context=context)
                            categ_issue_from_optional_location = product_data.product_tmpl_id.categ_id.issue_from_optional_location
                            principle_is_separate_srn=product_data.product_tmpl_id.main_group.is_separate_transition
                            if issue_from_optional_location == categ_issue_from_optional_location and principle_is_separate_srn==is_separate_srn:
                                sequence = product_data.sequence
                                uom_id = product_data.uom_id.id
                                quantity = move_data.product_qty
                                normal_stock_id = stock_return_obj.search(cr, uid , [('line_id', '=', ids[0]) , ('product_id', '=', product_id), ('status', '=', 'Stock Return')])
                                if normal_stock_id and exchange_date == to_return_date:
                                    cr.execute('update stock_return_line set return_quantity = return_quantity - %s where id=%s ', (quantity, normal_stock_id[0],))                        
                                     
                                return_stock_id = stock_return_obj.search(cr, uid , [('line_id', '=', ids[0]) , ('product_id', '=', product_id), ('status', '=', location_type)])
                                if  return_stock_id:
                                    cr.execute('update stock_return_line set exchange_qty =exchange_qty - %s where id=%s ', (quantity, return_stock_id[0],))
                                else:                       
                                    stock_return_obj.create(cr, uid, {'line_id': ids[0],
                                                               'sequence':sequence,
                                                              'product_id': product_id,
                                                              'product_uom': uom_id,
                                                              'return_quantity':0,
                                                              'exchange_qty':-1 * quantity,
                                                              'sale_quantity':0,
                                                              'status':location_type,
                                                              'from_location_id':from_location_id ,
                                                              'to_location_id': customer_location_id,
                                                              }, context=context)                
                
                
                
            # NormalReturn Location    
            if return_data.from_wh_normal_return_location_id:      
                location_id = return_data.from_wh_normal_return_location_id.id
                to_location_id = return_data.to_wh_normal_return_location_id.id
                location_type = "Normal Return"                
                return_quant_ids = quant_obj.search(cr, uid, [('location_id', '=', location_id)])
                if  return_quant_ids:        
                    for quant_id in return_quant_ids:
                        quant_data = quant_obj.browse(cr, uid, quant_id, context=context)
                        product_id = quant_data.product_id.id
                        product_data = product_obj.browse(cr, uid, product_id, context=context)
                        categ_issue_from_optional_location = product_data.product_tmpl_id.categ_id.issue_from_optional_location
                        principle_is_separate_srn=product_data.product_tmpl_id.main_group.is_separate_transition
                        if issue_from_optional_location == categ_issue_from_optional_location and principle_is_separate_srn==is_separate_srn:
                            sequence = product_data.sequence
                            uom_id = product_data.uom_id.id
                            quantity = quant_data.qty
    #                             normal_stock_id = stock_return_obj.search(cr, uid , [('line_id', '=', ids[0]) , ('product_id', '=', product_id), ('status', '=', 'Stock Return')])
    #                             if normal_stock_id:
    #                                 cr.execute('update stock_return_line set return_quantity = return_quantity - %s where id=%s ', (quantity, normal_stock_id[0],))                        
    #                             
                            return_stock_id = stock_return_obj.search(cr, uid , [('line_id', '=', ids[0]) , ('product_id', '=', product_id), ('status', '=', location_type)])
                            if  return_stock_id:
                                cr.execute('update stock_return_line set exchange_qty =exchange_qty + %s,return_quantity =return_quantity+ %s where id=%s ', (quantity, quantity, return_stock_id[0],))
                            else:                       
                                stock_return_obj.create(cr, uid, {'line_id': ids[0],
                                                           'sequence':sequence,
                                                          'product_id': product_id,
                                                          'product_uom': uom_id,
                                                          'return_quantity':quantity,
                                                          'exchange_qty':quantity,
                                                          'sale_quantity':0,
                                                          'status':location_type,
                                                       #   'rec_small_uom_id':small_uom_id,
                                                       #   'rec_big_uom_id':big_uom,
                                                          'from_location_id':location_id ,
                                                          'to_location_id': to_location_id,
                                                          }, context=context)
            # Exp Location
            if return_data.from_wh_exp_location_id:      
                location_id = return_data.from_wh_exp_location_id.id
                to_location_id = return_data.to_wh_exp_location_id.id
                location_type = "Expired Return"                
                return_quant_ids = quant_obj.search(cr, uid, [('location_id', '=', location_id)])
                if  return_quant_ids:        
                    for quant_id in return_quant_ids:
                        quant_data = quant_obj.browse(cr, uid, quant_id, context=context)
                        product_id = quant_data.product_id.id
                        product_data = product_obj.browse(cr, uid, product_id, context=context)
                        categ_issue_from_optional_location = product_data.product_tmpl_id.categ_id.issue_from_optional_location
                        principle_is_separate_srn=product_data.product_tmpl_id.main_group.is_separate_transition
                        if issue_from_optional_location == categ_issue_from_optional_location and principle_is_separate_srn==is_separate_srn:
                            sequence = product_data.sequence
                            uom_id = product_data.uom_id.id
                            quantity = quant_data.qty
                            normal_stock_id = stock_return_obj.search(cr, uid , [('line_id', '=', ids[0]) , ('product_id', '=', product_id), ('status', '=', 'Stock Return')])
    #                             if normal_stock_id:
    #                                 cr.execute('update stock_return_line set return_quantity = return_quantity - %s where id=%s ', (quantity, normal_stock_id[0],))
                            return_stock_id = stock_return_obj.search(cr, uid , [('line_id', '=', ids[0]) , ('product_id', '=', product_id), ('status', '=', location_type)])
                            if  return_stock_id:
                                cr.execute('update stock_return_line set exchange_qty =exchange_qty + %s,return_quantity =return_quantity+ %s where id=%s ', (quantity, quantity, return_stock_id[0],))
                            else:                       
                                stock_return_obj.create(cr, uid, {'line_id': ids[0],
                                                           'sequence':sequence,
                                                          'product_id': product_id,
                                                          'product_uom': uom_id,
                                                          'return_quantity':quantity,
                                                          'exchange_qty':quantity,
                                                          'sale_quantity':0,
                                                          'status':location_type,
                                                        #  'rec_small_uom_id':small_uom_id,
                                                         # 'rec_big_uom_id':big_uom,
                                                          'from_location_id':location_id ,
                                                          'to_location_id': to_location_id,
                                                          }, context=context)                
            # Near Exp Location
            if return_data.from_wh_near_exp_location_id:      
                location_id = return_data.from_wh_near_exp_location_id.id
                to_location_id = return_data.to_wh_near_exp_location_id.id
                
                location_type = "Near Expired Return"                
                return_quant_ids = quant_obj.search(cr, uid, [('location_id', '=', location_id)])
                if  return_quant_ids:        
                    for quant_id in return_quant_ids:
                        quant_data = quant_obj.browse(cr, uid, quant_id, context=context)
                        product_id = quant_data.product_id.id
                        product_data = product_obj.browse(cr, uid, product_id, context=context)
                        categ_issue_from_optional_location = product_data.product_tmpl_id.categ_id.issue_from_optional_location
                        principle_is_separate_srn=product_data.product_tmpl_id.main_group.is_separate_transition
                        if issue_from_optional_location == categ_issue_from_optional_location and principle_is_separate_srn==is_separate_srn:
                            sequence = product_data.sequence
                            uom_id = product_data.uom_id.id
                            quantity = quant_data.qty
    #                             normal_stock_id = stock_return_obj.search(cr, uid , [('line_id', '=', ids[0]) , ('product_id', '=', product_id), ('status', '=', 'Stock Return')])
    #                             if normal_stock_id:
    #                                 cr.execute('update stock_return_line set return_quantity = return_quantity - %s where id=%s ', (quantity, normal_stock_id[0],))                                                
                            return_stock_id = stock_return_obj.search(cr, uid , [('line_id', '=', ids[0]) , ('product_id', '=', product_id), ('status', '=', location_type)])
                            if  return_stock_id:
                                cr.execute('update stock_return_line set exchange_qty =exchange_qty + %s,return_quantity =return_quantity+ %s where id=%s ', (quantity, quantity, return_stock_id[0],))
                            else:                       
                                stock_return_obj.create(cr, uid, {'line_id': ids[0],
                                                           'sequence':sequence,
                                                          'product_id': product_id,
                                                          'product_uom': uom_id,
                                                          'return_quantity':quantity,
                                                          'exchange_qty':quantity,
                                                          'sale_quantity':0,
                                                          'status':location_type,
                                                       #   'rec_small_uom_id':small_uom_id,
                                                         # 'rec_big_uom_id':big_uom,
                                                          'from_location_id':location_id ,
                                                          'to_location_id': to_location_id,
                                                          }, context=context)                 
            # Damage Location
            if return_data.from_wh_damage_location_id:      
                location_id = return_data.from_wh_damage_location_id.id
                to_location_id = return_data.to_wh_damage_location_id.id
                
                location_type = "Damage Return"                
                return_quant_ids = quant_obj.search(cr, uid, [('location_id', '=', location_id)])
                if  return_quant_ids:        
                    for quant_id in return_quant_ids:
                        quant_data = quant_obj.browse(cr, uid, quant_id, context=context)
                        product_id = quant_data.product_id.id
                        product_data = product_obj.browse(cr, uid, product_id, context=context)
                        categ_issue_from_optional_location = product_data.product_tmpl_id.categ_id.issue_from_optional_location
                        principle_is_separate_srn=product_data.product_tmpl_id.main_group.is_separate_transition
                        if issue_from_optional_location == categ_issue_from_optional_location  and principle_is_separate_srn==is_separate_srn:
                            sequence = product_data.sequence
                            uom_id = product_data.uom_id.id
                            quantity = quant_data.qty
    #                             normal_stock_id = stock_return_obj.search(cr, uid , [('line_id', '=', ids[0]) , ('product_id', '=', product_id), ('status', '=', 'Stock Return')])
    #                             if normal_stock_id:
    #                                 cr.execute('update stock_return_line set return_quantity = return_quantity - %s where id=%s ', (quantity, normal_stock_id[0],))                                                
                            return_stock_id = stock_return_obj.search(cr, uid , [('line_id', '=', ids[0]) , ('product_id', '=', product_id), ('status', '=', location_type)])
                            if  return_stock_id:
                                cr.execute('update stock_return_line set exchange_qty =exchange_qty + %s,return_quantity =return_quantity+ %s where id=%s ', (quantity, quantity, return_stock_id[0],))
                            else:                       
                                stock_return_obj.create(cr, uid, {'line_id': ids[0],
                                                           'sequence':sequence,
                                                          'product_id': product_id,
                                                          'product_uom': uom_id,
                                                          'return_quantity':quantity,
                                                          'exchange_qty':quantity,
                                                          'sale_quantity':0,
                                                          'status':location_type,
                                                         # 'rec_small_uom_id':small_uom_id,
                                                          # 'rec_big_uom_id':big_uom,
                                                          'from_location_id':location_id ,
                                                          'to_location_id': to_location_id,
                                                          }, context=context)                  
            # Fresh Stock Location
            if return_data.from_wh_fresh_stock_not_good_location_id:      
                location_id = return_data.from_wh_fresh_stock_not_good_location_id.id
                to_location_id = return_data.to_wh_fresh_stock_not_good_location_id.id
                location_type = "Not Good Return"                
                return_quant_ids = quant_obj.search(cr, uid, [('location_id', '=', location_id)])
                if  return_quant_ids:        
                    for quant_id in return_quant_ids:
                        quant_data = quant_obj.browse(cr, uid, quant_id, context=context)
                        product_id = quant_data.product_id.id
                        product_data = product_obj.browse(cr, uid, product_id, context=context)
                        categ_issue_from_optional_location = product_data.product_tmpl_id.categ_id.issue_from_optional_location
                        principle_is_separate_srn=product_data.product_tmpl_id.main_group.is_separate_transition
                        if issue_from_optional_location == categ_issue_from_optional_location and principle_is_separate_srn==is_separate_srn:
                            sequence = product_data.sequence
                            uom_id = product_data.uom_id.id
                            quantity = quant_data.qty
    #                             normal_stock_id = stock_return_obj.search(cr, uid , [('line_id', '=', ids[0]) , ('product_id', '=', product_id), ('status', '=', 'Stock Return')])
    #                             if normal_stock_id:
    #                                 cr.execute('update stock_return_line set return_quantity = return_quantity - %s where id=%s ', (quantity, normal_stock_id[0],))                                                
                            return_stock_id = stock_return_obj.search(cr, uid , [('line_id', '=', ids[0]) , ('product_id', '=', product_id), ('status', '=', location_type)])
                            if  return_stock_id:
                                cr.execute('update stock_return_line set exchange_qty =exchange_qty + %s,return_quantity =return_quantity+ %s where id=%s ', (quantity, quantity, return_stock_id[0],))
                            else:                       
                                stock_return_obj.create(cr, uid, {'line_id': ids[0],
                                                           'sequence':sequence,
                                                          'product_id': product_id,
                                                          'product_uom': uom_id,
                                                          'return_quantity':quantity,
                                                          'exchange_qty':quantity,
                                                          'sale_quantity':0,
                                                          'status':location_type,
                                                        #  'rec_small_uom_id':small_uom_id,
                                                          # 'rec_big_uom_id':big_uom,
                                                          'from_location_id':location_id ,
                                                          'to_location_id': to_location_id,
                                                          }, context=context)                
    #                 for trans_line in trans_data.item_line:
#                     product_id = trans_line.product_id.id
#                     return_quantity = trans_line.product_qty
#                     sale_quantity = 0
#                     foc_quantity = 0
#                     small_uom_id = trans_line.uom_id.id     
#                     product_trans_line_data=product_trans_line_obj.browse(cr, uid, trans_line.id, context=context)
#                     if product_trans_line_data.trans_type == 'Out':
#                         return_quantity = -1*return_quantity
#                         cr.execute("update stock_return_line set return_quantity = return_quantity  + %s where product_id=%s and  ex_return_id is null",(return_quantity,product_id,))
#                     product = self.pool.get('product.product').browse(cr, uid, product_id, context=context)
#                     sequence=product.sequence
#                     stock_return_obj.create(cr, uid, {'line_id': ids[0],
#                                              'sequence':sequence,
#                                               'product_id': product_id,
#                                               'product_uom': small_uom_id,
#                                               'receive_quantity':0,
#                                               'return_quantity':return_quantity,
#                                               'sale_quantity':0,
#                                               'foc_quantity':0,
#                                               'status':location_type,
#                                               'rec_small_uom_id':small_uom_id,
#                                               'rec_big_uom_id':big_uom,
#                                               'remark':exchange_type,
#                                               'ex_return_id':t_id,
#                                               }, context=context)     
#            return_data = stock_return_obj.search(cr, uid, [('line_id', '=', ids[0])], context=context) 
#             for data in return_data:
#                 return_record = stock_return_obj.browse(cr, uid, data, context=context)
#                 record_id= return_record.id
#                 product_id = return_record.product_id.id
#                 return_qty = return_record.return_quantity
#                 product = product_obj.browse(cr, uid, product_id, context=context)
#                 if return_qty >0: 
#                     cr.execute("select floor(round(1/factor,2)) as ratio from product_uom where active = true and id=%s", (product.product_tmpl_id.big_uom_id.id,))
#                     bigger_qty = cr.fetchone()[0]
#                     bigger_qty = int(bigger_qty)
#                     big_uom_qty = divmod(return_qty, bigger_qty)
#                     if  big_uom_qty:
#                         big_quantity = big_uom_qty[0]
#                         small_quantity = big_uom_qty[1]
#                         cr.execute("update stock_return_line set return_quantity_big=%s,return_quantity=%s where product_id=%s and line_id=%s and id=%s", (big_quantity, small_quantity, product_id, ids[0],record_id,))
#                 else:
#                         cr.execute("update stock_return_line set return_quantity_big=0,return_quantity=%s where product_id=%s and line_id=%s and id=%s", ( return_qty, product_id, ids[0],record_id,))

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
         'returner' : fields.char('Returned By'),
         'wh_receiver' : fields.char('WH Receiver'),
         'return_date':fields.date('From Date of Return', required=True),
         'to_return_date':fields.date('To Date of Return', required=True),
         'vehicle_id':fields.many2one('fleet.vehicle', 'Vehicle No'),
#         'branch_id':fields.many2one('res.branch', 'Branch'),
         'state': fields.selection([
            ('draft', 'Pending'),
            ('received', 'Received'),
            ('cancel', 'Cancel'),
            ('reversed', 'Reversed'),
            ], 'Status', readonly=True, copy=False, help="Gives the status of the quotation or sales order.\
              \nThe exception status is automatically set when a cancel operation occurs \
              in the invoice validation (Invoice Exception) or in the picking list process (Shipping Exception).\nThe 'Waiting Schedule' status is set when the invoice is confirmed\
               but waiting for the scheduler to run on the order date.", select=True),
        'p_line':fields.one2many('stock.return.line', 'line_id', 'Product Lines',
                              copy=True),
                'company_id':fields.many2one('res.company', 'Company'),
				'partner_id':fields.many2one('res.partner', 'Customer'),
        'from_wh_normal_return_location_id': fields.many2one('stock.location', 'From Normal Return location'),
        'from_wh_exp_location_id': fields.many2one('stock.location', 'From Expiry location'),
        'from_wh_near_exp_location_id': fields.many2one('stock.location', 'From Near Expiry location'),
        'from_wh_damage_location_id': fields.many2one('stock.location', 'From Damage location'),
        'from_wh_fresh_stock_not_good_location_id': fields.many2one('stock.location', 'From Fresh stock minor damage location'),
        
        'to_wh_normal_return_location_id': fields.many2one('stock.location', 'To Normal Return location'),
        'to_wh_exp_location_id': fields.many2one('stock.location', 'To Expiry location'),
        'to_wh_near_exp_location_id': fields.many2one('stock.location', 'To Near Expiry location'),
        'to_wh_damage_location_id': fields.many2one('stock.location', 'To Damage location'),
        'to_wh_fresh_stock_not_good_location_id': fields.many2one('stock.location', 'To Fresh stock minor damage location'),
         'issue_from_optional_location':fields.boolean('Issue from Optional Location'),
         'is_separate_srn':fields.boolean('Stock Return For OML', default=False,readonly=False),

}		
    
    _defaults = {
        'state' : 'draft',
         'company_id': _get_default_company,
         'branch_id': _get_default_branch,
         'return_date' :fields.datetime.now
    }     
    
    def create(self, cursor, user, vals, context=None):
        if vals['sale_team_id']:
            sale_team_id = vals['sale_team_id']
            sale_team = self.pool.get('crm.case.section').browse(cursor, user, sale_team_id, context=context)
            to_location_id = sale_team.issue_location_id.id            
            from_location_id = sale_team.location_id.id
        if  vals['issue_from_optional_location']:
            if vals['issue_from_optional_location'] == True:
                to_location_id = sale_team.optional_issue_location_id.id    
            else:
                to_location_id = to_location_id   
   
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
    
    def set_to_draft(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'draft', })    

    def reversed(self, cr, uid, ids, context=None):
        pick_obj = self.pool.get('stock.picking')
        move_obj = self.pool.get('stock.move')
        stockDetailObj = self.pool.get('stock.transfer_details')
        detailObj = None
        srn_value = self.browse(cr, uid, ids[0], context=context)
        srn_no = srn_value.name
        return_date = srn_value.to_return_date
        move_ids = []
        move_ids = move_obj.search(cr, uid, [('origin', '=', srn_no), ('state', '=', 'done')], context=context)
        # choose the view_mode accordingly
        for move_id in move_ids:
            move = move_obj.browse(cr, uid, move_id, context=context)                
#             #Create new picking for returned products
#             pick_type_id = pick.picking_type_id.return_picking_type_id and pick.picking_type_id.return_picking_type_id.id or pick.picking_type_id.id
#             new_picking = pick_obj.copy(cr, uid, pick.id, {
#                 'move_lines': [],
#                 'picking_type_id': pick_type_id,
#                 'state': 'draft',
#                 'origin': pick.name,
#             }, context=context)
#             for move in pick.move_lines:
            if move.origin_returned_move_id.move_dest_id.id and move.origin_returned_move_id.move_dest_id.state != 'cancel':
                move_dest_id = move.origin_returned_move_id.move_dest_id.id
            else:
                move_dest_id = False
            if move.product_uom_qty > 0:
                existing_moves = move_obj.search(cr, uid, [('origin', '=', 'Reverse ' + move.origin),
                                                           ('product_id', '=', move.product_id.id),
                                                           ('product_uom_qty', '=', move.product_uom_qty),
                                                           ('product_uos_qty', '=', move.product_uom_qty * move.product_uos_qty / move.product_uom_qty)], context=context)
                if not existing_moves:
                    move_new_id = move_obj.copy(cr, uid, move.id, {
                                        'product_id': move.product_id.id,
                                        'product_uom_qty': move.product_uom_qty,
                                        'product_uos_qty': move.product_uom_qty * move.product_uos_qty / move.product_uom_qty,
                                        # 'picking_id': new_picking,
                                        'state': 'draft',
                                        'location_id': move.location_dest_id.id,
                                        'location_dest_id': move.location_id.id,
                                     #   'picking_type_id': pick_type_id,
                                      #  'warehouse_id': pick.picking_type_id.warehouse_id.id,
                                        'origin_returned_move_id': move.id,
                                        'procure_method': 'make_to_stock',
                                      #  'restrict_lot_id': data_get.lot_id.id,
                                        'origin':'Reverse ' + move.origin,
    
                                        'move_dest_id': move_dest_id,
                                })
                    move_obj.action_done(cr, uid, move_new_id, context=context)
            cr.execute("update stock_move set date=%s where origin=%s", (return_date, 'Reverse ' +move.origin,))
        return self.write(cr, uid, ids, {'state': 'reversed', })    
        
    def received(self, cr, uid, ids, context=None):
        move_obj = self.pool.get('stock.move')     
        location_obj = self.pool.get('stock.location')   
        check_obj = self.pool.get('stock.return.check')  
        check_line_obj = self.pool.get('stock.return.check.line')     
        product_obj = self.pool.get('product.product')  
        return_obj = self.browse(cr, uid, ids, context=context)    
        tmp_location_id = return_obj.sale_team_id.temp_location_id.id
        return_date = return_obj.to_return_date
        origin = return_obj.name
        team_id = return_obj.sale_team_id.id
        branch_id = return_obj.branch_id.id
        for line in return_obj.p_line:
            from_location_id = line.from_location_id.id
            to_location_id = line.to_location_id.id
            product_id = line.product_id.id
            name = line.product_id.name_template          
            onground_quantity = line.onground_quantity
            return_quantity = line.return_quantity
            actual_return_quantity = line.actual_return_quantity
            uom_id = line.product_uom.id
            if  line.status:
                different_qty = 0
                different_qty = return_quantity - onground_quantity
                cr.execute("update stock_return_line set different_qty= %s where id=%s", (different_qty, line.id,))            
                if different_qty:
                    if different_qty < 0:
                        # Tmp===> Car
                        # inventory_location_id = location_obj.search(cr, uid, [('name', '=', 'Inventory loss')])
                        
                        existing_moves = move_obj.search(cr, uid, [('origin', '=', origin),
                                                                   ('product_id', '=', product_id),
                                                                   ('product_uom_qty', '=', -1 * different_qty),
                                                                   ('product_uos_qty', '=', -1 * different_qty),
                                                                   ('product_uom', '=', uom_id)], context=context)
                        if not existing_moves:
                            move_id = move_obj.create(cr, uid, {
                                                  'product_id': product_id,
                                                  'product_uom_qty':-1 * different_qty ,
                                                  'product_uos_qty':-1 * different_qty,
                                                  'product_uom':uom_id,
                                                  'location_id':tmp_location_id,
                                                  'location_dest_id':from_location_id,
                                                  'name':name,
                                                   'origin':origin,
                                                   'manual':True,
                                                  'state':'confirmed'}, context=context)     
                            move_obj.action_done(cr, uid, move_id, context=context)
                    if different_qty > 0:
    #                 Car===> tmp  
                        existing_moves = move_obj.search(cr, uid, [('origin', '=', origin),
                                                                   ('product_id', '=', product_id),
                                                                   ('product_uom_qty', '=', different_qty),
                                                                   ('product_uos_qty', '=', different_qty),
                                                                   ('product_uom', '=', uom_id)], context=context)
                        if not existing_moves:                  
                            move_id = move_obj.create(cr, uid, {
                                                  'product_id': product_id,
                                                  'product_uom_qty':  different_qty ,
                                                  'product_uos_qty':  different_qty,
                                                  'product_uom':uom_id,
                                                  'location_id':from_location_id,
                                                  'location_dest_id':tmp_location_id,
                                                  'name':name,
                                                   'origin':origin,
                                                 'manual':True,
                                                  'state':'confirmed'}, context=context)     
                            move_obj.action_done(cr, uid, move_id, context=context)        
                if actual_return_quantity > 0:
                    # Car===> To Location     
                    existing_moves = move_obj.search(cr, uid, [('origin', '=', origin),
                                                               ('product_id', '=', product_id),
                                                               ('product_uom_qty', '=', actual_return_quantity),
                                                               ('product_uos_qty', '=', actual_return_quantity),
                                                               ('product_uom', '=', uom_id)], context=context)
                    if not existing_moves:                 
                        move_id = move_obj.create(cr, uid, {
                                              'product_id': product_id,
                                              'product_uom_qty':  actual_return_quantity ,
                                              'product_uos_qty':  actual_return_quantity,
                                              'product_uom':uom_id,
                                              'location_id':from_location_id,
                                              'location_dest_id':to_location_id,
                                              'name':name,
                                              'origin':origin,
                                             'manual':False,
                                              'state':'confirmed'}, context=context)     
                        move_obj.action_done(cr, uid, move_id, context=context)      
        check_value = {'name':return_obj.id,
                                      'return_date':return_date,
                                      'sale_team_id':team_id,
                                      'branch_id':branch_id,
                                     }    
        check_id = check_obj.create(cr, uid, check_value, context=context)
        cr.execute('select srnl.product_id,srnl.product_uom,srnl.actual_return_quantity,srnl.to_location_id,srnl.status,srn.return_date from stock_return srn, stock_return_line srnl where srn.id=srnl.line_id and srnl.actual_return_quantity >0 and srnl.status != %s and srn.id = %s', ('Stock Return', return_obj.id,))
        stock_return = cr.fetchall()
        if stock_return:
            for srn_data_line in stock_return:
                product_id = srn_data_line[0]
                pro_data = product_obj.browse(cr, uid, product_id, context=context)
                sequence = pro_data.sequence
                uom_id = srn_data_line[1]
                qty = srn_data_line[2]
                current_location = srn_data_line[3]            
                if pro_data.product_tmpl_id.type == 'product':
                    check_line_obj.create(cr, uid, {
                                      'line_id':check_id,
                                      'sequence':sequence,
                                      'product_id':product_id,
                                      'current_product_uom': uom_id,
                                      'to_product_uom':uom_id,
                                      'current_location':current_location,
                                      'current_qty':qty,
                                      }, context=context)    
        cr.execute("update stock_move set is_exchange =False,date=%s where origin=%s", (return_date, origin,))
        return self.write(cr, uid, ids, {'state':'received'})      

            
class stock_return_line(osv.osv):  # #prod_pricelist_update_line
    _name = 'stock.return.line'
    _description = 'Return Line'
    
    def _amount_compute(self, cursor, user, ids, name, attr, context=None):
        res = {}
        for line in self.browse(cursor, user, ids, context=context):
            res[line.id] = line.closing_stock_qty + line.actual_return_quantity
        return res
    
    _columns = {                
        'line_id':fields.many2one('stock.return', 'Line', ondelete='cascade', select=True),
        'product_id': fields.many2one('product.product', 'Product', required=True),
        'product_uom': fields.many2one('product.uom', 'UOM', required=True),
        'status' : fields.char('Status'),
        'state': fields.related('line_id', 'state', string='State', readonly=True, type='selection', selection=[
            ('draft', 'Pending'),
            ('received', 'Received'),
            ('cancel', 'Cancel'),
            ('reversed', 'Reversed'),
            ]),
        'opening_stock_qty' : fields.float(string='Opening Stock Qty', digits=(16, 0)),
        'sale_quantity' : fields.float(string='Sales Qty', digits=(16, 0)),
        'return_quantity' : fields.float(string='Returned Qty', digits=(16, 0)),
       # 'onground_quantity' : fields.float(string='All Physical Stock Qty', digits=(16, 0),readonly=True),
        
        'onground_quantity': fields.function(_amount_compute, string='All Physical Stock Qty', store=True, digits=(16, 0), readonly=True, type='float'),

        'actual_return_quantity' : fields.float(string='Actual Return Qty', digits=(16, 0)),
        'closing_stock_qty' : fields.float(string='Closing Stock Qty', digits=(16, 0)),
        # 'receive_quantity' : fields.float(string='Received Qty', digits=(16, 0)),
        # 'return_quantity_big' : fields.float(string='Returned Big Qty', digits=(16, 0)),
        
        # 'sale_quantity_big' : fields.float(string='Sales Qty Big', digits=(16, 0)),
        # 'foc_quantity' : fields.float(string='FOC Qty', digits=(16, 0)),
     #   'exchange_quantity' : fields.float(string='Sale/Exchange Qty', digits=(16, 0)),
        
        # 'uom_ratio':fields.char('Packing Unit'),
        'expiry_date':fields.date('Expiry'),
        'remark':fields.char('Remark'),
        # 'rec_big_uom_id': fields.many2one('product.uom', 'Rec Bigger UoM',help="Default Unit of Measure used for all stock operation."),
        # 'rec_big_quantity' : fields.float(string='Rec Qty', digits=(16, 0)),        
        # 'rec_small_quantity' : fields.float(string='Rec Small Qty', digits=(16, 0)),
        # 'rec_small_uom_id': fields.many2one('product.uom', 'Rec Smaller UoM'),         
        'sequence':fields.integer('Sequence'),
        # 'ex_return_id':fields.many2one('product.transactions','Exchange ID'),
        'different_qty':fields.integer('Different Qty'),
        'from_location_id':fields.many2one('stock.location', 'From Location'),
        'to_location_id':fields.many2one('stock.location', 'To Location'),
        'in_stock_qty':fields.float('In Qty'),
        'exchange_qty':fields.float('Exchange Qty'),
        'assembly_qty' :fields.float('Disassembly Qty'),
        'miss_qty' :fields.float('Missed Order Qty',readonly=False),
        'checked' : fields.boolean(string='Checked', default=False),


    }
        
    def on_change_return_quantity(self, cr, uid, ids, closing_stock_qty, return_quantity, context=None):
        values = {}
        closing_qty = closing_stock_qty + return_quantity
        values = {
            'onground_quantity': closing_qty,
        }
        if ids:
            cr.execute("update stock_return_line set onground_quantity=%s where id =%s", (closing_qty, ids[0],))
        return {'value': values}        
    
    def on_change_ground_quantity(self, cr, uid, ids, closing_stock_qty, return_quantity, context=None):
        values = {}
        closing_qty = closing_stock_qty + return_quantity
        values = {
            'onground_quantity': closing_qty,
        }
        if ids:
            cr.execute("update stock_return_line set onground_quantity=%s where id =%s", (closing_qty, ids[0],))
        return {'value': values}     
    
