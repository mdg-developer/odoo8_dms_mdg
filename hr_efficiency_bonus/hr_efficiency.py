# -*- coding:utf-8 -*-
#
#
#    Copyright (C) 2013 Michael Telahun Makonnen <mmakonnen@gmail.com>.
#    All Rights Reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#

from datetime import datetime
from dateutil.relativedelta import relativedelta

from openerp import netsvc
from openerp.osv import fields, osv
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from openerp.tools.translate import _


class hr_efficiency(osv.Model):

    _name = 'hr.efficiency.value'
    _description = 'Efficiency Bonus Information'
    _columns = {
        'employee_id': fields.many2one('hr.employee', 'Employee', required=True),
        'badge_id': fields.char('Badge ID'),
        'department_id': fields.many2one('hr.department', 'Department'),
        'section_id': fields.many2one('hr.section', 'Section'),
        'job_id': fields.many2one('hr.job', 'Position'),
        'date': fields.date('Date', required=True),
        'amount': fields.float('Amount', required=True),
        'note': fields.text('Reason'),
        'code':fields.char('Code'),


    }
    _rec_name = 'date'
    _defaults = {
        'date':fields.date.context_today,
    }
    
    def onchange_employee_id(self, cr, uid, ids, employee_id, context=None):
        emp_obj = self.pool.get('hr.employee')
        department_id = False
        job_id = False
        section_id = False
        badge_id = False    
        if employee_id:
            employee = emp_obj.browse(cr, uid, employee_id, context=context)
            department_id = employee.department_id.id
            job_id = employee.job_id.id
            section_id = employee.section_id.id
            badge_id = employee.employee_id

        return {'value': {'department_id': department_id, 'job_id':job_id, 'section_id':section_id, 'badge_id':badge_id}}    

