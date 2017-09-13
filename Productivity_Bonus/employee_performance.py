'''
Created on Jul 21, 2015

@author: Naw Zar
'''
from openerp import tools
from openerp.osv import fields, osv
from openerp import workflow
from pkg_resources import require

MONTH_SELECTION = [('1','Jan'),
            ('2','Feb'),
            ('3', 'Mar'),
            ('4','Apr'),
            ('5 ','May'),
            ('6','Jun'),
            ('7','Jul'),
            ('8','Aug'),
            ('9','Sep'),
            ('10','Oct'),
            ('11','Nov'),
            ('12','Dec')]

class productivity_bonus(osv.osv):
    _name = "employee.performance"
    _description = "Employee Performance And Abnormal"

    _columns = {
                'department_id':fields.many2one('hr.department','Department', required=True),
                'employee_id':fields.many2one('hr.employee','Employee Name'),
                'job_id':fields.char('Position'),
                'performance':fields.float('Performance(%)',require=True),
                'abnormal':fields.float('Abnormal(%)',require=True),
                'contribution':fields.float('Contribution(%)',require=True),
                'date':fields.date('Date'),
                'total_percent':fields.float('Total %'),
                'total_amount':fields.float('Total Amount'),
                'emp_type':fields.boolean('Employee Type'),
                'type':fields.char('Type'),
                'month':fields.selection(MONTH_SELECTION,'Month'),
             }
    
    def onchange_employee(self,cr,uid,ids,department_id,employee_id,context=None):
        print 'onchange'
        result={}
        if not department_id:
            print 'No Product'
            return True
#         select *From product_template t ,product_product p where t.id=p.product_tmpl_id
        else:
#             cr.execute('select hj.name from hr_job hj,hr_department hd,hr_employee he where hj.department_id=%s and he.id=%s',(department_id,employee_id,))
            cr.execute('select hj.name,hj.id,he.supervisor,he.employee_type from hr_job hj, hr_employee he where hj.id = he.job_id and he.id=%s',(employee_id,))
            emp_list = cr.fetchone()
            if emp_list :
                print 'price record',emp_list
                job_name = emp_list[0]
                emp_type = emp_list[2]
                type = emp_list[3]
                result.update({'job_id':job_name,'emp_type':emp_type,'type':type})
                return{'value' : result}