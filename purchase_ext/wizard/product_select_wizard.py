# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, fields, api


class product_select_wizard(models.TransientModel):
    _name = 'product.select.wizard'
    _description = 'Product Select Wizard'

    quantity = fields.Float('Quantity',
                            default='1.0')
    products_ids = fields.Many2many('product.product', string='Products',
        #domain=[('sale_ok', '=', True)],
    )

    @api.one
    def select_product(self):
        active_id = self._context['active_id']
        sale = self.env['purchase.order'].browse(active_id)
        for product_id in self.products_ids:
#             product = self.env['sale.order.line'].product_id_change(
#                 sale.pricelist_id.id,
#                 product_id.id,
#                 qty=self.quantity,
#                 uom=product_id.uom_id.id,
#                 partner_id=sale.partner_id.id)
            val = {
                'name': product_id.name,
                'product_quantity': self.quantity,
                'order_id': active_id,
                'product_id': product_id.id or False,
                'product_uos': product_id.uom_id.id,
                'price_unit': product_id.list_price,
                'date_planned':sale.date_order ,
                'supplier_code':product_id.supplier_code ,
                'state':'draft',
                #'tax_id': [(6, 0, product['value'].get('tax_id'))],
            }
            self.env['purchase.order.line'].create(val)
