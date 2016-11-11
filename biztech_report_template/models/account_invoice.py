# -*- coding: utf-8 -*-
import openerp
import datetime
from openerp import fields, models, api, tools
from openerp import tools
import os

env = os.environ.copy()

def formatLang(env, value, digits=None, grouping=True, monetary=False, dp=False, currency_obj=False):
    """
        Assuming 'Account' decimal.precision=3:
            formatLang(value) -> digits=2 (default)
            formatLang(value, digits=4) -> digits=4
            formatLang(value, dp='Account') -> digits=3
            formatLang(value, digits=5, dp='Account') -> digits=5
    """

    if digits is None:
        digits = DEFAULT_DIGITS = 2
        if dp:
            decimal_precision_obj = env['decimal.precision']
            digits = decimal_precision_obj.precision_get(dp)
        elif (hasattr(value, '_field') and isinstance(value._field, (float_field, function_field)) and value._field.digits):
                digits = value._field.digits[1]
                if not digits and digits is not 0:
                    digits = DEFAULT_DIGITS

    if isinstance(value, (str, unicode)) and not value:
        return ''

    lang = env.user.company_id.partner_id.lang or 'en_US'
    lang_objs = env['res.lang'].search([('code', '=', lang)])
    if not lang_objs:
        lang_objs = env['res.lang'].search([('code', '=', 'en_US')])
    lang_obj = lang_objs[0]

    res = lang_obj.format('%.' + str(digits) + 'f', value, grouping=grouping, monetary=monetary)

    if currency_obj:
        if currency_obj.position == 'after':
            res = '%s %s' % (res, currency_obj.symbol)
        elif currency_obj and currency_obj.position == 'before':
            res = '%s %s' % (currency_obj.symbol, res)
    return res

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'
    
    @api.model
    def _default_report_template(self):
        report_obj = self.env['ir.actions.report.xml']
        report_id = report_obj.search([('model', '=', 'account.invoice'), ('report_name' ,'=', 'biztech_report_template.report_invoice_template_custom')])
        if report_id:
            report_id = report_id[0]
        else:
            report_id = report_obj.search([('model', '=', 'account.invoice')])[0]
        return report_id

    @api.one
    @api.depends('partner_id')
    def _default_report_template1(self):
        report_obj = self.env['ir.actions.report.xml']
        report_id = report_obj.search([('model', '=', 'account.invoice'), ('report_name' ,'=', 'biztech_report_template.report_invoice_template_custom')])
        if report_id:
            report_id = report_id[0]
        else:
            report_id = report_obj.search([('model', '=', 'account.invoice')])[0]
        if self.report_template_id and self.report_template_id.id < report_id.id:
            self.write({'report_template_id': report_id and report_id.id or False})
            #self.report_template_id = report_id and report_id.id or False
        self.report_template_id1 = report_id and report_id.id or False

    @api.multi
    def invoice_print(self):
        """ Print the invoice and mark it as sent, so that we can see more
            easily the next step of the workflow
        """
        self.ensure_one()
        self.sent = True
        res = super(AccountInvoice, self).invoice_print()
        if self.report_template_id or self.partner_id and self.partner_id.report_template_id or self.company_id and self.company_id.report_template_id:
            report = self.env['report'].get_action(self, self.report_template_id and self.report_template_id.report_name or self.partner_id and self.partner_id.report_template_id.report_name or self.company_id and self.company_id.report_template_id.report_name)
            report.update({'report_name': 'account.report_invoice'})
            return report
        return res

    @api.multi
    def _get_street(self, partner):
        self.ensure_one()
        res = {}
        address = ''
        if partner.street:
            address = "%s" % (partner.street)
        if partner.street2:
            address += ", %s" % (partner.street2)
        html_text= str(tools.plaintext2html(address,container_tag=True))
        data = html_text.split('p>')
        if data:
            return data[1][:-2]
        return False
    
    @api.multi
    def _get_address_details(self, partner):
        self.ensure_one()
        res = {}
        address = ''
        if partner.city:
            address = "%s" % (partner.city)
        if partner.state_id.name:
            address += ", %s" % (partner.state_id.name)
        if partner.zip:
            address += ", %s" % (partner.zip)
        if partner.country_id.name:
            address += ", %s" % (partner.country_id.name)
        html_text= str(tools.plaintext2html(address,container_tag=True))
        data = html_text.split('p>')
        if data:
            return data[1][:-2]
        return False

    @api.multi
    def _get_origin_date(self, origin):
        self.ensure_one()
        res = {}
        sale_obj = self.env['sale.order']
        lang = self._context.get("lang")
        lang_obj = self.env['res.lang']
        ids = lang_obj.search([("code", "=", lang or 'en_US')])
        sale = sale_obj.search([('name', '=', origin)])
        if sale:
            timestamp = datetime.datetime.strptime(sale.date_order, tools.DEFAULT_SERVER_DATETIME_FORMAT)
            ts = openerp.osv.fields.datetime.context_timestamp(self._cr, self._uid, timestamp)
            n_date = ts.strftime(ids.date_format).decode('utf-8')
            if sale:
                return n_date
        return False

    @api.multi
    def _get_invoice_date(self):
        self.ensure_one()
        res = {}
        #sale_obj = self.env['sale.order']
        lang = self._context.get("lang")
        lang_obj = self.env['res.lang']
        ids = lang_obj.search([("code", "=", lang or 'en_US')])
        if self.date_invoice:
            timestamp = datetime.datetime.strptime(self.date_invoice, tools.DEFAULT_SERVER_DATE_FORMAT)
            ts = openerp.osv.fields.datetime.context_timestamp(self._cr, self._uid, timestamp)
            n_date = ts.strftime(ids.date_format).decode('utf-8')
            if self:
                return n_date
        return False

    @api.multi
    def _get_invoice_due_date(self):
        self.ensure_one()
        res = {}
        #sale_obj = self.env['sale.order']
        lang = self._context.get("lang")
        lang_obj = self.env['res.lang']
        ids = lang_obj.search([("code", "=", lang or 'en_US')])
        if self.date_due:
            timestamp = datetime.datetime.strptime(self.date_due, tools.DEFAULT_SERVER_DATE_FORMAT)
            ts = openerp.osv.fields.datetime.context_timestamp(self._cr, self._uid, timestamp)
            n_date = ts.strftime(ids.date_format).decode('utf-8')
            if self:
                return n_date
        return False

    @api.multi
    def _get_tax_amount(self, amount):
        self.ensure_one()
        res = {}
        currency = self.currency_id or self.company_id.currency_id
        res = formatLang(self.env, amount, currency_obj=currency)
        return res

    report_template_id1 = fields.Many2one('ir.actions.report.xml' , string="Invoice Template", compute='_default_report_template1', help="Please select Template report for Invoice", domain=[('model', '=', 'account.invoice')])
    report_template_id = fields.Many2one('ir.actions.report.xml' , string="Invoice Template", default=_default_report_template, help="Please select Template report for Invoice", domain=[('model', '=', 'account.invoice')])
