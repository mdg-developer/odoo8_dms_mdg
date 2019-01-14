from openerp.osv import fields, osv
import time
from openerp.tools.translate import _
from openerp.exceptions import except_orm, Warning, RedirectWarning

class exchange_product(osv.osv):
    
    _name = "product.transactions"
    _description = "Exchange Product"
    _columns = {
                'name':fields.char('SEN No', readonly=True),
                'transaction_id':fields.char('ID', readonly=False),
                'customer_id':fields.many2one('res.partner', 'Customer Name'),
                'invoice_id':fields.many2one('account.invoice', 'Refund Invoice'),
                'customer_code':fields.char('Customer Code', readonly=True),
                'team_id'  : fields.many2one('crm.case.section', 'Sale Team', required=True),
                'date':fields.datetime('Date',required=True),
              'exchange_type':fields.selection([('Exchange', 'Exchange'), ('Sale Return', 'Sale Return'), ], 'Type',required=True),
                'item_line': fields.one2many('product.transactions.line', 'transaction_id', 'Items Lines', copy=True),
                'void_flag':fields.selection([('none', 'Unvoid'), ('voided', 'Voided')], 'Void Status'),
                'location_id': fields.many2one('stock.location', 'Location', required=True),
                'e_status':fields.char('Status'),
                'note':fields.text('Note'),
                'location_type':fields.selection([('Normal stock returned', 'Normal stock returned'), ('Expired', 'Expired'), ('Near expiry', 'Near expiry'), ('Fresh stock minor damage', 'Fresh stock minor damage'), ('Damaged', 'Damaged')], 'Location Type', required=True),
               # 'location_type':fields.char('Location Type', readonly=True),
                'partner_id':fields.many2one('res.partner', string='Partner'),
                'latitude':fields.float('Geo Latitude', digits=(14,15)),
                'longitude':fields.float('Geo Longitude', digits=(14,15)),
                'distance_status':fields.char('Distance Status'),
                'geo_point':fields.char('Geo Point'),
    }
    
    _defaults = {        
                 'e_status' : 'draft',
                 }
    def create(self, cursor, user, vals, context=None):
        id_code = self.pool.get('ir.sequence').get(cursor, user,
                                                'product.transactions.code') or '/'
        vals['name'] = id_code
        if vals.get('customer_id'):
            customer_id=vals['customer_id']
            if type(customer_id)==str:
                customer_id=int(customer_id)            
            defaults = self.onchange_customer_id(cursor, user, [], customer_id, context=context)['value']
            vals = dict(defaults, **vals)            
        return super(exchange_product, self).create(cursor, user, vals, context=context)    
    
    def onchange_customer_id(self, cr, uid, ids, customer_id, context=None):
        
        result = {}
        res_partner = self.pool.get('res.partner')
        datas = res_partner.read(cr, uid, customer_id, ['customer_code'], context=context)
        print 'datas', datas
        if datas:
            result.update({'customer_code':datas['customer_code']})            
        return {'value':result} 
    
    def onchange_team_id(self, cr, uid, ids, team_id, context=None):
        
        result = {}
        section = self.pool.get('crm.case.section')
        datas = section.read(cr, uid, team_id, ['location_id'], context=context)
        if datas:
            result.update({'location_id':datas['location_id']})            
        return {'value':result}     
    
    def onchange_location_type(self, cr, uid, ids, team_id, type, context=None):
        
        result = {}
        section = self.pool.get('crm.case.section')
        if team_id:
            sale_team_data = section.browse(cr, uid, team_id, context=context)
            if type == 'Normal stock returned':
                location_type_id = sale_team_data.normal_return_location_id.id
            elif type == 'Expired':
                location_type_id = sale_team_data.exp_location_id.id
            elif type == 'Near expiry':
                location_type_id = sale_team_data.near_exp_location_id.id
            elif type == 'Fresh stock minor damage':
                location_type_id = sale_team_data.fresh_stock_not_good_location_id.id
            elif type == 'Damaged':
                location_type_id = sale_team_data.damage_location_id.id            
            result.update({'location_id':location_type_id})            
        return {'value':result}     

    def action_create_invoice(self, cr, uid, ids, context=None):
        trans_obj=self.pool.get('product.transactions.line')
        invoice_line_obj = self.pool.get('account.invoice.line')
        invoice_obj = self.pool.get('account.invoice')
        journal_obj = self.pool.get('account.journal')
        payment_obj = self.pool.get('account.payment.term')   
        currency_obj = self.pool.get('res.currency')           
        return_data = self.browse(cr, uid, ids, context=context)
        name = return_data.name
        note=return_data.note
        team_id=return_data.team_id.id
        journal_ids = journal_obj.search(cr, uid, [('code', '=', 'SCNJ')], context=context)
        journal_id=journal_obj.browse(cr, uid, journal_ids, context=context).id
        partner_id = return_data.customer_id.id
        pricelist_id= return_data.customer_id.property_product_pricelist.id
        payment_id = payment_obj.search(cr, uid, [('name', '=', 'Immediate Payment')], context=context)
        currency_id = currency_obj.search(cr, uid, [('name', '=', 'MMK')], context=context)
        inv = {
            'name': name,
            'origin': name,
            'type': 'out_refund',
            'journal_id': journal_id,
            'reference': name,
            'partner_id': partner_id,
            'currency_id': currency_id[0],
            'comment': note,
            'payment_term': payment_id[0],
            'section_id':team_id,
             'user_id':uid,
            'fiscal_position': return_data.customer_id.property_account_position.id
        }
        inv_id = invoice_obj.create(cr, uid, inv, context=context)
        for line_id in return_data.item_line:
            product_line_ids = trans_obj.browse(cr, uid, line_id.id, context=context)
            product_id=product_line_ids.product_id.id
            product_name =product_line_ids.product_id.name_template
            uom_id=product_line_ids.uom_id.id
            product_qty=product_line_ids.product_qty
            if not pricelist_id:
                raise except_orm(_('No PriceList!'), _('Please Insert PriceList.'))        
            product = self.pool.get('product.product').browse(cr, uid, product_id, context=context)
            cr.execute("select new_price from product_pricelist_item where price_version_id in ( select id from product_pricelist_version where pricelist_id=%s) and product_id=%s and product_uom_id=%s", (pricelist_id, product.id,uom_id,))
            product_price = cr.fetchone()
            if not product_price:
                raise except_orm(_('No PriceList!'), _('Please Insert PriceList.'))    
                        
            if product_price and inv_id:
                inv_line = {'name': product_name,
                            'invoice_id':inv_id,
                    'account_id': product_line_ids.product_id.product_tmpl_id.categ_id.property_account_income_categ.id,
                    'price_unit': product_price[0],
                    'quantity': product_qty,
                    'product_id': product_id,
                    'uos_id': uom_id,
                    'agreed_price': 0.0,
                    'gross_margin':0.0,
                    'line_paid':False,
                    }
                invoice_line_obj.create(cr, uid, inv_line, context=context)        
        
        return self.write(cr, uid, ids, {'e_status':'complete','invoice_id':inv_id})          

    
    def action_convert_ep(self, cr, uid, ids, context=None):
        product_line_obj = self.pool.get('product.transactions.line')
        product_obj = self.pool.get('product.transactions')
        move_obj = self.pool.get('stock.move')
        if ids:
            product_value = product_obj.browse(cr, uid, ids[0], context=context)
            if product_value.void_flag=='none':
                location_id = product_value.customer_id.property_stock_customer.id
                payment_type = product_value.location_type
                if payment_type == 'Normal stock returned':
                    from_location_id = product_value.team_id.normal_return_location_id.id
                elif payment_type == 'Expired':
                    from_location_id = product_value.team_id.exp_location_id.id
                elif payment_type == 'Near expiry':
                    from_location_id = product_value.team_id.near_exp_location_id.id
                elif payment_type == 'Fresh stock minor damage':
                    from_location_id = product_value.team_id.fresh_stock_not_good_location_id.id
                elif payment_type == 'Damaged':
                    from_location_id = product_value.team_id.damage_location_id.id            
                
                # from_location_id = product_value.team_id.return_location_id.id
                car_location_id = product_value.team_id.location_id.id
                origin = product_value.transaction_id
                product_line_id = product_line_obj.search(cr, uid, [('transaction_id', '=', ids[0])], context=context)
                if product_line_id:
                    for line_id in product_line_id:
                        product_line_value = product_line_obj.browse(cr, uid, line_id, context=context)
                        product_id = product_line_value.product_id.id
                        name = product_line_value.product_id.name_template
                        product_uom = product_line_value.uom_id.id
                        origin = origin
                        quantity = product_line_value.product_qty
                        trans_type = product_line_value.trans_type
                        if trans_type == 'In':
                            move_id = move_obj.create(cr, uid, {
                                                  'product_id': product_id,
                                                  'product_uom_qty': quantity,
                                                  'product_uos_qty': quantity,
                                                  'product_uom':product_uom,
                                                  'is_exchange':True,
                                                  'location_id':location_id,
                                                  'location_dest_id':from_location_id,
                                                  'name':name,
                                                   'origin':origin,
                                                  'state':'confirmed'}, context=context)     
                        if trans_type == 'Out'  :
                            move_id = move_obj.create(cr, uid, {
                                                  'product_id': product_id,
                                                  'product_uom_qty': quantity,
                                                  'product_uos_qty': quantity,
                                                  'product_uom':product_uom,
                                                     'is_exchange':True,
                                                  'location_id':car_location_id,
                                                  'location_dest_id':location_id,
                                                  'name':name,
                                                   'origin':origin,
                                                  'state':'confirmed'}, context=context)     
                        move_obj.action_done(cr, uid, move_id, context=context)                            
                return self.write(cr, uid, ids, {'e_status':'done'})          
            
            
                     
#     def action_convert_ep(self, cr, uid, ids, context=None):
#         product_line_obj = self.pool.get('product.transactions.line')
#         product_obj = self.pool.get('product.transactions')
#         picking_obj = self.pool.get('stock.picking')
#         move_obj = self.pool.get('stock.move')
#         if ids:
#             product_value = product_obj.browse(cr, uid, ids[0], context=context)
#             issue_date = product_value.date
#             location_id = product_value.customer_id.property_stock_customer.id
#             from_location_id = product_value.team_id.location_id.id
#             origin = product_value.transaction_id
#             cr.execute('select id from stock_picking_type where default_location_dest_id=%s and default_location_src_id = %s', (location_id, from_location_id,))
#             price_rec = cr.fetchone()
#             if price_rec: 
#                 picking_type_id = price_rec[0] 
#             else:
#                 raise osv.except_osv(_('Warning'),
#                                      _('Picking Type has not for this transition'))
#             picking_id = picking_obj.create(cr, uid, {
#                                           'date': issue_date,
#                                           'origin':origin,
#                                           'picking_type_id':picking_type_id}, context=context)
#             product_line_id = product_line_obj.search(cr, uid, [('transaction_id', '=', ids[0])], context=context)
#             if product_line_id and picking_id:
#                 for line_id in product_line_id:
#                     product_line_value = product_line_obj.browse(cr, uid, line_id, context=context)
#                     product_id = product_line_value.product_id.id
#                     name = product_line_value.product_id.name_template
#                     product_uom = product_line_value.uom_id.id
#                     origin = origin
#                     quantity = product_line_value.product_qty
#                     trans_type=product_line_value.trans_type
#                     if trans_type == 'In':
#                         move_id=move_obj.create(cr, uid, {'picking_id': picking_id,
#                                              'picking_type_id':picking_type_id,
#                                               'product_id': product_id,
#                                               'product_uom_qty': quantity,
#                                               'product_uos_qty': quantity,
#                                               'product_uom':product_uom,
#                                               'location_id':location_id,
#                                               'location_dest_id':from_location_id,
#                                               'name':name,
#                                                'origin':origin,
#                                               'state':'confirmed'}, context=context)     
#                     else:
#                         move_id=move_obj.create(cr, uid, {'picking_id': picking_id,
#                                              'picking_type_id':picking_type_id,
#                                               'product_id': product_id,
#                                               'product_uom_qty': quantity,
#                                               'product_uos_qty': quantity,
#                                               'product_uom':product_uom,
#                                               'location_id':from_location_id,
#                                               'location_dest_id':location_id,
#                                               'name':name,
#                                                'origin':origin,
#                                               'state':'confirmed'}, context=context)     
#                     move_obj.action_done(cr, uid, move_id, context=context)                            
#                 return self.write(cr, uid, ids, {'e_status':'done'}) 
exchange_product()

class exchange_product_line_item(osv.osv):
    
    _name = "product.transactions.line"
    _description = "Exchange Product"

    _columns = {
                'transaction_id': fields.many2one('product.transactions', 'Form,'),
                'product_id':fields.many2one('product.product', 'Product'),
                'uom_id': fields.many2one('product.uom', 'UOM', required=True, help="Default Unit of Measure used for all stock operation."),
                'product_qty':fields.integer('Qty'),
                'so_No':fields.char('SO Reference'),
                'trans_type':fields.selection([('In', 'In'), ('Out', 'Out')], 'Type', required=True),
                'transaction_name':fields.char('Transaction Name'),
                'note':fields.char('Note'),
                'exp_date':fields.date('Expired Date'),
                'batchno':fields.char('Batch No'),
                }

    def onchange_product_id(self, cr, uid, ids, product_id, uom_id, context=None):
        """ Changes UoM and name if product_id changes.
        @param name: Name of the field
        @param product_id: Changed product_id
        @return:  Dictionary of changed values
        """
        # global prod_uom_ids
        prod_uom_ids = []
        value = {'uom_id': []}
        domain = {'uom_id': []}
        if product_id:
            prod = self.pool.get('product.product').browse(cr, uid, product_id, context=context)
            cr.execute("select product_uom_id from product_template_product_uom_rel where product_template_id=%s", (prod.product_tmpl_id.id,))
            prod_uom_ids = cr.fetchall()
            value = {'uom_id': prod_uom_ids}
            domain = {'uom_id': [('id', 'in', prod_uom_ids)]}
        return {'value': value, 'domain': domain}
    
        
exchange_product_line_item()
