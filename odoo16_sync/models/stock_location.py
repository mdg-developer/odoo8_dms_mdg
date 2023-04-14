from openerp.osv import orm
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
from openerp.osv.fields import _column
import xmlrpclib
import logging

class stock_location(osv.osv):
    _inherit = "stock.location"

    _columns = {

        'is_cellar_location': fields.boolean('Is Cellar18 Location'),
    }
    _defaults = {
        'is_cellar_location': False,
    }