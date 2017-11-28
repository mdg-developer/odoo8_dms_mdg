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

import time
from lxml import etree

from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _
from openerp.tools import float_compare
from openerp.report import report_sxw
import openerp


class hr_functional_units(osv.osv):
    _name = 'hr.functional.units'
    _description = 'HR Functional Units'
    _columns = {
       'name':fields.char('Functional Units'),
       'manager_id': fields.many2one('hr.employee', 'Manager'),
       'company_id': fields.many2one('res.company', 'Company'),
       'parent_id': fields.many2one('hr.functional.units', 'Parent Functional Units'),
       'analytic_id': fields.many2one('account.analytic.account', 'Analytic Account'),  
    } 
    
    
hr_functional_units()