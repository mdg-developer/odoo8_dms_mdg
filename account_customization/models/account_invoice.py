import itertools
from lxml import etree
from openerp.osv import fields, osv
from openerp import models, fields, api, _
from openerp.tools import float_compare
import openerp.addons.decimal_precision as dp

class account_invoice(osv.osv):
    _inherit = 'account.invoice'

    @api.onchange('origin')
    def _onchange_origin(self):
        self.get_sale_order_date_order()

    @api.depends('origin')
    def get_sale_order_date_order(self):
        for rec in self:
            so = rec.env['sale.order'].search([('name', '=', rec.origin)], limit=1)
            rec.order_date = so.date_order if so else False

    order_date = fields.Datetime(compute='get_sale_order_date_order')
