from openerp import models, fields, api, _
from openerp.exceptions import Warning

class woo_process_import_export(models.TransientModel):
    _name = 'woo.process.import.export'   
    
    instance_ids = fields.Many2many("woo.instance.ept",'woo_instance_import_export_rel','process_id','woo_instance_id',"Instances")
    
    update_price_in_product=fields.Boolean("Set Price",default=False)
    update_stock_in_product=fields.Boolean("Set Stock",default=False)
    publish=fields.Boolean("Publish In Website",default=False)

    is_export_products=fields.Boolean("Export Products")    
    sync_product_from_woo=fields.Boolean("Sync Products")
    
    is_publish_products=fields.Boolean("Publish Products")
    is_unpublish_products=fields.Boolean("UnPublish Products")
    is_update_products=fields.Boolean("Update Products")    
    is_update_stock=fields.Boolean("Update Stock")
    is_update_price=fields.Boolean("Update Price")     
    
    is_import_orders=fields.Boolean("Import Orders")
    is_import_customers=fields.Boolean("Import Customers")
    is_update_order_status=fields.Boolean("Update Order Status")
    
    is_export_product_tags=fields.Boolean("Export Product Tags")
    is_update_product_tags=fields.Boolean("Update Product Tags")
    
    is_export_product_categ=fields.Boolean("Export Product Category")
    is_update_product_categ=fields.Boolean("Update Product Category")
    sync_product_category_from_woo=fields.Boolean("Sync/Import Product Category")    
    sync_product_tags_from_woo=fields.Boolean("Sync/Import Product Tags")
    
    sync_woo_coupons=fields.Boolean("Sync Coupons")
    is_export_coupons=fields.Boolean("Export Coupons")
    is_update_coupon=fields.Boolean("Update Coupons")
    
    @api.model
    def default_get(self,fields):
        res = super(woo_process_import_export,self).default_get(fields)
        if 'instance_ids' in fields:
            instances = self.env['woo.instance.ept'].search([('state','=','confirmed')])
            res.update({'instance_ids':[(6,0,instances.ids)]})
        return res
    
    @api.multi
    def execute(self):                                          
        if self.is_export_products:
            self.export_products()
        if self.is_update_products:
            self.update_products()
        if self.is_update_price:
            self.update_price()
        if self.is_update_stock:
            self.update_stock_in_woo()
        if self.is_publish_products:
            self.publish_multiple_products()
        if self.is_unpublish_products:
            self.unpublish_multiple_products()    
        if self.sync_product_from_woo:
            self.sync_products()
        if self.is_import_orders:
            self.import_sale_orders()
        if self.is_import_customers:
            self.import_woo_customers()
        if self.is_update_order_status:
            self.update_order_status()
        if self.is_export_product_tags:
            self.export_product_tags()
        if self.is_update_product_tags:
            self.update_product_tags()
        if self.is_export_product_categ:
            self.export_product_categ()
        if self.is_update_product_categ:
            self.update_product_categ()
        if self.sync_product_category_from_woo:
            self.sync_product_category()
        if self.sync_product_tags_from_woo:
            self.sync_product_tags()      
        if self.sync_woo_coupons:
            self.sync_coupons() 
        if self.is_export_coupons:
            self.export_coupons()
        if self.is_update_coupon:
            self.update_coupons()                                                
        return True
    
    @api.multi
    def export_product_tags(self):
        product_tag_obj=self.env['woo.tags.ept']        
        instances=[]
        woo_tag_ids=[]
        if self._context.get('process')=='export_product_tags':
            woo_tag_ids=self._context.get('active_ids')
            instances = self.env['woo.instance.ept'].search([('state','=','confirmed')])
        else:                       
            instances=self.instance_ids
             
        for instance in instances:
            woo_product_tags=[]
            
            if woo_tag_ids:
                woo_product_tags=product_tag_obj.search([('woo_instance_id','=',instance.id),('id','in',woo_tag_ids),('exported_in_woo','=',False)])                
            else:
                woo_product_tags=product_tag_obj.search([('woo_instance_id','=',instance.id),('exported_in_woo','=',False)])                
                
            if woo_product_tags:
                product_tag_obj.export_product_tags(instance,woo_product_tags)
        return True   
   
    @api.multi
    def update_product_tags(self):
        product_tag_obj=self.env['woo.tags.ept']
        woo_tag_ids=[]
        instances=[]
        
        if self._context.get('process')=='update_product_tags':
            woo_tag_ids=self._context.get('active_ids')
            instances=self.env['woo.instance.ept'].search([('state','=','confirmed')])
        else:            
            instances=self.instance_ids
            
        for instance in instances:
            woo_product_tags=[]
            if woo_tag_ids:
                woo_product_tags=product_tag_obj.search([('woo_tag_id','!=',False),('woo_instance_id','=',instance.id),('id','in',woo_tag_ids),('exported_in_woo','=',True)])
            else:
                woo_product_tags=product_tag_obj.search([('woo_tag_id','!=',False),('woo_instance_id','=',instance.id),('exported_in_woo','=',True)])

            if woo_product_tags:
                product_tag_obj.update_product_tags_in_woo(instance,woo_product_tags)
        return True    
    
    """This method is used to export coupons from odoo to woocommerce"""
    @api.multi
    def export_coupons(self):
        woo_coupons_obj=self.env['woo.coupons.ept']        
        instances=[]
        woo_coupons_code=[]
        if self._context.get('process')=='export_coupons':
            woo_coupons_code=self._context.get('active_ids')
            instances = self.env['woo.instance.ept'].search([('state','=','confirmed')])
        else:                       
            instances=self.instance_ids
             
        for instance in instances:
            woo_coupons=[]
            
            if woo_coupons_code:
                woo_coupons=woo_coupons_obj.search([('woo_instance_id','=',instance.id),('id','in',woo_coupons_code)])                
            else:
                woo_coupons=woo_coupons_obj.search([('woo_instance_id','=',instance.id)])                
                
            if woo_coupons:
                woo_coupons_obj.export_coupons(instance,woo_coupons)
                
        return True
    
    
    """This method is used to sync coupons"""
    @api.multi
    def sync_coupons(self):
        coupons_obj=self.env['woo.coupons.ept']
        for instance in self.instance_ids:            
            coupons_obj.sync_coupons(instance)
        return True
    
    """This method is used to update coupons from odoo to woocommerce"""
    @api.multi
    def update_coupons(self):
        woo_coupons_obj=self.env['woo.coupons.ept']        
        instances=[]
        woo_coupons_code=[]
        if self._context.get('process')=='update_coupons':
            woo_coupons_code=self._context.get('active_ids')
            instances = self.env['woo.instance.ept'].search([('state','=','confirmed')])
        else:                       
            instances=self.instance_ids
             
        for instance in instances:
            woo_coupons=[]
            
            if woo_coupons_code:
                woo_coupons=woo_coupons_obj.search([('woo_instance_id','=',instance.id),('id','in',woo_coupons_code)])                
            else:
                woo_coupons=woo_coupons_obj.search([('woo_instance_id','=',instance.id)])                
                
            if woo_coupons:
                woo_coupons_obj.update_coupons(instance,woo_coupons)
                
        return True
    
    @api.multi
    def export_product_categ(self):
        product_categ_obj=self.env['woo.product.categ.ept']
        woo_categ_ids=[]
        woo_product_categs=[]
        instances=[]
        
        if self._context.get('process') == 'export_product_categ':
            woo_categ_ids=self._context.get('active_ids')
            instances = self.env['woo.instance.ept'].search([('state','=','confirmed')])
        else:
            instances=self.instance_ids                
                     
        for instance in instances:
            if woo_categ_ids:                      
                woo_product_categs=product_categ_obj.search([('woo_instance_id','=',instance.id),('exported_in_woo','=',False),('id','in',woo_categ_ids)])                
            else:
                woo_product_categs=product_categ_obj.search([('woo_instance_id','=',instance.id),('exported_in_woo','=',False)])
            if woo_product_categs:    
                product_categ_obj.export_product_categs(instance,woo_product_categs)
        return True
    
    @api.multi
    def update_product_categ(self):
        product_categ_obj=self.env['woo.product.categ.ept']        
        woo_categ_ids=[]
        woo_product_categs=[]
        instances=[]
        
        if self._context.get('process') == 'update_product_categ':
            woo_categ_ids=self._context.get('active_ids')
            instances = self.env['woo.instance.ept'].search([('state','=','confirmed')])
        else:
            instances=self.instance_ids            
            
        for instance in instances:
            if woo_categ_ids:
                woo_product_categs=product_categ_obj.search([('woo_categ_id','!=',False),('woo_instance_id','=',instance.id),('exported_in_woo','=',True),('id','in',woo_categ_ids)])
            else:
                woo_product_categs=product_categ_obj.search([('woo_categ_id','!=',False),('woo_instance_id','=',instance.id),('exported_in_woo','=',True)])

            if woo_product_categs:
                product_categ_obj.update_product_categs_in_woo(instance,woo_product_categs)
        return True
    
    @api.multi
    def sync_product_category(self):
        product_categ_obj=self.env['woo.product.categ.ept']
        for instance in self.instance_ids:            
            product_categ_obj.sync_product_category(instance)
        return True
    
    @api.multi
    def sync_product_tags(self):
        product_tags_obj=self.env['woo.tags.ept']
        for instance in self.instance_ids:            
            product_tags_obj.sync_product_tags(instance)
        return True         
    
    @api.multi
    def import_sale_orders(self):
        sale_order_obj=self.env['sale.order']        
        for instance in self.instance_ids:
            if instance.woo_version == 'old':
                sale_order_obj.import_woo_orders(instance)
            elif instance.woo_version == 'new':
                sale_order_obj.import_new_woo_orders(instance)
        return True
    
    @api.multi
    def import_woo_customers(self):
        res_partner_obj=self.env['res.partner']        
        for instance in self.instance_ids:        
            res_partner_obj.import_woo_customers(instance)
        return True
    
    @api.multi
    def update_order_status(self):
        sale_order_obj=self.env['sale.order']
        for instance in self.instance_ids:
            sale_order_obj.update_woo_order_status(instance)
        return True            
    
    @api.multi
    def prepare_product_for_export(self):
        woo_template_obj=self.env['woo.product.template.ept']
        woo_product_obj=self.env['woo.product.product.ept']
        woo_product_categ=self.env['woo.product.categ.ept']
        template_ids=self._context.get('active_ids',[])
        odoo_templates=self.env['product.template'].search([('id','in',template_ids),('type','!=','service')])
        for instance in self.instance_ids:
            for odoo_template in odoo_templates:
                woo_categ_ids = [(6, 0, [])]
                woo_template = woo_template_obj.search([('woo_instance_id','=',instance.id),('product_tmpl_id','=',odoo_template.id)])                
                if not woo_template:
                    categ_name = odoo_template.categ_id.name or ''
                    if categ_name:
                        ctg = categ_name.lower().replace('\'','\'\'')
                        self._cr.execute("select id from woo_product_categ_ept where LOWER(name) = '%s' and woo_instance_id = %s limit 1"%(ctg,instance.id))
                        woo_product_categ_id = self._cr.dictfetchall()
                        woo_categ_id = False            
                        if woo_product_categ_id:
                            woo_categ_id = woo_product_categ.browse(woo_product_categ_id[0].get('id'))                        
                        if not woo_categ_id:                        
                            woo_categ_id = woo_product_categ.create({'name':categ_name,'woo_instance_id':instance.id})
                        else:
                            woo_categ_id.write({'name':categ_name})
                        woo_categ_ids = [(6, 0, woo_categ_id.ids)]
                    if odoo_template.short_name:
                        product_name = odoo_template.short_name
                    else:
                        product_name = odoo_template.name
                    woo_template=woo_template_obj.create({'woo_instance_id':instance.id,'product_tmpl_id':odoo_template.id,'name':product_name,'woo_categ_ids':woo_categ_ids,'description':odoo_template.description_sale,'short_description':odoo_template.description})                
                for variant in odoo_template.product_variant_ids:
                    woo_variant = woo_product_obj.search([('woo_instance_id','=',instance.id),('product_id','=',variant.id)])
                    if not woo_variant:
                        woo_variant.create({'woo_instance_id':instance.id,'product_id':variant.id,'woo_template_id':woo_template.id,'default_code':variant.default_code,'name':variant.display_name,'woo_variant_url':variant.image_url or ''})                 
        return True

    @api.multi
    def publish_multiple_products(self):
        woo_template_obj=self.env['woo.product.template.ept']
        if self._context.get('process')=='publish_multiple_products':
            woo_template_ids=self._context.get('active_ids',[])
            woo_templates=woo_template_obj.search([('id','in',woo_template_ids),('exported_in_woo','=',True),('website_published','=',False)])
        else:
            woo_templates=woo_template_obj.search([('exported_in_woo','=',True),('website_published','=',False)])
        for woo_template in woo_templates:
            woo_template.woo_published()
        return True
    
    @api.multi
    def unpublish_multiple_products(self):
        woo_template_obj=self.env['woo.product.template.ept']
        if self._context.get('process')=='unpublish_multiple_products':
            woo_template_ids=self._context.get('active_ids',[])
            woo_templates=woo_template_obj.search([('id','in',woo_template_ids),('exported_in_woo','=',True),('website_published','=',True)])
        else:
            woo_templates=woo_template_obj.search([('exported_in_woo','=',True),('website_published','=',True)])
        for woo_template in woo_templates:
            woo_template.woo_unpublished()
        return True    
    
    @api.multi
    def update_products(self):
        woo_product_tmpl_obj=self.env['woo.product.template.ept']
        if self._context.get('process')=='update_products':
            woo_tmpl_ids=self._context.get('active_ids')
            instances=self.env['woo.instance.ept'].search([('state','=','confirmed')])
        else:
            woo_tmpl_ids=[]            
            instances=self.instance_ids            

        for instance in instances:
            if woo_tmpl_ids:
                woo_templates=woo_product_tmpl_obj.search([('woo_instance_id','=',instance.id),('id','in',woo_tmpl_ids),('exported_in_woo','=',True)])
            else:
                woo_templates=woo_product_tmpl_obj.search([('woo_instance_id','=',instance.id),('exported_in_woo','=',True)])
            if instance.woo_version == 'old':
                woo_product_tmpl_obj.update_products_in_woo(instance,woo_templates)
            elif instance.woo_version == 'new':
                woo_product_tmpl_obj.update_new_products_in_woo(instance,woo_templates)
        return True    
    
    @api.multi
    def update_stock_in_woo(self):
        woo_product_tmpl_obj=self.env['woo.product.template.ept']
        if self._context.get('process')=='update_stock':
            woo_tmpl_ids=self._context.get('active_ids')
            instances=self.env['woo.instance.ept'].search([('state','=','confirmed')])
        else:            
            woo_tmpl_ids=[]
            instances=self.instance_ids

        
        for instance in instances:
            if woo_tmpl_ids:
                woo_templates=woo_product_tmpl_obj.search([('woo_instance_id','=',instance.id),('id','in',woo_tmpl_ids)])
            else:
                woo_templates=woo_product_tmpl_obj.search([('woo_instance_id','=',instance.id),('exported_in_woo','=',True)])
            if instance.woo_version == 'old':    
                woo_product_tmpl_obj.update_stock_in_woo(instance,woo_templates)
            elif instance.woo_version == 'new':
                woo_product_tmpl_obj.update_new_stock_in_woo(instance,woo_templates)
        return True    
    
    @api.multi
    def update_price(self):
        woo_product_tmpl_obj=self.env['woo.product.template.ept']
        if self._context.get('process')=='update_price':
            woo_product_tmpl_ids=self._context.get('active_ids')
            instances=self.env['woo.instance.ept'].search([('state','=','confirmed')])
        else:            
            woo_product_tmpl_ids=[]
            instances=self.instance_ids

        for instance in instances:
            if woo_product_tmpl_ids:
                woo_templates=woo_product_tmpl_obj.search([('woo_instance_id','=',instance.id),('exported_in_woo','=',True),('id','in',woo_product_tmpl_ids)])
            else:
                woo_templates=woo_product_tmpl_obj.search([('woo_instance_id','=',instance.id),('exported_in_woo','=',True)])
            if instance.woo_version == 'old':
                woo_product_tmpl_obj.update_price_in_woo(instance,woo_templates)
            elif instance.woo_version == 'new':
                woo_product_tmpl_obj.update_new_price_in_woo(instance,woo_templates)
        return True    

    @api.multi
    def check_products(self,woo_templates):
        if self.env['woo.product.product.ept'].search([('woo_template_id','in',woo_templates.ids),('default_code','=',False)]):
            raise Warning("Default code is not set in some variants")
    
    @api.multi
    def filter_templates(self,woo_templates):
        filter_templates=[]
        for woo_template in woo_templates:
            if not self.env['woo.product.product.ept'].search([('woo_template_id','=',woo_template.id),('default_code','=',False)]):
                filter_templates.append(woo_template)
        return filter_templates    
    
    @api.multi
    def export_products(self):
        woo_product_tmpl_obj=self.env['woo.product.template.ept']
        if self._context.get('process')=='export_products':
            woo_template_ids=self._context.get('active_ids')
            instances = self.env['woo.instance.ept'].search([('state','=','confirmed')])
        else:            
            woo_template_ids=[]
            instances=self.instance_ids

        for instance in instances:
            if woo_template_ids:                
                woo_templates=woo_product_tmpl_obj.search([('woo_instance_id','=',instance.id),('id','in',woo_template_ids)])
                woo_templates=self.filter_templates(woo_templates)                
            else:
                woo_templates=woo_product_tmpl_obj.search([('woo_instance_id','=',instance.id),('exported_in_woo','=',False)])
                self.check_products(woo_templates)
            if instance.woo_version == 'old':                
                woo_product_tmpl_obj.export_products_in_woo(instance,woo_templates,self.update_price_in_product,self.update_stock_in_product,self.publish)
            elif instance.woo_version == 'new':
                woo_product_tmpl_obj.export_new_products_in_woo(instance,woo_templates,self.update_price_in_product,self.update_stock_in_product,self.publish)
        return True
    
    @api.multi
    def sync_selective_products(self):
        active_ids=self._context.get('active_ids')
        woo_template_obj=self.env['woo.product.template.ept']        
        woo_templates=woo_template_obj.search([('id','in',active_ids),('woo_tmpl_id','=',False)])
        if woo_templates:
            raise Warning("You can only sync already exported products")
        woo_templates=woo_template_obj.search([('id','in',active_ids)])
        for woo_template in woo_templates:
            if woo_template.woo_instance_id.woo_version == 'old':
                woo_template_obj.sync_products(woo_template.woo_instance_id,woo_tmpl_id=woo_template.woo_tmpl_id)
            elif woo_template.woo_instance_id.woo_version == 'new':
                woo_template_obj.sync_new_products(woo_template.woo_instance_id,woo_tmpl_id=woo_template.woo_tmpl_id)
        return True
    
    @api.multi
    def sync_products(self):
        woo_template_obj=self.env['woo.product.template.ept']
        for instance in self.instance_ids:
            if instance.woo_version == 'old':
                woo_template_obj.sync_products(instance)
            elif instance.woo_version == 'new':
                woo_template_obj.sync_new_products(instance)
        return True    