# -*- coding: utf-8 -*-
# Part of AppJetty. See LICENSE file for full copyright and licensing details.

from openerp import api, fields, models


class EventInherit(models.Model):
    _inherit = "event.event"

    event_cover_poster = fields.Binary(string="Event Image")
