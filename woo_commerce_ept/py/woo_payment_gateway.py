from openerp import models,fields

class woo_payment_gateway(models.Model):
    _name="woo.payment.gateway"
    
    name=fields.Char("Payment Method",required=1)
    code=fields.Char("Payment Code",required=1)
    woo_instance_id=fields.Many2one("woo.instance.ept",string="Instance",required=1)
    _sql_constraints=[('_payment_gateway_unique_constraint','unique(code,woo_instance_id)',"Payment Gateway code must be unique for instance")]