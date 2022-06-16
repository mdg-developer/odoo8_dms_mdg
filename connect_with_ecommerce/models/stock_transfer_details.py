from openerp import models, fields, api

class stock_transfer_details(models.TransientModel):
    _inherit = 'stock.transfer_details'
    
    @api.one
    def do_detailed_transfer(self):
        
        res = super(stock_transfer_details,self).do_detailed_transfer()
        if self.picking_id:
            sale_order = self.env['sale.order'].search([('name','=', self.picking_id.origin)])
            if sale_order and sale_order.woo_order_number:
                one_signal_values = {
                                        'partner_id': sale_order.partner_id.id,
                                        'contents': "Your order " + sale_order.name + " is shipped.",
                                        'headings': "Burmart"
                                    }     
                self.env['one.signal.notification.messages'].create(one_signal_values)
        return res
    