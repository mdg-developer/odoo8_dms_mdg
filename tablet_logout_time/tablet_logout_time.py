from openerp.osv import orm
from openerp.osv import fields, osv
import xlrd
from xlrd import open_workbook
from openerp.tools.translate import _
from datetime import datetime

class employee(osv.osv):
    _name = 'tablet.logout.time'
    _columns = {               
                'section_id':fields.many2one('crm.case.section','Sale Team',readonly=True),
                'user_id':fields.many2one('res.users','Salesperson',readonly=True),
                'logout_time':fields.datetime('Logout Time',readonly=True),
                'branch_id':fields.many2one('res.branch', 'Branch',readonly=True),
              }

    