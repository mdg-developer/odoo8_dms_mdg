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
                'competitor_product_lines': fields.one2many('partner.stock.check.competitor.line', 'stock_check_ids', string='Competitor Product'),
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
        competitor_line_obj = self.pool.get('partner.stock.check.competitor.line')
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
            cr.execute(
                """select cpp.id,cpp.sequence,(select product_uom_id as bigger_uom
                from
                (
                    select 1/factor ratio,product_uom_id
                    from competitor_product cp,competitor_product_product_uom_rel rel,product_uom uom
                    where cp.id=rel.competitor_product_id
                    and rel.product_uom_id=uom.id
                    and cp.id=cpp.id
                    and uom_type='bigger'
                )A
                order by ratio desc limit 1) 
                from competitor_product cpp 
                where cpp.id not in (select competitor_product_id from partner_stock_check_competitor_line where stock_check_ids =%s) 
                order by cpp.sequence asc""",
                (ids[0],))
            competitor_product_data = cr.fetchall()
            for cp_line in competitor_product_data:
                if cp_line:
                    competitor_product_id = cp_line[0]
                    cp_sequence = cp_line[1]
                    cp_uom = cp_line[2]
                    competitor_line_obj.create(cr, uid, {'stock_check_ids': ids[0],
                                                         'sequence': cp_sequence,
                                                         'competitor_product_id': competitor_product_id,
                                                         'product_uom': cp_uom,
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
                #'available': fields.boolean('Available', default=False),
                'available': fields.selection([('none', '-'),
                                               ('yes', 'Yes'),
                                               ('no', 'No')], string='Available', default='none'),                
                'product_uom_qty':fields.float('QTY'),
                'facing':fields.float('Facing', default=False),
                'chiller':fields.float('Chiller Qty'),
                'remark_id':fields.many2one('partner.stock.check.remark', 'Remark'),      
                'description':fields.char( 'Description'),
                'expiry_date':fields.date('Expiry Date'),
                          
                }


class customer_stock_check_competitor_line(osv.osv):
    _name = 'partner.stock.check.competitor.line'

    _columns = {
        'stock_check_ids': fields.many2one('partner.stock.check', 'Partner Stock Check Line'),
        'sequence': fields.integer('Sequence'),
        'competitor_product_id': fields.many2one('competitor.product', 'Product Name'),
        'product_uom': fields.many2one('product.uom', 'UOM'),
        'available': fields.selection([('none', '-'),
                                       ('yes', 'Yes'),
                                       ('no', 'No')], string='Available', default='none'),
        'product_uom_qty': fields.float('QTY'),
        'facing': fields.float('Facing', default=False),
        'chiller': fields.float('Chiller Qty'),
        'remark_id': fields.many2one('partner.stock.check.remark', 'Remark'),
        'description': fields.char('Description'),

    }


customer_stock_check_line()    

class customer_stock_check_remark(osv.osv):    
    _name = 'partner.stock.check.remark'      
    _columns = {
                        'name':fields.char('Name'),
                        'active':fields.boolean('Active', default=False),
                        'sequence':fields.integer('Sequence'),

        }