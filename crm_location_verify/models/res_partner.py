from openerp.osv import fields, osv


class res_partner(osv.osv):
    _inherit = 'res.partner'
    _columns = {
        'verify':fields.boolean('Is Verify', default=False),
        'verify_person_id':fields.many2one('res.users', 'Verify Person'),
    }

    def verify_lat_long(self, cr, uid, ids, context=None):
        partner_obj = self.pool.get('res.partner')
        for partner in self.browse(cr, uid, ids):
            vals = {'verify_person_id': uid,
                    'verify': True,
                    # 'date_localization': datetime.now().date()
                    }
            # cr.execute('''update res_partner set verify_person_id=%s,verify=True,date_localization=%s where id =%s''',
            #            (uid, datetime.now().date(), partner.id,))

            cr.execute('''update res_partner set verify_person_id=%s,verify=True where id =%s''',
                       (uid, partner.id,))

        return True


res_partner()