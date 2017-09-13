
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


class hr_employee(osv.osv):
    _inherit = "hr.employee"

    _columns = {
                'english_name': fields.char('English Name'),
                'ssn_no':fields.char('SSN.No', size=50),
           'education_id': fields.many2one('hr.recruitment.degree', "Education"),
           'working_exp':fields.text('Working Experience', size=50),
           'other':fields.text('Other qualification', size=50),
                'is_fam_father':fields.boolean('Is Stay With Together'),
                'is_fam_mother':fields.boolean('Is Stay With Together'),
                 'f_name':fields.char("Father-In-Law's Name"),
                'is_father_inlaw':fields.boolean('Is Stay With Father-In-Law'),
                  'm_name':fields.char("Mother-In-Law's Name"),

                'is_mother_inlaw':fields.boolean('Is Stay With Mother-In-Law'),
                'religion':fields.char('Religion'),        
                'race':fields.char('Race'),   
                'payroll_cash':fields.boolean('By Cash'),    
                'payroll_bank':fields.boolean('By Card'),                        
        } 
    _defaults = {
        'is_father_inlaw': False,
        'is_mother_inlaw':False,
    }    
hr_employee()

