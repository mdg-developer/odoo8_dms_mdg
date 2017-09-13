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

class hr_timesheet_settings(osv.Model):
    _name='hr.emp.bonus.settings'
    _columns = {
                'over_target_amount': fields.float('Over Target Amount'),
                'worker_w1_hit_ration': fields.float('Employee(%)'),
                'worker_w2_hit_ration': fields.float('Employee(%)'),
                'worker_w3_hit_ration': fields.float('Employee(%)'),
                'worker_w4_hit_ration': fields.float('Employee(%)'),
                'factory_w1_hit_ration': fields.float('Supervisor(%)'),
                'factory_w2_hit_ration': fields.float('Supervisor(%)'),
                'factory_w3_hit_ration': fields.float('Supervisor(%)'),
                'factory_w4_hit_ration': fields.float('Supervisor(%)'),
                'grade_a_emp':fields.float('Employee(%)'),
                'grade_b_emp':fields.float('Employee(%)'),
                'grade_c_emp':fields.float('Employee(%)'),
                'grade_d_emp':fields.float('Employee(%)'),
                'grade_a_sup':fields.float('Supervisor(%)'),
                'grade_b_sup':fields.float('Supervisor(%)'),
                'grade_c_sup':fields.float('Supervisor(%)'),
                'grade_d_sup':fields.float('Supervisor(%)'),

    }

   