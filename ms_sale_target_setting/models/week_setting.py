from openerp.osv import fields,osv

class week_setting(osv.osv):
    _name = "setting.week"
    _description = "Weeks Setting"

    _columns = {
                'name':fields.char('Name'),
                'from_date':fields.date('From Date'),
                'to_date':fields.date('To Date'),
                'total_days_of_week':fields.integer('To Days Of Week'),
                'sequence':fields.integer('Sequence'),
                }
    
    def create(self, cursor, user, vals, context=None):
        print vals
        seq = self.pool.get('ir.sequence').get(cursor, user,
            'setting.week')
        vals['sequence'] = seq
        return super(week_setting, self).create(cursor, user, vals, context=context)
    
week_setting()