from openerp.osv import orm
from openerp.osv import fields, osv
import xlrd
from xlrd import open_workbook
from openerp.tools.translate import _

class stockdeliveryreprint(osv.osv):
    _name = 'stock.delivery.reprint'
    _columns = {
                'reprint_date':fields.date('Date',readonly=True),          
                'section_id':fields.many2one('crm.case.section','Sale Team',readonly=True),
                'branch_id':fields.many2one('res.branch','Branch',readonly=True),
                'presaleorder_id':fields.many2one('sale.order','Order Reference',readonly=True),
                'partner_id':fields.many2one('res.partner','Customer',readonly=True),
                'customer_code':fields.char('Customer Code',readonly=True),
                'total_amount':fields.char('Total Amount',readonly=True),
                'reprint_count':fields.char('Reprint Count',readonly=True),
              }

    