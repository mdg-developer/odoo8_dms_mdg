from openerp.osv import fields, osv

class res_company(osv.osv):
    _inherit = "res.company"
    
    _columns = {
        'credit_invoice_msg': fields.text(string="Credit invoice message"),        
    }

class account_config_settings(osv.osv_memory):
    _name = 'account.config.settings'
    _inherit = 'account.config.settings'
    
    _columns = {      
        'credit_invoice_msg': fields.related(
              'company_id', 'credit_invoice_msg',
              type='text',            
              string="Credit invoice message"),       
    }  
    
    def onchange_company_id(self, cr, uid, ids, company_id, context=None):
        res = super(account_config_settings, self).onchange_company_id(cr, uid, ids, company_id, context=context)
        if company_id:
            company = self.pool.get('res.company').browse(cr, uid, company_id, context=context)
            res['value'].update({'credit_invoice_msg': company.credit_invoice_msg or False})                               
        else: 
            res['value'].update({'credit_invoice_msg': False})
        return res
    