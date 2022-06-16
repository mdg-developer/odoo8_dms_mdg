from openerp.osv import fields , osv


class customer_stock_check(osv.osv):
    _name = "partner.stock.check"
    _description = "Customer Stock Check"
    _rec_name = "partner_id"
    _columns = {      
                'partner_id':fields.many2one('res.partner', 'Customer name'),
                'sale_team_id':fields.many2one('crm.case.section', 'Sales Team'),
                'user_id':fields.many2one('res.users', 'Sale Person'),
                'township_id':fields.many2one('res.township', 'Township'),
                'outlet_type': fields.many2one('outlettype.outlettype', 'Outlet Type'),
                'date': fields.date('Checked Date'),
                'check_datetime': fields.datetime('Checked Date Time'),
                'customer_code':fields.char('Customer Code'),
                'branch_id' :fields.many2one('res.branch', 'Branch'),
                'stock_check_line':fields.one2many('partner.stock.check.line', 'stock_check_ids', string='Product'),
                'latitude':fields.float('Geo Latitude', digits=(16, 5), readonly=True),
                    'longitude':fields.float('Geo Longitude', digits=(16, 5), readonly=True),
                    'distance_status':fields.char('Distance Status', readonly=True),
                }    
    
    def on_change_partner_id(self, cr, uid, ids, partner_id, context=None):
        values = {}
        if partner_id:
            partner = self.pool.get('res.partner').browse(cr, uid, partner_id, context=context)
            values = {
                'customer_code':partner.customer_code,
                'township_id':partner.township.id,
                'outlet_type':partner.outlet_type.id,
                'branch_id':partner.branch_id.id,
            }
        return {'value': values}
    
    def retrieve_stock(self, cr, uid, ids, context=None):  
        stock_line_obj = self.pool.get('partner.stock.check.line')
        if ids:
            stock_check_data = self.browse(cr, uid, ids[0], context=context) 
            sale_team_id = stock_check_data.sale_team_id.id
            sale_team = self.pool.get('crm.case.section').browse(cr, uid, sale_team_id, context=context)           
            product_line = sale_team.sale_group_id.product_ids   
            cr.execute ("delete from partner_stock_check_line where stock_check_ids =%s", (ids[0],))
            for p_line in product_line:
                if p_line:
                    stock_line_obj.create(cr, uid, {'stock_check_ids': ids[0],
                                        'sequence':p_line.sequence,
                                        'product_id': p_line.id,
                                        'product_uom': p_line.product_tmpl_id.uom_id.id,
                                        }, context=context)
        return True 


customer_stock_check()


class customer_stock_check_line(osv.osv):    
    _name = 'partner.stock.check.line'      
    
    _columns = {
                'stock_check_ids': fields.many2one('partner.stock.check', 'Partner Stock Check Line'),
                'sequence':fields.integer('Sequence'),
                'product_id':fields.many2one('product.product', 'Product'),
                'product_uom':fields.many2one('product.uom', 'UOM'),
                'available': fields.boolean('Available', default=False),
                'product_uom_qty':fields.float('QTY'),
                'facing':fields.float('Facing', default=False),
                'chiller':fields.float('Chiller Qty'),
                'remark_id':fields.many2one('partner.stock.check.remark', 'Remark'),      
                'description':fields.char( 'Description'),                
                          
                }


customer_stock_check_line()    

class customer_stock_check_remark(osv.osv):    
    _name = 'partner.stock.check.remark'      
    _columns = {
                        'name':fields.char('Name'),
                        'active':fields.boolean('Active', default=False),
                        'sequence':fields.integer('Sequence'),

        }