
import time
from lxml import etree

from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _
from openerp.tools import float_compare
from openerp.report import report_sxw
import openerp


class hr_team(osv.osv):
    _name = 'hr.team'
    _description = 'HR Team'
    _columns = {
       'name':fields.char('HR Team'),
       'parent_id': fields.many2one('hr.team', 'Parent Team'),
       'company_id': fields.many2one('res.company', 'Company'),
       'parent_dep_id': fields.many2one('hr.department', 'Parent Department'),
       'manager_id': fields.many2one('hr.employee', 'Manager'),
       'analytic_id': fields.many2one('account.analytic.account', 'Analytic Account'),  
    } 
    
hr_team()