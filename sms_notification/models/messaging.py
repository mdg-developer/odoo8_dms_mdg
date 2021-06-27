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
from openerp.exceptions import except_orm, Warning, RedirectWarning
from urllib3.exceptions import HTTPError
import datetime


import logging
_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.multi
    def action_confirm(self):
        self.ensure_one()
        res = super(SaleOrder, self).action_confirm()
        # Code to send sms to customer of the order.
        sms_template_objs = self.env["sms.template"].sudo().search(
            [('condition', '=', 'order_confirm')])
        for sms_template_obj in sms_template_objs:
            mobile = sms_template_obj._get_partner_mobile(self.partner_id)
            if mobile:
                sms_template_obj.send_sms_using_template(
                    mobile, sms_template_obj, obj=self)
        return res

    @api.multi
    def action_cancel(self):
        res = super(SaleOrder, self).action_cancel()
        sms_template_objs = self.env["sms.template"].sudo().search(
            [('condition', '=', 'order_cancel')])
        for obj in self:

            for sms_template_obj in sms_template_objs:
                mobile = sms_template_obj._get_partner_mobile(obj.partner_id)
                if mobile:
                    sms_template_obj.send_sms_using_template(
                        mobile, sms_template_obj, obj=obj)
        return res

    @api.multi
    def write(self, vals):
        result = super(SaleOrder, self).write(vals)
        for res in self:
            if res and vals.get("state", False) == 'sent':
                sms_template_objs = self.env["sms.template"].sudo().search(
                    [('condition', '=', 'order_placed')])
                for sms_template_obj in sms_template_objs:
                    mobile = sms_template_obj._get_partner_mobile(
                        res.partner_id)
                    if mobile:
                        sms_template_obj.send_sms_using_template(
                            mobile, sms_template_obj, obj=res)
        return result


class stock_picking(models.Model):
    _inherit = "stock.picking"

    @api.multi
    def write(self, vals):
        result = super(stock_picking, self).write(vals)
        for res in self:
            if res and vals.get("date_done", False):
                sms_template_objs = self.env["sms.template"].sudo().search(
                    [('condition', '=', 'order_delivered')])
                for sms_template_obj in sms_template_objs:
                    mobile = sms_template_obj._get_partner_mobile(
                        res.partner_id)
                    if mobile:
                        sms_template_obj.send_sms_using_template(
                            mobile, sms_template_obj, obj=res)
        return result


class account_invoice(models.Model):
    _inherit = "account.invoice"

    @api.multi
    def write(self, vals):
        result = super(account_invoice, self).write(vals)
        for res in self:
            if res and vals.get("state", False) in ["open", "paid"]:
                if vals.get('state') == 'open':
                    sms_template_objs = self.env["sms.template"].sudo().search(
                        [('condition', '=', 'invoice_vaildate')])
                    for sms_template_obj in sms_template_objs:
                        mobile = sms_template_obj._get_partner_mobile(
                            res.partner_id)
                        if mobile:
                            sms_template_obj.send_sms_using_template(
                            mobile, sms_template_obj, obj=res)
                if vals.get('state') == 'paid':
                    sms_template_objs = self.env["sms.template"].sudo().search(
                        [('condition', '=', 'invoice_paid')])
                    for sms_template_obj in sms_template_objs:
                        mobile = sms_template_obj._get_partner_mobile(
                            res.partner_id)
                        if mobile:
                            sms_template_obj.send_sms_using_template(
                                mobile, sms_template_obj, obj=res)
        return result
