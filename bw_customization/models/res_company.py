import logging

from openerp.osv import fields, osv
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

class res_company(osv.osv):
    _inherit = "res.company"
    _columns = {
        'issued_location_id': fields.many2one(
            'stock.location',string="Issued Location" 
            ),
        
    }

res_company()

class stock_config_settings(osv.osv_memory):
    _name = 'stock.config.settings'
    _inherit = 'stock.config.settings'

    
    _columns = {
        
      
      'issued_location_id': fields.related(
            'company_id', 'issued_location_id',
            type='many2one',
            relation='stock.location',
            string="Issued Location", 
           ),
      
        
    }
    
    def onchange_company_id(self, cr, uid, ids, company_id, context=None):
        res = {'value': {'issued_location_id':  False}}
        if company_id:
            company = self.pool.get('res.company').browse(cr, uid, company_id, context=context)
            res['value'].update({'issued_location_id': company.issued_location_id and company.issued_location_id.id or False})
        else: 
            res['value'].update({'issued_location_id': False})
        return res
    
    def create(self, cr, uid, vals, context=None):
        
        if vals['issued_location_id']:
            new_id = super(stock_config_settings, self).create(cr, uid, vals, context=context)
            issued_location = vals['issued_location_id']
            data = self.browse(cr, uid, new_id, context=context)
            if data:
                company_obj = self.pool.get('res.company')
                company_obj.write(cr,uid,data.company_id.id,{'issued_location_id':issued_location},context=context)
        else:
            new_id = super(stock_config_settings, self).create(cr, uid, vals, context=context)
            issued_location = vals['issued_location_id']
            data = self.browse(cr, uid, new_id, context=context)
            if data:
                company_obj = self.pool.get('res.company')
                company_obj.write(cr,uid,data.company_id.id,{'issued_location_id':issued_location},context=context)
                    
        #new_id = super(stock_config_settings, self).create(cr, uid, vals, context=context)
        return new_id        
    def write(self, cr, user, ids, vals, context=None):
        new_id = osv.osv_memory.write(self, cr, user, ids, vals, context=context)
        if vals['issued_location_id']:
            issued_location = vals['issued_location_id']
            data = self.browse(cr, user, new_id, context=context)
            if data:
                company_obj = self.pool.get('res.company')
                company_obj.write(cr,user,data.company_id.id,{'issued_location_id':issued_location},context=context)
        return new_id             
stock_config_settings()