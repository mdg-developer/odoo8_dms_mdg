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


class stock_return_check(osv.osv):
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _name = "stock.return.check"
    _description = "Stock Return Check"
    _order = "id desc"    
     
    def on_change_stock_return(self, cr, uid, ids, srn_id, context=None):
        values = {}
        data_line = []
        product_obj = self.pool.get('product.product')
        if srn_id:
            cr.execute('select srnl.product_id,srnl.product_uom,srnl.actual_return_quantity,srnl.to_location,srnl.status,srn.return_date from stock_return srn, stock_return_line srnl where srn.id=srnl.line_id and srnl.status != %s and srn.id = %s', ('Stock Return',srn_id,))
            stock_return = cr.fetchall()
            if stock_return:
                for srn_data_line in stock_return:
                    product_id = srn_data_line[0]
                    pro_data = product_obj.browse(cr, uid, product_id, context=context)
                    sequence=pro_data.sequence
                    uom_id = srn_data_line[1]
                    qty = srn_data_line[2]
                    current_location = srn_data_line[3]
                    status = srn_data_line[4]
                    return_date = srn_data_line[5]
                
                    if pro_data.product_tmpl_id.type=='product':
                        data_line.append({
                                          'sequence':sequence,
                                          'product_id':product_id,
                                          'current_product_uom': pro_data.product_tmpl_id.uom_id and pro_data.product_tmpl_id.uom_id.id or False,
                                          'current_location':current_location,
                                          'current_qty':qty,
                                            })
                
            values = {
                        's_line': data_line,
                    }
        return {'value': values}
    
    def _get_default_branch(self, cr, uid, context=None):
        branch_id = self.pool.get('res.users')._get_branch(cr, uid, context=context)
        if not branch_id:
            raise osv.except_osv(_('Error!'), _('There is no default branch for the current user!'))
        return branch_id
        
    _columns = {
        'sale_team_id':fields.many2one('crm.case.section', 'Sales Team' , required=True),
        'srn_id':fields.many2one('stock.return', 'SRN Ref' , required=True),
        'branch_id':fields.many2one('res.branch', 'Branch',required=True),
        'return_date':fields.date('Date of Return'),
        'state': fields.selection([
            ('draft', 'Pending'),
            ('received', 'Received'),
            ('cancel','Cancel')
            ],'Status', readonly=True, copy=False, help="Gives the status of the quotation or sales order.\
              \nThe exception status is automatically set when a cancel operation occurs \
              in the invoice validation (Invoice Exception) or in the picking list process (Shipping Exception).\nThe 'Waiting Schedule' status is set when the invoice is confirmed\
               but waiting for the scheduler to run on the order date.", select=True),
        's_line':fields.one2many('stock.return.check.line', 'line_id', 'Product Lines',copy=True),
}
    
    _defaults = {
        'state' : 'draft',
        'branch_id': _get_default_branch
        }
    def create(self, cursor, user, vals, context=None):
        data_line = []
        if vals['srn_id']:
            ref_id=vals['srn_id']
            srn_data = self.pool.get('stock.return')
            product_obj = self.pool.get('product.product')
            if ref_id:
                cursor.execute('select srnl.product_id,srnl.product_uom,srnl.actual_return_quantity,srnl.to_location,srnl.status,srn.return_date from stock_return srn, stock_return_line srnl where srn.id=srnl.line_id and srnl.status != %s and srn.id = %s', ('Stock Return',ref_id,))
                stock_return = cursor.fetchall()
                if stock_return:
                    for srn_data_line in stock_return:
                        product_id = srn_data_line[0]
                        pro_data = product_obj.browse(cursor, user, product_id, context=context)
                        sequence=pro_data.sequence
                        uom_id = srn_data_line[1]
                        qty = srn_data_line[2]
                        current_location = srn_data_line[3]
                        status = srn_data_line[4]
                        return_date = srn_data_line[5]
            
                        if pro_data.product_tmpl_id.type=='product':
                            data_line.append({
                                              'sequence':sequence,
                                              'product_id':product_id,
                                              'current_product_uom': pro_data.product_tmpl_id.uom_id and pro_data.product_tmpl_id.uom_id.id or False,
                                              'current_location':current_location,
                                              'current_qty':qty,
                                              })
                
                values = {
                          's_line': data_line,
                        }
        return super(stock_return_check, self).create(cursor, user, vals, context=context)

class stock_return_check_line(osv.osv):
    _name = 'stock.return.check.line'
    _description = 'Return Check Line'
           
    _columns = {                
        'line_id':fields.many2one('stock.return.check', 'Line', ondelete='cascade', select=True),
        'product_id': fields.many2one('product.product', 'Product', required=True),
        'sequence':fields.integer('Sequence'),
        'current_location':fields.many2one('stock.location', 'Current Location', readonly=True),
        'current_product_uom': fields.many2one('product.uom', 'UOM', required=True),
        'current_qty':  fields.float(string='Current Qty', digits=(16, 0)),
        'to_location':fields.many2one('stock.location', 'To Location'),
        'to_product_uom': fields.many2one('product.uom', 'UOM', required=True),
        'to_qty':  fields.float(string='To Qty', digits=(16, 0)),
    }     
   
    
