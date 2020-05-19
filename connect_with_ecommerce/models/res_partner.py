
from openerp.osv import fields,osv

class res_partner(osv.osv):
    _inherit = 'res.partner'
    
    _columns = {  
        'ecom_street': fields.char('Street'),
        'ecom_street2': fields.char('Street2'),      
        'ecom_city_id': fields.many2one('res.city', 'City', ondelete='restrict'),
        'ecom_state_id': fields.many2one("res.country.state", 'State', ondelete='restrict'),
        'ecom_country_id': fields.many2one('res.country', 'Country', ondelete='restrict'),       
        'ecom_township_id':fields.many2one('res.township','Township'),
        'ecom_phone': fields.char('Phone'),
#         'ecommerce_phone': fields.char('Phone'),     

    }

