#-*- coding:utf-8 -*-
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

import time

from datetime import datetime

from openerp import netsvc
from openerp.osv import fields, osv
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from openerp.tools.translate import _


class bonus_entry(osv.Model):

    _name = 'hr.bonus.entry'

    _columns = {
         'employee_id':fields.many2one('hr.employee','Employee', required=True,readonly=True,  states={'draft':[('readonly',False)]}),
        'department_id':fields.many2one('hr.department','Department', required=True,readonly=True,  states={'draft':[('readonly',False)]}),         
        'entry_date':fields.date('Entry Date', required=True,readonly=True,  states={'draft':[('readonly',False)]}),
        'state': fields.selection([
            ('draft', 'Draft'),
            ('confirm', 'Done'),
            ], 'Status', readonly=True),
        'entry_id': fields.many2one('hr.bonus.entry', 'Entry', ondelete='cascade', select=True, readonly=True, states={'draft':[('readonly',False)]}),                  
        'skill_type_id': fields.selection([('full_skill', 'Full Skill'), ('multi_skill', 'Multi Skill')], 'Skill Type',readonly=True,  states={'draft':[('readonly',False)]}),
        'critical_grade_id': fields.many2one('hr.critical.input','Critical Grade',readonly=True,  states={'draft':[('readonly',False)]}),
        'position_grade_id': fields.many2one('hr.position.input','Position Grade', readonly=True, states={'draft':[('readonly',False)]}),
        'language_grade_id': fields.many2one('hr.language.input','Language Grade', readonly=True, states={'draft':[('readonly',False)]}),
        'amount':fields.float('Special Bonus',readonly=True,  states={'draft':[('readonly',False)]}),
        'internal_note':fields.text('Reason',readonly=True,  states={'draft':[('readonly',False)]}),
        'special_amount':fields.float('Special Position Bonus',readonly=True,  states={'draft':[('readonly',False)]}),               
        'factory_driver_license_amt':fields.boolean('Factory Driver License Bonus',readonly=True,  states={'draft':[('readonly',False)]}),
        'electricity_certificate_amt':fields.boolean('Electricity Certificate Bonus',readonly=True,  states={'draft':[('readonly',False)]}),                
   }   
    _defaults = {
        'entry_date': fields.date.context_today,
        'state': 'draft',
        'paid_amount':0.0,
        'user_id': lambda cr, uid, id, c={}: id,
    }  
#     def unlink(self, cr, uid, ids, context=None):
#         sale_orders = self.read(cr, uid, ids, ['state'], context=context)
#         unlink_ids = []
#         for s in sale_orders:
#             if s['state'] in ['draft']:
#                 unlink_ids.append(s['id'])
#             else:
#                 raise osv.except_osv(_('Invalid Action!'), _('In order to delete a confirmed sales order, you must cancel it before!'))
# 
#         return osv.osv.unlink(self, cr, uid, unlink_ids, context=context)    
    def onchange_employee_id(self, cr, uid, ids, employee_id, context=None):
        emp_obj = self.pool.get('hr.employee')
        department_id = False
        company_id = False
        if employee_id:
            employee = emp_obj.browse(cr, uid, employee_id, context=context)
            department_id = employee.department_id.id
            company_id = employee.company_id.id
        return {'value': {'department_id': department_id}}
    def confirm(self, cr, uid, ids, context=None):
         for record in self.browse(cr, uid, ids, context=context):
            if record.employee_id and record.employee_id.parent_id and record.employee_id.parent_id.user_id:
                self.message_subscribe_users(cr, uid, [record.id], user_ids=[record.employee_id.parent_id.user_id.id], context=context)
         return self.write(cr, uid, ids, {'state':'confirm'})         
bonus_entry()       
