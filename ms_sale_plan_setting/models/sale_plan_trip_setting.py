from openerp.osv import fields, osv
   
class sale_plan_for_trip_setting(osv.osv):
    _name = 'sale.plan.trip.setting'
    
    def on_change_sale_team_id(self, cr, uid, ids, sale_team_id, context=None):
        customer_obj = self.pool.get('res.partner')
        values = {}
        data_line = []
        sale_team_obj = self.pool.get('crm.case.section')                
        sale_team = sale_team_obj.search(cr, uid, [('id', '=', sale_team_id)], context=context)
        team_data=sale_team_obj.browse(cr, uid, sale_team, context=context)
        main_group=team_data.main_group_id
        branch_id=team_data.branch_id.id        
        if sale_team_id:            
            partner_ids = customer_obj.search(cr, uid, [('section_id', '=', sale_team_id),('mobile_customer','!=',True),('active','=',True)], context=context)
            if  partner_ids:                
                for line in partner_ids:
                    print ' line', line
                    cr.execute("select date_order::date from sale_order  where partner_id =%s order by id desc",(line,))
                    last_order=cr.fetchone()
                    if last_order:
                        last_order_date=last_order[0]
                    else:
                        last_order_date=False                    
                    partner = customer_obj.browse(cr, uid, line, context=context)
                    data_line.append({
                                        'code':partner.customer_code,
                                         'class':partner.class_id.id,
                                        'partner_id': line,
                                         'purchase_date':last_order_date,
                                        'frequency':partner.frequency_id.id,
                                                  })
            values = {
                      'main_group':main_group,
                      'branch_id':branch_id,                      
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
             'main_group':fields.many2many('product.maingroup', 'product_maingroup_sale_plan_trip_setting_rel', id1='sale_plan_trip_setting_id', id2='product_maingroup_id', string='Main Group'),
           'branch_id':fields.many2one('res.branch', 'Branch'),                
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
        plan_obj = self.pool.get('sale.plan.trip')
        plan_setting = self.browse(cr, uid, ids, context=context)
        sale_team_id = plan_setting.sale_team_id.id
        sale_team_name = plan_setting.sale_team_id.name
        main_group = plan_setting.main_group.ids
        trip_name =plan_setting.name
        print ' main_group',main_group
        branch = plan_setting.branch_id.id
        date = plan_setting.date
        for plan_line in plan_setting.plan_line:
            day_count_1 = plan_line.day_1
            day_count_2 = plan_line.day_2
            day_count_3 = plan_line.day_3
            day_count_4 = plan_line.day_4
            day_count_5 = plan_line.day_5           
            day_count_6 = plan_line.day_6           
            day_count_7 = plan_line.day_7
            day_count_8 = plan_line.day_8
            day_count_9 = plan_line.day_9
            day_count_10 = plan_line.day_10
            day_count_11 = plan_line.day_11           
            day_count_12 = plan_line.day_12       
            day_count_13 = plan_line.day_13
            day_count_14 = plan_line.day_14
            day_count_15 = plan_line.day_15                           
            partner_id = plan_line.partner_id.id
            if day_count_1 == True:
                if day_count_1 == True:status = trip_name + ' Day 01'                 
                setting_id = plan_obj.search(cr, uid, [('date', '=',date ), ('sale_team', '=', sale_team_id),('name','=',status)], context=context)             
                if setting_id:
                    cr.execute("select partner_id from res_partner_sale_plan_trip_rel where sale_plan_trip_id=%s and partner_id=%s", (setting_id[0], partner_id,))
                    rel_partner_id = cr.fetchone()
                    if rel_partner_id:
                        cr.execute("delete from res_partner_sale_plan_trip_rel where partner_id=%s and sale_plan_trip_id=%s", (rel_partner_id[0], setting_id[0]))                    
                    cr.execute('INSERT INTO res_partner_sale_plan_trip_rel (sale_plan_trip_id,partner_id) VALUES (%s,%s)', (setting_id[0], partner_id,))                    
                else:                
                    plan_id = plan_obj.create(cr, uid, {'name': status,
                                                        'sale_team':sale_team_id,
                                                        'date':date,
                                                  'branch_id':branch,
                                                  'main_group':main_group,
                                                  'active':True,
                                                  }, context=context)   
                    cr.execute('INSERT INTO res_partner_sale_plan_trip_rel (sale_plan_trip_id,partner_id) VALUES (%s,%s)', (plan_id, partner_id,))
                    for main_group_id in main_group:
                        cr.execute('INSERT INTO product_maingroup_sale_plan_trip_rel (sale_plan_trip_id,product_maingroup_id) VALUES (%s,%s)', (plan_id,main_group_id,))     

            if day_count_2 == True:
                if day_count_2 == True:status =  trip_name + ' Day 02'                 
                setting_id = plan_obj.search(cr, uid, [('date', '=',date ), ('sale_team', '=', sale_team_id),('name','=',status)], context=context)             
                if setting_id:
                    cr.execute("select partner_id from res_partner_sale_plan_trip_rel where sale_plan_trip_id=%s and partner_id=%s", (setting_id[0], partner_id,))
                    rel_partner_id = cr.fetchone()
                    if rel_partner_id:
                        cr.execute("delete from res_partner_sale_plan_trip_rel where partner_id=%s and sale_plan_trip_id=%s", (rel_partner_id[0], setting_id[0]))                    
                    cr.execute('INSERT INTO res_partner_sale_plan_trip_rel (sale_plan_trip_id,partner_id) VALUES (%s,%s)', (setting_id[0], partner_id,))                    
                else:                
                    plan_id = plan_obj.create(cr, uid, {'name': status,
                                                        'sale_team':sale_team_id,
                                                        'date':date,
                                                  'branch_id':branch,
                                                  'main_group':main_group,
                                                  'active':True,
                                                  }, context=context)   
                    cr.execute('INSERT INTO res_partner_sale_plan_trip_rel (sale_plan_trip_id,partner_id) VALUES (%s,%s)', (plan_id, partner_id,))
                    for main_group_id in main_group:
                        cr.execute('INSERT INTO product_maingroup_sale_plan_trip_rel (sale_plan_trip_id,product_maingroup_id) VALUES (%s,%s)', (plan_id,main_group_id,))     
            if day_count_3 == True:
                if day_count_3 == True:status =  trip_name + ' Day 03'                 
                setting_id = plan_obj.search(cr, uid, [('date', '=',date ), ('sale_team', '=', sale_team_id),('name','=',status)], context=context)             
                if setting_id:
                    cr.execute("select partner_id from res_partner_sale_plan_trip_rel where sale_plan_trip_id=%s and partner_id=%s", (setting_id[0], partner_id,))
                    rel_partner_id = cr.fetchone()
                    if rel_partner_id:
                        cr.execute("delete from res_partner_sale_plan_trip_rel where partner_id=%s and sale_plan_trip_id=%s", (rel_partner_id[0], setting_id[0]))                    
                    cr.execute('INSERT INTO res_partner_sale_plan_trip_rel (sale_plan_trip_id,partner_id) VALUES (%s,%s)', (setting_id[0], partner_id,))                    
                else:                
                    plan_id = plan_obj.create(cr, uid, {'name': status,
                                                        'sale_team':sale_team_id,
                                                        'date':date,
                                                  'branch_id':branch,
                                                  'main_group':main_group,
                                                  'active':True,
                                                  }, context=context)   
                    cr.execute('INSERT INTO res_partner_sale_plan_trip_rel (sale_plan_trip_id,partner_id) VALUES (%s,%s)', (plan_id, partner_id,))
                    for main_group_id in main_group:
                        cr.execute('INSERT INTO product_maingroup_sale_plan_trip_rel (sale_plan_trip_id,product_maingroup_id) VALUES (%s,%s)', (plan_id,main_group_id,))     
            if day_count_4 == True:
                if day_count_4 == True:status =  trip_name + ' Day 04'                 
                setting_id = plan_obj.search(cr, uid, [('date', '=',date ), ('sale_team', '=', sale_team_id),('name','=',status)], context=context)             
                if setting_id:
                    cr.execute("select partner_id from res_partner_sale_plan_trip_rel where sale_plan_trip_id=%s and partner_id=%s", (setting_id[0], partner_id,))
                    rel_partner_id = cr.fetchone()
                    if rel_partner_id:
                        cr.execute("delete from res_partner_sale_plan_trip_rel where partner_id=%s and sale_plan_trip_id=%s", (rel_partner_id[0], setting_id[0]))                    
                    cr.execute('INSERT INTO res_partner_sale_plan_trip_rel (sale_plan_trip_id,partner_id) VALUES (%s,%s)', (setting_id[0], partner_id,))                    
                else:                
                    plan_id = plan_obj.create(cr, uid, {'name': status,
                                                        'sale_team':sale_team_id,
                                                        'date':date,
                                                  'branch_id':branch,
                                                  'main_group':main_group,
                                                  'active':True,
                                                  }, context=context)   
                    cr.execute('INSERT INTO res_partner_sale_plan_trip_rel (sale_plan_trip_id,partner_id) VALUES (%s,%s)', (plan_id, partner_id,))
                    for main_group_id in main_group:
                        cr.execute('INSERT INTO product_maingroup_sale_plan_trip_rel (sale_plan_trip_id,product_maingroup_id) VALUES (%s,%s)', (plan_id,main_group_id,))     
            if day_count_5 == True:
                if day_count_5 == True:status =  trip_name + ' Day 05'                 
                setting_id = plan_obj.search(cr, uid, [('date', '=',date ), ('sale_team', '=', sale_team_id),('name','=',status)], context=context)             
                if setting_id:
                    cr.execute("select partner_id from res_partner_sale_plan_trip_rel where sale_plan_trip_id=%s and partner_id=%s", (setting_id[0], partner_id,))
                    rel_partner_id = cr.fetchone()
                    if rel_partner_id:
                        cr.execute("delete from res_partner_sale_plan_trip_rel where partner_id=%s and sale_plan_trip_id=%s", (rel_partner_id[0], setting_id[0]))                    
                    cr.execute('INSERT INTO res_partner_sale_plan_trip_rel (sale_plan_trip_id,partner_id) VALUES (%s,%s)', (setting_id[0], partner_id,))                    
                else:                
                    plan_id = plan_obj.create(cr, uid, {'name': status,
                                                        'sale_team':sale_team_id,
                                                        'date':date,
                                                  'branch_id':branch,
                                                  'main_group':main_group,
                                                  'active':True,
                                                  }, context=context)   
                    cr.execute('INSERT INTO res_partner_sale_plan_trip_rel (sale_plan_trip_id,partner_id) VALUES (%s,%s)', (plan_id, partner_id,))
                    for main_group_id in main_group:
                        cr.execute('INSERT INTO product_maingroup_sale_plan_trip_rel (sale_plan_trip_id,product_maingroup_id) VALUES (%s,%s)', (plan_id,main_group_id,))     
            if day_count_6 == True:
                if day_count_6 == True:status =  trip_name + ' Day 06'                 
                setting_id = plan_obj.search(cr, uid, [('date', '=',date ), ('sale_team', '=', sale_team_id),('name','=',status)], context=context)             
                if setting_id:
                    cr.execute("select partner_id from res_partner_sale_plan_trip_rel where sale_plan_trip_id=%s and partner_id=%s", (setting_id[0], partner_id,))
                    rel_partner_id = cr.fetchone()
                    if rel_partner_id:
                        cr.execute("delete from res_partner_sale_plan_trip_rel where partner_id=%s and sale_plan_trip_id=%s", (rel_partner_id[0], setting_id[0]))                    
                    cr.execute('INSERT INTO res_partner_sale_plan_trip_rel (sale_plan_trip_id,partner_id) VALUES (%s,%s)', (setting_id[0], partner_id,))                    
                else:                
                    plan_id = plan_obj.create(cr, uid, {'name': status,
                                                        'sale_team':sale_team_id,
                                                        'date':date,
                                                  'branch_id':branch,
                                                  'main_group':main_group,
                                                  'active':True,
                                                  }, context=context)   
                    cr.execute('INSERT INTO res_partner_sale_plan_trip_rel (sale_plan_trip_id,partner_id) VALUES (%s,%s)', (plan_id, partner_id,))
                    for main_group_id in main_group:
                        cr.execute('INSERT INTO product_maingroup_sale_plan_trip_rel (sale_plan_trip_id,product_maingroup_id) VALUES (%s,%s)', (plan_id,main_group_id,))     
            if day_count_7== True:
                if day_count_7 == True:status =  trip_name + ' Day 07'                 
                setting_id = plan_obj.search(cr, uid, [('date', '=',date ), ('sale_team', '=', sale_team_id),('name','=',status)], context=context)             
                if setting_id:
                    cr.execute("select partner_id from res_partner_sale_plan_trip_rel where sale_plan_trip_id=%s and partner_id=%s", (setting_id[0], partner_id,))
                    rel_partner_id = cr.fetchone()
                    if rel_partner_id:
                        cr.execute("delete from res_partner_sale_plan_trip_rel where partner_id=%s and sale_plan_trip_id=%s", (rel_partner_id[0], setting_id[0]))                    
                    cr.execute('INSERT INTO res_partner_sale_plan_trip_rel (sale_plan_trip_id,partner_id) VALUES (%s,%s)', (setting_id[0], partner_id,))                    
                else:                
                    plan_id = plan_obj.create(cr, uid, {'name': status,
                                                        'sale_team':sale_team_id,
                                                        'date':date,
                                                  'branch_id':branch,
                                                  'main_group':main_group,
                                                  'active':True,
                                                  }, context=context)   
                    cr.execute('INSERT INTO res_partner_sale_plan_trip_rel (sale_plan_trip_id,partner_id) VALUES (%s,%s)', (plan_id, partner_id,))
                    for main_group_id in main_group:
                        cr.execute('INSERT INTO product_maingroup_sale_plan_trip_rel (sale_plan_trip_id,product_maingroup_id) VALUES (%s,%s)', (plan_id,main_group_id,))     
            if day_count_8 == True:
                if day_count_8 == True:status = trip_name +  ' Day 08'                 
                setting_id = plan_obj.search(cr, uid, [('date', '=',date ), ('sale_team', '=', sale_team_id),('name','=',status)], context=context)             
                if setting_id:
                    cr.execute("select partner_id from res_partner_sale_plan_trip_rel where sale_plan_trip_id=%s and partner_id=%s", (setting_id[0], partner_id,))
                    rel_partner_id = cr.fetchone()
                    if rel_partner_id:
                        cr.execute("delete from res_partner_sale_plan_trip_rel where partner_id=%s and sale_plan_trip_id=%s", (rel_partner_id[0], setting_id[0]))                    
                    cr.execute('INSERT INTO res_partner_sale_plan_trip_rel (sale_plan_trip_id,partner_id) VALUES (%s,%s)', (setting_id[0], partner_id,))                    
                else:                
                    plan_id = plan_obj.create(cr, uid, {'name': status,
                                                        'sale_team':sale_team_id,
                                                        'date':date,
                                                  'branch_id':branch,
                                                  'main_group':main_group,
                                                  'active':True,
                                                  }, context=context)   
                    cr.execute('INSERT INTO res_partner_sale_plan_trip_rel (sale_plan_trip_id,partner_id) VALUES (%s,%s)', (plan_id, partner_id,))
                    for main_group_id in main_group:
                        cr.execute('INSERT INTO product_maingroup_sale_plan_trip_rel (sale_plan_trip_id,product_maingroup_id) VALUES (%s,%s)', (plan_id,main_group_id,))     
            if day_count_9 == True:
                if day_count_9 == True:status = trip_name +  ' Day 09'                 
                setting_id = plan_obj.search(cr, uid, [('date', '=',date ), ('sale_team', '=', sale_team_id),('name','=',status)], context=context)             
                if setting_id:
                    cr.execute("select partner_id from res_partner_sale_plan_trip_rel where sale_plan_trip_id=%s and partner_id=%s", (setting_id[0], partner_id,))
                    rel_partner_id = cr.fetchone()
                    if rel_partner_id:
                        cr.execute("delete from res_partner_sale_plan_trip_rel where partner_id=%s and sale_plan_trip_id=%s", (rel_partner_id[0], setting_id[0]))                    
                    cr.execute('INSERT INTO res_partner_sale_plan_trip_rel (sale_plan_trip_id,partner_id) VALUES (%s,%s)', (setting_id[0], partner_id,))                    
                else:                
                    plan_id = plan_obj.create(cr, uid, {'name': status,
                                                        'sale_team':sale_team_id,
                                                        'date':date,
                                                  'branch_id':branch,
                                                  'main_group':main_group,
                                                  'active':True,
                                                  }, context=context)   
                    cr.execute('INSERT INTO res_partner_sale_plan_trip_rel (sale_plan_trip_id,partner_id) VALUES (%s,%s)', (plan_id, partner_id,))
                    for main_group_id in main_group:
                        cr.execute('INSERT INTO product_maingroup_sale_plan_trip_rel (sale_plan_trip_id,product_maingroup_id) VALUES (%s,%s)', (plan_id,main_group_id,))     
            if day_count_10 == True:
                if day_count_10 == True:status =  trip_name + ' Day 10'                 
                setting_id = plan_obj.search(cr, uid, [('date', '=',date ), ('sale_team', '=', sale_team_id),('name','=',status)], context=context)             
                if setting_id:
                    cr.execute("select partner_id from res_partner_sale_plan_trip_rel where sale_plan_trip_id=%s and partner_id=%s", (setting_id[0], partner_id,))
                    rel_partner_id = cr.fetchone()
                    if rel_partner_id:
                        cr.execute("delete from res_partner_sale_plan_trip_rel where partner_id=%s and sale_plan_trip_id=%s", (rel_partner_id[0], setting_id[0]))                    
                    cr.execute('INSERT INTO res_partner_sale_plan_trip_rel (sale_plan_trip_id,partner_id) VALUES (%s,%s)', (setting_id[0], partner_id,))                    
                else:                
                    plan_id = plan_obj.create(cr, uid, {'name': status,
                                                        'sale_team':sale_team_id,
                                                        'date':date,
                                                  'branch_id':branch,
                                                  'main_group':main_group,
                                                  'active':True,
                                                  }, context=context)   
                    cr.execute('INSERT INTO res_partner_sale_plan_trip_rel (sale_plan_trip_id,partner_id) VALUES (%s,%s)', (plan_id, partner_id,))
                    for main_group_id in main_group:
                        cr.execute('INSERT INTO product_maingroup_sale_plan_trip_rel (sale_plan_trip_id,product_maingroup_id) VALUES (%s,%s)', (plan_id,main_group_id,))     
            if day_count_11 == True:
                if day_count_11 == True:status = trip_name +  ' Day 11'                 
                setting_id = plan_obj.search(cr, uid, [('date', '=',date ), ('sale_team', '=', sale_team_id),('name','=',status)], context=context)             
                if setting_id:
                    cr.execute("select partner_id from res_partner_sale_plan_trip_rel where sale_plan_trip_id=%s and partner_id=%s", (setting_id[0], partner_id,))
                    rel_partner_id = cr.fetchone()
                    if rel_partner_id:
                        cr.execute("delete from res_partner_sale_plan_trip_rel where partner_id=%s and sale_plan_trip_id=%s", (rel_partner_id[0], setting_id[0]))                    
                    cr.execute('INSERT INTO res_partner_sale_plan_trip_rel (sale_plan_trip_id,partner_id) VALUES (%s,%s)', (setting_id[0], partner_id,))                    
                else:                
                    plan_id = plan_obj.create(cr, uid, {'name': status,
                                                        'sale_team':sale_team_id,
                                                        'date':date,
                                                  'branch_id':branch,
                                                  'main_group':main_group,
                                                  'active':True,
                                                  }, context=context)   
                    cr.execute('INSERT INTO res_partner_sale_plan_trip_rel (sale_plan_trip_id,partner_id) VALUES (%s,%s)', (plan_id, partner_id,))
                    for main_group_id in main_group:
                        cr.execute('INSERT INTO product_maingroup_sale_plan_trip_rel (sale_plan_trip_id,product_maingroup_id) VALUES (%s,%s)', (plan_id,main_group_id,))     
            if day_count_12 == True:
                if day_count_12 == True:status = trip_name +  ' Day 12'                 
                setting_id = plan_obj.search(cr, uid, [('date', '=',date ), ('sale_team', '=', sale_team_id),('name','=',status)], context=context)             
                if setting_id:
                    cr.execute("select partner_id from res_partner_sale_plan_trip_rel where sale_plan_trip_id=%s and partner_id=%s", (setting_id[0], partner_id,))
                    rel_partner_id = cr.fetchone()
                    if rel_partner_id:
                        cr.execute("delete from res_partner_sale_plan_trip_rel where partner_id=%s and sale_plan_trip_id=%s", (rel_partner_id[0], setting_id[0]))                    
                    cr.execute('INSERT INTO res_partner_sale_plan_trip_rel (sale_plan_trip_id,partner_id) VALUES (%s,%s)', (setting_id[0], partner_id,))                    
                else:                
                    plan_id = plan_obj.create(cr, uid, {'name': status,
                                                        'sale_team':sale_team_id,
                                                        'date':date,
                                                  'branch_id':branch,
                                                  'main_group':main_group,
                                                  'active':True,
                                                  }, context=context)   
                    cr.execute('INSERT INTO res_partner_sale_plan_trip_rel (sale_plan_trip_id,partner_id) VALUES (%s,%s)', (plan_id, partner_id,))
                    for main_group_id in main_group:
                        cr.execute('INSERT INTO product_maingroup_sale_plan_trip_rel (sale_plan_trip_id,product_maingroup_id) VALUES (%s,%s)', (plan_id,main_group_id,))     
            if day_count_13 == True:
                if day_count_13 == True:status = trip_name +  ' Day 13'                 
                setting_id = plan_obj.search(cr, uid, [('date', '=',date ), ('sale_team', '=', sale_team_id),('name','=',status)], context=context)             
                if setting_id:
                    cr.execute("select partner_id from res_partner_sale_plan_trip_rel where sale_plan_trip_id=%s and partner_id=%s", (setting_id[0], partner_id,))
                    rel_partner_id = cr.fetchone()
                    if rel_partner_id:
                        cr.execute("delete from res_partner_sale_plan_trip_rel where partner_id=%s and sale_plan_trip_id=%s", (rel_partner_id[0], setting_id[0]))                    
                    cr.execute('INSERT INTO res_partner_sale_plan_trip_rel (sale_plan_trip_id,partner_id) VALUES (%s,%s)', (setting_id[0], partner_id,))                    
                else:                
                    plan_id = plan_obj.create(cr, uid, {'name': status,
                                                        'sale_team':sale_team_id,
                                                        'date':date,
                                                  'branch_id':branch,
                                                  'main_group':main_group,
                                                  'active':True,
                                                  }, context=context)   
                    cr.execute('INSERT INTO res_partner_sale_plan_trip_rel (sale_plan_trip_id,partner_id) VALUES (%s,%s)', (plan_id, partner_id,))
                    for main_group_id in main_group:
                        cr.execute('INSERT INTO product_maingroup_sale_plan_trip_rel (sale_plan_trip_id,product_maingroup_id) VALUES (%s,%s)', (plan_id,main_group_id,))     
            if day_count_14 == True:
                if day_count_14 == True:status =  trip_name + ' Day 14'                 
                setting_id = plan_obj.search(cr, uid, [('date', '=',date ), ('sale_team', '=', sale_team_id),('name','=',status)], context=context)             
                if setting_id:
                    cr.execute("select partner_id from res_partner_sale_plan_trip_rel where sale_plan_trip_id=%s and partner_id=%s", (setting_id[0], partner_id,))
                    rel_partner_id = cr.fetchone()
                    if rel_partner_id:
                        cr.execute("delete from res_partner_sale_plan_trip_rel where partner_id=%s and sale_plan_trip_id=%s", (rel_partner_id[0], setting_id[0]))                    
                    cr.execute('INSERT INTO res_partner_sale_plan_trip_rel (sale_plan_trip_id,partner_id) VALUES (%s,%s)', (setting_id[0], partner_id,))                    
                else:                
                    plan_id = plan_obj.create(cr, uid, {'name': status,
                                                        'sale_team':sale_team_id,
                                                        'date':date,
                                                  'branch_id':branch,
                                                  'main_group':main_group,
                                                  'active':True,
                                                  }, context=context)   
                    cr.execute('INSERT INTO res_partner_sale_plan_trip_rel (sale_plan_trip_id,partner_id) VALUES (%s,%s)', (plan_id, partner_id,))
                    for main_group_id in main_group:
                        cr.execute('INSERT INTO product_maingroup_sale_plan_trip_rel (sale_plan_trip_id,product_maingroup_id) VALUES (%s,%s)', (plan_id,main_group_id,))     
            if day_count_15== True:
                if day_count_15 == True:status =  trip_name + ' Day 15'                 
                setting_id = plan_obj.search(cr, uid, [('date', '=',date ), ('sale_team', '=', sale_team_id),('name','=',status)], context=context)             
                if setting_id:
                    cr.execute("select partner_id from res_partner_sale_plan_trip_rel where sale_plan_trip_id=%s and partner_id=%s", (setting_id[0], partner_id,))
                    rel_partner_id = cr.fetchone()
                    if rel_partner_id:
                        cr.execute("delete from res_partner_sale_plan_trip_rel where partner_id=%s and sale_plan_trip_id=%s", (rel_partner_id[0], setting_id[0]))                    
                    cr.execute('INSERT INTO res_partner_sale_plan_trip_rel (sale_plan_trip_id,partner_id) VALUES (%s,%s)', (setting_id[0], partner_id,))                    
                else:                
                    plan_id = plan_obj.create(cr, uid, {'name': status,
                                                        'sale_team':sale_team_id,
                                                        'date':date,
                                                  'branch_id':branch,
                                                  'main_group':main_group,
                                                  'active':True,
                                                  }, context=context)   
                    cr.execute('INSERT INTO res_partner_sale_plan_trip_rel (sale_plan_trip_id,partner_id) VALUES (%s,%s)', (plan_id, partner_id,))
                    for main_group_id in main_group:
                        cr.execute('INSERT INTO product_maingroup_sale_plan_trip_rel (sale_plan_trip_id,product_maingroup_id) VALUES (%s,%s)', (plan_id,main_group_id,))     
                                  
        return self.write(cr, uid, ids, {'state': 'confirm' })      
    
    def refresh_customer(self, cr, uid, ids, context=None):
        data_line=[]
        res=[]
        customer_obj=self.pool.get('res.partner')
        sale_plan_obj=self.pool.get('sale.plan.trip.setting')       
        plan_obj=self.pool.get('sale.plan.trip.setting.line')
        plan = self.browse(cr, uid, ids, context=context)
        partner_count=plan.partner_count
        plan_line=plan.plan_line
        for plan_line_id in plan_line:
            partner_id=plan_line_id.partner_id.id
            partner_code= plan_line_id.partner_id.customer_code
            cr.execute("update sale_plan_trip_setting_line set code =%s where partner_id=%s and id = %s",(partner_code,partner_id,plan_line_id.id,))
            data_line.append(partner_id)
        sale_team_id=plan.sale_team_id.id
        partner_ids = customer_obj.search(cr, uid, [('section_id', '=', sale_team_id),('id','not in',data_line),('mobile_customer','!=',True),('active','=',True)], context=context)
        if  partner_ids:
                count=len(partner_ids)                
                for line in partner_ids:
                    print ' line',line,ids
                    partner = customer_obj.browse(cr, uid, line, context=context)
                    cr.execute("select date_order::date from sale_order  where partner_id =%s and state!='cancel' order by id desc", (partner.id,))
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
        cr.execute("delete from sale_plan_trip_setting_line where partner_id in (select id from res_partner where active=False)")
        cr.execute("delete from res_partner_sale_plan_trip_rel where partner_id in (select id from res_partner where active=False)")
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
