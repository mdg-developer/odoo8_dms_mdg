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
     
    def on_change_stock_return(self, cr, uid, ids, name, context=None):
        values = {}
        data_line = []
        team_id   =[]    
        product_obj = self.pool.get('product.product')
        if name:
            cr.execute('select srnl.product_id,srnl.product_uom,srnl.actual_return_quantity,srnl.to_location_id,srnl.status,srn.return_date,srn.sale_team_id from stock_return srn, stock_return_line srnl where srn.id=srnl.line_id and srnl.actual_return_quantity >0 and srnl.status != %s and srn.id = %s', ('Stock Return',name,))
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
                    team_id = srn_data_line[6]
                
                    if pro_data.product_tmpl_id.type=='product':
                        data_line.append({
                                          'sequence':sequence,
                                          'product_id':product_id,
                                         'to_product_uom':uom_id,
                                          'current_product_uom': uom_id,
                                          'current_location':current_location,
                                          'current_qty':qty,
                                            })
                
            values = {
                        's_line': data_line,
                        'sale_team_id':team_id,
                    }
        return {'value': values}
    
    def _get_default_branch(self, cr, uid, context=None):
        branch_id = self.pool.get('res.users')._get_branch(cr, uid, context=context)
        if not branch_id:
            raise osv.except_osv(_('Error!'), _('There is no default branch for the current user!'))
        return branch_id
    
    def _get_default_company(self, cr, uid, context=None):
        company_id = self.pool.get('res.users')._get_company(cr, uid, context=context)
        if not company_id:
            raise osv.except_osv(_('Error!'), _('There is no default company for the current user!'))
        return company_id
    
    def cancel(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'cancel', })
    
    def received(self, cr, uid, ids, context=None):
        move_obj = self.pool.get('stock.move')     
        user_obj = self.pool.get('res.users')     
        user_data=user_obj.browse(cr, uid, uid, context=context)    
        return_obj = self.browse(cr, uid, ids, context=context)    
        ids
        origin = return_obj.name.name
        for line in return_obj.s_line:
            from_location_id =line.current_location.id
            to_location_id = line.to_location.id
            product_id = line.product_id.id
            name = line.product_id.name_template          
            to_quantity = line.to_qty
            uom_id = line.to_product_uom.id
            if to_quantity:
                if to_quantity > 0:
#                 From Location===> Change Location                    
                    move_id = move_obj.create(cr, uid, {
                                          'product_id': product_id,
                                          'product_uom_qty':  to_quantity ,
                                          'product_uos_qty':  to_quantity,
                                          'product_uom':uom_id,
                                          'location_id':from_location_id,
                                          'location_dest_id':to_location_id,
                                          'name':name,
                                           'origin':origin,
                                         'manual':True,
                                          'state':'confirmed'}, context=context)     
                    move_obj.action_done(cr, uid, move_id, context=context)        
        return self.write(cr, uid, ids, {'state':'received','receive_by':user_data.name})        
        
    _columns = {
        'sale_team_id':fields.many2one('crm.case.section', 'Sales Team' , required=True),
        'name':fields.many2one('stock.return', 'SRN Ref' , required=True),
        'return_date':fields.date('Date of Return', required=True),
        'branch_id':fields.many2one('res.branch', 'Branch',required=True),
        'company_id':fields.many2one('res.company', 'Company'),
        'partner_id':fields.many2one('res.partner', 'Customer'),
        'receive_by' : fields.char('Receive By'),
        'approve_by':fields.many2one('res.users', "Approved By"),
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
        'branch_id': _get_default_branch,
        'company_id': _get_default_company,
        'return_date' :fields.datetime.now,

        }
    def create(self, cursor, user, vals, context=None):
        data_line = []
        if vals['name']:
            ref_id=vals['name']
            srn_data = self.pool.get('stock.return')
            product_obj = self.pool.get('product.product')
            if ref_id:
                cursor.execute('select srnl.product_id,srnl.product_uom,srnl.actual_return_quantity,srnl.to_location_id,srnl.status,srn.return_date from stock_return srn, stock_return_line srnl where srn.id=srnl.line_id and srnl.status != %s and srn.id = %s', ('Stock Return',ref_id,))
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
                                              'current_product_uom': uom_id,
                                              'to_product_uom':uom_id,
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


    def on_change_product_id(self, cr, uid, ids, product_id, context=None):
        values = {}
        domain={}
        if product_id:
            product = self.pool.get('product.product').browse(cr, uid, product_id, context=context)
            values = {
                      'current_product_uom':product.product_tmpl_id.uom_id and product.product_tmpl_id.uom_id.id or False,
                'to_product_uom': product.product_tmpl_id.uom_id and product.product_tmpl_id.uom_id.id or False,
            }
            
        return {'value': values}
    
    def create(self, cr, uid, values, context=None):
        if values.get('line_id') and values.get('product_id'):
            defaults = self.on_change_product_id(cr, uid, [], values['product_id'], context=dict(context or {}))['value']
            values = dict(defaults, **values)
        return super(stock_return_check_line, self).create(cr, uid, values, context=context)
    
               
    _columns = {                
        'line_id':fields.many2one('stock.return.check', 'Line', ondelete='cascade', select=True),
        'product_id': fields.many2one('product.product', 'Product', required=True),
        'sequence':fields.integer('Sequence'),
        'current_location':fields.many2one('stock.location', 'Current Location',  required=True,readonly=False),
        'current_product_uom': fields.many2one('product.uom', 'UOM', required=True, readonly=True),
        'current_qty':  fields.float(string='Current Qty', digits=(16, 0)),
        'to_location':fields.many2one('stock.location', 'To Location'),
        'to_product_uom': fields.many2one('product.uom', 'UOM', required=False, readonly=True),
        'to_qty':  fields.float(string='Qty', digits=(16, 0)),
    }     
   
    
