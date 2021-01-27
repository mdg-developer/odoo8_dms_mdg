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
import re
from openerp import tools, api


from HTMLParser import HTMLParser

import logging
_logger = logging.getLogger(__name__)


# http://stackoverflow.com/questions/38200739/extract-text-from-html-mail-odoo
class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []

    def handle_data(self, d):
        self.fed.append(d)

    def get_data(self):
        return ''.join(self.fed)


def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()


class SmsTemplate(models.Model):
    "Templates for sending sms"
    _name = "sms.template"
    _description = 'SMS Templates'
    _order = 'name'

    active = fields.Boolean(string="Active", default=True)
    name = fields.Char('Name', required=True)
    auto_delete = fields.Boolean("Auto Delete")
    globally_access = fields.Boolean(
        string="Global", help="if enable then it will consider normal(global) template.You can use it while sending the bulk message. If not enable the you have to select condition on which the template applies.")
    condition = fields.Selection([('order_placed', 'Order Placed'),
                                  ('order_confirm', 'Order Confirmed'),
                                  ('order_delivered', 'Order Delivered'),
                                  ('invoice_vaildate', 'Invoice Validate'),
                                  ('invoice_paid', 'Invoice Paid'),
                                  ('order_cancel', 'Order Cancelled'),
                                  ('before_invoice_is_due', 'Before invoice is due'),
                                  ('collection_noti', 'Invoice Due Date'),
                                  ('overdue_noti', 'After invoice is due'),
                                  ], string="Conditions", help="Condition on which the template has been applied.")
    model_id = fields.Many2one(
        'ir.model', 'Applies to', compute="onchange_condition", help="The kind of document with this template can be used. Note if not selected then it will consider normal(global) template.", store=True)
    model = fields.Char(related="model_id.model", string='Related Document Model',
                        select=True, store=True, readonly=True)
    sms_body_html = fields.Text('Body', translate=True, sanitize=False,
                                help="SMS text. You can also use ${object.partner_id} for dynamic text. Here partner_id is a field of the document(obj/model).", )

    @api.onchange('globally_access')
    def onchange_globally_access(self):
        if self.globally_access:
            self.condition = False

    def _get_partner_mobile(self, partner):
        mobile = partner.mobile if partner.mobile else partner.phone
        return mobile

    @api.depends('condition')
    def onchange_condition(self):
        if self.condition:
            if self.condition in ['order_placed', 'order_confirm', 'order_cancel']:
                model_id = self.env['ir.model'].search(
                    [('model', '=', 'sale.order')])
                self.model_id = model_id.id if model_id else False
            elif self.condition in ['order_delivered']:
                model_id = self.env['ir.model'].search(
                    [('model', '=', 'stock.picking')])
                self.model_id = model_id.id if model_id else False
            elif self.condition in ['invoice_vaildate', 'invoice_paid']:
                model_id = self.env['ir.model'].search(
                    [('model', '=', 'account.invoice')])
                self.model_id = model_id.id if model_id else False
            elif self.condition in ['before_invoice_is_due', 'collection_noti', 'overdue_noti']:
                model_id = self.env['ir.model'].search(
                    [('model', '=', 'account.invoice')])
                self.model_id = model_id.id if model_id else False
        else:
            self.model_id = False

    @api.onchange('model_id')
    def onchange_model_id(self):
        if self.model_id:
            self.model = self.model_id.model
        else:
            self.model = False

    @api.multi
    def get_body_data(self, obj):
        self.ensure_one()
        if obj:
            body_msg = self.env["email.template"].with_context(lang=obj.partner_id.lang).sudo().render_template_batch(
                self.sms_body_html, self.model, [obj.id])
            new_body_msg = re.sub("<.*?>", " ", body_msg[obj.id])
            return new_body_msg
            return " ".join(strip_tags(new_body_msg).split())

    @api.model
    def send_sms_using_template(self, mob_no, sms_tmpl, sms_gateway=None, obj=None):
        if not sms_gateway:
            gateway_id = self.env["sms.mail.server"].search(
                [], order='sequence asc', limit=1)
        else:
            gateway_id = sms_gateway
        if mob_no and sms_tmpl and obj:
            sms_sms_obj = self.env["sms.sms"].create({
                'sms_gateway_config_id': gateway_id.id,
                'partner_id': obj.partner_id.id,
                'to': mob_no,
                'group_type': 'individual',
                'auto_delete': sms_tmpl.auto_delete,
                'msg': sms_tmpl.get_body_data(obj),
                'template_id': False
            })
            sms_sms_obj.send_sms_via_gateway(
                sms_sms_obj.msg, [sms_sms_obj.to], from_mob=None, sms_gateway=gateway_id)
