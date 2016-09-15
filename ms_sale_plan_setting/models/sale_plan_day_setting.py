from openerp.osv import fields, osv

class plan_frequency(osv.osv):
    _name='plan.frequency'
    _columns={
              'name':fields.char('Name'),
              }
plan_frequency()    
class sale_plan_for_day_setting(osv.osv):
    _name = 'sale.plan.day.setting'
    
    def on_change_sale_team_id(self, cr, uid, ids, sale_team_id, context=None):
        customer_obj=self.pool.get('res.partner')
        values = {}
        data_line = []
        if sale_team_id:            
            partner_ids = customer_obj.search(cr, uid, [('section_id', '=', sale_team_id)], context=context)
            if  partner_ids:                
                for line in partner_ids:
                    print ' line',line
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
                              copy=True), }
    _defaults = {
               'state':'draft',
    }
    def confirm(self, cr, uid, ids, context=None):               
        return self.write(cr, uid, ids, {'state': 'confirm' })      
    
    def refresh(self, cr, uid, ids, context=None):
        #data_line=[]
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
        #print 'res',res
        return True   
sale_plan_for_day_setting()
    
class sale_plan_setting_line(osv.osv):  # #prod_pricelist_update_line
    _name = 'sale.plan.day.setting.line'
    _description = 'Plan Line'
        
    _columns = {                
        'line_id':fields.many2one('sale.plan.day.setting', 'Line', ondelete='cascade', select=True),
        'code':fields.char('Code',readonly=True),
        'class':fields.many2one('sale.class', 'Class',readonly=True),
        'frequency':fields.many2one('plan.frequency', 'Freq',readonly=True),
        'partner_id': fields.many2one('res.partner', 'Customer',readonly=True),
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