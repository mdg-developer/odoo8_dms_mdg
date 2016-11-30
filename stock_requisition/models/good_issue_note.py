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

class good_issue_note(osv.osv):
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _name = "good.issue.note"
    _description = "Good Issue Note"
    _order = "id desc"    
    _track = {
        'state': {
            'good_issue_note.mt_note_confirm': lambda self, cr, uid, obj, ctx = None: obj.state in ['confirm'],
            'good_issue_note.mt_note_approve': lambda self, cr, uid, obj, ctx = None: obj.state in ['approve']
        },
    }  
#     
#     def _get_default_branch(self, cr, uid, context=None):
#         branch_id = self.pool.get('res.users')._get_branch(cr, uid, context=context)
#         if not branch_id:
#             raise osv.except_osv(_('Error!'), _('There is no default branch for the current user!'))
#         return branch_id
        
      
    def _get_default_company(self, cr, uid, context=None):
        company_id = self.pool.get('res.users')._get_company(cr, uid, context=context)
        if not company_id:
            raise osv.except_osv(_('Error!'), _('There is no default company for the current user!'))
        return company_id   
    
    _columns = {
        'name': fields.char('GIN Ref', readonly=True),
        'request_id':fields.many2one('stock.requisition', 'RFI Ref', readonly=True),
        'to_location_id':fields.many2one('stock.location', 'Requesting Location', required=True),
        'from_location_id':fields.many2one('stock.location', 'Request Warehouse', required=True),
        'sale_team_id':fields.many2one('crm.case.section', 'Delivery Team'),
     #   'branch_id':fields.many2one('res.branch', 'Branch',required=True),
#         'so_no' : fields.char('Sales Order/Inv Ref;No.'),
         'issue_by':fields.char("Issuer"),
       'request_by':fields.many2one('res.users', "Requested By"),
        'approve_by':fields.many2one('res.users', "Approved By"),
        'receiver':fields.char("Receiver"),
       
#         'request_date' : fields.date('Date Requested'),
         'issue_date':fields.date('Date for Issue',required=True),
        'vehicle_id':fields.many2one('fleet.vehicle', 'Vehicle No'),
        'state': fields.selection([
            ('draft', 'Pending'),
            ('approve', 'Approved'),
            ('issue','Issued'),
            ('cancel', 'Cancel'),
            ], 'Status', readonly=True, copy=False, help="Gives the status of the quotation or sales order.\
              \nThe exception status is automatically set when a cancel operation occurs \
              in the invoice validation (Invoice Exception) or in the picking list process (Shipping Exception).\nThe 'Waiting Schedule' status is set when the invoice is confirmed\
               but waiting for the scheduler to run on the order date.", select=True),
                 'p_line':fields.one2many('good.issue.note.line', 'line_id', 'Product Lines',
                              copy=True),
                'company_id':fields.many2one('res.company', 'Company'),
                'partner_id':fields.many2one('res.partner', string='Partner'),
                'is_return':fields.boolean('Return'),
}
    _defaults = {
        'state' : 'draft',
         'company_id': _get_default_company,
        # 'branch_id': _get_default_branch,
         'is_return':False,
    }     
    def create(self, cursor, user, vals, context=None):
        id_code = self.pool.get('ir.sequence').get(cursor, user,
                                                'good.issue.note.code') or '/'
        vals['name'] = id_code
        return super(good_issue_note, self).create(cursor, user, vals, context=context)
    
    def approve(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'approve','approve_by':uid })
    
    def cancel(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state':'cancel' })
    
    def unlink(self, cr, uid, ids, context=None):
        good_issue_notes = self.read(cr, uid, ids, ['state'], context=context)
        unlink_ids = []
        for s in good_issue_notes:
            if s['state'] in ['draft','approve', 'cancel']:
                unlink_ids.append(s['id'])
            else:
                raise osv.except_osv(_('Invalid Action!'), _('You cannot cancel the issued Good Issue Note!'))

        return super(good_issue_notes, self).unlink(cr, uid, unlink_ids, context=context)

            
    def issue(self, cr, uid, ids, context=None):
        product_line_obj = self.pool.get('good.issue.note.line')
        note_obj = self.pool.get('good.issue.note')
        picking_obj = self.pool.get('stock.picking')
        move_obj = self.pool.get('stock.move')
        note_value = req_lines = {}
        if ids:
            note_value = note_obj.browse(cr, uid, ids[0], context=context)
            issue_date = note_value.issue_date
            location_id = note_value.to_location_id.id
            from_location_id = note_value.from_location_id.id
            origin = note_value.name
            cr.execute('select id from stock_picking_type where default_location_dest_id=%s and name like %s', (location_id, '%Internal Transfer%',))
            price_rec = cr.fetchone()
            if price_rec: 
                picking_type_id = price_rec[0] 
            else:
                raise osv.except_osv(_('Warning'),
                                     _('Picking Type has not for this transition'))
            picking_id = picking_obj.create(cr, uid, {
                                          'date': issue_date,
                                          'origin':origin,
                                          'picking_type_id':picking_type_id}, context=context)
            note_line_id = product_line_obj.search(cr, uid, [('line_id', '=', ids[0])], context=context)
            if note_line_id and picking_id:
                for id in note_line_id:
                    note_line_value = product_line_obj.browse(cr, uid, id, context=context)
                    product_id = note_line_value.product_id.id
                    name = note_line_value.product_id.name_template
                    product_uom = note_line_value.product_uom.id
                    origin = origin
                    quantity = note_line_value.issue_quantity
                    big_qty=note_line_value.big_issue_quantity
                    big_uom=note_line_value.big_uom_id.id
                    lot_id=note_line_value.batch_no.id
                    bigger_qty=0
                    if big_uom:
                        cr.execute("select floor(round(1/factor,2)) as ratio from product_uom where active = true and id=%s", (big_uom,))
                        bigger_qty=cr.fetchone()
                        if bigger_qty:
                            bigger_qty=bigger_qty[0]*big_qty

                        
                    move_id=move_obj.create(cr, uid, {'picking_id': picking_id,
                                              'picking_type_id':picking_type_id,
                                              'restrict_lot_id':lot_id,
                                          'product_id': product_id,
                                          'product_uom_qty': quantity+bigger_qty,
                                          'product_uos_qty': quantity+bigger_qty,
                                          'product_uom':product_uom,
                                          'location_id':location_id,
                                          'location_dest_id':from_location_id,
                                          'name':name,
                                           'origin':origin,
                                          'state':'confirmed'}, context=context)     
                    move_obj.action_done(cr, uid, move_id, context=context)  
        return self.write(cr, uid, ids, {'state': 'issue'})  
                            
class good_issue_line(osv.osv):  # #prod_pricelist_update_line
    _name = 'good.issue.note.line'
    _description = 'Note Line'

    def on_change_product_id(self, cr, uid, ids, product_id, context=None):
        values = {}
        if product_id:
            product = self.pool.get('product.product').browse(cr, uid, product_id, context=context)
            values = {
                      'big_uom_id':product.product_tmpl_id.uom_id and product.product_tmpl_id.uom_id.id or False,
                'product_uom': product.product_tmpl_id.uom_id and product.product_tmpl_id.uom_id.id or False,
                'uom_ratio': product.product_tmpl_id.uom_ratio,
            }
        return {'value': values}
    
    def on_change_expired_date(self, cr, uid, ids, batch_no, context=None):
        values = {}
        if batch_no:
            lot_obj = self.pool.get('stock.production.lot').browse(cr, uid, batch_no, context=context)
            values = {
                'expiry_date': lot_obj.life_date,
            }
        return {'value': values}    
        
    _columns = {                
        'line_id':fields.many2one('good.issue.note', 'Line', ondelete='cascade', select=True),
        'product_id': fields.many2one('product.product', 'Product', required=True),
        'issue_quantity' : fields.float(string='Qty', digits=(16, 0)),
        'product_uom': fields.many2one('product.uom', 'Smaller UoM', required=True,readonly=True),
                'uom_ratio':fields.char('Packing Unit'),
                'batch_no':fields.many2one('stock.production.lot','Batch No'),
                'expiry_date':fields.date('Expiry'),
                 'remark':fields.char('Remark'),
        'big_uom_id': fields.many2one('product.uom', 'Bigger UoM', required=True,readonly=True, help="Default Unit of Measure used for all stock operation."),
        'big_issue_quantity' : fields.float(string='Qty', digits=(16, 0)),               
         'qty_on_hand':fields.float(string='Qty On Hand', digits=(16, 0),readonly=True),
        'sequence':fields.integer('Sequence'),

    }
        
   
    
