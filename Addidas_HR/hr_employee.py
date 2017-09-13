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


class hr_employee(osv.Model):

    _name = 'hr.employee'
    _inherit = 'hr.employee'

    _columns = {
         'supervisor':fields.boolean('Supervisor') ,     
        'employee_type': fields.selection([('direct', 'Direct'), ('indirect', 'Indirect')], 'Employee Type'),
           'working_no':fields.char('Working Number', required=True),
           'education_id': fields.many2one('hr.recruitment.degree', "Education"),
           'working_exp':fields.char('Working Experience', size=50),
           'other':fields.text('Other qualification', size=50),   
    }

    _defaults = {
        'supervisor': False,
    }    
    
   
    
    
