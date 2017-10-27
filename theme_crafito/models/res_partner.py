# -*- coding: utf-8 -*-
# Part of AppJetty. See LICENSE file for full copyright and licensing details.

from openerp import api, fields, models


class ResPartnerInherit(models.Model):

    _inherit = "res.partner"

    add_to_slider = fields.Boolean(string="Add to client slider")


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    include_inourteam = fields.Boolean(string="Enable to make the employee visible in snippet")
    emp_social_twitter = fields.Char(string="Twitter account", default="https://twitter.com/Odoo")
    emp_social_facebook = fields.Char(
        string="Facebook account", default="https://www.facebook.com/Odoo")
    emp_social_linkdin = fields.Char(
        string="Linkedin account", default="https://www.linkedin.com/company/odoo")
    emp_description = fields.Text(
        string="Short description about employee", translate=True)

    @api.model
    def create(self, vals):
        if vals.get('include_inourteam') == True:
            vals.update({'website_published': True})
        res = super(HrEmployee, self).create(vals)
        return res

    @api.multi
    def write(self, vals):
        if vals.get('include_inourteam') == True:
            vals.update({'website_published': True})
        if vals.get('include_inourteam') == False:
            vals.update({'website_published': False})
        res = super(HrEmployee, self).write(vals)
        return res
