from openerp.osv import fields,osv

class res_partner(osv.osv):
    _inherit = 'res.partner'

    def _point_count(self, cr, uid, ids, field_name, arg, context=None):
        res = dict(map(lambda x: (x,0), ids))
        # The current user may not have access rights for sale orders
        try:
            for partner in self.browse(cr, uid, ids, context):
                cr.execute("select COALESCE(sum(getting_point),0) from point_history where partner_id=%s", (partner.id,))    
                point_data = cr.fetchall()
                if point_data:
                    res[partner.id] = point_data[0][0]
#                     res[partner.id] = len(partner.point_history_ids) + len(partner.mapped('child_ids.point_history_ids'))
        except:
            pass
        return res
    
    def _get_membership_level(self, cr, uid, ids, field_name, arg, context=None):
        res = dict(map(lambda x: (x,0), ids))
        # The current user may not have access rights for sale orders
        try:
            membership_id = None
            for partner in self.browse(cr, uid, ids, context):                
                config = self.pool.get('membership.config').search(cr, uid, [], context=context)
                if config:
                    config_data = self.pool.get('membership.config').browse(cr, uid, config, context=context)
                    for data in config_data:
                        print 'partner.point_count',partner.point_count
                        print 'data.points',data.points
                        if partner.point_count >= data.points and partner.point_count > 0:
                            continue
                        elif partner.point_count <= data.points and partner.point_count > 0:
                            membership_id = data.id
                            break
                res[partner.id] = membership_id
        except:
            pass
        return res

    _columns = {
        'point_count': fields.function(_point_count, string='# of Point', type='integer'),
        'point_history_ids': fields.one2many('point.history','partner_id','Point History'),
        'membership_id':fields.function(_get_membership_level, type='many2one', relation='membership.config', string='Membership Level'),
        'total_points': fields.integer(string='Total Points'),
    }
    