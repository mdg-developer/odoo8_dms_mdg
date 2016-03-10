from openerp.osv import fields, osv

class sale_plan_for_day_setup(osv.osv):
    _name = 'sale.plan.day'
    _columns = {
                'name': fields.char('Day Name', required=True),
                'sale_team':fields.many2one('crm.case.section', 'Sale Team', required=True),
                'principal':fields.many2one('product.principal', 'Principal', required=True),
            #    'day_customer_ids': fields.many2many('res.partner', id1='sale_plan_day_id', id2='partner_id', string='Partners'),
               
                 'day_customer_ids':fields.many2many('res.partner','res_partner_sale_plan_day_rel', id1='sale_plan_day_id', id2='partner_id', string='Day Customer'),
                 'trip_customer_ids':fields.many2many('res.partner','res_partner_sale_plan_day_rel', id1='sale_plan_day_id', id2='partner_id', string='Trip Customer'),
                 'date':fields.date('Date', required=True),
                 'main_group':fields.many2many('product.maingroup', 'product_maingroup_sale_plan_day_rel',id1='sale_plan_day_id',id2='product_maingroup_id', string='Main Group'),
                 # 'branch_id' :fields.many2one('sale.branch'),
                 'active':fields.boolean('Active'),
               }
    _defaults = {
               'active':True
    }  
sale_plan_for_day_setup()


