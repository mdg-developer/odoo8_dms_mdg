#-*- coding:utf-8 -*-
#
#
#    Copyright (C) 2011,2013 Michael Telahun Makonnen <mmakonnen@gmail.com>.
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

from openerp.osv import fields, osv
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as OE_DFORMAT
from openerp.osv import fields, osv, expression

class hr_employee(osv.osv):

    _inherit = "hr.employee"
    _columns = {
        'employee_id': fields.char('Badge ID'),
        'fingerprint_id': fields.char('FingerPrint ID'),
    }
    
    def create(self, cr, uid, vals, context=None):
        txnCode = section_code = None
        if vals:
#             txnCode = self.pool.get('ir.sequence').get(cr, uid,
#                 'hr.employee.code') or '/'
            txnCode = self.pool.get('ir.sequence').get(cr, uid,
                                                       'hr.employee.prefix') or '/'
            print 'txnCode>>>', txnCode
            if txnCode is not None:
                txnCode = txnCode[2:]
                
            section_obj = self.pool.get('hr.section') 
            if vals['section_id']:
                section = vals['section_id']
                section_id = section_obj.browse(cr,uid,section,context=context)
                if section_id:
                    section_code = section_id.parent_section_id.code or section_id.code
                    vals['employee_id'] = section_code +'-'+ txnCode
                    vals['fingerprint_id'] = txnCode   
              
        new_id = super(hr_employee, self).create(cr, uid, vals, context=context)
        print 'new_id>>>', new_id
        return new_id
hr_employee()
