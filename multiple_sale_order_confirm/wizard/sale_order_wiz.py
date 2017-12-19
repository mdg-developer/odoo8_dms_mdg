from openerp import models, fields, api, _

class MultiSaleOrderWiz(models.TransientModel):
    _name = 'multi.sale.order.wiz'

    @api.multi
    def confirm_multi_sale_order(self):
    	sale_order_ids = self.env['sale.order'].browse(self._context.get('active_ids'))
    	for sale in sale_order_ids:
    		if sale.state == 'draft':
    			sale.action_button_confirm()
