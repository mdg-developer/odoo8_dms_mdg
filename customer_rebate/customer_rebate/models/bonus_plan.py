from openerp.osv import osv, fields
from openerp import netsvc
from openerp.tools.translate import _
from openerp import tools

class one_month_plan(osv.Model):
    _name = "bonus.plan"
    _description = __doc__
    def on_change_partner_id(self, cr, uid, ids, partner_id, context=None):
        values = {}
        if partner_id:
            partner = self.pool.get('res.partner').browse(cr, uid, partner_id, context=context)
            values = {
                'street': partner.street,
                'street2': partner.street2,
                'city': partner.city and partner.city.id or False,
                'state_id': partner.state_id and partner.state_id.id or False,
                'country_id': partner.country_id and partner.country_id.id or False,
                'township': partner.township and partner.township.id or False,
                'outlet_type': partner.outlet_type and partner.outlet_type.id or False,
            }
        return {'value': values}
        
    _columns = {
        
         'partner_id':fields.many2one('res.partner', 'Customer', ondelete='cascade',required=True),
         'name':fields.char('Description'),
         'street': fields.char('Street'),
        'street2': fields.char('Street2'),
        'city': fields.many2one('res.city', 'City', ondelete='restrict'),   
        'state_id': fields.many2one("res.country.state", 'State', ondelete='restrict'),
        'country_id': fields.many2one('res.country', 'Country', ondelete='restrict'),   
        'township': fields.many2one('res.township', 'Township', ondelete='restrict'),   
         'outlet_type': fields.many2one('outlettype.outlettype', 'Outlet Type', required=True),
         'date':fields.date('Date'),
         'shop_name':fields.char('Shop Name'),
         'year':fields.char('Year',required=True),
         'amount':fields.float('Amount',required=True),
         'note': fields.text('Remark'),
    }
one_month_plan()