from openerp.osv import fields, osv

class CountryState(osv.osv):
    _inherit = 'res.country.state'
    
    _columns = {
    'name': fields.char('Division/State Name', required=True,
                        help='Administrative divisions of a country. E.g. Fed. State, Departement, Canton'),
    'code': fields.char('Division/State Code', size=3,
                        help='The state code in max. three chars.', required=True),
                }
    _sql_constraints = [
        ('name_uniq', 'unique (name)',
            'The name of the Division/State must be unique !'),
        ('code_uniq', 'unique (code)',
            'The code of the Division/State must be unique !')
    ]
    
CountryState()