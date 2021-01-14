from openerp.osv import fields, osv

class stock_warehouse(osv.osv):
    _inherit = "stock.warehouse"
    
    _columns = {
        'main_location':fields.boolean('Is Main Location', default=False),
    }