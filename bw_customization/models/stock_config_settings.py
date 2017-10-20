from openerp.osv import fields, osv

class stock_config_settings(osv.osv_memory):
    _inherit = 'stock.config.settings'
    _columns={
         'issued_location': fields.many2one('stock.location', 'Issued Location'),
              }