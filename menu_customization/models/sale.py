from openerp.osv import fields, osv
  
class pre_sale_order(osv.osv):
    _inherit = 'pre.sale.order'
    
pre_sale_order()

class stock_request(osv.osv):
    _inherit = 'stock.requisition'
    
stock_request()
    
