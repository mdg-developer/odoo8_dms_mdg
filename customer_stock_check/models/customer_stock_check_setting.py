from openerp.osv import fields , osv

class customer_stock_check(osv.osv):
    _name = "stock.check.setting"
    _description = "Customer Stock Check Setting"
    _rec_name = "name"
    _columns = {      
                'outlet_type': fields.many2one('outlettype.outlettype', 'Outlet Type'), 
                'date': fields.date('Checked Date'),   
                'stock_setting_line':fields.one2many('stock.check.setting.line', 'stock_setting_ids', string='Product',copy=True),
                'competitor_product_lines': fields.one2many('stock.check.setting.competitor.line', 'stock_setting_ids', string='Competitor Products', copy=True),
                'name': fields.char('Name'),
                'sale_group_id': fields.many2many('sales.group', 'stock_check_sale_group_rel', id1='stock_check_id',
                                                    id2='sale_group_id', string='Sale Group'),
                'is_show_specific_categ': fields.boolean(string='Is Show Specific Categ'),
    }
    def action_is_product_categ_show(self, cr, uid, ids, context=None):
        vals = {}
        is_show_specific_categ = True
        for rec in self.browse(cr, uid, ids, context=None):
            if rec.is_show_specific_categ == True:
                is_show_specific_categ = False
        vals.update({'is_show_specific_categ':is_show_specific_categ})
        return self.write(cr, uid, ids, vals)

    def retrieve_stock(self, cr, uid, ids, context=None):  
        stock_line_obj = self.pool.get('stock.check.setting.line')
        competitor_line_obj = self.pool.get('stock.check.setting.competitor.line')
        if ids:
            cr.execute("""select pp.id,pp.sequence from product_product pp,product_template pt
                where pp.product_tmpl_id = pt.id and pt.type!='service' and pt.is_foc !=True and pt.active='True'
                and pp.active='True' and pp.id not in (select product_id from stock_check_setting_line where stock_setting_ids =%s) order by pp.sequence asc""",(ids[0],))
            product_data = cr.fetchall()
            for p_line in product_data:
                if p_line:
                    product_id = p_line[0]
                    sequence = p_line[1]
                    stock_line_obj.create(cr, uid, {'stock_setting_ids': ids[0],
                                'sequence':sequence,
                                'product_id': product_id, 
                                }, context=context)
            cr.execute("""select id,sequence from competitor_product where id not in (select competitor_product_id from stock_check_setting_competitor_line where stock_setting_ids =%s) order by sequence asc""",(ids[0],))
            competitor_product_data = cr.fetchall()
            for cp_line in competitor_product_data:
                if cp_line:
                    competitor_product_id = cp_line[0]
                    cp_sequence = cp_line[1]
                    competitor_line_obj.create(cr, uid, {'stock_setting_ids': ids[0],
                                                         'sequence': cp_sequence,
                                                         'competitor_product_id': competitor_product_id,
                                                    }, context=context)
        return True 
customer_stock_check()

class customer_stock_check_line(osv.osv):    
    _name = 'stock.check.setting.line'      
    
    _columns = {
                'stock_setting_ids': fields.many2one('stock.check.setting', 'Partner Stock Check Setting'),
                'sequence':fields.integer('Sequence'),                 
                'product_id':fields.many2one('product.product', 'Product'),
                'available': fields.boolean('Available',default=False),
                'product_uom_qty':fields.boolean('QTY',default=False),
                'facing':fields.boolean('Facing',default=False),    
                'chiller':fields.boolean('Chiller',default=False),
                'expiry': fields.boolean('Expiry', default=False),
    }
customer_stock_check_line()

class stock_check_setting_competitor_line(osv.osv):
    _name = 'stock.check.setting.competitor.line'

    _columns = {
        'stock_setting_ids': fields.many2one('stock.check.setting', 'Partner Stock Check Setting'),
        'sequence': fields.integer('Sequence'),
        'competitor_product_id': fields.many2one('competitor.product', 'Product Name'),
        'available': fields.boolean('Available', default=False),
        'product_uom_qty': fields.boolean('QTY', default=False),
        'facing': fields.boolean('Facing', default=False),
        'chiller': fields.boolean('Chiller', default=False),
        'expiry': fields.boolean('Expiry', default=False),
    }

stock_check_setting_competitor_line()