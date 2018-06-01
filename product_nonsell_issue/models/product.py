from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.exceptions import except_orm, Warning, RedirectWarning

class product_nonsell_issue(osv.osv):

    _name = "product.nonsell.issue"    
    
    def _get_default_branch(self, cr, uid, context=None):
        branch_id = self.pool.get('res.users')._get_branch(cr, uid, context=context)
        if not branch_id:
            raise osv.except_osv(_('Error!'), _('There is no default branch for the current user!'))
        return branch_id        
    _columns = {
        'name': fields.char('Ref ID', readonly=True),
        'date': fields.date('Request Date',required=True),
        'user_id': fields.many2one('res.partner', 'Receiver',required=True),
        'branch_id': fields.many2one('res.branch', 'Branch',required=True),
        'warehouse_id': fields.many2one('stock.warehouse', 'Issue Warehouse',required=True),
        'location_id': fields.many2one('stock.location', 'Issue Location',required=True),
        'product_lines': fields.one2many('product.nonsell.issue.line', 'line_id', 'Items Lines', copy=True),
         'is_claim_attachment': fields.boolean('Is Claim Attachment'),
         'claim_attachment':fields.char('Related Credit Note Attachment'),
         'issue_type':fields.selection([
            ('donation', 'Donation'),
            ('sampling', 'Sampling'),
            ('other', 'Others'),
            ], 'Issue Type'),
          'is_claim': fields.boolean('Is Claim?'),
          'principle_id': fields.many2one('product.maingroup', 'Principle'),
          'principle_support': fields.float('Principle Support'),
          'picking_id': fields.many2one('stock.picking', 'Do Ref No',readonly=True),
         'debit_note':fields.char('Debit Note Ref No'),
         'receive_date': fields.date('Receive Date',required=True),
        'journal_id': fields.many2one('account.journal', 'Journal',required=True),
        'pricelist_id': fields.many2one('product.pricelist', 'Price list',required=True),
        'note': fields.text('Remark'),
         'state': fields.selection([
            ('draft', 'Draft'),
            ('approve', 'Awaiting Claimed'),
            ('cancel', 'Cancel'),
            ('done', 'Done'),
            ], 'Status', readonly=True, copy=False, help="Gives the status of the quotation or sales order.\
              \nThe exception status is automatically set when a cancel operation occurs \
              in the invoice validation (Invoice Exception) or in the picking list process (Shipping Exception).\nThe 'Waiting Schedule' status is set when the invoice is confirmed\
               but waiting for the scheduler to run on the order date.", select=True),
    }
    _defaults = {        
         'date':fields.datetime.now,
          'user_id':lambda obj, cr, uid, context: uid,
          'issue_type':'donation',
        'branch_id': _get_default_branch,
        'state': 'draft',
        'receive_date':fields.datetime.now,
                  }    
    
    
    def create(self, cursor, user, vals, context=None):
        id_code = self.pool.get('ir.sequence').get(cursor, user,
                                                'product.nonsell.issue.code') or '/'
        vals['name'] = id_code

        return super(product_nonsell_issue, self).create(cursor, user, vals, context=context)
    
    def approve(self, cr, uid, ids, context=None):
        sell_data=self.browse(cr, uid, ids, context=context)
        picking_obj=self.pool.get('stock.picking')
        move_obj=self.pool.get('stock.move')
        location_obj=self.pool.get('stock.location')
        product_line_obj=self.pool.get('product.nonsell.issue.line')
        location_id = sell_data.location_id.id
        warehouse_id = sell_data.warehouse_id.id
        origin = sell_data.name
        cr.execute('''select id from stock_picking_type where warehouse_id=%s and code ='outgoing' and default_location_src_id = %s''', (warehouse_id,location_id,))
        price_rec = cr.fetchone()
        if price_rec: 
            picking_type_id = price_rec[0] 
        else:
            raise osv.except_osv(_('Warning'),
                                 _('Picking Type has not for this transition'))
        picking_id = picking_obj.create(cr, uid, {
                                      'date': sell_data.receive_date,
                                      'origin':origin,
                                      'picking_type_id':picking_type_id}, context=context)
        product_line_ids = product_line_obj.search(cr, uid, [('line_id', '=', ids[0])], context=context)
        if product_line_ids and picking_id:
            for id in product_line_ids:
                line_value = product_line_obj.browse(cr, uid, id, context=context)
                product_id = line_value.product_id.id
                name = line_value.product_id.name_template
                product_uom = line_value.uom_id.id
                origin = origin
                quantity = line_value.quantity
                if  sell_data.issue_type=='donation':
                    from_location_id=location_obj.search(cr, uid, [('name', '=','Donation')], context=context)
                if  sell_data.issue_type=='sampling':
                    from_location_id=location_obj.search(cr, uid, [('name', '=','Sampling')], context=context)                
                if  sell_data.issue_type=='other':
                    from_location_id=location_obj.search(cr, uid, [('name', '=','Other Uses Location')], context=context)                 
                move_id=move_obj.create(cr, uid, {'picking_id': picking_id,
                                       'picking_type_id':picking_type_id,
                                      'product_id': product_id,
                                      'product_uom_qty': quantity,
                                      'product_uos_qty': quantity,
                                      'product_uom':product_uom,
                                      'location_id':location_id,
                                      'location_dest_id':from_location_id,
                                      'name':name,
                                       'origin':origin,
                                      'state':'confirmed'}, context=context)     
                move_obj.action_done(cr, uid, move_id, context=context)          
        return self.write(cr, uid, ids, {'state': 'approve'})    
    
    def submit(self, cr, uid, ids, context=None):
        
        return self.write(cr, uid, ids, {'state': 'done'})        
    
    def cancel(self, cr, uid, ids, context=None):
        
        return self.write(cr, uid, ids, {'state': 'cancel'})           
    
product_nonsell_issue()   

class product_nonsell_issue_line(osv.osv):

    _name = "product.nonsell.issue.line"    
    
    def _amount_total(self, cr, uid, ids, prop, arg, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            product_qty = line.quantity
            price_unit = line.price_unit
            total_price = price_unit * product_qty
            res[line.id] = total_price
        return res    
        
    _columns = {
        'line_id': fields.many2one('product.nonsell.issue', 'Master Data'),
        'product_id': fields.many2one('product.product', 'Product Name',required=True),
        'uom_id': fields.many2one('product.uom', 'UoM',required=True),
        'quantity': fields.float('Qty',required=True),
        'price_unit': fields.float('Unit Price',required=True),
        'sub_total':fields.function(_amount_total, string='Sub Total', store=True),
        'sequence':fields.integer('Sequence'),
    }
    
    def on_change_product_id(self, cr, uid, ids, product_id,pricelist_id, context=None):
        values = {}
        domain = {}
        if not pricelist_id:
            raise except_orm(_('No PriceList!'), _('Please Insert PriceList.'))        
        if product_id and pricelist_id:
            product = self.pool.get('product.product').browse(cr, uid, product_id, context=context)
            cr.execute("select new_price from product_pricelist_item where price_version_id in ( select id from product_pricelist_version where pricelist_id=%s) and product_id=%s and product_uom_id=%s",(pricelist_id,product.id,product.product_tmpl_id.uom_id.id,))
            product_price=cr.fetchone()[0]
            cr.execute("""SELECT uom.id FROM product_product pp 
                          LEFT JOIN product_template pt ON (pp.product_tmpl_id=pt.id)
                          LEFT JOIN product_template_product_uom_rel rel ON (rel.product_template_id=pt.id)
                          LEFT JOIN product_uom uom ON (rel.product_uom_id=uom.id)
                          WHERE pp.id = %s""", (product.id,))
            uom_list = cr.fetchall()
            print 'UOM-->>',uom_list            
            domain = {'uom_id':
                        [('id', 'in', uom_list)],}          
            values = {
                'uom_id': product.product_tmpl_id.uom_id and product.product_tmpl_id.uom_id.id or False,
                'sequence':product.sequence,
                'price_unit':product_price,
                'quantity':1,
                'sub_total':product_price * 1,
                
            }
        return {'value': values, 'domain': domain}

    def on_change_product_uom(self, cr, uid, ids, product_id,pricelist_id,uom_id,qty, context=None):
        values = {}
        if not pricelist_id:
            raise except_orm(_('No PriceList!'), _('Please Insert PriceList.'))        
        if product_id and pricelist_id:
            product = self.pool.get('product.product').browse(cr, uid, product_id, context=context)
            cr.execute("select new_price  from product_pricelist_item where price_version_id in ( select id from product_pricelist_version where pricelist_id=%s) and product_id=%s and product_uom_id=%s",(pricelist_id,product.id,uom_id,))
            product_price=cr.fetchone()[0]
            values = {
                'price_unit':product_price,
                'sub_total':product_price * qty,
                
            }
        return {'value': values}    
product_nonsell_issue_line()   

