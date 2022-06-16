import logging
from datetime import datetime
from dateutil.relativedelta import relativedelta
from operator import itemgetter
import time

import openerp
from openerp import SUPERUSER_ID, api
from openerp import tools
from openerp.osv import fields, osv, expression
from openerp.tools.translate import _
from openerp.tools.float_utils import float_round as round
from openerp.tools.safe_eval import safe_eval as eval

import openerp.addons.decimal_precision as dp

_logger = logging.getLogger(__name__)


class account_move_reconcile(osv.osv):
    _inherit = "account.move.reconcile"
    
    def _check_same_partner(self, cr, uid, ids, context=None):
        for reconcile in self.browse(cr, uid, ids, context=context):
            move_lines = []
            if not reconcile.opening_reconciliation:
                if reconcile.line_id:
                    first_partner = reconcile.line_id[0].partner_id.id
                    move_lines = reconcile.line_id
                elif reconcile.line_partial_ids:
                    first_partner = reconcile.line_partial_ids[0].partner_id.id
                    move_lines = reconcile.line_partial_ids
                #if any([(line.account_id.type in ('receivable', 'payable') and line.partner_id.id  != first_partner) for line in move_lines]):
                #    return False
                for line in move_lines:
                    partner_id = line.partner_id.commercial_partner_id.id or line.partner_id.id
                    if (line.account_id.type in ('receivable', 'payable') and partner_id != first_partner):
                         return False
                    #return True
        return True

    _constraints = [
        (_check_same_partner, 'You can only reconcile journal items with the same partner.', ['line_id', 'line_partial_ids']),
    ]