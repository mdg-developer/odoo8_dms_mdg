# -*- coding: utf-8 -*-
##########################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2017-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
##########################################################################

from openerp import models, fields, api, _
from openerp import SUPERUSER_ID
import re
import operator
from openerp.exceptions import except_orm, Warning, RedirectWarning

class SmsHistory(models.Model):
    """SMS history for every mobile number of sms."""

    _name = "sms.history"    
    _description = "Model for sms history."
    
    state = fields.Selection([
        ('success', 'Success'),
        ('fail', 'Fail'),        
    ], string="Status")
    partner_id = fields.Many2one("res.partner", string="Customer")
    phone = fields.Char(string="Phone")
    date = fields.Datetime(string="Date")
    message = fields.Text(string="Message")
    error_log = fields.Text(string="Error Log")
    user_id = fields.Many2one("res.users", string="User")
    name = fields.Char(string="Reference")
