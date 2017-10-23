from openerp.osv import fields, osv

class stock_config_settings(osv.osv_memory):
    _inherit = 'stock.config.settings'
    _columns={
         #'issued_location': fields.many2one('stock.location', 'Issued Location'),
         'issued_location': fields.related(
            'company_id', 'issued_location',
            type='many2one',
            relation='stock.location',
            string="Issued Location" 
            ),
              }
    
    def onchange_company_id(self, cr, uid, ids, company_id, context=None):
        #res = self.onchange_company_id(cr, uid, ids, company_id, context=context)
        res = {'value': {'issued_location':  False}}
        if company_id:
            company = self.pool.get('res.company').browse(cr, uid, company_id, context=context)
            res['value'].update({'issued_location': company.issued_location and company.issued_location.id})
        else: 
            res['value'].update({'issued_location': False 
                                 })
        return res