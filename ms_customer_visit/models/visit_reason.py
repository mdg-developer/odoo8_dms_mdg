import openerp
from openerp import tools, api
from openerp.osv import osv, fields

class visit_reason(osv.osv):
    _name = "visit.reason"
    _description = "Visit Reason"

    _columns = {
        'name': fields.char('Name'),
        'sequence': fields.char('Sequence'),
        'active': fields.boolean('Active', default=True),
    }

visit_reason()