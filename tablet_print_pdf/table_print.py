from openerp.osv import orm
from openerp.osv import fields, osv
import xlrd
from xlrd import open_workbook
from openerp.tools.translate import _
from datetime import datetime
import base64

class employee(osv.osv):
    _name = 'tablet.pdf.print'
    _columns = {
                'section_id':fields.many2one('crm.case.section','Sale Team'),
                'user_id':fields.many2one('res.users','Salesperson'),
              'name':fields.char('Description'),
              'print_date':fields.date('Date', readonly=True),
              'print_fname': fields.char('Filename', size=128),
              'print_file':fields.binary('File', required=True),
              }
    _defaults = {
            'print_date':datetime.today(),
                 }
    