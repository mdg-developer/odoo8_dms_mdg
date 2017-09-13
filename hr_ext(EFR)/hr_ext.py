from openerp.osv import fields, osv
from openerp import tools
from datetime import datetime
class hr_employee_inherit(osv.osv):
    _inherit = 'hr.employee'
    
    _columns = {
              'birthday':fields.date('Birthday'),
              'birthday_month':fields.char('Birthday Month'),
              'company_id':fields.many2one('res.company', 'Company'),
              'active':fields.boolean('Active',type='boolean', store=True),
              }

     
    _defaults = {
                 'birthday':datetime.today(),
               'company_id':lambda self, cr, uid, context:uid,
               'active':1,
               }
    def get_month(self, cr, uid, ids, vals, context=None):      
        dateformat = datetime.strptime(vals, "%Y-%m-%d")
        value = {}
        date_change = dateformat.timetuple()
        print date_change
        finalvalue = date_change.tm_mon - 1
        totalmonth = {}
        totalmonth[0] = 'January'
        totalmonth[1] = 'February'
        totalmonth[2] = 'March'
        totalmonth[3] = 'April'
        totalmonth[4] = 'May'
        totalmonth[5] = 'June'
        totalmonth[6] = 'July'
        totalmonth[7] = 'August'
        totalmonth[8] = 'September'
        totalmonth[9] = 'October'
        totalmonth[10] = 'November'
        totalmonth[11] = 'December'
        if finalvalue == 0:
            result = totalmonth[0]
        if finalvalue == 1:
            result = totalmonth[1]
        if finalvalue == 2:
            result = totalmonth[2]
        if finalvalue == 3:
            result = totalmonth[3]
        if finalvalue == 4:
            result = totalmonth[4]
        if finalvalue == 5:
            result = totalmonth[5]
        if finalvalue == 6:
            result = totalmonth[6]
        if finalvalue == 7:
            result = totalmonth[7]
        if finalvalue == 8:
            result = totalmonth[8]
        if finalvalue == 9:
            result = totalmonth[9]
        if finalvalue == 10:
            result = totalmonth[10]
        if finalvalue == 11:
            result = totalmonth[11]
             
        value.update({'birthday_month':result})
         
        return {'value':value}
    
    
hr_employee_inherit()        
        
class hr_holidays(osv.osv):
    _inherit = 'hr.holidays'
    _columns = {
                'company_id':fields.many2one('res.company', 'Company'),
                
                }
    _defaults = {
               'company_id':lambda self, cr, uid, context:uid,

               }
class hr_attendance(osv.osv):
    _inherit='hr.attendance'
    ####this take the all field_name of form  ###this work when the button save state
    def _calculate_date(self, cr, uid, ids, field_name, arg, context=None):
        res = dict.fromkeys(ids, False)
        for ee in self.browse(cr, uid, ids, context=context):
            if ee.name:
                #print 'this is datetime I got->',ee.name
                res[ee.id] = ee.name
        return res
    _columns={
              'name':fields.datetime('Date Time'),
               'company_id':fields.many2one('res.company', 'Company'),
               'date':fields.function(_calculate_date,type='date',method=True),
               'date_related': fields.related('date', type='date', string='Date Only', readonly=True, store=True),
              }
    _defaults = {
               'company_id':lambda self, cr, uid, context:uid,
               }
        
class res_partner(osv.osv):
    _inherit = 'res.partner'
    _columns={
               'department_id':fields.many2one('hr.department','Department'),

             }


        


        
