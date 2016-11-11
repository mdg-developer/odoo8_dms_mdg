# -*- coding: utf-8 -*-
import openerp
from openerp import fields, models, api, tools

template ={
           'report_invoice_template_custom': {
               'theme_color': '#a24689',
               'theme_text_color': '#FFFFFF',
               'text_color': '#000000',
               'company_color': '#4D4D4F',
               'customer_color': '#000000',
               'company_address_color': '#4D4D4F',
               'customer_address_color': '#000000',
               'odd_party_color': '#FFFFFF',
               'even_party_color': '#e6e8ed',
               },
           'report_invoice_template_custom_elegant' : {
               'theme_color': '#eb5554',
               'theme_text_color': '#FFFFFF',
               'text_color': '#000000',
               'company_color': '#4D4D4F',
               'customer_color': '#000000',
               'company_address_color': '#4D4D4F',
               'customer_address_color': '#000000',
               'odd_party_color': '#FFFFFF',
               'even_party_color': '#e6e8ed',
               },
           'report_invoice_template_custom_creative' : {
               'theme_color': '#0692C3',
               'theme_text_color': '#FFFFFF',
               'text_color': '#000000',
               'company_color': '#4D4D4F',
               'customer_color': '#000000',
               'company_address_color': '#4D4D4F',
               'customer_address_color': '#000000',
               'odd_party_color': '#FFFFFF',
               'even_party_color': '#e6e8ed',
               },
           'report_invoice_template_custom_professional' : {
               'theme_color': '#FF6340',
               'theme_text_color': '#FFFFFF',
               'text_color': '#000000',
               'company_color': '#4D4D4F',
               'customer_color': '#000000',
               'company_address_color': '#4D4D4F',
               'customer_address_color': '#000000',
               'odd_party_color': '#FFFFFF',
               'even_party_color': '#e6e8ed',
               },
           'report_invoice_template_custom_advanced' : {
               'theme_color': '#3D50A5',
               'theme_text_color': '#FFFFFF',
               'text_color': '#000000',
               'company_color': '#4D4D4F',
               'customer_color': '#000000',
               'company_address_color': '#4D4D4F',
               'customer_address_color': '#000000',
               'odd_party_color': '#FFFFFF',
               'even_party_color': '#e6e8ed',
               },
           'report_invoice_template_custom_exclusive' : {
               'theme_color': '#46A764',
               'theme_text_color': '#FFFFFF',
               'text_color': '#000000',
               'company_color': '#4D4D4F',
               'customer_color': '#000000',
               'company_address_color': '#4D4D4F',
               'customer_address_color': '#000000',
               'odd_party_color': '#FFFFFF',
               'even_party_color': '#e6e8ed',
               },
           }

class ResCompany(models.Model):
    _inherit = 'res.company'
    
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

    @api.model
    def _get_default_image(self, is_company, colorize=False):
        img_path = openerp.modules.get_module_resource(
            'biztech_report_template', 'static/src/img', 'avatar.png')
        with open(img_path, 'rb') as f:
            image = f.read()

        # colorize user avatars
        if not is_company:
            image = tools.image_colorize(image)

        return tools.image_resize_image_big(image.encode('base64'))

    @api.onchange('report_template_id')
    def _onchange_invoice_template(self):
        if self.report_template_id or self.partner_id and self.partner_id.report_template_id or self.company_id and self.company_id.report_template_id:
            report_name = self.report_template_id and self.report_template_id.report_name or self.partner_id and self.partner_id.report_template_id and self.partner.report_template_id.report_name or self.company_id and self.company_id.report_template_id and self.company_id.report_template_id.report_name
            template_name = report_name.split('.')
            template_value = template.get(str(template_name[1]))
            self.theme_color = template_value.get('theme_color', '#000000')
            self.theme_text_color  = template_value.get('theme_text_color', '#000000')
            self.text_color = template_value.get('text_color', '#000000')
            self.company_color = template_value.get('company_color', '#000000')
            self.company_address_color = template_value.get('company_address_color', '#000000')
            self.customer_color = template_value.get('customer_color', '#000000')
            self.customer_address_color = template_value.get('customer_address_color', '#000000')
            self.odd_party_color = template_value.get('odd_party_color', '#000000')
            self.even_party_color = template_value.get('even_party_color', '#000000')
        return

    theme_color = fields.Char(string="Template Base Color", required=True, help="Please set Hex color for Template.", default="#d4d2d2")
    theme_text_color = fields.Char(string="Template Text Color", required=True, help="Please set Hex color for Template Text.", default="#5cc2d2")
    text_color = fields.Char(string="General Text Color", required=True, help="Please set Hex color for General Text.", default="#5bb3d2")
    company_color = fields.Char(string="Company Name Color", required=True, help="Please set Hex color for Company Name.", default="#b30000")
    customer_color = fields.Char(string="Customer Name Color", required=True, help="Please set Hex color for Customer Name.", default="#2763a1")
    company_address_color = fields.Char(string="Company Address Color", required=True, help="Please set Hex color for Company Address.", default="#b32010")
    customer_address_color = fields.Char(string="Customer Address Color", required=True, help="Please set Hex color for Customer Address.", default="#2763c1")
    odd_party_color = fields.Char(string="Table Odd Parity Color", required=True, help="Please set Hex color for Table Odd Parity.", default="#aea8a8")
    even_party_color = fields.Char(string="Table Even Parity Color", required=True, help="Please set Hex color for Table Even Parity.", default="#aeb8aa")
    report_template_id1 = fields.Many2one('ir.actions.report.xml' , string="Default Invoice Template", compute='_default_report_template1', help="Please select Template report for Invoice", domain=[('model', '=', 'account.invoice')])
    report_template_id = fields.Many2one('ir.actions.report.xml' , string="Default Invoice Template", required=True, default=_default_report_template, help="Please select Template report for Invoice", domain=[('model', '=', 'account.invoice')])
    invoice_logo = fields.Binary("Report Logo", attachment=True, required=True, default=lambda self: self._get_default_image(False, True),  
        help="This field holds the image used as Logo for Invoice template report")
    is_description = fields.Boolean(string="Display Product Description", default=True, help="Please check it if you want to show product description in report.")
    watermark_logo = fields.Binary("Report Watermark Logo", default=lambda self: self._get_default_image(False, True), help="Please set Watermark Logo for Report.")
    is_company_bold = fields.Boolean(string="Display Company Name in Bold", default=False, help="Please check it if you want to show Company Name in Bold.")
    is_customer_bold = fields.Boolean(string="Display Customer Name in Bold", default=False, help="Please check it if you want to show Customer Name in Bold.")
