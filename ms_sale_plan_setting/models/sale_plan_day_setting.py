from openerp.osv import fields, osv

class plan_frequency(osv.osv):
    _name = 'plan.frequency'
    _columns = {
              'name':fields.char('Name'),
              }
plan_frequency()    

class sale_plan_for_day_setting(osv.osv):
    _name = 'sale.plan.day.setting'
    
    def on_change_sale_team_id(self, cr, uid, ids, sale_team_id, context=None):
        customer_obj = self.pool.get('res.partner')
        values = {}
        data_line = []
        if sale_team_id:            
            partner_ids = customer_obj.search(cr, uid, [('section_id', '=', sale_team_id)], context=context)
            if  partner_ids:                
                for line in partner_ids:
                    print ' line', line
                    partner = customer_obj.browse(cr, uid, line, context=context)
                    data_line.append({
                                        'code':partner.customer_code,
                                         'class':partner.class_id.id,
                                         'frequency':partner.frequency_id.id,
                                        'partner_id': line,
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

    def w1_mon_count(self, cr, uid, ids, field, arg, context=None):
        
        setting_line_obj = self.pool.get('sale.plan.day.setting.line')
        print ' w1_mon_count'
        res = {}
        for data in self.browse(cr, uid, ids, context=context):

            line_ids = setting_line_obj.search(cr, uid, [('line_id', '=', data.id), ('w1_mon', '=', True)], context=context)
            if line_ids:
                res[data.id] = len(line_ids)
        return res
    
    def w1_tue_count(self, cr, uid, ids, field, arg, context=None):
        
        setting_line_obj = self.pool.get('sale.plan.day.setting.line')
        res = {}
        for data in self.browse(cr, uid, ids, context=context):
            line_ids = setting_line_obj.search(cr, uid, [('line_id', '=', data.id), ('w1_tue', '=', True)], context=context)
            print ' line_ids',line_ids
            if line_ids:
                res[data.id] = len(line_ids)
        return res        

    def w1_wed_count(self, cr, uid, ids, field, arg, context=None):
        
        setting_line_obj = self.pool.get('sale.plan.day.setting.line')
        res = {}
        for data in self.browse(cr, uid, ids, context=context):
            line_ids = setting_line_obj.search(cr, uid, [('line_id', '=', data.id), ('w1_wed', '=', True)], context=context)
            if line_ids:
                res[data.id] = len(line_ids)
        return res
    
    def w1_thur_count(self, cr, uid, ids, field, arg, context=None):
        setting_line_obj = self.pool.get('sale.plan.day.setting.line')
        res = {}
        for data in self.browse(cr, uid, ids, context=context):

            line_ids = setting_line_obj.search(cr, uid, [('line_id', '=', data.id), ('w1_thur', '=', True)], context=context)
            if line_ids:
                res[data.id] = len(line_ids)
        return res    
    
    def w1_fri_count(self, cr, uid, ids, field, arg, context=None):
        setting_line_obj = self.pool.get('sale.plan.day.setting.line')
        res = {}
        for data in self.browse(cr, uid, ids, context=context):

            line_ids = setting_line_obj.search(cr, uid, [('line_id', '=', data.id), ('w1_fri', '=', True)], context=context)
            if line_ids:
                res[data.id] = len(line_ids)
        return res    
    
    def w1_sat_count(self, cr, uid, ids, field, arg, context=None):
        
        setting_line_obj = self.pool.get('sale.plan.day.setting.line')
        res = {}
        for data in self.browse(cr, uid, ids, context=context):

            print ' w1_tue_count', data.id
            line_ids = setting_line_obj.search(cr, uid, [('line_id', '=', data.id), ('w1_sat', '=', True)], context=context)
            if line_ids:
                res[data.id] = len(line_ids)
        return res   

    def w2_mon_count(self, cr, uid, ids, field, arg, context=None):
        
        setting_line_obj = self.pool.get('sale.plan.day.setting.line')
        res = {}
        for data in self.browse(cr, uid, ids, context=context):

            line_ids = setting_line_obj.search(cr, uid, [('line_id', '=', data.id), ('w2_mon', '=', True)], context=context)
            if line_ids:
                res[data.id] = len(line_ids)
        return res
    
    def w2_tue_count(self, cr, uid, ids, field, arg, context=None):
        
        setting_line_obj = self.pool.get('sale.plan.day.setting.line')
        res = {}
        for data in self.browse(cr, uid, ids, context=context):

            print ' w1_tue_count', data.id
            line_ids = setting_line_obj.search(cr, uid, [('line_id', '=', data.id), ('w2_tue', '=', True)], context=context)
            if line_ids:
                res[data.id] = len(line_ids)
        return res        

    def w2_wed_count(self, cr, uid, ids, field, arg, context=None):
        
        setting_line_obj = self.pool.get('sale.plan.day.setting.line')
        res = {}
        for data in self.browse(cr, uid, ids, context=context):

            line_ids = setting_line_obj.search(cr, uid, [('line_id', '=', data.id), ('w2_wed', '=', True)], context=context)
            if line_ids:
                res[data.id] = len(line_ids)
        return res
    
    def w2_thur_count(self, cr, uid, ids, field, arg, context=None):
        
        setting_line_obj = self.pool.get('sale.plan.day.setting.line')
        res = {}
        for data in self.browse(cr, uid, ids, context=context):

            line_ids = setting_line_obj.search(cr, uid, [('line_id', '=', data.id), ('w2_thur', '=', True)], context=context)
            if line_ids:
                res[data.id] = len(line_ids)
        return res    
    
    def w2_fri_count(self, cr, uid, ids, field, arg, context=None):
        
        setting_line_obj = self.pool.get('sale.plan.day.setting.line')
        res = {}
        for data in self.browse(cr, uid, ids, context=context):

            line_ids = setting_line_obj.search(cr, uid, [('line_id', '=', data.id), ('w2_fri', '=', True)], context=context)
            if line_ids:
                res[data.id] = len(line_ids)
        return res    
    
    def w2_sat_count(self, cr, uid, ids, field, arg, context=None):
        
        setting_line_obj = self.pool.get('sale.plan.day.setting.line')
        res = {}
        for data in self.browse(cr, uid, ids, context=context):

            line_ids = setting_line_obj.search(cr, uid, [('line_id', '=', data.id), ('w2_sat', '=', True)], context=context)
            if line_ids:
                res[data.id] = len(line_ids)
        return res    
    
    def w3_mon_count(self, cr, uid, ids, field, arg, context=None):
        
        setting_line_obj = self.pool.get('sale.plan.day.setting.line')
        res = {}
        for data in self.browse(cr, uid, ids, context=context):

            line_ids = setting_line_obj.search(cr, uid, [('line_id', '=', data.id), ('w3_mon', '=', True)], context=context)
            if line_ids:
                res[data.id] = len(line_ids)
        return res
    
    def w3_tue_count(self, cr, uid, ids, field, arg, context=None):
        
        setting_line_obj = self.pool.get('sale.plan.day.setting.line')
        res = {}
        for data in self.browse(cr, uid, ids, context=context):

            print ' w1_tue_count', data.id
            line_ids = setting_line_obj.search(cr, uid, [('line_id', '=', data.id), ('w3_tue', '=', True)], context=context)
            if line_ids:
                res[data.id] = len(line_ids)
        return res        

    def w3_wed_count(self, cr, uid, ids, field, arg, context=None):
        
        setting_line_obj = self.pool.get('sale.plan.day.setting.line')
        res = {}
        for data in self.browse(cr, uid, ids, context=context):

            line_ids = setting_line_obj.search(cr, uid, [('line_id', '=', data.id), ('w3_wed', '=', True)], context=context)
            if line_ids:
                res[data.id] = len(line_ids)
        return res
    
    def w3_thur_count(self, cr, uid, ids, field, arg, context=None):
        
        setting_line_obj = self.pool.get('sale.plan.day.setting.line')
        res = {}
        for data in self.browse(cr, uid, ids, context=context):

            line_ids = setting_line_obj.search(cr, uid, [('line_id', '=', data.id), ('w3_thur', '=', True)], context=context)
            if line_ids:
                res[data.id] = len(line_ids)
        return res    
    
    def w3_fri_count(self, cr, uid, ids, field, arg, context=None):
        
        setting_line_obj = self.pool.get('sale.plan.day.setting.line')
        res = {}
        for data in self.browse(cr, uid, ids, context=context):

            line_ids = setting_line_obj.search(cr, uid, [('line_id', '=', data.id), ('w3_fri', '=', True)], context=context)
            if line_ids:
                res[data.id] = len(line_ids)
        return res    
    
    def w3_sat_count(self, cr, uid, ids, field, arg, context=None):
        
        setting_line_obj = self.pool.get('sale.plan.day.setting.line')
        res = {}
        for data in self.browse(cr, uid, ids, context=context):

            line_ids = setting_line_obj.search(cr, uid, [('line_id', '=', data.id), ('w3_sat', '=', True)], context=context)
            if line_ids:
                res[data.id] = len(line_ids)
        return res   
    def w4_mon_count(self, cr, uid, ids, field, arg, context=None):
        
        setting_line_obj = self.pool.get('sale.plan.day.setting.line')
        res = {}
        for data in self.browse(cr, uid, ids, context=context):

            line_ids = setting_line_obj.search(cr, uid, [('line_id', '=', data.id), ('w4_mon', '=', True)], context=context)
            if line_ids:
                res[data.id] = len(line_ids)
        return res
    
    def w4_tue_count(self, cr, uid, ids, field, arg, context=None):
        
        setting_line_obj = self.pool.get('sale.plan.day.setting.line')
        res = {}
        for data in self.browse(cr, uid, ids, context=context):

            line_ids = setting_line_obj.search(cr, uid, [('line_id', '=', data.id), ('w4_tue', '=', True)], context=context)
            if line_ids:
                res[data.id] = len(line_ids)
        return res        

    def w4_wed_count(self, cr, uid, ids, field, arg, context=None):
        
        setting_line_obj = self.pool.get('sale.plan.day.setting.line')
        res = {}
        for data in self.browse(cr, uid, ids, context=context):

            line_ids = setting_line_obj.search(cr, uid, [('line_id', '=', data.id), ('w4_wed', '=', True)], context=context)
            if line_ids:
                res[data.id] = len(line_ids)
        return res
    
    def w4_thur_count(self, cr, uid, ids, field, arg, context=None):
        
        setting_line_obj = self.pool.get('sale.plan.day.setting.line')
        res = {}
        for data in self.browse(cr, uid, ids, context=context):

            line_ids = setting_line_obj.search(cr, uid, [('line_id', '=', data.id), ('w4_thur', '=', True)], context=context)
            if line_ids:
                res[data.id] = len(line_ids)
        return res    
    
    def w4_fri_count(self, cr, uid, ids, field, arg, context=None):
        
        setting_line_obj = self.pool.get('sale.plan.day.setting.line')
        res = {}
        for data in self.browse(cr, uid, ids, context=context):

            line_ids = setting_line_obj.search(cr, uid, [('line_id', '=', data.id), ('w4_fri', '=', True)], context=context)
            if line_ids:
                res[data.id] = len(line_ids)
        return res    
    
    def w4_sat_count(self, cr, uid, ids, field, arg, context=None):
        setting_line_obj = self.pool.get('sale.plan.day.setting.line')
        res = {}
        for data in self.browse(cr, uid, ids, context=context):
            line_ids = setting_line_obj.search(cr, uid, [('line_id', '=', data.id), ('w4_sat', '=', True)], context=context)
            if line_ids:
                res[data.id] = len(line_ids)
        return res
    
    _columns = {
                'name': fields.char('Description', required=True),
                'sale_team_id':fields.many2one('crm.case.section', 'Sale Team', required=True),
                 'date':fields.date('Apply Date', required=True),
                 'start_date':fields.date('W1 Monday', required=True),
                'state': fields.selection([
            ('draft', 'Pending'),
            ('confirm', 'Confirm'),
            ], 'Status', readonly=True, copy=False, help="Gives the status of the quotation or sales order.\
              \nThe exception status is automatically set when a cancel operation occurs \
              in the invoice validation (Invoice Exception) or in the picking list process (Shipping Exception).\nThe 'Waiting Schedule' status is set when the invoice is confirmed\
               but waiting for the scheduler to run on the order date.", select=True),
        'plan_line':fields.one2many('sale.plan.day.setting.line', 'line_id', 'Plan Lines',
                              copy=True),
        'partner_count' : fields.function(get_partner_count, string='Customer Count', readonly=True, store=True, type='integer'),
        'w1_count_mon' : fields.function(w1_mon_count, string='Count', readonly=True, store=True, type='integer'),
        'w1_count_tue' : fields.function(w1_tue_count, string='Count', readonly=True, store=True, type='integer'),
        'w1_count_wed' : fields.function(w1_wed_count, string='Count', readonly=True, store=True, type='integer'),
        'w1_count_thur' : fields.function(w1_thur_count, string='Count', readonly=True, store=True, type='integer'),
        'w1_count_fri' : fields.function(w1_fri_count, string='Count', readonly=True, store=True, type='integer'),
        'w1_count_sat' : fields.function(w1_sat_count, string='Count', readonly=True, store=True, type='integer'),
        'w2_count_mon' : fields.function(w2_mon_count, string='Count', readonly=True, store=True, type='integer'),
        'w2_count_tue' : fields.function(w2_tue_count, string='Count', readonly=True, store=True, type='integer'),
        'w2_count_wed' : fields.function(w2_wed_count, string='Count', readonly=True, store=True, type='integer'),
        'w2_count_thur' : fields.function(w2_thur_count, string='Count', readonly=True, store=True, type='integer'),
        'w2_count_fri' : fields.function(w2_fri_count, string='Count', readonly=True, store=True, type='integer'),
        'w2_count_sat' : fields.function(w2_sat_count, string='Count', readonly=True, store=True, type='integer'),
        'w3_count_mon' : fields.function(w3_mon_count, string='Count', readonly=True, store=True, type='integer'),
        'w3_count_tue' : fields.function(w3_tue_count, string='Count', readonly=True, store=True, type='integer'),
        'w3_count_wed' : fields.function(w3_wed_count, string='Count', readonly=True, store=True, type='integer'),
        'w3_count_thur' : fields.function(w3_thur_count, string='Count', readonly=True, store=True, type='integer'),
        'w3_count_fri' : fields.function(w3_fri_count, string='Count', readonly=True, store=True, type='integer'),
        'w3_count_sat' : fields.function(w3_sat_count, string='Count', readonly=True, store=True, type='integer'),        
        'w4_count_mon' : fields.function(w4_mon_count, string='Count', readonly=True, store=True, type='integer'),
        'w4_count_tue' : fields.function(w4_tue_count, string='Count', readonly=True, store=True, type='integer'),
        'w4_count_wed' : fields.function(w4_wed_count, string='Count', readonly=True, store=True, type='integer'),
        'w4_count_thur' : fields.function(w4_thur_count, string='Count', readonly=True, store=True, type='integer'),
        'w4_count_fri' : fields.function(w4_fri_count, string='Count', readonly=True, store=True, type='integer'),
        'w4_count_sat' : fields.function(w4_sat_count, string='Count', readonly=True, store=True, type='integer'),        
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
sale_plan_for_day_setting()
    
class sale_plan_setting_line(osv.osv):  # #prod_pricelist_update_line
    _name = 'sale.plan.day.setting.line'
    _description = 'Plan Line'
        
    _columns = {                
        'line_id':fields.many2one('sale.plan.day.setting', 'Line', ondelete='cascade', select=True),
        'code':fields.char('Code', readonly=True),
        'class':fields.many2one('sale.class', 'Class', readonly=True),
        'frequency':fields.many2one('plan.frequency', 'Freq', readonly=True),
        'partner_id': fields.many2one('res.partner', 'Customer', readonly=True),
        'purchase_date':fields.date('Last Purchase Date'),
        'w1_mon':fields.boolean('W1 MON'),
        'w1_tue':fields.boolean('W1 TUE'),
        'w1_wed':fields.boolean('W1 WED'),
        'w1_thur':fields.boolean('W1 THUR'),
        'w1_fri':fields.boolean('W1 FRI'),
        'w1_sat':fields.boolean('W1 SAT'),
        'w2_mon':fields.boolean('W2 MON'),
        'w2_tue':fields.boolean('W2 TUE'),
        'w2_wed':fields.boolean('W2 WED'),
        'w2_thur':fields.boolean('W2 THUR'),
        'w2_fri':fields.boolean('W2 FRI'),
        'w2_sat':fields.boolean('W2 SAT'),
        'w3_mon':fields.boolean('W3 MON'),
        'w3_tue':fields.boolean('W3 TUE'),
        'w3_wed':fields.boolean('W3 WED'),
        'w3_thur':fields.boolean('W3 THUR'),
        'w3_fri':fields.boolean('W3 FRI'),
        'w3_sat':fields.boolean('W3 SAT'),
        'w4_mon':fields.boolean('W4 MON'),
        'w4_tue':fields.boolean('W4 TUE'),
        'w4_wed':fields.boolean('W4 WED'),
        'w4_thur':fields.boolean('W4 THUR'),
        'w4_fri':fields.boolean('W4 FRI'),
        'w4_sat':fields.boolean('W4 SAT'),
    }
sale_plan_setting_line()  
