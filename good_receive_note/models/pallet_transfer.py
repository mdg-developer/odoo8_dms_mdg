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
    
    def transfer(self, cr, uid, ids, context=None):
        
        return self.write(cr, uid, ids, {'state': 'transfer', 'transfer_by':uid})
    
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
        
   
    
