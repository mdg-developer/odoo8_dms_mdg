'''
Created on 2015-03-25'

'''
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

from pytz import timezone, utc

import openerp.addons.decimal_precision as dp
from datetime import datetime, timedelta
from openerp import models, fields, api, _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as OE_DATEFORMAT
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as OE_DATETIMEFORMAT
from openerp.tools.translate import _
from openerp.osv import fields, osv


class hr_contract(osv.osv):
    _inherit = "hr.contract"

    def job_title(self, cr, uid, ids, fields, arg, context):
         
        print 'ids',ids
        x={}
        data = self.browse(cr, uid, ids)[0]
        emp_id = data.employee_id.id
        print 'emp_id',emp_id
        
        cr.execute('update hr_employee set contract_id=(select id from hr_contract where employee_id=%s order by create_date desc limit 1),\
                    job_id=(select hj.id from hr_contract hc,hr_job hj where hc.job_id=hj.id \
                    and employee_id=%s order by hc.create_date desc limit 1) \
                    where id=%s',(emp_id,emp_id,emp_id,)) 
        

        cr.execute('update hr_contract set department_id=(select department_id from hr_employee he where he.id=hr_contract.employee_id and he.id = %s);',(emp_id,))                   
        print 'success'
        return x    
    
    def onchange_job(self, cr, uid, ids, job_id=False, context=None):
        department_id = False
        user_id = False
        if job_id:
            job_record = self.pool.get('hr.job').browse(cr, uid, job_id, context=context)
            #print 'job_record-----', job_record
            department_id = job_record and job_record.department_id and job_record.department_id.id or False
            wage = job_record and job_record.wage
            allowance = job_record and job_record.allowance
            contribution = job_record and job_record.contribution
            s_wage = job_record and job_record.s_wage
            s_allowance = job_record and job_record.s_allowance
            s_contribution = job_record and job_record.s_contribution
            user_id = job_record and job_record.user_id and job_record.user_id.id or False
            return {'value': {'department_id': department_id, 'user_id': user_id, 'wage':wage, 'allowance':allowance, 'contribution':contribution, 's_wage':s_wage, 's_allowance':s_allowance, 's_contribution':s_contribution}}
    
    _columns = {
        'wage':fields.float('Probation Wage' , required=True, states={'draft': [('readonly', False)]
}),

        'allowance':fields.float('Probation Aid to Staff' , required=True, readonly=True, states={'draft': [('readonly', False)]
}),
        'contribution':fields.float("Probation Labour Welfare", required=True, readonly=True, states={'draft': [('readonly', False)]
}),
        's_wage':fields.float('Permanent Wage' , required=True, readonly=True,
                            states={'draft': [('readonly', False)]
}),
        's_allowance':fields.float('Permanent Aid to Staff' , required=True, readonly=True,
                             states={'draft': [('readonly', False)]
}),
        's_contribution':fields.float("Permanent Labour Welfare", required=True, readonly=True,
                           states={'draft': [('readonly', False)]}),
        'life_insurance':fields.float("Life Insurance", help="Amount of Life Insurance"),
        'year':fields.integer("Life Insurance Year", help="Year of Life Insurance (Default=one year)"),
         'job_id': fields.many2one('hr.job', 'Job Title', required=True),
         'allowance_amount':fields.float('Travelling Allowance'),
        'job_title': fields.function(job_title, type='many2one',obj='hr.job', string="Job",store=True),           

        }
    _defaults = {
        'year': 1,
    }    
hr_contract()