from openerp.osv import fields, osv

class sale_plan_for_day_setup(osv.osv):
    _name = 'sale.plan.day'
    _columns = {
                'name': fields.char('Day Name', required=True),
                'sale_team':fields.many2one('crm.case.section', 'Sale Team', required=True),
            #    'day_customer_ids': fields.many2many('res.partner', id1='sale_plan_day_id', id2='partner_id', string='Partners'),               
                 'day_customer_ids':fields.many2many('res.partner', 'res_partner_sale_plan_day_rel', id1='sale_plan_day_id', id2='partner_id', string='Day Customer'),
                 'trip_customer_ids':fields.many2many('res.partner', 'res_partner_sale_plan_day_rel', id1='sale_plan_day_id', id2='partner_id', string='Trip Customer'),
                 'date':fields.date('Date'),
                'principal':fields.many2one('product.principal', 'Principal'),
                 'main_group':fields.many2many('product.maingroup', 'product_maingroup_sale_plan_day_rel', id1='sale_plan_day_id', id2='product_maingroup_id', string='Main Group'),
                 'branch_id':fields.many2one('res.branch', 'Branch'),                
                 'active':fields.boolean('Active'),
                 'week':fields.integer('Week'),
                 'day_line_ids':fields.one2many('sale.plan.day.line', 'line_id', 'Sale Plan Day Items'),
                 'week_day': fields.selection([('1', 'monday'), ('2', 'Tuesday'), ('3', 'Wednesday'),('4', 'Thursday'),('5','Friday'),('6','Saturday'),('0','Sunday')], 'Day')                 
               }
    _defaults = {
               'active':True,
               
    }     

sale_plan_for_day_setup()

class sale_plan_day_line(osv.osv):
    _name = 'sale.plan.day.line'
    
    _columns = {                
                'line_id':fields.many2one('sale.plan.day', 'Sale Plan Day Items'),
                               
                'partner_id':fields.many2one('res.partner', 'Partner'),#               
                'sequence':fields.float('Sequence'),
                'outlet_type': fields.many2one('outlettype.outlettype',string="Outlet type"), 
                'address': fields.char(string='Address'),                  
                'township': fields.many2one('res.township',string="Township"),
                'branch_id': fields.many2one('res.branch',string="Branch"),
                'section_ids': fields.many2many('crm.case.section','sale_plan_day_team_rel','day_id','section_id',string="Sale Team"),
                'sales_channel' : fields.many2one('sale.channel',string="Sale Channel"),
                'frequency_id' : fields.many2one('plan.frequency',string="Frequency"),
                'class_id' : fields.many2one('sale.class',string="Class"),
                'delivery_team_id': fields.many2one('crm.case.section',string="Delivery Team"),
                }
    _defaults = {
               'sequence':1,
    }   
    
    def write(self, cr, uid, ids, vals, context=None):
        
        plan_day_seq_obj = self.pool.get('sale.plan.day.sequence')
        plan_setting = self.browse(cr, uid, ids, context=context)
        if vals.get('sequence'):
            plan_day = plan_day_seq_obj.search(cr, uid, [('sale_plan_day_id', '=', plan_setting.line_id.id), 
                                                         ('partner_id', '=', plan_setting.partner_id.id)], context=context)
            if plan_day:
                plan_day_obj = plan_day_seq_obj.browse(cr,uid,plan_day,context=context)                
                plan_day_obj.write({'sequence':vals.get('sequence')})
            else:
                result = {
                            'sale_plan_day_id': plan_setting.line_id.id,
                            'sequence': vals.get('sequence'),
                            'partner_id': plan_setting.partner_id.id,
                        }                                                     
                plan_day_seq_obj.create(cr, uid, result, context=context)   
        new_id = super(sale_plan_day_line, self).write(cr, uid, ids, vals, context=context)
        return new_id  
       
sale_plan_day_line()

class sale_plan_day_sequence(osv.osv):
    _name = 'sale.plan.day.sequence'
    
    _columns = {
                'sale_plan_day_id':fields.many2one('sale.plan.day', 'Sale Plan Day'),
                'sequence':fields.float('Sequence'),
                'partner_id':fields.many2one('res.partner', 'Customer'),
            }  

sale_plan_day_sequence()
