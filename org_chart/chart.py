from openerp import api, fields, models, _
import base64

class hr_employee(models.Model):
    _inherit = 'hr.department'

    @api.multi
    def employee_dept(self):
        employee_obj = self.env['hr.employee']
        employee_ids = employee_obj.search([])
        department_ids = self.search([])
        dept_details = []
        emp_details = []

        for employee in employee_ids:
            emp_child_details = []
            if employee.parent_id :
                emp_details.append({
                                    'emp_name':employee.name,
                                    'emp_id':employee.id,
                                    'parent':employee.parent_id.id,
                                    'emp_email':employee.work_email,
                                    'emp_job_title':employee.job_id.name
                                });
        for department in department_ids:
            dept_emp_childs = []
            dept_childs = []
            dept_details.append({
                                 'dept_id':"dept_"+str(department.id),
                                 'dept_name':department.name,
                                 'dept_parent_id':"dept_"+ str(department.parent_id.id),
                                 'dept_employee_id':department.manager_id.id,
                                 'dept_employee_name':department.manager_id.name,
                                 'dept_employee_email':department.manager_id.work_email,
                                 'dept_employee_job_title':department.manager_id.job_id.name,
                             })
        return [emp_details,dept_details]
