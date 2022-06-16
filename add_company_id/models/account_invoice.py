from openerp.osv import fields, osv
  

class account_financial_report(osv.osv):
    _inherit = 'account.financial.report'
    _columns = {
                'company_id':fields.many2one('res.company','Company')
                }
    
account_financial_report()  