

# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


from openerp import tools
from openerp.osv import fields, osv
from openerp import workflow


class hr_abnormal_employee(osv.osv):
    _name = 'hrabnormal.employee'
    _description = "Abnormal Employee Setting"
     
    _columns = {
                
               'employee_id' :fields.many2one('hr.employee', string='Employee Name',),
                'job_id' :fields.many2one('hr.job', string='Job Type',),
               'employee_performance':fields.float('Performance (%)', required=True),
               'employee_abnormal':fields.float('Abnormal (%)'),
               'employee_contribution':fields.float('Contribution (%)'),
               'abnormal_date':fields.date('Date', required=True),

              }
    
    _defaults = {
                 'employee_performance': 100,
                 'employee_contribution': 0,
                 } 
    
    def onchange_employee_id(self, cr, uid, ids, employee_id, context=None):
        emp_obj = self.pool.get('hr.employee')
        
        job_id = False
        
        if employee_id:
            employee = emp_obj.browse(cr, uid, employee_id, context=context)
            job_id = employee.job_id.id
            
        return {'value': {'job_id':job_id, }}  
    
hr_abnormal_employee()
