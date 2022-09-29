from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
import time
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from openerp import SUPERUSER_ID


class sale_order(osv.osv):
    _inherit = "sale.order"
    _columns = {
        # 'cancel_user_id': fields.many2one('res.users', 'Cancel By'),
        # 'is_revised': fields.boolean('Is Revised', readonly=True, default=False),
        'revise_reason_id': fields.many2one('revise.reason', 'Revise Reason'),
        'cancel_reason_id': fields.many2one('cancel.reason', 'Cancel Reason'),
    }


sale_order()

