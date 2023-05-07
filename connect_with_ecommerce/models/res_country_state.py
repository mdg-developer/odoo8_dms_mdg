from openerp.osv import fields, osv


class CountryState(osv.osv):
    _inherit = 'res.country.state'

    _columns = {
        # 'delivery_team_id':fields.many2one('crm.case.section', 'Delivery Team',required=False),
        'myanmar_name': fields.char('Myanmar Name', size=128),
    }


CountryState()