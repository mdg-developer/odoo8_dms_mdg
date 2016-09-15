from openerp.osv import fields, osv
   
class sale_plan_for_trip_setting(osv.osv):
    _name = 'sale.plan.trip.setting'
    
    def on_change_sale_team_id(self, cr, uid, ids, sale_team_id, context=None):
        customer_obj = self.pool.get('res.partner')
        values = {}
        data_line = []
        if sale_team_id:            
            partner_ids = customer_obj.search(cr, uid, [('section_id', '=', sale_team_id)], context=context)
            if  partner_ids:                
                for line in partner_ids:
                    partner = customer_obj.browse(cr, uid, line, context=context)
                    data_line.append({
                                        'code':partner.customer_code,
                                         'class':partner.class_id.id,
                                        'partner_id': line,
                                        'frequency':partner.frequency_id.id,
                                                  })
            values = {
                'plan_line': data_line,
            }
        return {'value': values}    
    
    def get_partner_count(self, cr, uid, ids, field, arg, context=None):
        
        res = {}
        for data in self.browse(cr, uid, ids, context=context):
            res[data.id] = len(data.plan_line)
            print 'res',res
        return res             
        
    def day_1_count(self, cr, uid, ids, field, arg, context=None):
        setting_line_obj = self.pool.get('sale.plan.trip.setting.line')
        res = {}
        for data in self.browse(cr, uid, ids, context=context):
            line_ids = setting_line_obj.search(cr, uid, [('line_id', '=', data.id), ('day_1', '=', True)], context=context)
            if line_ids:
                res[data.id] = len(line_ids)
        return res        
    
    def day_2_count(self, cr, uid, ids, field, arg, context=None):
        setting_line_obj = self.pool.get('sale.plan.trip.setting.line')
        res = {}
        for data in self.browse(cr, uid, ids, context=context):
            line_ids = setting_line_obj.search(cr, uid, [('line_id', '=', data.id), ('day_2', '=', True)], context=context)
            if line_ids:
                res[data.id] = len(line_ids)
        return res   
    def day_3_count(self, cr, uid, ids, field, arg, context=None):
        setting_line_obj = self.pool.get('sale.plan.trip.setting.line')
        res = {}
        for data in self.browse(cr, uid, ids, context=context):
            line_ids = setting_line_obj.search(cr, uid, [('line_id', '=', data.id), ('day_3', '=', True)], context=context)
            if line_ids:
                res[data.id] = len(line_ids)
        return res   
    def day_4_count(self, cr, uid, ids, field, arg, context=None):
        setting_line_obj = self.pool.get('sale.plan.trip.setting.line')
        res = {}
        for data in self.browse(cr, uid, ids, context=context):
            line_ids = setting_line_obj.search(cr, uid, [('line_id', '=', data.id), ('day_4', '=', True)], context=context)
            if line_ids:
                res[data.id] = len(line_ids)
        return res   
    def day_5_count(self, cr, uid, ids, field, arg, context=None):
        setting_line_obj = self.pool.get('sale.plan.trip.setting.line')
        res = {}
        for data in self.browse(cr, uid, ids, context=context):
            line_ids = setting_line_obj.search(cr, uid, [('line_id', '=', data.id), ('day_5', '=', True)], context=context)
            if line_ids:
                res[data.id] = len(line_ids)
        return res   
    def day_6_count(self, cr, uid, ids, field, arg, context=None):
        setting_line_obj = self.pool.get('sale.plan.trip.setting.line')
        res = {}
        for data in self.browse(cr, uid, ids, context=context):
            line_ids = setting_line_obj.search(cr, uid, [('line_id', '=', data.id), ('day_6', '=', True)], context=context)
            if line_ids:
                res[data.id] = len(line_ids)
        return res   
    def day_7_count(self, cr, uid, ids, field, arg, context=None):
        setting_line_obj = self.pool.get('sale.plan.trip.setting.line')
        res = {}
        for data in self.browse(cr, uid, ids, context=context):
            line_ids = setting_line_obj.search(cr, uid, [('line_id', '=', data.id), ('day_7', '=', True)], context=context)
            if line_ids:
                res[data.id] = len(line_ids)
        return res   
    def day_8_count(self, cr, uid, ids, field, arg, context=None):
        setting_line_obj = self.pool.get('sale.plan.trip.setting.line')
        res = {}
        for data in self.browse(cr, uid, ids, context=context):
            line_ids = setting_line_obj.search(cr, uid, [('line_id', '=', data.id), ('day_8', '=', True)], context=context)
            if line_ids:
                res[data.id] = len(line_ids)
        return res   
    def day_9_count(self, cr, uid, ids, field, arg, context=None):
        setting_line_obj = self.pool.get('sale.plan.trip.setting.line')
        res = {}
        for data in self.browse(cr, uid, ids, context=context):
            line_ids = setting_line_obj.search(cr, uid, [('line_id', '=', data.id), ('day_9', '=', True)], context=context)
            if line_ids:
                res[data.id] = len(line_ids)
        return res   
    def day_10_count(self, cr, uid, ids, field, arg, context=None):
        setting_line_obj = self.pool.get('sale.plan.trip.setting.line')
        res = {}
        for data in self.browse(cr, uid, ids, context=context):
            line_ids = setting_line_obj.search(cr, uid, [('line_id', '=', data.id), ('day_10', '=', True)], context=context)
            if line_ids:
                res[data.id] = len(line_ids)
        return res   
    def day_11_count(self, cr, uid, ids, field, arg, context=None):
        setting_line_obj = self.pool.get('sale.plan.trip.setting.line')
        res = {}
        for data in self.browse(cr, uid, ids, context=context):
            line_ids = setting_line_obj.search(cr, uid, [('line_id', '=', data.id), ('day_11', '=', True)], context=context)
            if line_ids:
                res[data.id] = len(line_ids)
        return res   
    def day_12_count(self, cr, uid, ids, field, arg, context=None):
        setting_line_obj = self.pool.get('sale.plan.trip.setting.line')
        res = {}
        for data in self.browse(cr, uid, ids, context=context):
            line_ids = setting_line_obj.search(cr, uid, [('line_id', '=', data.id), ('day_12', '=', True)], context=context)
            if line_ids:
                res[data.id] = len(line_ids)
        return res   
    def day_13_count(self, cr, uid, ids, field, arg, context=None):
        setting_line_obj = self.pool.get('sale.plan.trip.setting.line')
        res = {}
        for data in self.browse(cr, uid, ids, context=context):
            line_ids = setting_line_obj.search(cr, uid, [('line_id', '=', data.id), ('day_13', '=', True)], context=context)
            if line_ids:
                res[data.id] = len(line_ids)
        return res   
    def day_14_count(self, cr, uid, ids, field, arg, context=None):
        setting_line_obj = self.pool.get('sale.plan.trip.setting.line')
        res = {}
        for data in self.browse(cr, uid, ids, context=context):
            line_ids = setting_line_obj.search(cr, uid, [('line_id', '=', data.id), ('day_14', '=', True)], context=context)
            if line_ids:
                res[data.id] = len(line_ids)
        return res   
    def day_15_count(self, cr, uid, ids, field, arg, context=None):
        setting_line_obj = self.pool.get('sale.plan.trip.setting.line')
        res = {}
        for data in self.browse(cr, uid, ids, context=context):
            line_ids = setting_line_obj.search(cr, uid, [('line_id', '=', data.id), ('day_15', '=', True)], context=context)
            if line_ids:
                res[data.id] = len(line_ids)
        return res   
    _columns = {
                'name': fields.char('Trip Name', required=True),
                'sale_team_id':fields.many2one('crm.case.section', 'Sale Team', required=True),
                 'date':fields.date('Apply Date', required=True),
                 'from_date':fields.date('From Date', required=True),
                 'to_date':fields.date('To Date', required=True),
                'state': fields.selection([
            ('draft', 'Pending'),
            ('confirm', 'Confirm'),
            ], 'Status', readonly=True, copy=False, help="Gives the status of the quotation or sales order.\
              \nThe exception status is automatically set when a cancel operation occurs \
              in the invoice validation (Invoice Exception) or in the picking list process (Shipping Exception).\nThe 'Waiting Schedule' status is set when the invoice is confirmed\
               but waiting for the scheduler to run on the order date.", select=True),
        'plan_line':fields.one2many('sale.plan.trip.setting.line', 'line_id', 'Plan Lines',
                              copy=True),
        'partner_count' : fields.function(get_partner_count, string='Customer Count', readonly=True, store=True, type='integer'),
                
        'day_count_1' : fields.function(day_1_count, string='Count', readonly=True, store=True, type='integer'),
        'day_count_2' : fields.function(day_2_count, string='Count', readonly=True, store=True, type='integer'),
        'day_count_3' : fields.function(day_3_count, string='Count', readonly=True, store=True, type='integer'),
        'day_count_4' : fields.function(day_4_count, string='Count', readonly=True, store=True, type='integer'),
        'day_count_5' : fields.function(day_5_count, string='Count', readonly=True, store=True, type='integer'),
        'day_count_6' : fields.function(day_6_count, string='Count', readonly=True, store=True, type='integer'),
        'day_count_7' : fields.function(day_7_count, string='Count', readonly=True, store=True, type='integer'),
        'day_count_8' : fields.function(day_8_count, string='Count', readonly=True, store=True, type='integer'),
        'day_count_9' : fields.function(day_9_count, string='Count', readonly=True, store=True, type='integer'),
        'day_count_10' : fields.function(day_10_count, string='Count', readonly=True, store=True, type='integer'),
        'day_count_11' : fields.function(day_11_count, string='Count', readonly=True, store=True, type='integer'),
        'day_count_12' : fields.function(day_12_count, string='Count', readonly=True, store=True, type='integer'),
        'day_count_13' : fields.function(day_13_count, string='Count', readonly=True, store=True, type='integer'),
        'day_count_14' : fields.function(day_14_count, string='Count', readonly=True, store=True, type='integer'),
        'day_count_15' : fields.function(day_15_count, string='Count', readonly=True, store=True, type='integer'),
        
                 }
    _defaults = {
               'state':'draft',
    }
    def confirm(self, cr, uid, ids, context=None):               
        return self.write(cr, uid, ids, {'state': 'confirm' })      
    
    def refresh(self, cr, uid, ids, context=None):
        # data_line=[]
#         res=[]
#         customer_obj=self.pool.get('res.partner')
#         plan = self.browse(cr, uid, ids, context=context)
#         customer_list=plan.plan_line.partner_id.id
#         sale_team_id=plan.sale_team_id.id
#         partner_ids = customer_obj.search(cr, uid, [('section_id', '=', sale_team_id),('id','not in',[customer_list])], context=context)
#         if  partner_ids:                
#                 for line in partner_ids:
#                     print ' line',line,ids
#                     partner = customer_obj.browse(cr, uid, line, context=context)
#                     plan_line={
#                                         'code':partner.customer_code,
#                                          'class':partner.class_id.id,
#                                         'partner_id': line,
#                                         'line_id':ids[0],
#                                                   }
#                     print 'data_line',plan_line
# 
#                     res.append(plan_line) 
        # print 'res',res
        return True   
sale_plan_for_trip_setting()
    
class sale_plan_setting_line(osv.osv):  # #prod_pricelist_update_line
    _name = 'sale.plan.trip.setting.line'
    _description = 'Plan Line'
        
    _columns = {                
        'line_id':fields.many2one('sale.plan.trip.setting', 'Line', ondelete='cascade', select=True),
        'code':fields.char('Code',readonly=True),
        'class':fields.many2one('sale.class', 'Class',readonly=True),
        'frequency':fields.many2one('plan.frequency', 'Freq',readonly=True),
        'partner_id': fields.many2one('res.partner', 'Customer',readonly=True),
        'purchase_date':fields.date('Last Purchase Date'),
        'day_1':fields.boolean('Day 1'),
        'day_2':fields.boolean('Day 2'),
        'day_3':fields.boolean('Day 3'),
        'day_4':fields.boolean('Day 4'),
        'day_5':fields.boolean('Day 5'),
        'day_6':fields.boolean('Day 6'),
        'day_7':fields.boolean('Day 7'),
        'day_8':fields.boolean('Day 8'),
        'day_9':fields.boolean('Day 9'),
        'day_10':fields.boolean('Day 10'),
        'day_11':fields.boolean('Day 11'),
        'day_12':fields.boolean('Day 12'),
        'day_13':fields.boolean('Day 13'),
        'day_14':fields.boolean('Day 14'),
        'day_15':fields.boolean('Day 15'),
 
    }
sale_plan_setting_line()  
