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
import math
from datetime import datetime, timedelta

class pallet_transfer(osv.osv):
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _name = "pallet.transfer"
    _description = "Pallet Transfer"
    _order = "id desc"    
    _track = {
        'state': {
            'pallet_transfer.pallet_transfer_transfer': lambda self, cr, uid, obj, ctx = None: obj.state in ['transfer'],
        },
    }  
     
    def _get_default_branch(self, cr, uid, context=None):
        branch_id = self.pool.get('res.users')._get_branch(cr, uid, context=context)
        if not branch_id:
            raise osv.except_osv(_('Error!'), _('There is no default branch for the current user!'))
        return branch_id
    
    _columns = {
        'name': fields.char('PT-Ref:No', readonly=True),
         'good_receive_id':fields.many2one('good.receive.note', 'GRN No'),
         'transfer_date':fields.date('Transfer Date', required=True),
         'receive_date':fields.date('Receive Date', required=True),
         'transfer_by':fields.many2one('res.users', 'Transfer By'),
        'state': fields.selection([
            ('draft', 'Pending'),
            ('reserve', 'Reserved'),
            ('transfer', 'Transfered'),
            ('cancel', 'Cancel'),
            ], 'Status', readonly=True, copy=False, help="Gives the status of the quotation or sales order.\
              \nThe exception status is automatically set when a cancel operation occurs \
              in the invoice validation (Invoice Exception) or in the picking list process (Shipping Exception).\nThe 'Waiting Schedule' status is set when the invoice is confirmed\
               but waiting for the scheduler to run on the order date.", select=True),
                 'p_line':fields.one2many('pallet.transfer.line', 'line_id', 'Product Lines',
                              copy=True),
                                'partner_id':fields.many2one('res.partner', string='Partner'),
       'branch_id':fields.many2one('res.branch', 'Branch'),

}
    _defaults = {
        'state' : 'draft',
         'branch_id': _get_default_branch,
    }     

    def create(self, cursor, user, vals, context=None):
        id_code = self.pool.get('ir.sequence').get(cursor, user,
                                                'transfer.code') or '/'
        vals['name'] = id_code
        return super(pallet_transfer, self).create(cursor, user, vals, context=context)
    
    def reserve(self, cr, uid, ids, context=None):
        transfer_line_obj = self.pool.get('pallet.transfer.line')       
        product_obj = self.pool.get('product.product')       
        quant_obj = self.pool.get('stock.quant')
        transfer_line_ids = transfer_line_obj.search(cr, uid, [('line_id', '=', ids[0])], context=context) 
        location_data = []
        for transfer_id in transfer_line_ids:
            transfer_data = transfer_line_obj.browse(cr, uid, transfer_id, context=context)
            location_id = transfer_data.src_location_id.id 
            pallet_id = transfer_data.pallet_id.id
            cr.execute("select product_id from stock_quant where package_id =%s", (pallet_id,))
            product_id = cr.fetchone()
            if product_id:
                product_id = product_id[0]
                product_data = product_obj.browse(cr, uid, product_id, context=context)
                principle_id = product_data.product_tmpl_id.main_group.id
            else:
                raise osv.except_osv(_('Warning'),
                                     _('Please Press Your Pallet'))               
            cr.execute("""select sl.id from product_product pp ,product_template pt ,stock_location sl 
            where pp.product_tmpl_id =pt.id 
            and pt.main_group=sl.maingroup_id
            and sl.location_id=%s
            and pt.main_group = %s
            group by  sl.id,pt.main_group""", (location_id, principle_id,))
            location_ids = cr.fetchall()
            for location in location_ids:
                location_id = location[0]
                quant_id = quant_obj.search(cr, uid, [('location_id', '=', location_id), ('qty', '>', 0)], context=context)         
                if len(quant_id) == 0:
                    location_data.append(location_id)       
            cr.execute("select id from stock_location where id in %s order by row ,layer,room,cell", (tuple(location_data),))
            pallet_location = cr.fetchone()[0]
            transfer_line_obj.write(cr, uid, transfer_id, {'dest_location_id':pallet_location}, context=context)                            
        return self.write(cr, uid, ids, {'state': 'reserve'})
    
    def transfer(self, cr, uid, ids, context=None):
        
        return self.write(cr, uid, ids, {'state': 'transfer', 'transfer_by':uid, 'transfer_date':datetime.now(), })
    
    def cancel(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state':'cancel' })
                            
class pallet_transfer_line(osv.osv):
    _name = 'pallet.transfer.line'
    _description = 'Pallet Transfer Line'        
    _columns = {                
        'line_id':fields.many2one('pallet.transfer', 'Line', ondelete='cascade', select=True),
        'pallet_id': fields.many2one('stock.quant.package', 'Pallet', required=True),
        'src_location_id': fields.many2one('stock.location', 'Source Location'),
        'dest_location_id': fields.many2one('stock.location', 'Destination Location'),
        'remark':fields.char('Remark'),
    }
        
   
    
