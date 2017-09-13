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

from openerp.osv import fields, osv

class hr_job(osv.osv):
    _inherit = "hr.job"
    _columns = {
                
                'cla_amount':fields.float('CLA Amount', size=50 , required=True),
                'day':fields.float('Day For CLA Calculation', size=50 , required=True),
                'wage':fields.float('Probation Wage' , required=True),
                'allowance':fields.float('Probation Aid to Staff' , required=True),
                'contribution':fields.float("Probation Labour Welfare", required=True),
                's_wage':fields.float('Permanent Wage' , required=True),
                's_allowance':fields.float('Permanent Aid to Staff' , required=True),
                's_contribution':fields.float("Permanent Labour Welfare", required=True),
                'sequence':fields.integer('Sequence'),
                'myanmar_jb_name': fields.char('Myanmar Job Name'),
        }
        
    def write(self, cr, uid, ids, vals, context=None):
        res = super(hr_job, self).write(cr, uid, ids, vals, context=context)      
        self.update_contract(cr, uid, ids, vals, context=context) 
         
        return res
    
    def update_contract(self, cr, uid, ids, vals, context=None):
        wage = allowance = contribution = s_wage = s_allowance = s_contribution = None
        hr_job_obj = self.pool.get('hr.job')
        
        if ids:
            for val in hr_job_obj.browse(cr, uid, ids[0], context=None):
                wage = val.wage
                allowance = val.allowance
                contribution = val.contribution
                s_wage = val.s_wage
                s_allowance = val.s_allowance
                s_contribution = val.s_contribution
                
        if ids:
            cr.execute("""update hr_contract set wage =%s, allowance=%s, contribution =%s, s_wage =%s, s_allowance =%s, s_contribution =%s where job_id = %s""", (wage, allowance, contribution, s_wage, s_allowance, s_contribution, ids[0],))  

        return True    
hr_job()
