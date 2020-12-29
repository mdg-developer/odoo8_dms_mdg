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

from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as OE_DATEFORMAT
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as OE_DATETIMEFORMAT
from openerp.tools.translate import _
from openerp.osv import fields, osv
import dateutil.parser

class hr_employee(osv.osv):

    _inherit = 'hr.employee'                              
        
    def _calculate_age(self, cr, uid, ids, field_name, arg, context=None):

        res = dict.fromkeys(ids, False)        
        for emp in self.browse(cr, uid, ids, context=context):
            if emp.birthday:
                Bday = datetime.strptime(emp.birthday, OE_DATEFORMAT).date()                       
                Today = datetime.now().date()                
                res[emp.id] = (Today - Bday).days / 365                
        return res    

    _columns = {
        'age': fields.function(_calculate_age, type='integer', method=True, string='Age'),            
    } 
   




     


    
    
    
