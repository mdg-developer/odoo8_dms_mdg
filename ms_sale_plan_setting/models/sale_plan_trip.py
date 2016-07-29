from openerp.osv import fields, osv

class sale_plan_for_trip_setup(osv.osv):
    _name = 'sale.plan.trip'
    _columns = {
                'sale_team':fields.many2one('crm.case.section', 'Sale Team', required=True),
                'principal':fields.many2one('product.principal', 'Principal'),
                 'day_customer_ids':fields.many2many('res.partner', 'res_partner_sale_plan_trip_rel', id1='sale_plan_trip_id', id2='partner_id', string='Day Customer'),
                 'trip_customer_ids':fields.many2many('res.partner', 'res_partner_sale_plan_trip_rel', id1='sale_plan_trip_id', id2='partner_id', string='Trip Customer'),
                'date':fields.date('Date', required=True),
                'name':fields.char('Trip Name', required=True),
                'main_group':fields.many2many('product.maingroup', 'product_maingroup_sale_plan_day_reltrip', id1='sale_plan_trip_id', id2='product_maingroup_id', string='Main Group'),
                # 'main_group':fields.many2one('product.maingroup',required = True),
                'active':fields.boolean('Active'),
               }
    _defaults = {
               'active':True
    }  
   
sale_plan_for_trip_setup()
