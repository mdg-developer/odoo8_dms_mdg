from openerp.osv import fields, osv

class res_users(osv.osv):
    
    _inherit='res.users'
    _columns={
              'branch_id':fields.many2one('branch',string='Branch'),
              'analytic_ids': fields.many2many('account.analytic.account', string='Analytic Account'),
              }
     
res_users()