from openerp.osv import fields, osv
from datetime import datetime

class res_partner(osv.osv):

    _inherit = 'res.partner'

    _columns = {
        'unverify_person_id':fields.many2one('res.users', 'Unverify Person'),

    }

    def unverify_lat_long(self, cr, uid, ids, context=None):
        partner_obj = self.pool.get('res.partner')
        for partner in self.browse(cr, uid, ids):
            vals = {'unverify_person_id': uid,
                    'verify': False,
                    # 'date_localization': datetime.now().date()
                    }
            # partner_obj.write(cr, uid, partner.id, vals, context=None)
            cr.execute('''update res_partner set unverify_person_id=%s,verify=False where id =%s''',
                       (uid, partner.id,))


        return True


res_partner()