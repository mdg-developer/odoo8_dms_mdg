from openerp.osv import fields,osv

class res_partner(osv.osv):
    _inherit = 'res.partner'

    def _point_count(self, cr, uid, ids, field_name, arg, context=None):
        res = dict(map(lambda x: (x,0), ids))
        # The current user may not have access rights for sale orders
        try:
            for partner in self.browse(cr, uid, ids, context):
                res[partner.id] = len(partner.point_history_ids) + len(partner.mapped('child_ids.point_history_ids'))
        except:
            pass
        return res

    _columns = {
        'point_count': fields.function(_point_count, string='# of Point', type='integer'),
        'point_history_ids': fields.one2many('point.history','partner_id','Point History'),
        'membership_id':fields.many2one('membership.config', 'Membership Level'),
    }
    