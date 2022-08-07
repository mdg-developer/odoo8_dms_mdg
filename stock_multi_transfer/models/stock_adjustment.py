from openerp.osv import fields, osv
from datetime import datetime
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _

class stock_adjustment(osv.osv):
    _name = "stock.transfer.adjustment"
    _description = "Stock Adjustment Transfer"
    
    _columns = {
            'name':fields.char('TxnID'),
            'branch_id':fields.many2one('res.branch', 'Branch',required=True),
            'from_location_id':fields.many2one('stock.location', 'Source Location',required=True),
            'to_location_id':fields.many2one('stock.location', 'To Location',required=True),
            'sale_team_id':fields.many2one('crm.case.section', 'Sale Team'),
            'date':fields.date('Date'),
            'state': fields.selection([
                                        ('draft', 'Draft'),
                                        ('cancel', 'Cancel'),                                       
                                        ('confirmed', 'Confirm'),                                                                              
                                        ], 'Status', readonly=True, copy=False, select=True),
            'adj_line':fields.one2many('stock.transfer.adjustment.line', 'line_id', 'Product Lines',
                              copy=True),
            'notes': fields.text('Note'),    
            }
    
    _defaults = {
        'state' : 'draft'        
         
    }     
    
    def create(self, cursor, user, vals, context=None):
        id_code = self.pool.get('ir.sequence').get(cursor, user,
                                                'stock.adjustment.code') or '/'
        vals['name'] = id_code
        return super(stock_adjustment, self).create(cursor, user, vals, context=context)
    
    def retrieve_data(self, cr, uid, ids, context=None):
        stock_transfer_obj = self.pool.get('stock.transfer.adjustment.line')
        transfer_data=self.browse(cr, uid, ids, context=context)
        location_id=transfer_data.from_location_id.id
        cr.execute('delete from stock_transfer_adjustment_line where line_id=%s', (ids[0],))
        cr.execute("select sum(qty),product_id from stock_quant where location_id=%s group by product_id",(location_id,))
        product_data=cr.fetchall()
        if product_data:                
            for val in product_data:
                product_qty=val[0]    
                product_id =val[1]   
                product = self.pool.get('product.product').browse(cr, uid, product_id, context=context)
                stock_transfer_obj.create(cr, uid, {'line_id': ids[0],
                               'sequence':product.sequence,
                              'product_id': product_id,
                              'current_qty':product_qty,
                              'transfer_qty':0,
                              'product_uom': product.product_tmpl_id.uom_id.id ,
                        }, context=context)    
    
    def cancel(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state':'cancel' })
    
    def confirmed(self, cr, uid, ids, context=None):
        product_line_obj = self.pool.get('stock.transfer.adjustment.line')
        note_obj = self.pool.get('stock.transfer.adjustment')
        picking_obj = self.pool.get('stock.picking')
        move_obj = self.pool.get('stock.move')
        note_value = req_lines = {}
        if ids:
            note_value = note_obj.browse(cr, uid, ids[0], context=context)
            issue_date = note_value.date
            location_id = note_value.to_location_id.id
            from_location_id = note_value.from_location_id.id
            origin = note_value.name    
            cr.execute('select id from stock_picking_type where default_location_dest_id=%s and name like %s', (from_location_id, '%Internal Transfer%',))
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
                    quantity = note_line_value.transfer_qty   
                    if quantity>0:                    
                        move_id=move_obj.create(cr, uid, {'picking_id': picking_id,
                                                  'picking_type_id':picking_type_id,
                                              'product_id': product_id,
                                              'product_uom_qty': quantity,
                                              'product_uos_qty': quantity,
                                              'product_uom':product_uom,
                                              'location_id':from_location_id,
                                              'location_dest_id':location_id,
                                              'name':name,
                                               'origin':origin,
                                              'state':'confirmed'}, context=context)     
                        move_obj.action_done(cr, uid, move_id, context=context)  
                    cr.execute('''update stock_move set date=((%s::date)::text || ' ' || date::time(0))::timestamp where state='done' and origin =%s''',(issue_date,origin,))

        return self.write(cr, uid, ids, {'state': 'confirmed'})                    
stock_adjustment()    

class stock_adjustment_line(osv.osv):
    _name = "stock.transfer.adjustment.line"
    _description = "Adjustment Transfer Line"
    
    def on_change_product_id(self, cr, uid, ids, product_id, context=None):
        product_obj = self.pool.get('product.product')
        uom_id=False
        if product_id:
            product_data = product_obj.browse(cr, uid, product_id, context=context)
            uom_id = product_data.uom_id.id    
        return {'value': {'product_uom': uom_id,'current_qty':0}}    

    def create(self, cr, uid, data, context=None):
        product=data['product_id']
        if product:
            if type(product)==str:
                product=int(product)
            product_data= self.pool.get('product.product').browse(cr, uid, product, context=context)
            uom_id=product_data.uom_id.id
            data['product_uom']=uom_id
        return super(stock_adjustment_line, self).create(cr, uid, data, context=context) 
            
    _columns = {
            'line_id':fields.many2one('stock.transfer.adjustment', 'Line', ondelete='cascade', select=True),
            'product_id': fields.many2one('product.product', 'Product', select=True, required=True),
            'product_uom': fields.many2one('product.uom', 'UOM',readonly=True),
            'current_qty': fields.float('Current Qty',readonly=True),    
            'transfer_qty': fields.float('Transfer Qty'), 
            'sequence':fields.integer('Sequence'),         
            }
     
stock_adjustment_line()
