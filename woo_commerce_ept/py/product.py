from openerp import models,fields,api
import requests

class product_product(models.Model):
    _inherit= 'product.product'
    
    @api.multi
    def _woo_product_count(self):
        woo_product_obj = self.env['woo.product.product.ept']
        for product in self:
            woo_products=woo_product_obj.search([('product_id','=',product.id)])
            product.woo_product_count = len(woo_products) if woo_products else 0
                           
    woo_product_count = fields.Integer(string='# Sales',compute='_woo_product_count')
    image_url = fields.Char(size=600, string='Image URL')    
    
class product_template(models.Model):
    _inherit= 'product.template'
    
    @api.multi
    def _woo_template_count(self):
        woo_product_template_obj = self.env['woo.product.template.ept']
        for template in self:
            woo_templates=woo_product_template_obj.search([('product_tmpl_id','=',template.id)])
            template.woo_template_count = len(woo_templates) if woo_templates else 0
                           
    woo_template_count = fields.Integer(string='# Sales',compute='_woo_template_count')   
    
    @api.model
    def auto_import_woo_product_template_ept(self):
        woo_instance_obj=self.env['woo.instance.ept']
        ctx = dict(self._context) or {}
        woo_instance_id = ctx.get('woo_instance_id',False)
        instance=woo_instance_obj.search([('state','=','confirmed')],limit=1)       
        
        woo_template_obj=self.env['woo.product.template.ept']
        if instance and instance.woo_version == 'old':
            woo_template_obj.sync_products(instance)
        elif instance and instance.woo_version == 'new':
            woo_template_obj.sync_new_products(instance)
        return True 
    
    @api.model
    def auto_update_woo_product_short_name(self):
        woo_instance_obj=self.env['woo.instance.ept']
        instance=woo_instance_obj.search([('state','=','confirmed')], limit=1)
        if instance:               
            wcapi = instance.connect_in_woo() 
            if wcapi:                
                response = wcapi.get('products')
                response_data = response.json()  
                if instance.woo_version == 'old':                
                    woo_products = response_data.get("products")                    
                elif instance.woo_version == 'new':
                    woo_products = response_data
                
                for product in woo_products:                
                    
                    product_id = product.get('id',False)
                    product_code = product.get('sku',False)
                    product_name = product.get('title',False)
                    product_obj = self.env['product.product'].search([('default_code', '=', product_code)])
                    if product_obj:
                        short_name = product_obj.product_tmpl_id.short_name  
                        if short_name:                    
                            if product_name != short_name:
                                data = {
                                    "product": {
                                        "title": short_name
                                    }
                                }                            
                                wcapi.put("products/%s"%(product_id), data).json()  
        return True 
    
class product_uom(models.Model):
    _inherit = 'product.uom'    
    
    is_sync_woo = fields.Boolean('Is Sync Woo', default=False)    
    