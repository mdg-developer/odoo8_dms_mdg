from openerp.osv import orm
from openerp.osv import fields, osv
import xlrd
from xlrd import open_workbook
from openerp.tools.translate import _
from datetime import datetime

class employee(osv.osv):
    _name = 'tablet.sync.log'
    _columns = {               
                'section_id':fields.many2one('crm.case.section','Sale Team'),
                'user_id':fields.many2one('res.users','Salesperson'),
                'sync_time':fields.datetime('Sync Time'),
                'status': fields.selection([('pull', 'Pull'), ('push', 'Push')],'Status'),
                'tablet_id':fields.many2one('tablets.information','Tablet Name'),
                'branch_id':fields.many2one('res.branch', 'Branch'),
              }

    