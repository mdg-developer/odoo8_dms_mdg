from openerp.osv import fields, osv


class sync_log(osv.osv):
    _name = "sync.log"
    _description = "Sync Log"

    _columns = {
                'user_id':fields.many2one('res.users', 'User'),
                'date':fields.date('Date'),
                'sale_team_id':fields.many2one('crm.case.section', 'Sale Team'),
                'tablet_id':fields.many2one('tablets.information', 'Tablet'),
                'log_description':fields.text('Log Description')
  }
        
    def create(self, cr, user, vals, context=None):
        date = vals['date']
        tablet_id = vals['tablet_id']
        sale_team_id = vals['sale_team_id']
        log_description = vals['log_description']
        return super(sync_log, self).create(cr, user, vals, context=context)
sync_log()
