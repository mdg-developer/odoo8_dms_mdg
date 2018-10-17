import os
import re
import openerp
from openerp import SUPERUSER_ID, tools
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.tools.safe_eval import safe_eval as eval
from openerp.tools import image_resize_image


class res_company(osv.osv):
    _inherit = "res.company"
    
    _columns = {
        'email': fields.related('partner_id', 'email', type='char', string="Email", store=True, size=1000),
    }