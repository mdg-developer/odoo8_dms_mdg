from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
from openerp.osv.fields import _column
import xmlrpclib

class product_pricelist(osv.osv):
    _inherit = "product.pricelist"
    
    _columns = {
                'city_id':fields.many2one('res.city','City'),
                'township_id':fields.many2one('res.township','Township'),
            }    
    
class product_pricelist_version(osv.osv):
    _inherit = 'product.pricelist.version'
    
    _columns = {
                'city_id' : fields.related('pricelist_id', 'city_id',
                                       type='many2one',
                                       readonly=True,
                                     relation='res.city',
                                       string='City'),
                'township_id' : fields.related('pricelist_id', 'township_id',
                                       type='many2one',
                                       readonly=True,
                                     relation='res.township',
                                       string='Township'),
            }