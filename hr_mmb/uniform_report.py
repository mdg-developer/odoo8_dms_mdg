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

from openerp import models, fields
from openerp import tools


class uniform_report(models.Model):
    """Events Analysis"""
    _name = "uniform.report"

    _auto = False

    date = fields.Date('Date', readonly=True)
    employee_id = fields.Many2one('hr.employee', 'Employee Name', readonly=True)
    job_id = fields.Many2one('hr.job', 'Post', readonly=True)
    e_id = fields.Integer('Time')
    uni_name = fields.Many2one('uniform.name', 'Uniform Name', readonly=True)
    amount = fields.Float('Amount')
    uni_time=fields.Integer('Uniform Time')
    qty=fields.Float('Quantity')

    


    def init(self, cr):
        """Initialize the sql view for the event registration"""
        tools.drop_view_if_exists(cr, 'uniform_report')

        # TOFIX this request won't select events that have no registration
        cr.execute(""" CREATE VIEW uniform_report AS (
              select * from

           (SELECT
                e.id::varchar || '/' || coalesce(r.id::varchar,'') AS id,
                e.employee_id as employee_id,
                e.job_id as job_id,
                e.date as date,
                r.name as uni_name,
                r.unit_amount AS amount,
                r.ref AS uni_time,
                r.unit_quantity AS qty
                
            FROM
                hr_ulm_expense e
                LEFT JOIN hr_ulm_expense_line r ON (e.id=r.expense_id)

            GROUP BY               
                e.employee_id,
                e.job_id,
                r.name,
                e.date,
                r.unit_amount,
                r.unit_quantity,
                e.id,
                r.id
            )A,

       (select count(employee_id) as e_id,employee_id as aaa_id from hr_ulm_expense group by employee_id)B
       where A.employee_id = B.aaa_id

        )
        """)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
