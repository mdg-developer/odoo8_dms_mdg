# -*- coding: utf-8 -*-
##############################################################################
#
# Odoo, Open Source Management Solution
# Copyright (C) 2013 webkul
# Author :
# www.webkul.com
#
##############################################################################

from openerp import models, fields, api, _

class res_users(models.Model):
	_inherit  = 'res.users'

	notify_sms = fields.Boolean(string='Receive Notification by SMS')
	mob_number = fields.Char(string="Mobile Number", help="Mobile number should be valid ten digit number including prefix using country code(e.g.+91) ")

