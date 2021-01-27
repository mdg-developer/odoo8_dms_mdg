from openerp import models,fields,api
class res_partner(models.Model):
    _inherit="res.partner"
    
    def _commercial_fields(self, cr, uid, context=None):
        result=super(res_partner,self)._commercial_fields(cr,uid,context=context)
        if 'last_reconciliation_date' in result:
            result.remove('last_reconciliation_date')
        return result