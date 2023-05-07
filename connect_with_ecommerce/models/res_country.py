from openerp.osv import fields, osv

class Country(osv.osv):
    _inherit = 'res.country'

    _columns = {
        'myanmar_name': fields.char('Myanmar Name', size=128),
    }


Country()