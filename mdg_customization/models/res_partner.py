from openerp.osv import osv, fields
from openerp import tools
from openerp.tools.translate import _
class res_partner(osv.osv):
    _inherit = "res.partner"
    _columns = {
        'partner_latitude': fields.float('Geo Latitude', digits=(16, 5), readonly=True),
        'partner_longitude': fields.float('Geo Longitude', digits=(16, 5), readonly=True),
        'date_localization': fields.date('Geo Localization Date'),
        'contact_note': fields.text('Note'),
         'gain_account_id': fields.property(
            type='many2one',
            relation='account.account',
            string="Gain Account",
        #    domain="[('type', '=', 'receivable')]",
          ),
            'loss_account_id': fields.property(
            type='many2one',
            relation='account.account',
            string="Loss Account",
           # domain="[('type', '=', 'receivable')]",
          ),


    }
