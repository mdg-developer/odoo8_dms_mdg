from openerp import models,fields,api
import requests

class WooOrderDiscount(models.Model):
    _name = "woo.order.discount"
      
    api_id = fields.Integer("API Id") 
    order_id = fields.Integer("Order Id")
    cart_discount_label = fields.Char("Cart Discount Label") 
    odoo_discount_id = fields.Integer("Odoo Discount Id")