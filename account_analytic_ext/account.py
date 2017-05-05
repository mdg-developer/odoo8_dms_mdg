
from openerp.osv import fields, osv
from openerp.tools.translate import _
import time
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta
from openerp import tools
import calendar
from openerp import SUPERUSER_ID


class account_move(osv.osv):
    _name = "account.move"
    
    _inherit = 'account.move'
    def _get_move_from_lines(self, cr, uid, ids, context=None):
        line_obj = self.pool.get('account.move.line')
        return [line.move_id.id for line in line_obj.browse(cr, uid, ids, context=context)]    
    _columns = {
        'analytic_account_id': fields.related('line_id', 'analytic_account_id', type="many2one", relation="account.analytic.account", string="Analytic Account", store={
            _name: (lambda self, cr,uid,ids,c: ids, ['line_id'], 10),
            'account.move.line': (_get_move_from_lines, ['analytic_account_id'],10)
            }),
                                      }

