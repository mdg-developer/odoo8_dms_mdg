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


class incometax_report(models.Model):
    """Events Analysis"""
    _name = "incometax.report"

    _auto = False

    date = fields.Date('Date', readonly=True)
    employee_id = fields.Many2one('hr.employee', 'Employee Name', readonly=True)
    job_id = fields.Many2one('hr.job', 'Post', readonly=True)
    incometax=fields.Float('Income Amount')

    


    def init(self, cr):
        """Initialize the sql view for the event registration"""
        tools.drop_view_if_exists(cr, 'incometax_report')

        # TOFIX this request won't select events that have no registration
        cr.execute(""" CREATE VIEW incometax_report AS (

           select row_number() over (order by id) as id,employee_id,job_id,date,    
            round(sum(coalesce(child.incometax, 0))) as incometax    
            from
            (
                select payslip.*,
                case
                    when lower(payslip_line.code) = lower('ICT')
                    then payslip_line.total
                end as incometax
                FROM
                (
                    select HP.employee_id,HJ.id as job_id,HP.date_to as date,hp.id
                    from hr_contract HC ,hr_payslip HP,hr_job HJ                                     
                    where HC.job_id=HJ.id
                    and HC.id=HP.contract_id

                )payslip,
                (
                    select round(total,2) as total, slip_id, code
                    from hr_payslip_line 
                )payslip_line
                where payslip.id = payslip_line.slip_id
            )child
            group by employee_id, job_id,id,date
                
 
        )
        """)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
