from openerp.osv import fields,osv

class sale_target(osv.osv):
    
    _name = "sale.target"
    _description = "Sales Targets"

    _columns = {
                  
                    'name':fields.char('Name'),
                    'outlet_target':fields.integer('New Outlet Target'),
                     'day_name':fields.many2one('sale.plan.day', 'Day Name'),
                    'date':fields.date('Creation Date'),
                    'sale_team':fields.many2one('crm.case.section', 'Sale Team'),
                    'note':fields.text('Notes'),
                     'week':fields.many2one('setting.week', 'Week'),
                   'target_type': fields.selection([
                            ('product', 'Products')
                        ], 'Target Type'),
                   'schedule': fields.selection([
                            ('daily', 'Daily'),
                            ('weekly', 'Weekly')
                        ], 'Schedule Type'),
                        'product_target_line': fields.one2many('sale.target.line', 'target_id', 'Product Targets Lines', copy=True),
                         'category_target_line': fields.one2many('sale.target.line', 'target_id', 'Category Targets Lines', copy=True),
                         'category_id':fields.many2one('product.category', 'Category'),
                         'categ_target_qty':fields.integer('Category Target Qty'),
                         'categ_target_amt':fields.float('Category Target Amount'),
                         'total_shop_to_visit':fields.integer('Shops To Visit'),

                }
    
    def on_change_day_name(self, cr, uid, ids, day_name, context=None):
        if not day_name:
            return {}
        cr.execute("""select count(*)  from sale_plan_day SPD ,
                                            res_partner_sale_plan_day_rel RPS , res_partner RP 
                                            where SPD.id = RPS.sale_plan_day_id 
                                            and RPS.res_partner_id = RP.id 
                                            and SPD.id = %s""", (day_name,))
        datas = cr.fetchone()
        return {'value': {'total_shop_to_visit': datas[0]}
                    }
sale_target()

class sale_target_line(osv.osv):
    
    _name = "sale.target.line"
    _description = "Sales Targets"

    _columns = {    'target_id':fields.many2one('sale.target', 'Target Lines'),
                    'product_id':fields.many2one('product.product', 'Product'),
                    'category_id':fields.many2one('product.category', 'Category'),
                    'target_amt':fields.float('Target Amount'),
                    'target_qty':fields.integer('Target Quantity'),
                    'date':fields.date('Date'),
                  
                }
   
sale_target_line()