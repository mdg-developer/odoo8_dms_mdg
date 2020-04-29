from openerp import models, fields, api
from openerp.exceptions import Warning
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from datetime import datetime
 
 
class stock_transfer_details_items(models.TransientModel):
     
    _inherit = 'stock.transfer_details_items'
     
    bigger_uom_id = fields.Many2one('product.uom', string='Bigger UoM',
        #related='product_id.report_uom_id', copy=False,readonly=True,
        help="The commercial entity that will be used on Journal Entries for this invoice")    
     
    bigger_qty = fields.Float('Bigger Qty', digits=dp.get_precision('Product Unit of Measure'), default = 0.0)
     
    @api.onchange('quantity')
    def _compute_bigger_qty(self):
        bigger_qty = 0
        if self.quantity:
            if self.bigger_uom_id:
                bigger_uom = (1 / self.bigger_uom_id.factor)
                if bigger_uom > 0:
                    bigger_qty = self.quantity / bigger_uom
                if self.bigger_uom_id:
                    self.bigger_uom_id = self.bigger_uom_id    
                     
        if self.bigger_uom_id:
            self.bigger_uom_id = self.bigger_uom_id
                            
        self.bigger_qty = bigger_qty
         
stock_transfer_details_items()                    