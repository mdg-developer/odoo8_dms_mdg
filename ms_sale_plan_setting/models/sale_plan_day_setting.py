from openerp.osv import fields, osv

class plan_frequency(osv.osv):
    _name = 'plan.frequency'
    _columns = {
              'name':fields.char('Name'),
            'frequency_count': fields.integer('Frequency Count')

              }
plan_frequency()    

class sale_plan_for_day_setting(osv.osv):
    _name = 'sale.plan.day.setting'
    
#     def on_change_sale_team_id(self, cr, uid, ids, sale_team_id, context=None):
#         customer_obj = self.pool.get('res.partner')
#         sale_team_obj = self.pool.get('crm.case.section')        
#         sale_team = sale_team_obj.search(cr, uid, [('id', '=', sale_team_id)], context=context)
#         team_data=sale_team_obj.browse(cr, uid, sale_team, context=context)
#         main_group=team_data.main_group_id
#         branch_id=team_data.branch_id.id
#         print 'dddddddddd',branch_id,main_group
#         values = {}
#         data_line = []
#         if sale_team_id:            
#             partner_ids = customer_obj.search(cr, uid, [('section_id', '=', sale_team_id),('mobile_customer','!=',True),('active','=',True)], context=context)
#             if  partner_ids:                
#                 for line in partner_ids:
#                     print ' line', line
#                     cr.execute("select date_order::date from sale_order  where partner_id =%s order by id desc", (line,))
#                     last_order = cr.fetchone()
#                     if last_order:
#                         last_order_date = last_order[0]
#                     else:
#                         last_order_date = False
#                     partner = customer_obj.browse(cr, uid, line, context=context)
#                     print 'partner.class_id.id',partner.class_id.id
#                     data_line.append({
#                                         'code':partner.customer_code,
#                                          'class':partner.class_id.id,
#                                          'frequency':partner.frequency_id.id,
#                                          'purchase_date':last_order_date,
#                                         'partner_id': line,
#                                                   })
#             values = {
#                       'main_group':main_group,
#                       'branch_id':branch_id,
#                 'plan_line': data_line,
#             }
#         return {'value': values}    
    
    def get_partner_count(self, cr, uid, ids, field, arg, context=None):
        
        res = {}
        for data in self.browse(cr, uid, ids, context=context):
            res[data.id] = len(data.plan_line)
            print 'res', res
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
            print ' line_ids', line_ids
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
                'sale_team_id':fields.many2many('crm.case.section', 'sale_plan_day_sale_team_rel', 'sale_plan_day_id', 'sale_team_id', 'Sale Team',required=False),
                 'date':fields.date('Apply Date', required=True),
                 'start_date':fields.date('W1 Monday'),
                'state': fields.selection([
            ('draft', 'Pending'),
            ('confirm', 'Confirm'),
            ], 'Status', readonly=True, copy=False, help="Gives the status of the quotation or sales order.\
              \nThe exception status is automatically set when a cancel operation occurs \
              in the invoice validation (Invoice Exception) or in the picking list process (Shipping Exception).\nThe 'Waiting Schedule' status is set when the invoice is confirmed\
               but waiting for the scheduler to run on the order date.", select=True),
        'plan_line':fields.one2many('sale.plan.day.setting.line', 'line_id', 'Plan Lines',
                              copy=True),
            'principal':fields.many2one('product.principal', 'Principal'),             
             'main_group':fields.many2many('product.maingroup', 'product_maingroup_sale_plan_day_setting_rel', id1='sale_plan_day_setting_id', id2='product_maingroup_id', string='Main Group'),
           'branch_id':fields.many2one('res.branch', 'Branch'),
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
    
    def create_sale_team_rel(self,cr,uid,day_id,partner_id,context=None):
        cr.execute("delete from sale_plan_day_team_rel where day_id in(select id from sale_plan_day_line where line_id=%s)",(day_id,))
        cr.execute("select id from sale_plan_day_line where line_id=%s",(day_id,))
        data = cr.fetchall()
        for d_id in data:
            plan_id = d_id[0]
            #cr.execute("delete from sale_plan_day_team_rel where day_id=%s",(plan_id,))            
            cr.execute("""insert into sale_plan_day_team_rel select %s,sale_team_id from sale_team_customer_rel where partner_id=%s""",(plan_id,partner_id,))
        
    def confirm(self, cr, uid, ids, context=None):  
        plan_obj = self.pool.get('sale.plan.day')
        sale_plan_day_line_obj = self.pool.get('sale.plan.day.line')
        plan_setting = self.browse(cr, uid, ids, context=context)
        sale_team_ids = plan_setting.sale_team_id
        principal = plan_setting.principal.id
        main_group = plan_setting.main_group.ids
        print ' main_group',main_group
        branch = plan_setting.branch_id.id
        
        date = plan_setting.date
        for sale_team in sale_team_ids:
            sale_team_id=sale_team.id
            cr.execute("delete from sale_plan_day_line where line_id in (select id from sale_plan_day where sale_team= %s)",(sale_team_id,))
            
            for plan_line in plan_setting.plan_line:
                w1_mon = plan_line.w1_mon
                w1_tue = plan_line.w1_tue
                w1_wed = plan_line.w1_wed
                w1_thur = plan_line.w1_thur
                w1_fri = plan_line.w1_fri           
                w1_sat = plan_line.w1_sat           
                w2_mon = plan_line.w2_mon
                w2_tue = plan_line.w2_tue
                w2_wed = plan_line.w2_wed
                w2_thur = plan_line.w2_thur
                w2_fri = plan_line.w2_fri           
                w2_sat = plan_line.w2_sat       
                w3_mon = plan_line.w3_mon
                w3_tue = plan_line.w3_tue
                w3_wed = plan_line.w3_wed
                w3_thur = plan_line.w3_thur
                w3_fri = plan_line.w3_fri           
                w3_sat = plan_line.w3_sat
                w4_mon = plan_line.w4_mon
                w4_tue = plan_line.w4_tue
                w4_wed = plan_line.w4_wed
                w4_thur = plan_line.w4_thur
                w4_fri = plan_line.w4_fri           
                w4_sat = plan_line.w4_sat                                  
                partner_id = plan_line.partner_id.id
                if w1_mon == True:
                   # if w1_mon == True:status = 'Monday' + '(' + sale_team_name + ')'                
                    
                    if w1_mon == True:status = 'Monday'          
                    setting_id = plan_obj.search(cr, uid, [('week', '=', 1), ('sale_team', '=', sale_team_id), ('name', '=', status)], context=context)             
                    if setting_id:
                        #cr.execute("select partner_id from res_partner_sale_plan_day_rel where sale_plan_day_id=%s and partner_id=%s", (setting_id[0], partner_id,))
                        #
                        for res_id in self.pool.get('res.partner').browse(cr,uid,partner_id,context=context):
                            partner = {'line_id':setting_id[0],'partner_id': res_id.id,'outlet_type':res_id.outlet_type.id,'township':res_id.township.id,'address':res_id.street,'delivery_team_id':res_id.delivery_team_id.id,'branch_id':res_id.branch_id.id,'sales_channel':res_id.sales_channel.id,'frequency_id':res_id.frequency_id.id,'class_id':res_id.class_id.id}
                            sale_plan_day_line_obj.create(cr,uid,partner,context=context)
#                             self.create_sale_team_rel(cr, uid, setting_id[0], res_id.id, context=context)                        
                        #cr.execute('INSERT INTO res_partner_sale_plan_day_rel (sale_plan_day_id,partner_id) VALUES (%s,%s)', (setting_id[0], partner_id,))                    
                    else:                
                        plan_id = plan_obj.create(cr, uid, {'name': status,
                                                            'sale_team':sale_team_id,
                                                            'date':date,
                                                      'principal': principal,
                                                      'branch_id':branch,
                                                      'main_group':main_group,
                                                      'active':True,
                                                      'week':1,
                                                      }, context=context)   
                        #cr.execute('INSERT INTO res_partner_sale_plan_day_rel (sale_plan_day_id,partner_id) VALUES (%s,%s)', (plan_id, partner_id,))
                        for res_id in self.pool.get('res.partner').browse(cr,uid,partner_id,context=context):
                            partner = {'line_id':plan_id,'partner_id': res_id.id,'outlet_type':res_id.outlet_type.id,'township':res_id.township.id,'address':res_id.street,'delivery_team_id':res_id.delivery_team_id.id,'branch_id':res_id.branch_id.id,'sales_channel':res_id.sales_channel.id,'frequency_id':res_id.frequency_id.id,'class_id':res_id.class_id.id}
                            sale_plan_day_line_obj.create(cr,uid,partner,context=context)
#                             self.create_sale_team_rel(cr, uid, plan_id, res_id.id, context=context)
                            
#                         for main_group_id in main_group:
#                             cr.execute('INSERT INTO product_maingroup_sale_plan_day_rel (sale_plan_day_id,product_maingroup_id) VALUES (%s,%s)', (plan_id,main_group_id,))                    
                if w1_tue == True:
                    if w1_tue == True:status = 'Tuesday'                   
                    setting_id = plan_obj.search(cr, uid, [('week', '=', 2), ('sale_team', '=', sale_team_id), ('name', '=', status)], context=context)             
                    if setting_id:
                        #cr.execute("select partner_id from res_partner_sale_plan_day_rel where sale_plan_day_id=%s and partner_id=%s", (setting_id[0], partner_id,))
                        #
                        for res_id in self.pool.get('res.partner').browse(cr,uid,partner_id,context=context):
                            partner = {'line_id':setting_id[0],'partner_id': res_id.id,'outlet_type':res_id.outlet_type.id,'township':res_id.township.id,'address':res_id.street,'delivery_team_id':res_id.delivery_team_id.id,'branch_id':res_id.branch_id.id,'sales_channel':res_id.sales_channel.id,'frequency_id':res_id.frequency_id.id,'class_id':res_id.class_id.id}
                            sale_plan_day_line_obj.create(cr,uid,partner,context=context)
                            #self.create_sale_team_rel(cr, uid, setting_id[0], res_id.id, context=context)                        
                        #cr.execute('INSERT INTO res_partner_sale_plan_day_rel (sale_plan_day_id,partner_id) VALUES (%s,%s)', (setting_id[0], partner_id,))
                    else:                
                        plan_id = plan_obj.create(cr, uid, {'name': status,
                                                            'sale_team':sale_team_id,
                                                            'date':date,
                                                      'principal': principal,
                                                      'main_group':main_group,
                                                      'branch_id':branch,
                                                      'active':True,
                                                      'week':2,
                                                      }, context=context)   
                        #cr.execute('INSERT INTO res_partner_sale_plan_day_rel (sale_plan_day_id,partner_id) VALUES (%s,%s)', (plan_id, partner_id,))
                        for res_id in self.pool.get('res.partner').browse(cr,uid,partner_id,context=context):
                            #partner = {'line_id':plan_id,'partner_id': partner_id.id,'outlet_type':partner_id.outlet_type.id,'township':partner_id.township.id,'address':partner_id.street,'delivery_team_id':partner_id.delivery_team_id.id,'branch_id':partner_id.branch_id.id}
                            partner = {'line_id':plan_id,'partner_id': res_id.id,'outlet_type':res_id.outlet_type.id,'township':res_id.township.id,'address':res_id.street,'delivery_team_id':res_id.delivery_team_id.id,'branch_id':res_id.branch_id.id,'sales_channel':res_id.sales_channel.id,'frequency_id':res_id.frequency_id.id,'class_id':res_id.class_id.id}
                            sale_plan_day_line_obj.create(cr,uid,partner,context=context)
                            #self.create_sale_team_rel(cr, uid, plan_id, res_id.id, context=context)
#                             
#                         for main_group_id in main_group:
#                             cr.execute('INSERT INTO product_maingroup_sale_plan_day_rel (sale_plan_day_id,product_maingroup_id) VALUES (%s,%s)', (plan_id,main_group_id,))                        
                if w1_wed == True:
                    if w1_wed == True:status = 'Wednesday'                      
                    setting_id = plan_obj.search(cr, uid, [('week', '=', 3), ('sale_team', '=', sale_team_id), ('name', '=', status)], context=context)             
                    if setting_id:
                        #cr.execute("select partner_id from res_partner_sale_plan_day_rel where sale_plan_day_id=%s and partner_id=%s", (setting_id[0], partner_id,))
                        #                    
                        #cr.execute('INSERT INTO res_partner_sale_plan_day_rel (sale_plan_day_id,partner_id) VALUES (%s,%s)', (setting_id[0], partner_id,))
                        for res_id in self.pool.get('res.partner').browse(cr,uid,partner_id,context=context):
                            partner = {'line_id':setting_id[0],'partner_id': res_id.id,'outlet_type':res_id.outlet_type.id,'township':res_id.township.id,'address':res_id.street,'delivery_team_id':res_id.delivery_team_id.id,'branch_id':res_id.branch_id.id,'sales_channel':res_id.sales_channel.id,'frequency_id':res_id.frequency_id.id,'class_id':res_id.class_id.id}
                            sale_plan_day_line_obj.create(cr,uid,partner,context=context)
                            #self.create_sale_team_rel(cr, uid, setting_id[0], res_id.id, context=context) 
                    else:                
                        plan_id = plan_obj.create(cr, uid, {'name': status,
                                                            'sale_team':sale_team_id,
                                                            'date':date,
                                                      'principal': principal,
                                                      'main_group':main_group,
                                                      'branch_id':branch,
                                                      'active':True,
                                                      'week':3,
                                                      }, context=context)   
                        #cr.execute('INSERT INTO res_partner_sale_plan_day_rel (sale_plan_day_id,partner_id) VALUES (%s,%s)', (plan_id, partner_id,))
                        for res_id in self.pool.get('res.partner').browse(cr,uid,partner_id,context=context):
                            partner = {'line_id':plan_id,'partner_id': res_id.id,'outlet_type':res_id.outlet_type.id,'township':res_id.township.id,'address':res_id.street,'delivery_team_id':res_id.delivery_team_id.id,'branch_id':res_id.branch_id.id,'sales_channel':res_id.sales_channel.id,'frequency_id':res_id.frequency_id.id,'class_id':res_id.class_id.id}
                            sale_plan_day_line_obj.create(cr,uid,partner,context=context)
                            #self.create_sale_team_rel(cr, uid, plan_id, res_id.id, context=context)  
#                         for main_group_id in main_group:
#                             cr.execute('INSERT INTO product_maingroup_sale_plan_day_rel (sale_plan_day_id,product_maingroup_id) VALUES (%s,%s)', (plan_id,main_group_id,))                        
                if w1_thur == True:
                    if w1_thur == True:status = 'Thursday'                 
                    setting_id = plan_obj.search(cr, uid, [('week', '=', 4), ('sale_team', '=', sale_team_id), ('name', '=', status)], context=context)             
                    if setting_id:
                        #cr.execute("select partner_id from res_partner_sale_plan_day_rel where sale_plan_day_id=%s and partner_id=%s", (setting_id[0], partner_id,))
                        #
                        for res_id in self.pool.get('res.partner').browse(cr,uid,partner_id,context=context):
                            partner = {'line_id':setting_id[0],'partner_id': res_id.id,'outlet_type':res_id.outlet_type.id,'township':res_id.township.id,'address':res_id.street,'delivery_team_id':res_id.delivery_team_id.id,'branch_id':res_id.branch_id.id,'sales_channel':res_id.sales_channel.id,'frequency_id':res_id.frequency_id.id,'class_id':res_id.class_id.id}
                            sale_plan_day_line_obj.create(cr,uid,partner,context=context)
                            #self.create_sale_team_rel(cr, uid, setting_id[0], res_id.id, context=context)                         
                        #cr.execute('INSERT INTO res_partner_sale_plan_day_rel (sale_plan_day_id,partner_id) VALUES (%s,%s)', (setting_id[0], partner_id,))
                    else:                
                        plan_id = plan_obj.create(cr, uid, {'name': status,
                                                            'sale_team':sale_team_id,
                                                            'date':date,
                                                      'principal': principal,
                                                      'main_group':main_group,
                                                      'branch_id':branch,
                                                      'active':True,
                                                      'week':4,
                                                      }, context=context)
                        for res_id in self.pool.get('res.partner').browse(cr,uid,partner_id,context=context):
                            partner = {'line_id':plan_id,'partner_id': res_id.id,'outlet_type':res_id.outlet_type.id,'township':res_id.township.id,'address':res_id.street,'delivery_team_id':res_id.delivery_team_id.id,'branch_id':res_id.branch_id.id,'sales_channel':res_id.sales_channel.id,'frequency_id':res_id.frequency_id.id,'class_id':res_id.class_id.id}
                            sale_plan_day_line_obj.create(cr,uid,partner,context=context)
                            #self.create_sale_team_rel(cr, uid, plan_id, res_id.id, context=context)    
                        #cr.execute('INSERT INTO res_partner_sale_plan_day_rel (sale_plan_day_id,partner_id) VALUES (%s,%s)', (plan_id, partner_id,))
#                         for main_group_id in main_group:
#                             cr.execute('INSERT INTO product_maingroup_sale_plan_day_rel (sale_plan_day_id,product_maingroup_id) VALUES (%s,%s)', (plan_id,main_group_id,))                        
                if w1_fri == True:
                    if w1_fri == True:status = 'Friday'                   
                    setting_id = plan_obj.search(cr, uid, [('week', '=', 5), ('sale_team', '=', sale_team_id), ('name', '=', status)], context=context)             
                    if setting_id:
                        #cr.execute("select partner_id from res_partner_sale_plan_day_rel where sale_plan_day_id=%s and partner_id=%s", (setting_id[0], partner_id,))
                        #

                            #cr.execute("delete from res_partner_sale_plan_day_rel where partner_id=%s and sale_plan_day_id=%s", (rel_partner_id[0], setting_id[0]))                    
                        #cr.execute('INSERT INTO res_partner_sale_plan_day_rel (sale_plan_day_id,partner_id) VALUES (%s,%s)', (setting_id[0], partner_id,))
                        for res_id in self.pool.get('res.partner').browse(cr,uid,partner_id,context=context):
                            partner = {'line_id':setting_id[0],'partner_id': res_id.id,'outlet_type':res_id.outlet_type.id,'township':res_id.township.id,'address':res_id.street,'delivery_team_id':res_id.delivery_team_id.id,'branch_id':res_id.branch_id.id,'sales_channel':res_id.sales_channel.id,'frequency_id':res_id.frequency_id.id,'class_id':res_id.class_id.id}
                            sale_plan_day_line_obj.create(cr,uid,partner,context=context)
                            #self.create_sale_team_rel(cr, uid, setting_id[0], res_id.id, context=context) 
                    else:                
                        plan_id = plan_obj.create(cr, uid, {'name': status,
                                                            'sale_team':sale_team_id,
                                                            'date':date,
                                                      'principal': principal,
                                                      'main_group':main_group,
                                                      'branch_id':branch,
                                                      'active':True,
                                                      'week':5,
                                                      }, context=context)   
                        #cr.execute('INSERT INTO res_partner_sale_plan_day_rel (sale_plan_day_id,partner_id) VALUES (%s,%s)', (plan_id, partner_id,))
                        for res_id in self.pool.get('res.partner').browse(cr,uid,partner_id,context=context):
                            partner = {'line_id':plan_id,'partner_id': res_id.id,'outlet_type':res_id.outlet_type.id,'township':res_id.township.id,'address':res_id.street,'delivery_team_id':res_id.delivery_team_id.id,'branch_id':res_id.branch_id.id,'sales_channel':res_id.sales_channel.id,'frequency_id':res_id.frequency_id.id,'class_id':res_id.class_id.id}
                            sale_plan_day_line_obj.create(cr,uid,partner,context=context) 
                            #self.create_sale_team_rel(cr, uid, plan_id, res_id.id, context=context)
#                         for main_group_id in main_group:
#                             cr.execute('INSERT INTO product_maingroup_sale_plan_day_rel (sale_plan_day_id,product_maingroup_id) VALUES (%s,%s)', (plan_id,main_group_id,))    
                if w1_sat == True:
                    if w1_sat == True:status = 'Saturday'              
                    setting_id = plan_obj.search(cr, uid, [('week', '=', 6), ('sale_team', '=', sale_team_id), ('name', '=', status)], context=context)             
                    if setting_id:
                        #cr.execute("select partner_id from res_partner_sale_plan_day_rel where sale_plan_day_id=%s and partner_id=%s", (setting_id[0], partner_id,))
                        #
                    
                        #cr.execute('INSERT INTO res_partner_sale_plan_day_rel (sale_plan_day_id,partner_id) VALUES (%s,%s)', (setting_id[0], partner_id,))
                        for res_id in self.pool.get('res.partner').browse(cr,uid,partner_id,context=context):
                            partner = {'line_id':setting_id[0],'partner_id': res_id.id,'outlet_type':res_id.outlet_type.id,'township':res_id.township.id,'address':res_id.street,'delivery_team_id':res_id.delivery_team_id.id,'branch_id':res_id.branch_id.id,'sales_channel':res_id.sales_channel.id,'frequency_id':res_id.frequency_id.id,'class_id':res_id.class_id.id}
                            sale_plan_day_line_obj.create(cr,uid,partner,context=context)
                            #self.create_sale_team_rel(cr, uid, setting_id[0], res_id.id, context=context) 
                    else:                
                        plan_id = plan_obj.create(cr, uid, {'name': status,
                                                            'sale_team':sale_team_id,
                                                            'date':date,
                                                      'principal': principal,
                                                      'main_group':main_group,
                                                      'branch_id':branch,
                                                      'active':True,
                                                      'week':6,
                                                      }, context=context)   
                        #cr.execute('INSERT INTO res_partner_sale_plan_day_rel (sale_plan_day_id,partner_id) VALUES (%s,%s)', (plan_id, partner_id,))
                        for res_id in self.pool.get('res.partner').browse(cr,uid,partner_id,context=context):
                            partner = {'line_id':plan_id,'partner_id': res_id.id,'outlet_type':res_id.outlet_type.id,'township':res_id.township.id,'address':res_id.street,'delivery_team_id':res_id.delivery_team_id.id,'branch_id':res_id.branch_id.id,'sales_channel':res_id.sales_channel.id,'frequency_id':res_id.frequency_id.id,'class_id':res_id.class_id.id}
                            sale_plan_day_line_obj.create(cr,uid,partner,context=context)
                            #self.create_sale_team_rel(cr, uid, plan_id, res_id.id, context=context)     
#                         for main_group_id in main_group:
#                             cr.execute('INSERT INTO product_maingroup_sale_plan_day_rel (sale_plan_day_id,product_maingroup_id) VALUES (%s,%s)', (plan_id,main_group_id,))                                                           
    # Week2
                if w2_mon == True:
                    if w2_mon == True:status = 'W2 Monday'            
                    setting_id = plan_obj.search(cr, uid, [('week', '=', 2), ('sale_team', '=', sale_team_id), ('name', '=', status)], context=context)             
                    if setting_id:
                        #cr.execute("select partner_id from res_partner_sale_plan_day_rel where sale_plan_day_id=%s and partner_id=%s", (setting_id[0], partner_id,))
                        #

                            #cr.execute("delete from res_partner_sale_plan_day_rel where partner_id=%s and sale_plan_day_id=%s", (rel_partner_id[0], setting_id[0]))                    
                        #cr.execute('INSERT INTO res_partner_sale_plan_day_rel (sale_plan_day_id,partner_id) VALUES (%s,%s)', (setting_id[0], partner_id,))
                        for res_id in self.pool.get('res.partner').browse(cr,uid,partner_id,context=context):
                            #partner = {'line_id':setting_id[0],'partner_id': partner_id.id,'outlet_type':partner_id.outlet_type.id,'township':partner_id.township.id,'address':partner_id.street,'delivery_team_id':partner_id.delivery_team_id.id,'branch_id':partner_id.branch_id.id}
                            partner = {'line_id':setting_id[0],'partner_id': res_id.id,'outlet_type':res_id.outlet_type.id,'township':res_id.township.id,'address':res_id.street,'delivery_team_id':res_id.delivery_team_id.id,'branch_id':res_id.branch_id.id,'sales_channel':res_id.sales_channel.id,'frequency_id':res_id.frequency_id.id,'class_id':res_id.class_id.id}
                            sale_plan_day_line_obj.create(cr,uid,partner,context=context)
                            #self.create_sale_team_rel(cr, uid, setting_id[0], res_id.id, context=context)
                    else:                
                        plan_id = plan_obj.create(cr, uid, {'name': status,
                                                            'sale_team':sale_team_id,
                                                            'date':date,
                                                      'principal': principal,
                                                      'main_group':main_group,
                                                      'branch_id':branch,
                                                      'active':True,
                                                      'week':2,
                                                      }, context=context)
                        for res_id in self.pool.get('res.partner').browse(cr,uid,partner_id,context=context):
                            partner = {'line_id':plan_id,'partner_id': res_id.id,'outlet_type':res_id.outlet_type.id,'township':res_id.township.id,'address':res_id.street,'delivery_team_id':res_id.delivery_team_id.id,'branch_id':res_id.branch_id.id,'sales_channel':res_id.sales_channel.id,'frequency_id':res_id.frequency_id.id,'class_id':res_id.class_id.id}
                            sale_plan_day_line_obj.create(cr,uid,partner,context=context) 
                            #self.create_sale_team_rel(cr, uid, plan_id, res_id.id, context=context)  
                        #cr.execute('INSERT INTO res_partner_sale_plan_day_rel (sale_plan_day_id,partner_id) VALUES (%s,%s)', (plan_id, partner_id,))
#                         for main_group_id in main_group:
#                             cr.execute('INSERT INTO product_maingroup_sale_plan_day_rel (sale_plan_day_id,product_maingroup_id) VALUES (%s,%s)', (plan_id,main_group_id,))                                            
                if w2_tue == True:
                    if w2_tue == True:status = 'W2 Tuesday'                     
                    setting_id = plan_obj.search(cr, uid, [('week', '=', 2), ('sale_team', '=', sale_team_id), ('name', '=', status)], context=context)             
                    if setting_id:
                        #cr.execute("select partner_id from res_partner_sale_plan_day_rel where sale_plan_day_id=%s and partner_id=%s", (setting_id[0], partner_id,))
                        #

                            #cr.execute("delete from res_partner_sale_plan_day_rel where partner_id=%s and sale_plan_day_id=%s", (rel_partner_id[0], setting_id[0]))                    
                        #cr.execute('INSERT INTO res_partner_sale_plan_day_rel (sale_plan_day_id,partner_id) VALUES (%s,%s)', (setting_id[0], partner_id,))
                        for res_id in self.pool.get('res.partner').browse(cr,uid,partner_id,context=context):
                            partner = {'line_id':setting_id[0],'partner_id': res_id.id,'outlet_type':res_id.outlet_type.id,'township':res_id.township.id,'address':res_id.street,'delivery_team_id':res_id.delivery_team_id.id,'branch_id':res_id.branch_id.id,'sales_channel':res_id.sales_channel.id,'frequency_id':res_id.frequency_id.id,'class_id':res_id.class_id.id}
                            sale_plan_day_line_obj.create(cr,uid,partner,context=context)
                            #self.create_sale_team_rel(cr, uid, setting_id[0], res_id.id, context=context) 
                    else:                
                        plan_id = plan_obj.create(cr, uid, {'name': status,
                                                            'sale_team':sale_team_id,
                                                            'date':date,
                                                     'principal': principal,
                                                      'main_group':main_group,
                                                      'branch_id':branch,
                                                      'active':True,
                                                      'week':2,
                                                      }, context=context)   
                        #cr.execute('INSERT INTO res_partner_sale_plan_day_rel (sale_plan_day_id,partner_id) VALUES (%s,%s)', (plan_id, partner_id,))
                        for res_id in self.pool.get('res.partner').browse(cr,uid,partner_id,context=context):
                            partner = {'line_id':plan_id,'partner_id': res_id.id,'outlet_type':res_id.outlet_type.id,'township':res_id.township.id,'address':res_id.street,'delivery_team_id':res_id.delivery_team_id.id,'branch_id':res_id.branch_id.id,'sales_channel':res_id.sales_channel.id,'frequency_id':res_id.frequency_id.id,'class_id':res_id.class_id.id}
                            sale_plan_day_line_obj.create(cr,uid,partner,context=context)
                            #self.create_sale_team_rel(cr, uid, plan_id, res_id.id, context=context) 
#                         for main_group_id in main_group:
#                             cr.execute('INSERT INTO product_maingroup_sale_plan_day_rel (sale_plan_day_id,product_maingroup_id) VALUES (%s,%s)', (plan_id,main_group_id,))                       
                if w2_wed == True:
                    if w2_wed == True:status = 'W2 Wednesday'                     
                    setting_id = plan_obj.search(cr, uid, [('week', '=', 2), ('sale_team', '=', sale_team_id), ('name', '=', status)], context=context)             
                    if setting_id:
                        #cr.execute("select partner_id from res_partner_sale_plan_day_rel where sale_plan_day_id=%s and partner_id=%s", (setting_id[0], partner_id,))
                        #
                   
                        #cr.execute('INSERT INTO res_partner_sale_plan_day_rel (sale_plan_day_id,partner_id) VALUES (%s,%s)', (setting_id[0], partner_id,))
                        for res_id in self.pool.get('res.partner').browse(cr,uid,partner_id,context=context):
                            partner = {'line_id':setting_id[0],'partner_id': res_id.id,'outlet_type':res_id.outlet_type.id,'township':res_id.township.id,'address':res_id.street,'delivery_team_id':res_id.delivery_team_id.id,'branch_id':res_id.branch_id.id,'sales_channel':res_id.sales_channel.id,'frequency_id':res_id.frequency_id.id,'class_id':res_id.class_id.id}
                            sale_plan_day_line_obj.create(cr,uid,partner,context=context)
                            #self.create_sale_team_rel(cr, uid, setting_id[0], res_id.id, context=context) 
                    else:                
                        plan_id = plan_obj.create(cr, uid, {'name': status,
                                                            'sale_team':sale_team_id,
                                                            'date':date,
                                                      'principal': principal,
                                                      'main_group':main_group,
                                                      'branch_id':branch,
                                                      'active':True,
                                                      'week':2,
                                                      }, context=context)
                        for res_id in self.pool.get('res.partner').browse(cr,uid,partner_id,context=context):
                            partner = {'line_id':plan_id,'partner_id': res_id.id,'outlet_type':res_id.outlet_type.id,'township':res_id.township.id,'address':res_id.street,'delivery_team_id':res_id.delivery_team_id.id,'branch_id':res_id.branch_id.id,'sales_channel':res_id.sales_channel.id,'frequency_id':res_id.frequency_id.id,'class_id':res_id.class_id.id}
                            sale_plan_day_line_obj.create(cr,uid,partner,context=context)
                            #self.create_sale_team_rel(cr, uid, plan_id, res_id.id, context=context)    
                        #cr.execute('INSERT INTO res_partner_sale_plan_day_rel (sale_plan_day_id,partner_id) VALUES (%s,%s)', (plan_id, partner_id,)) 
#                         for main_group_id in main_group:
#                             cr.execute('INSERT INTO product_maingroup_sale_plan_day_rel (sale_plan_day_id,product_maingroup_id) VALUES (%s,%s)', (plan_id,main_group_id,))                        
                if w2_thur == True:
                    if w2_thur == True:status = 'W2 Thursday'                        
                    setting_id = plan_obj.search(cr, uid, [('week', '=', 2), ('sale_team', '=', sale_team_id), ('name', '=', status)], context=context)             
                    if setting_id:
                        #cr.execute("select partner_id from res_partner_sale_plan_day_rel where sale_plan_day_id=%s and partner_id=%s", (setting_id[0], partner_id,))
                        #
                   
                        #cr.execute('INSERT INTO res_partner_sale_plan_day_rel (sale_plan_day_id,partner_id) VALUES (%s,%s)', (setting_id[0], partner_id,))
                        for res_id in self.pool.get('res.partner').browse(cr,uid,partner_id,context=context):
                            partner = {'line_id':setting_id[0],'partner_id': res_id.id,'outlet_type':res_id.outlet_type.id,'township':res_id.township.id,'address':res_id.street,'delivery_team_id':res_id.delivery_team_id.id,'branch_id':res_id.branch_id.id,'sales_channel':res_id.sales_channel.id,'frequency_id':res_id.frequency_id.id,'class_id':res_id.class_id.id}
                            sale_plan_day_line_obj.create(cr,uid,partner,context=context)
                            #self.create_sale_team_rel(cr, uid, setting_id[0], res_id.id, context=context) 
                    else:                
                        plan_id = plan_obj.create(cr, uid, {'name': status,
                                                            'sale_team':sale_team_id,
                                                            'date':date,
                                                     'principal': principal,
                                                      'main_group':main_group,
                                                      'branch_id':branch,
                                                      'active':True,
                                                      'week':2,
                                                      }, context=context)
                        for res_id in self.pool.get('res.partner').browse(cr,uid,partner_id,context=context):
                            partner = {'line_id':plan_id,'partner_id': res_id.id,'outlet_type':res_id.outlet_type.id,'township':res_id.township.id,'address':res_id.street,'delivery_team_id':res_id.delivery_team_id.id,'branch_id':res_id.branch_id.id,'sales_channel':res_id.sales_channel.id,'frequency_id':res_id.frequency_id.id,'class_id':res_id.class_id.id}
                            sale_plan_day_line_obj.create(cr,uid,partner,context=context)
                            #self.create_sale_team_rel(cr, uid, plan_id, res_id.id, context=context)    
                        #cr.execute('INSERT INTO res_partner_sale_plan_day_rel (sale_plan_day_id,partner_id) VALUES (%s,%s)', (plan_id, partner_id,))
#                         for main_group_id in main_group:
#                             cr.execute('INSERT INTO product_maingroup_sale_plan_day_rel (sale_plan_day_id,product_maingroup_id) VALUES (%s,%s)', (plan_id,main_group_id,))                        
                if w2_fri == True:
                    if w2_fri == True:status = 'W2 Friday'              
                    setting_id = plan_obj.search(cr, uid, [('week', '=', 2), ('sale_team', '=', sale_team_id), ('name', '=', status)], context=context)             
                    if setting_id:
                        #
                   
                        #cr.execute('INSERT INTO res_partner_sale_plan_day_rel (sale_plan_day_id,partner_id) VALUES (%s,%s)', (setting_id[0], partner_id,))
                        for res_id in self.pool.get('res.partner').browse(cr,uid,partner_id,context=context):
                            partner = {'line_id':setting_id[0],'partner_id': res_id.id,'outlet_type':res_id.outlet_type.id,'township':res_id.township.id,'address':res_id.street,'delivery_team_id':res_id.delivery_team_id.id,'branch_id':res_id.branch_id.id,'sales_channel':res_id.sales_channel.id,'frequency_id':res_id.frequency_id.id,'class_id':res_id.class_id.id}
                            sale_plan_day_line_obj.create(cr,uid,partner,context=context)
                            #self.create_sale_team_rel(cr, uid, setting_id[0], res_id.id, context=context)
                    else:                
                        plan_id = plan_obj.create(cr, uid, {'name': status,
                                                            'sale_team':sale_team_id,
                                                            'date':date,
                                                    'principal': principal,
                                                      'main_group':main_group,
                                                      'branch_id':branch,
                                                      'active':True,
                                                      'week':2,
                                                      }, context=context)
                        for res_id in self.pool.get('res.partner').browse(cr,uid,partner_id,context=context):
                            partner = {'line_id':plan_id,'partner_id': res_id.id,'outlet_type':res_id.outlet_type.id,'township':res_id.township.id,'address':res_id.street,'delivery_team_id':res_id.delivery_team_id.id,'branch_id':res_id.branch_id.id,'sales_channel':res_id.sales_channel.id,'frequency_id':res_id.frequency_id.id,'class_id':res_id.class_id.id}
                            sale_plan_day_line_obj.create(cr,uid,partner,context=context) 
                            #self.create_sale_team_rel(cr, uid, plan_id, res_id.id, context=context)  
                        #cr.execute('INSERT INTO res_partner_sale_plan_day_rel (sale_plan_day_id,partner_id) VALUES (%s,%s)', (plan_id, partner_id,))
#                         for main_group_id in main_group:
#                             cr.execute('INSERT INTO product_maingroup_sale_plan_day_rel (sale_plan_day_id,product_maingroup_id) VALUES (%s,%s)', (plan_id,main_group_id,))                        
    
                if w2_sat == True:
                    if w2_sat == True:status = 'W2 Saturday'    
                    setting_id = plan_obj.search(cr, uid, [('week', '=', 2), ('sale_team', '=', sale_team_id), ('name', '=', status)], context=context)             
                    if setting_id:
                        #cr.execute("select partner_id from res_partner_sale_plan_day_rel where sale_plan_day_id=%s and partner_id=%s", (setting_id[0], partner_id,))
                        #

                            #cr.execute("delete from res_partner_sale_plan_day_rel where partner_id=%s and sale_plan_day_id=%s", (rel_partner_id[0], setting_id[0]))                    
                        #cr.execute('INSERT INTO res_partner_sale_plan_day_rel (sale_plan_day_id,partner_id) VALUES (%s,%s)', (setting_id[0], partner_id,))
                        for res_id in self.pool.get('res.partner').browse(cr,uid,partner_id,context=context):
                            partner = {'line_id':setting_id[0],'partner_id': res_id.id,'outlet_type':res_id.outlet_type.id,'township':res_id.township.id,'address':res_id.street,'delivery_team_id':res_id.delivery_team_id.id,'branch_id':res_id.branch_id.id,'sales_channel':res_id.sales_channel.id,'frequency_id':res_id.frequency_id.id,'class_id':res_id.class_id.id}
                            sale_plan_day_line_obj.create(cr,uid,partner,context=context)
                            #self.create_sale_team_rel(cr, uid, setting_id[0], res_id.id, context=context)
                    else:                
                        plan_id = plan_obj.create(cr, uid, {'name': status,
                                                            'sale_team':sale_team_id,
                                                            'date':date,
                                                      'principal': principal,
                                                      'main_group':main_group,
                                                      'branch_id':branch,
                                                      'active':True,
                                                      'week':2,
                                                      }, context=context)   
                        #cr.execute('INSERT INTO res_partner_sale_plan_day_rel (sale_plan_day_id,partner_id) VALUES (%s,%s)', (plan_id, partner_id,))
                        for res_id in self.pool.get('res.partner').browse(cr,uid,partner_id,context=context):
                            partner = {'line_id':plan_id,'partner_id': res_id.id,'outlet_type':res_id.outlet_type.id,'township':res_id.township.id,'address':res_id.street,'delivery_team_id':res_id.delivery_team_id.id,'branch_id':res_id.branch_id.id,'sales_channel':res_id.sales_channel.id,'frequency_id':res_id.frequency_id.id,'class_id':res_id.class_id.id}
                            sale_plan_day_line_obj.create(cr,uid,partner,context=context) 
                            #self.create_sale_team_rel(cr, uid, plan_id, res_id.id, context=context)
                                       
#                         for main_group_id in main_group:
#                             cr.execute('INSERT INTO product_maingroup_sale_plan_day_rel (sale_plan_day_id,product_maingroup_id) VALUES (%s,%s)', (plan_id,main_group_id,)) 
                            
    #week3 
                if w3_mon == True:
                    if w3_mon == True:status = 'W3 Monday'      
                    setting_id = plan_obj.search(cr, uid, [('week', '=', 3), ('sale_team', '=', sale_team_id), ('name', '=', status)], context=context)             
                    if setting_id:
                        #cr.execute("select partner_id from res_partner_sale_plan_day_rel where sale_plan_day_id=%s and partner_id=%s", (setting_id[0], partner_id,))
                        #

                            #cr.execute("delete from res_partner_sale_plan_day_rel where partner_id=%s and sale_plan_day_id=%s", (rel_partner_id[0], setting_id[0]))                    
                        #cr.execute('INSERT INTO res_partner_sale_plan_day_rel (sale_plan_day_id,partner_id) VALUES (%s,%s)', (setting_id[0], partner_id,))
                        for res_id in self.pool.get('res.partner').browse(cr,uid,partner_id,context=context):
                            partner = {'line_id':setting_id[0],'partner_id': res_id.id,'outlet_type':res_id.outlet_type.id,'township':res_id.township.id,'address':res_id.street,'delivery_team_id':res_id.delivery_team_id.id,'branch_id':res_id.branch_id.id,'sales_channel':res_id.sales_channel.id,'frequency_id':res_id.frequency_id.id,'class_id':res_id.class_id.id}
                            sale_plan_day_line_obj.create(cr,uid,partner,context=context)
                            #self.create_sale_team_rel(cr, uid, setting_id[0], res_id.id, context=context) 
                    else:                
                        plan_id = plan_obj.create(cr, uid, {'name': status,
                                                            'sale_team':sale_team_id,
                                                            'date':date,
                                                      'principal': principal,
                                                      'main_group':main_group,
                                                      'branch_id':branch,
                                                      'active':True,
                                                      'week':3,
                                                      }, context=context)
                        for res_id in self.pool.get('res.partner').browse(cr,uid,partner_id,context=context):
                            partner = {'line_id':plan_id,'partner_id': res_id.id,'outlet_type':res_id.outlet_type.id,'township':res_id.township.id,'address':res_id.street,'delivery_team_id':res_id.delivery_team_id.id,'branch_id':res_id.branch_id.id,'sales_channel':res_id.sales_channel.id,'frequency_id':res_id.frequency_id.id,'class_id':res_id.class_id.id}
                            sale_plan_day_line_obj.create(cr,uid,partner,context=context)
                            #self.create_sale_team_rel(cr, uid, plan_id, res_id.id, context=context)    
                        #cr.execute('INSERT INTO res_partner_sale_plan_day_rel (sale_plan_day_id,partner_id) VALUES (%s,%s)', (plan_id, partner_id,))
#                         for main_group_id in main_group:
#                             cr.execute('INSERT INTO product_maingroup_sale_plan_day_rel (sale_plan_day_id,product_maingroup_id) VALUES (%s,%s)', (plan_id,main_group_id,))                                            
                if w3_tue == True:
                    if w3_tue == True:status = 'W3 Tuesday'       
                    setting_id = plan_obj.search(cr, uid, [('week', '=', 3), ('sale_team', '=', sale_team_id), ('name', '=', status)], context=context)             
                    if setting_id:
                        #cr.execute("select partner_id from res_partner_sale_plan_day_rel where sale_plan_day_id=%s and partner_id=%s", (setting_id[0], partner_id,))
                        #

                        
                        for res_id in self.pool.get('res.partner').browse(cr,uid,partner_id,context=context):
                            partner = {'line_id':setting_id[0],'partner_id': res_id.id,'outlet_type':res_id.outlet_type.id,'township':res_id.township.id,'address':res_id.street,'delivery_team_id':res_id.delivery_team_id.id,'branch_id':res_id.branch_id.id,'sales_channel':res_id.sales_channel.id,'frequency_id':res_id.frequency_id.id,'class_id':res_id.class_id.id}
                            sale_plan_day_line_obj.create(cr,uid,partner,context=context)
                            #self.create_sale_team_rel(cr, uid, setting_id[0], res_id.id, context=context)                         
                        #cr.execute('INSERT INTO res_partner_sale_plan_day_rel (sale_plan_day_id,partner_id) VALUES (%s,%s)', (setting_id[0], partner_id,))
                    else:                
                        plan_id = plan_obj.create(cr, uid, {'name': status,
                                                            'sale_team':sale_team_id,
                                                            'date':date,
                                                     'principal': principal,
                                                      'main_group':main_group,
                                                      'branch_id':branch,
                                                      'active':True,
                                                      'week':3,
                                                      }, context=context)
                        for res_id in self.pool.get('res.partner').browse(cr,uid,partner_id,context=context):
                            partner = {'line_id':plan_id,'partner_id': res_id.id,'outlet_type':res_id.outlet_type.id,'township':res_id.township.id,'address':res_id.street,'delivery_team_id':res_id.delivery_team_id.id,'branch_id':res_id.branch_id.id,'sales_channel':res_id.sales_channel.id,'frequency_id':res_id.frequency_id.id,'class_id':res_id.class_id.id}
                            sale_plan_day_line_obj.create(cr,uid,partner,context=context) 
                            #self.create_sale_team_rel(cr, uid, plan_id, res_id.id, context=context)   
                        #cr.execute('INSERT INTO res_partner_sale_plan_day_rel (sale_plan_day_id,partner_id) VALUES (%s,%s)', (plan_id, partner_id,))
#                         for main_group_id in main_group:
#                             cr.execute('INSERT INTO product_maingroup_sale_plan_day_rel (sale_plan_day_id,product_maingroup_id) VALUES (%s,%s)', (plan_id,main_group_id,))                       
                if w3_wed == True:
                    if w3_wed == True:status = 'W3 Wednesday'                        
                    setting_id = plan_obj.search(cr, uid, [('week', '=', 3), ('sale_team', '=', sale_team_id), ('name', '=', status)], context=context)             
                    if setting_id:
                        #cr.execute("select partner_id from res_partner_sale_plan_day_rel where sale_plan_day_id=%s and partner_id=%s", (setting_id[0], partner_id,))
                        #
                    
                        #cr.execute('INSERT INTO res_partner_sale_plan_day_rel (sale_plan_day_id,partner_id) VALUES (%s,%s)', (setting_id[0], partner_id,))
                        for res_id in self.pool.get('res.partner').browse(cr,uid,partner_id,context=context):
                            partner = {'line_id':setting_id[0],'partner_id': res_id.id,'outlet_type':res_id.outlet_type.id,'township':res_id.township.id,'address':res_id.street,'delivery_team_id':res_id.delivery_team_id.id,'branch_id':res_id.branch_id.id,'sales_channel':res_id.sales_channel.id,'frequency_id':res_id.frequency_id.id,'class_id':res_id.class_id.id}
                            sale_plan_day_line_obj.create(cr,uid,partner,context=context) 
                            #self.create_sale_team_rel(cr, uid, setting_id[0], res_id.id, context=context)
                    else:                
                        plan_id = plan_obj.create(cr, uid, {'name': status,
                                                            'sale_team':sale_team_id,
                                                            'date':date,
                                                      'principal': principal,
                                                      'main_group':main_group,
                                                      'branch_id':branch,
                                                      'active':True,
                                                      'week':3,
                                                      }, context=context)
                        for res_id in self.pool.get('res.partner').browse(cr,uid,partner_id,context=context):
                            partner = {'line_id':plan_id,'partner_id': res_id.id,'outlet_type':res_id.outlet_type.id,'township':res_id.township.id,'address':res_id.street,'delivery_team_id':res_id.delivery_team_id.id,'branch_id':res_id.branch_id.id,'sales_channel':res_id.sales_channel.id,'frequency_id':res_id.frequency_id.id,'class_id':res_id.class_id.id}
                            sale_plan_day_line_obj.create(cr,uid,partner,context=context) 
                            #self.create_sale_team_rel(cr, uid, plan_id, res_id.id, context=context)   
                        #cr.execute('INSERT INTO res_partner_sale_plan_day_rel (sale_plan_day_id,partner_id) VALUES (%s,%s)', (plan_id, partner_id,)) 
#                         for main_group_id in main_group:
#                             cr.execute('INSERT INTO product_maingroup_sale_plan_day_rel (sale_plan_day_id,product_maingroup_id) VALUES (%s,%s)', (plan_id,main_group_id,))                        
                if w3_thur == True:
                    if w3_thur == True:status = 'W3 Thursday'                  
                    setting_id = plan_obj.search(cr, uid, [('week', '=', 3), ('sale_team', '=', sale_team_id), ('name', '=', status)], context=context)             
                    if setting_id:
                        #cr.execute("select partner_id from res_partner_sale_plan_day_rel where sale_plan_day_id=%s and partner_id=%s", (setting_id[0], partner_id,))
                        #
                   
                        #cr.execute('INSERT INTO res_partner_sale_plan_day_rel (sale_plan_day_id,partner_id) VALUES (%s,%s)', (setting_id[0], partner_id,))
                        for res_id in self.pool.get('res.partner').browse(cr,uid,partner_id,context=context):
                            partner = {'line_id':setting_id[0],'partner_id': res_id.id,'outlet_type':res_id.outlet_type.id,'township':res_id.township.id,'address':res_id.street,'delivery_team_id':res_id.delivery_team_id.id,'branch_id':res_id.branch_id.id,'sales_channel':res_id.sales_channel.id,'frequency_id':res_id.frequency_id.id,'class_id':res_id.class_id.id}
                            sale_plan_day_line_obj.create(cr,uid,partner,context=context)
                            #self.create_sale_team_rel(cr, uid, setting_id[0], res_id.id, context=context) 
                    else:                
                        plan_id = plan_obj.create(cr, uid, {'name': status,
                                                            'sale_team':sale_team_id,
                                                            'date':date,
                                                     'principal': principal,
                                                      'main_group':main_group,
                                                      'branch_id':branch,
                                                      'active':True,
                                                      'week':3,
                                                      }, context=context)   
                        #cr.execute('INSERT INTO res_partner_sale_plan_day_rel (sale_plan_day_id,partner_id) VALUES (%s,%s)', (plan_id, partner_id,))
                        for res_id in self.pool.get('res.partner').browse(cr,uid,partner_id,context=context):
                            partner = {'line_id':plan_id,'partner_id': res_id.id,'outlet_type':res_id.outlet_type.id,'township':res_id.township.id,'address':res_id.street,'delivery_team_id':res_id.delivery_team_id.id,'branch_id':res_id.branch_id.id,'sales_channel':res_id.sales_channel.id,'frequency_id':res_id.frequency_id.id,'class_id':res_id.class_id.id}
                            sale_plan_day_line_obj.create(cr,uid,partner,context=context) 
                            #self.create_sale_team_rel(cr, uid, plan_id, res_id.id, context=context)
                            
#                         for main_group_id in main_group:
#                             cr.execute('INSERT INTO product_maingroup_sale_plan_day_rel (sale_plan_day_id,product_maingroup_id) VALUES (%s,%s)', (plan_id,main_group_id,))                        
                if w3_fri == True:
                    if w3_fri == True:status = 'W3 Friday'         
                    setting_id = plan_obj.search(cr, uid, [('week', '=', 3), ('sale_team', '=', sale_team_id), ('name', '=', status)], context=context)             
                    if setting_id:
                        #cr.execute("select partner_id from res_partner_sale_plan_day_rel where sale_plan_day_id=%s and partner_id=%s", (setting_id[0], partner_id,))
                        #
                    
                        #cr.execute('INSERT INTO res_partner_sale_plan_day_rel (sale_plan_day_id,partner_id) VALUES (%s,%s)', (setting_id[0], partner_id,))
                        for res_id in self.pool.get('res.partner').browse(cr,uid,partner_id,context=context):
                            partner = {'line_id':setting_id[0],'partner_id': res_id.id,'outlet_type':res_id.outlet_type.id,'township':res_id.township.id,'address':res_id.street,'delivery_team_id':res_id.delivery_team_id.id,'branch_id':res_id.branch_id.id,'sales_channel':res_id.sales_channel.id,'frequency_id':res_id.frequency_id.id,'class_id':res_id.class_id.id}
                            sale_plan_day_line_obj.create(cr,uid,partner,context=context)
                            #self.create_sale_team_rel(cr, uid, setting_id[0], res_id.id, context=context) 
                    else:                
                        plan_id = plan_obj.create(cr, uid, {'name': status,
                                                            'sale_team':sale_team_id,
                                                            'date':date,
                                                    'principal': principal,
                                                      'main_group':main_group,
                                                      'branch_id':branch,
                                                      'active':True,
                                                      'week':3,
                                                      }, context=context)   
                        #cr.execute('INSERT INTO res_partner_sale_plan_day_rel (sale_plan_day_id,partner_id) VALUES (%s,%s)', (plan_id, partner_id,))
                        for res_id in self.pool.get('res.partner').browse(cr,uid,partner_id,context=context):
                            partner = {'line_id':plan_id,'partner_id': res_id.id,'outlet_type':res_id.outlet_type.id,'township':res_id.township.id,'address':res_id.street,'delivery_team_id':res_id.delivery_team_id.id,'branch_id':res_id.branch_id.id,'sales_channel':res_id.sales_channel.id,'frequency_id':res_id.frequency_id.id,'class_id':res_id.class_id.id}
                            sale_plan_day_line_obj.create(cr,uid,partner,context=context)
                            #self.create_sale_team_rel(cr, uid, plan_id, res_id.id, context=context)
                             
#                         for main_group_id in main_group:
#                             cr.execute('INSERT INTO product_maingroup_sale_plan_day_rel (sale_plan_day_id,product_maingroup_id) VALUES (%s,%s)', (plan_id,main_group_id,))                        
    
                if w3_sat == True:
                    if w3_sat == True:status = 'W3 Saturday'                     
                    setting_id = plan_obj.search(cr, uid, [('week', '=', 3), ('sale_team', '=', sale_team_id), ('name', '=', status)], context=context)             
                    if setting_id:
                        #cr.execute("select partner_id from res_partner_sale_plan_day_rel where sale_plan_day_id=%s and partner_id=%s", (setting_id[0], partner_id,))
                        #
                   
                        #cr.execute('INSERT INTO res_partner_sale_plan_day_rel (sale_plan_day_id,partner_id) VALUES (%s,%s)', (setting_id[0], partner_id,))
                        for res_id in self.pool.get('res.partner').browse(cr,uid,partner_id,context=context):
                            partner = {'line_id':setting_id[0],'partner_id': res_id.id,'outlet_type':res_id.outlet_type.id,'township':res_id.township.id,'address':res_id.street,'delivery_team_id':res_id.delivery_team_id.id,'branch_id':res_id.branch_id.id,'sales_channel':res_id.sales_channel.id,'frequency_id':res_id.frequency_id.id,'class_id':res_id.class_id.id}
                            sale_plan_day_line_obj.create(cr,uid,partner,context=context)
                            #self.create_sale_team_rel(cr, uid, setting_id[0], res_id.id, context=context)
                             
                    else:                
                        plan_id = plan_obj.create(cr, uid, {'name': status,
                                                            'sale_team':sale_team_id,
                                                            'date':date,
                                                      'principal': principal,
                                                      'main_group':main_group,
                                                      'branch_id':branch,
                                                      'active':True,
                                                      'week':3,
                                                      }, context=context)   
                        #cr.execute('INSERT INTO res_partner_sale_plan_day_rel (sale_plan_day_id,partner_id) VALUES (%s,%s)', (plan_id, partner_id,))
                        for res_id in self.pool.get('res.partner').browse(cr,uid,partner_id,context=context):
                            partner = {'line_id':plan_id,'partner_id': res_id.id,'outlet_type':res_id.outlet_type.id,'township':res_id.township.id,'address':res_id.street,'delivery_team_id':res_id.delivery_team_id.id,'branch_id':res_id.branch_id.id,'sales_channel':res_id.sales_channel.id,'frequency_id':res_id.frequency_id.id,'class_id':res_id.class_id.id}
                            sale_plan_day_line_obj.create(cr,uid,partner,context=context)
                            #self.create_sale_team_rel(cr, uid, plan_id, res_id.id, context=context)             
#                         for main_group_id in main_group:
#                             cr.execute('INSERT INTO product_maingroup_sale_plan_day_rel (sale_plan_day_id,product_maingroup_id) VALUES (%s,%s)', (plan_id,main_group_id,)) 
    #Week4
                if w4_mon == True:
                    if w4_mon == True:status = 'W4 Monday' 
                    setting_id = plan_obj.search(cr, uid, [('week', '=', 4), ('sale_team', '=', sale_team_id), ('name', '=', status)], context=context)             
                    if setting_id:
                        #cr.execute("select partner_id from res_partner_sale_plan_day_rel where sale_plan_day_id=%s and partner_id=%s", (setting_id[0], partner_id,))
                        #
                    
                        #cr.execute('INSERT INTO res_partner_sale_plan_day_rel (sale_plan_day_id,partner_id) VALUES (%s,%s)', (setting_id[0], partner_id,))
                        for res_id in self.pool.get('res.partner').browse(cr,uid,partner_id,context=context):
                            partner = {'line_id':setting_id[0],'partner_id': res_id.id,'outlet_type':res_id.outlet_type.id,'township':res_id.township.id,'address':res_id.street,'delivery_team_id':res_id.delivery_team_id.id,'branch_id':res_id.branch_id.id,'sales_channel':res_id.sales_channel.id,'frequency_id':res_id.frequency_id.id,'class_id':res_id.class_id.id}
                            sale_plan_day_line_obj.create(cr,uid,partner,context=context)
                            #self.create_sale_team_rel(cr, uid, setting_id[0], res_id.id, context=context) 
                    else:                
                        plan_id = plan_obj.create(cr, uid, {'name': status,
                                                            'sale_team':sale_team_id,
                                                            'date':date,
                                                      'principal': principal,
                                                      'main_group':main_group,
                                                      'branch_id':branch,
                                                      'active':True,
                                                      'week':4,
                                                      }, context=context)   
                        #cr.execute('INSERT INTO res_partner_sale_plan_day_rel (sale_plan_day_id,partner_id) VALUES (%s,%s)', (plan_id, partner_id,))
                        for res_id in self.pool.get('res.partner').browse(cr,uid,partner_id,context=context):
                            partner = {'line_id':plan_id,'partner_id': res_id.id,'outlet_type':res_id.outlet_type.id,'township':res_id.township.id,'address':res_id.street,'delivery_team_id':res_id.delivery_team_id.id,'branch_id':res_id.branch_id.id,'sales_channel':res_id.sales_channel.id,'frequency_id':res_id.frequency_id.id,'class_id':res_id.class_id.id}
                            sale_plan_day_line_obj.create(cr,uid,partner,context=context)
                            #self.create_sale_team_rel(cr, uid, plan_id, res_id.id, context=context)
                             
#                         for main_group_id in main_group:
#                             cr.execute('INSERT INTO product_maingroup_sale_plan_day_rel (sale_plan_day_id,product_maingroup_id) VALUES (%s,%s)', (plan_id,main_group_id,))                                            
                if w4_tue == True:
                    if w4_tue == True:status = 'W4 Tuesday'              
                    setting_id = plan_obj.search(cr, uid, [('week', '=', 4), ('sale_team', '=', sale_team_id), ('name', '=', status)], context=context)             
                    if setting_id:
                        #cr.execute("select partner_id from res_partner_sale_plan_day_rel where sale_plan_day_id=%s and partner_id=%s", (setting_id[0], partner_id,))
                        #
                   
                        #cr.execute('INSERT INTO res_partner_sale_plan_day_rel (sale_plan_day_id,partner_id) VALUES (%s,%s)', (setting_id[0], partner_id,))
                        for res_id in self.pool.get('res.partner').browse(cr,uid,partner_id,context=context):
                            partner = {'line_id':setting_id[0],'partner_id': res_id.id,'outlet_type':res_id.outlet_type.id,'township':res_id.township.id,'address':res_id.street,'delivery_team_id':res_id.delivery_team_id.id,'branch_id':res_id.branch_id.id,'sales_channel':res_id.sales_channel.id,'frequency_id':res_id.frequency_id.id,'class_id':res_id.class_id.id}
                            sale_plan_day_line_obj.create(cr,uid,partner,context=context) 
                            #self.create_sale_team_rel(cr, uid, setting_id[0], res_id.id, context=context)
                    else:                
                        plan_id = plan_obj.create(cr, uid, {'name': status,
                                                            'sale_team':sale_team_id,
                                                            'date':date,
                                                     'principal': principal,
                                                      'main_group':main_group,
                                                      'branch_id':branch,
                                                      'active':True,
                                                      'week':4,
                                                      }, context=context)
                        for res_id in self.pool.get('res.partner').browse(cr,uid,partner_id,context=context):
                            partner = {'line_id':plan_id,'partner_id': res_id.id,'outlet_type':res_id.outlet_type.id,'township':res_id.township.id,'address':res_id.street,'delivery_team_id':res_id.delivery_team_id.id,'branch_id':res_id.branch_id.id,'sales_channel':res_id.sales_channel.id,'frequency_id':res_id.frequency_id.id,'class_id':res_id.class_id.id}
                            sale_plan_day_line_obj.create(cr,uid,partner,context=context)
                            #self.create_sale_team_rel(cr, uid, plan_id, res_id.id, context=context)    
                        #cr.execute('INSERT INTO res_partner_sale_plan_day_rel (sale_plan_day_id,partner_id) VALUES (%s,%s)', (plan_id, partner_id,))
#                         for main_group_id in main_group:
#                             cr.execute('INSERT INTO product_maingroup_sale_plan_day_rel (sale_plan_day_id,product_maingroup_id) VALUES (%s,%s)', (plan_id,main_group_id,))                       
                if w4_wed == True:
                    if w4_wed == True:status = 'W4 Wednesday'                      
                    setting_id = plan_obj.search(cr, uid, [('week', '=', 4), ('sale_team', '=', sale_team_id), ('name', '=', status)], context=context)             
                    if setting_id:
                        #cr.execute("select partner_id from res_partner_sale_plan_day_rel where sale_plan_day_id=%s and partner_id=%s", (setting_id[0], partner_id,))
                        #
                    
                        #cr.execute('INSERT INTO res_partner_sale_plan_day_rel (sale_plan_day_id,partner_id) VALUES (%s,%s)', (setting_id[0], partner_id,))
                        for res_id in self.pool.get('res.partner').browse(cr,uid,partner_id,context=context):
                            partner = {'line_id':setting_id[0],'partner_id': res_id.id,'outlet_type':res_id.outlet_type.id,'township':res_id.township.id,'address':res_id.street,'delivery_team_id':res_id.delivery_team_id.id,'branch_id':res_id.branch_id.id,'sales_channel':res_id.sales_channel.id,'frequency_id':res_id.frequency_id.id,'class_id':res_id.class_id.id}
                            sale_plan_day_line_obj.create(cr,uid,partner,context=context)
                            #self.create_sale_team_rel(cr, uid, setting_id[0], res_id.id, context=context) 
                    else:                
                        plan_id = plan_obj.create(cr, uid, {'name': status,
                                                            'sale_team':sale_team_id,
                                                            'date':date,
                                                      'principal': principal,
                                                      'main_group':main_group,
                                                      'branch_id':branch,
                                                      'active':True,
                                                      'week':4,
                                                      }, context=context)
                        for res_id in self.pool.get('res.partner').browse(cr,uid,partner_id,context=context):
                            partner = {'line_id':plan_id,'partner_id': res_id.id,'outlet_type':res_id.outlet_type.id,'township':res_id.township.id,'address':res_id.street,'delivery_team_id':res_id.delivery_team_id.id,'branch_id':res_id.branch_id.id,'sales_channel':res_id.sales_channel.id,'frequency_id':res_id.frequency_id.id,'class_id':res_id.class_id.id}
                            sale_plan_day_line_obj.create(cr,uid,partner,context=context)
                            #self.create_sale_team_rel(cr, uid, plan_id, res_id.id, context=context)    
                        #cr.execute('INSERT INTO res_partner_sale_plan_day_rel (sale_plan_day_id,partner_id) VALUES (%s,%s)', (plan_id, partner_id,)) 
#                         for main_group_id in main_group:
#                             cr.execute('INSERT INTO product_maingroup_sale_plan_day_rel (sale_plan_day_id,product_maingroup_id) VALUES (%s,%s)', (plan_id,main_group_id,))                        
                if w4_thur == True:
                    if w4_thur == True:status = 'W4 Thursday'                        
                    setting_id = plan_obj.search(cr, uid, [('week', '=', 4), ('sale_team', '=', sale_team_id), ('name', '=', status)], context=context)             
                    if setting_id:
                        #cr.execute("select partner_id from res_partner_sale_plan_day_rel where sale_plan_day_id=%s and partner_id=%s", (setting_id[0], partner_id,))
                        #
                   
                        #cr.execute('INSERT INTO res_partner_sale_plan_day_rel (sale_plan_day_id,partner_id) VALUES (%s,%s)', (setting_id[0], partner_id,))
                        for res_id in self.pool.get('res.partner').browse(cr,uid,partner_id,context=context):
                            partner = {'line_id':setting_id[0],'partner_id': res_id.id,'outlet_type':res_id.outlet_type.id,'township':res_id.township.id,'address':res_id.street,'delivery_team_id':res_id.delivery_team_id.id,'branch_id':res_id.branch_id.id,'sales_channel':res_id.sales_channel.id,'frequency_id':res_id.frequency_id.id,'class_id':res_id.class_id.id}
                            sale_plan_day_line_obj.create(cr,uid,partner,context=context)
                            #self.create_sale_team_rel(cr, uid, setting_id[0], res_id.id, context=context) 
                    else:                
                        plan_id = plan_obj.create(cr, uid, {'name': status,
                                                            'sale_team':sale_team_id,
                                                            'date':date,
                                                     'principal': principal,
                                                      'main_group':main_group,
                                                      'branch_id':branch,
                                                      'active':True,
                                                      'week':4,
                                                      }, context=context)
                        for res_id in self.pool.get('res.partner').browse(cr,uid,partner_id,context=context):
                            partner = {'line_id':plan_id,'partner_id': res_id.id,'outlet_type':res_id.outlet_type.id,'township':res_id.township.id,'address':res_id.street,'delivery_team_id':res_id.delivery_team_id.id,'branch_id':res_id.branch_id.id,'sales_channel':res_id.sales_channel.id,'frequency_id':res_id.frequency_id.id,'class_id':res_id.class_id.id}
                            sale_plan_day_line_obj.create(cr,uid,partner,context=context)
                            #self.create_sale_team_rel(cr, uid, plan_id, res_id.id, context=context)    
                        #cr.execute('INSERT INTO res_partner_sale_plan_day_rel (sale_plan_day_id,partner_id) VALUES (%s,%s)', (plan_id, partner_id,))
#                         for main_group_id in main_group:
#                             cr.execute('INSERT INTO product_maingroup_sale_plan_day_rel (sale_plan_day_id,product_maingroup_id) VALUES (%s,%s)', (plan_id,main_group_id,))                        
                if w4_fri == True:
                    if w4_fri == True:status = 'W4 Friday'                     
                    setting_id = plan_obj.search(cr, uid, [('week', '=', 4), ('sale_team', '=', sale_team_id), ('name', '=', status)], context=context)             
                    if setting_id:
                        #cr.execute("select partner_id from res_partner_sale_plan_day_rel where sale_plan_day_id=%s and partner_id=%s", (setting_id[0], partner_id,))
                        #
                    
                        #cr.execute('INSERT INTO res_partner_sale_plan_day_rel (sale_plan_day_id,partner_id) VALUES (%s,%s)', (setting_id[0], partner_id,))
                        for res_id in self.pool.get('res.partner').browse(cr,uid,partner_id,context=context):
                            partner = {'line_id':setting_id[0],'partner_id': res_id.id,'outlet_type':res_id.outlet_type.id,'township':res_id.township.id,'address':res_id.street,'delivery_team_id':res_id.delivery_team_id.id,'branch_id':res_id.branch_id.id,'sales_channel':res_id.sales_channel.id,'frequency_id':res_id.frequency_id.id,'class_id':res_id.class_id.id}
                            sale_plan_day_line_obj.create(cr,uid,partner,context=context)
                            #self.create_sale_team_rel(cr, uid, setting_id[0], res_id.id, context=context) 
                    else:                
                        plan_id = plan_obj.create(cr, uid, {'name': status,
                                                            'sale_team':sale_team_id,
                                                            'date':date,
                                                    'principal': principal,
                                                      'main_group':main_group,
                                                      'branch_id':branch,
                                                      'active':True,
                                                      'week':4,
                                                      }, context=context) 
                        for res_id in self.pool.get('res.partner').browse(cr,uid,partner_id,context=context):
                            partner = {'line_id':plan_id,'partner_id': res_id.id,'outlet_type':res_id.outlet_type.id,'township':res_id.township.id,'address':res_id.street,'delivery_team_id':res_id.delivery_team_id.id,'branch_id':res_id.branch_id.id,'sales_channel':res_id.sales_channel.id,'frequency_id':res_id.frequency_id.id,'class_id':res_id.class_id.id}
                            sale_plan_day_line_obj.create(cr,uid,partner,context=context)
                            #self.create_sale_team_rel(cr, uid, plan_id, res_id.id, context=context)   
                        #cr.execute('INSERT INTO res_partner_sale_plan_day_rel (sale_plan_day_id,partner_id) VALUES (%s,%s)', (plan_id, partner_id,))
#                         for main_group_id in main_group:
#                             cr.execute('INSERT INTO product_maingroup_sale_plan_day_rel (sale_plan_day_id,product_maingroup_id) VALUES (%s,%s)', (plan_id,main_group_id,))                        
    
                if w4_sat == True:
                    if w4_sat == True:status = 'W4 Saturday'                     
                    setting_id = plan_obj.search(cr, uid, [('week', '=', 4), ('sale_team', '=', sale_team_id), ('name', '=', status)], context=context)             
                    if setting_id:
                        #

                            #cr.execute("delete from res_partner_sale_plan_day_rel where partner_id=%s and sale_plan_day_id=%s", (rel_partner_id[0], setting_id[0]))                    
                        #cr.execute('INSERT INTO res_partner_sale_plan_day_rel (sale_plan_day_id,partner_id) VALUES (%s,%s)', (setting_id[0], partner_id,))
                        for res_id in self.pool.get('res.partner').browse(cr,uid,partner_id,context=context):
                            partner = {'line_id':setting_id[0],'partner_id': res_id.id,'outlet_type':res_id.outlet_type.id,'township':res_id.township.id,'address':res_id.street,'delivery_team_id':res_id.delivery_team_id.id,'branch_id':res_id.branch_id.id,'sales_channel':res_id.sales_channel.id,'frequency_id':res_id.frequency_id.id,'class_id':res_id.class_id.id}
                            sale_plan_day_line_obj.create(cr,uid,partner,context=context)
                            #self.create_sale_team_rel(cr, uid, setting_id[0], res_id.id, context=context) 
                    else:                
                        plan_id = plan_obj.create(cr, uid, {'name': status,
                                                            'sale_team':sale_team_id,
                                                            'date':date,
                                                      'principal': principal,
                                                      'main_group':main_group,
                                                      'branch_id':branch,
                                                      'active':True,
                                                      'week':4,
                                                      }, context=context)
                        for res_id in self.pool.get('res.partner').browse(cr,uid,partner_id,context=context):
                            partner = {'line_id':plan_id,'partner_id': res_id.id,'outlet_type':res_id.outlet_type.id,'township':res_id.township.id,'address':res_id.street,'delivery_team_id':res_id.delivery_team_id.id,'branch_id':res_id.branch_id.id,'sales_channel':res_id.sales_channel.id,'frequency_id':res_id.frequency_id.id,'class_id':res_id.class_id.id}
                            sale_plan_day_line_obj.create(cr,uid,partner,context=context)
                            #self.create_sale_team_rel(cr, uid, plan_id, res_id.id, context=context)    
                        #cr.execute('INSERT INTO res_partner_sale_plan_day_rel (sale_plan_day_id,partner_id) VALUES (%s,%s)', (plan_id, partner_id,))            
#                         for main_group_id in main_group:
#                             cr.execute('INSERT INTO product_maingroup_sale_plan_day_rel (sale_plan_day_id,product_maingroup_id) VALUES (%s,%s)', (plan_id,main_group_id,))                                                                                                  
        return self.write(cr, uid, ids, {'state': 'confirm' })      

    def retrieve_data(self, cr, uid, ids, context=None):
        data_line=[]
        res=[]
        customer_obj=self.pool.get('res.partner')
        sale_plan_obj=self.pool.get('sale.plan.day.setting')       
        plan_obj=self.pool.get('sale.plan.day.setting.line')
        plan = self.browse(cr, uid, ids, context=context)
        sale_team_obj = self.pool.get('crm.case.section') 
        partner_count=plan.partner_count
        sale_team_ids =plan.sale_team_id 
        cr.execute("delete from sale_plan_day_setting_line where line_id=%s",(plan.id,))       
        for sale_team in sale_team_ids:
            print 'sale_team',sale_team
            team_data=sale_team_obj.browse(cr, uid, sale_team.id, context=context)
            main_group=team_data.main_group_id
            branch_id=team_data.branch_id.id
            plan_line=plan.plan_line
            for plan_line_id in plan_line:
                partner_id=plan_line_id.partner_id.id
                partner_code= plan_line_id.partner_id.customer_code
                cr.execute("update sale_plan_day_setting_line set code =%s where partner_id=%s and id = %s",(partner_code,partner_id,plan_line_id.id,))
                data_line.append(partner_id)
            partner_ids = customer_obj.search(cr, uid, [('section_id', '=', sale_team.id),('id','not in',data_line),('mobile_customer','!=',True),('active','=',True)], context=context)
            if  partner_ids:                
                for partner_id in partner_ids:
                    partner = customer_obj.browse(cr, uid, partner_id, context=context)
                    cr.execute("select date_order::date from sale_order  where partner_id =%s order by id desc", (partner_id,))
                    last_order = cr.fetchone()
                    if last_order:
                        last_order_date = last_order[0]
                    else:
                        last_order_date = False
                    plan_obj.create(cr, uid, {
                                        'code':partner.customer_code,
                                         'class':partner.class_id.id,
                                         'frequency':partner.frequency_id.id,
                                         'purchase_date':last_order_date,
                                        'partner_id': partner_id,
                                        'line_id':plan.id,
                                                  }, context=context)    
        return True   
               
                        
    def refresh_customer(self, cr, uid, ids, context=None):
        data_line=[]
        res=[]
        customer_obj=self.pool.get('res.partner')
        sale_plan_obj=self.pool.get('sale.plan.day.setting')       
        plan_obj=self.pool.get('sale.plan.day.setting.line')
        plan = self.browse(cr, uid, ids, context=context)
        partner_count=plan.partner_count
        plan_line=plan.plan_line
        sale_team_ids =plan.sale_team_id        
        for sale_team_id in sale_team_ids:
            plan_line=plan.plan_line
            for plan_line_id in plan_line:
                partner_id=plan_line_id.partner_id.id
                partner_code= plan_line_id.partner_id.customer_code
                cr.execute("update sale_plan_day_setting_line set code =%s where partner_id=%s and id = %s",(partner_code,partner_id,plan_line_id.id,))
                data_line.append(partner_id)
            partner_ids = customer_obj.search(cr, uid, [('section_id', '=', sale_team_id.id),('id','not in',data_line),('mobile_customer','!=',True),('active','=',True)], context=context)
            if  partner_ids:
                    count=len(partner_ids)                
                    for line in partner_ids:
                        print ' line',line,ids
                        partner = customer_obj.browse(cr, uid, line, context=context)
                        cr.execute("select date_order::date from sale_order  where partner_id =%s order by id desc", (partner.id,))
                        last_order = cr.fetchone()
                        if last_order:
                            last_order_date = last_order[0]
                        else:
                            last_order_date = False                 
                        plan_id = plan_obj.create(cr, uid, {
                                            'code':partner.customer_code,
                                             'class':partner.class_id.id,
                                             'frequency':partner.frequency_id.id,
                                             'purchase_date':last_order_date,
                                            'partner_id': line,
                                            'line_id':plan.id,
                                                      }, context=context)   
                        sale_plan_obj.write(cr, uid, ids, {'partner_count':  partner_count+count})  
        cr.execute("delete from sale_plan_day_setting_line where partner_id in (select id from res_partner where active=False)")
        cr.execute("delete from sale_plan_day_line where partner_id in (select id from res_partner where active=False)")
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
        'purchase_date':fields.date('Last Purchase Date', readonly=True),
        'w1_mon':fields.boolean('MON'),
        'w1_tue':fields.boolean('TUE'),
        'w1_wed':fields.boolean('WED'),
        'w1_thur':fields.boolean('THU'),
        'w1_fri':fields.boolean('FRI'),
        'w1_sat':fields.boolean('SAT'),
        'w2_mon':fields.boolean('W2 MON'),
        'w2_tue':fields.boolean('W2 TUE'),
        'w2_wed':fields.boolean('W2 WED'),
        'w2_thur':fields.boolean('W2 THU'),
        'w2_fri':fields.boolean('W2 FRI'),
        'w2_sat':fields.boolean('W2 SAT'),
        'w3_mon':fields.boolean('W3 MON'),
        'w3_tue':fields.boolean('W3 TUE'),
        'w3_wed':fields.boolean('W3 WED'),
        'w3_thur':fields.boolean('W3 THU'),
        'w3_fri':fields.boolean('W3 FRI'),
        'w3_sat':fields.boolean('W3 SAT'),
        'w4_mon':fields.boolean('W4 MON'),
        'w4_tue':fields.boolean('W4 TUE'),
        'w4_wed':fields.boolean('W4 WED'),
        'w4_thur':fields.boolean('W4 THU'),
        'w4_fri':fields.boolean('W4 FRI'),
        'w4_sat':fields.boolean('W4 SAT'),
    }
sale_plan_setting_line()  
