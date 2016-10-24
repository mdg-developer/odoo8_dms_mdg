from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp

class sale_order(osv.osv):
    _inherit = "sale.order"
    _columns={
                     'delivery_id': fields.many2one('crm.case.section', 'Delivery Team'),

              }
sale_order()