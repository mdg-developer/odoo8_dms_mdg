from openerp.osv import fields, osv


class lead(osv.osv):
    _inherit = 'crm.lead'
    _columns = {
                'outlet_type': fields.many2one('outlettype.outlettype', 'Outlet Type', required=True),                
        }
    
lead()