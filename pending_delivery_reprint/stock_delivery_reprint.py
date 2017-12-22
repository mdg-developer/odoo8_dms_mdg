from openerp.osv import orm
from openerp.osv import fields, osv
import xlrd
from xlrd import open_workbook
from openerp.tools.translate import _

class stockdeliveryreprint(osv.osv):
    _name = 'stock.delivery.reprint'
    _columns = {
                'reprint_date':fields.date('Date',readonly=True),          
                'section_id':fields.many2one('crm.case.section','Sale Team'),
                'presaleorder_id':fields.char('Order Reference'),
                'customer':fields.many2one('res.partner','Customer'),
                'customer_code':fields.char('Customer Code'),
                'total_amount':fields.char('Total Amount'),
                'reprint_count':fields.char('Reprint Count'),
              }

    