from openerp.osv import orm
from openerp.osv import fields, osv
import xlrd
from xlrd import open_workbook
from openerp.tools.translate import _

class tabletlogoutauth(osv.osv):
    _name = 'tablet.logout.auth'
    _columns = {  
                'date':fields.date('Date'),                         
                'password':fields.char('Password'),
              }

    