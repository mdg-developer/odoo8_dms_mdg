from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
from openerp.osv.fields import _column


class product_template(osv.osv):
    _inherit = 'product.template'
    _columns = {
         'viss_value': fields.float('Viss', digits_compute=dp.get_precision('Cost Price')),
         'cbm_value': fields.float('CBM', digits_compute=dp.get_precision('Cost Price')),
         'ctn_pallet': fields.float('Ctn/Pallet'),
         'principal_description': fields.char('Principal Description'),
         'supplier_name': fields.many2one('res.partner', 'Supplier Name', domain="['is_supplier','=',True]"),
         'country': fields.many2one('res.country', 'Country'),
         'variety': fields.char('Variety'),
         'vintage': fields.many2one('sale.vintage', 'Vintage')
        }


class VintageSale(osv.osv):
    _name = 'sale.vintage'

    name = fields.char('Vintage Name')
    