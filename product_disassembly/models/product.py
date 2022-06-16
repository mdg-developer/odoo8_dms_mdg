from openerp.osv import fields, osv
from openerp.tools.translate import _

class product_disassembly(osv.osv):

    _name = "product.disassembly"    
        
    _columns = {
        'name': fields.char('PDS Ref', readonly=True),
        'date': fields.date('Date'),
        'create_date': fields.datetime('Create Date'),
        'location_id': fields.many2one('stock.location', 'Location'),
        'section_id': fields.many2one('crm.case.section', 'Sales Team', readonly=False),
        'user_id': fields.many2one('res.users', 'Person', readonly=False),
        'product_lines': fields.one2many('product.disassembly.line', 'line_id', 'Items Lines', copy=True),
         'is_disassembly': fields.boolean('Disassembly')
    }
    _defaults = {        
         'date':fields.datetime.now,
         'create_date':fields.datetime.now,
         'is_disassembly':False,
          'user_id':lambda obj, cr, uid, context: uid
                  }    
    
    
    def create(self, cursor, user, vals, context=None):
        id_code = self.pool.get('ir.sequence').get(cursor, user,
                                                'product.disassembly.code') or '/'
        vals['name'] = id_code

        return super(product_disassembly, self).create(cursor, user, vals, context=context)
        
    def product_disassembly(self, cr, uid, ids, context=None):
        move_obj = self.pool.get('stock.move')     
        location_obj = self.pool.get('stock.location')     
        disassembly_data = self.browse(cr, uid, ids, context=context)    
        team_location_id = disassembly_data.location_id.id
        production_location_id = location_obj.search(cr, uid, [('name', '=', 'Production')])[0]
        print 'production_location_id', production_location_id
        for line_id in disassembly_data.product_lines:
            move_id = move_obj.create(cr, uid, {
                                          'product_id': line_id.product_id.id,
                                          'product_uom_qty':line_id.big_quantity ,
                                          'product_uos_qty':line_id.big_quantity,
                                          'product_uom':line_id.big_uom_id.id,
                                          'location_id':team_location_id,
                                          'location_dest_id':production_location_id,
                                          'name':line_id.product_id.name_template,
                                           'origin':disassembly_data.name,
                                          'state':'confirmed'}, context=context)     
            move_obj.action_done(cr, uid, move_id, context=context)
            s_move_id = move_obj.create(cr, uid, {
                                          'product_id': line_id.to_product_id.id,
                                          'product_uom_qty':line_id.quantity ,
                                          'product_uos_qty':line_id.quantity,
                                          'product_uom':line_id.uom_id.id,
                                          'location_id':production_location_id,
                                          'location_dest_id':team_location_id,
                                          'name':line_id.to_product_id.name_template,
                                           'origin':disassembly_data.name,
                                          'state':'confirmed'}, context=context)     
            move_obj.action_done(cr, uid, s_move_id, context=context)            
        return self.write(cr, uid, ids, {'is_disassembly':True})              
product_disassembly()   

class product_disassembly_line(osv.osv):

    _name = "product.disassembly.line"    
    _columns = {
        'line_id': fields.many2one('product.disassembly', 'Master Data'),
        'product_id': fields.many2one('product.product', 'Big Product Name'),
        'big_uom_id': fields.many2one('product.uom', 'UoM'),
        'big_quantity': fields.float('Qty'),
        'to_product_id': fields.many2one('product.product', 'To Product'),
        'uom_id': fields.many2one('product.uom', 'UoM'),
        'quantity': fields.float('To Qty'),
        'sequence':fields.integer('Sequence'),
    }
    
    def on_change_product_id(self, cr, uid, ids, product_id, context=None):
        values = {}
        if product_id:
            product = self.pool.get('product.product').browse(cr, uid, product_id, context=context)
            cr.execute("select mb.product_id,mb.product_qty,mb.product_uom,mbl.product_qty as m_qty from mrp_bom mb ,mrp_bom_line mbl where mb.id=mbl.bom_id and mbl.product_id=%s", (product.id,))
            mo_data = cr.fetchone()
            values = {
                'big_uom_id': product.product_tmpl_id.uom_id and product.product_tmpl_id.uom_id.id or False,
                'sequence':product.sequence,
                'to_product_id':mo_data[0],
                'uom_id':mo_data[2],
                'quantity':mo_data[1],
                'big_quantity': mo_data[3],
            }
        return {'value': values}
    
    def on_change_product_qty(self, cr, uid, ids, product_id, big_quantity, quantity, context=None):
        values = {}
        if big_quantity:
            product = self.pool.get('product.product').browse(cr, uid, product_id, context=context)
            cr.execute("select mb.product_qty from mrp_bom mb ,mrp_bom_line mbl where mb.id=mbl.bom_id and mbl.product_id=%s", (product.id,))
            mo_qty = cr.fetchone()[0]            
            total_qty = big_quantity * mo_qty
            values = {
                'quantity':total_qty,
            }
        return {'value': values}    
product_disassembly()   

