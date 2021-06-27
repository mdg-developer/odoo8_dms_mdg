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
from openerp.tools.safe_eval import safe_eval


class BaseConfigSettings(models.TransientModel):
    _inherit = "base.config.settings"
    _description = "Base config for Twilio "

    def _check_twilio(self):
        result = self.env['ir.module.module'].search(
            [('name', '=', 'twilio_gateway')])
        if result:
            return True
        else:
            return False

    def _check_plivo(self):
        result = self.env['ir.module.module'].search(
            [('name', '=', 'plivo_gateway')])
        if result:
            return True
        else:
            return False

    def _check_clicksend(self):
        result = self.env['ir.module.module'].search(
            [('name', '=', 'clicksend_gateway')])
        if result:
            return True
        else:
            return False

    module_twilio_gateway = fields.Boolean(
        string='Install Twilio SMS Gateway', help='It will Install twilio sms gateway automatically.')
    is_twilio_in_addon = fields.Boolean(default=_check_twilio)

    module_plivo_gateway = fields.Boolean(
        string='Install Plivo SMS Gateway', help='It will Install plivo sms gateway automatically.')
    is_plivo_in_addon = fields.Boolean(default=_check_plivo)

    module_clicksend_gateway = fields.Boolean(
        string='Install Clicksend SMS Gateway', help='It will Install clicksend sms gateway automatically.')
    is_clicksend_in_addon = fields.Boolean(default=_check_clicksend)
