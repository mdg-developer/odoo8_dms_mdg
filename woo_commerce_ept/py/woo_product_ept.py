from openerp import models, fields, api, _
import openerp.addons.decimal_precision as dp
from datetime import datetime
from .. img_upload import img_file_upload
import base64
import requests
import hashlib
from openerp.osv.orm import except_orm

class woo_product_template_ept(models.Model):
    _name="woo.product.template.ept"
    _order='product_tmpl_id'

    @api.multi
    @api.depends('woo_product_ids.exported_in_woo','woo_product_ids.variant_id')
    def get_total_sync_variants(self):
        woo_product_obj=self.env['woo.product.product.ept']
        for template in self:
            variants=woo_product_obj.search([('id','in',template.woo_product_ids.ids),('exported_in_woo','=',True),('variant_id','!=',False)]) 
            template.total_sync_variants=len(variants.ids)
           
    name=fields.Char("Name")
    woo_instance_id=fields.Many2one("woo.instance.ept","Instance",required=1)
    product_tmpl_id=fields.Many2one("product.template","Product Template",required=1)
    woo_categ_ids = fields.Many2many('woo.product.categ.ept','woo_template_categ_rel','woo_template_id','woo_categ_id',"Categories")
    woo_tag_ids = fields.Many2many('woo.tags.ept','woo_template_tags_rel','woo_template_id','woo_tag_id',"Tags")
    woo_tmpl_id=fields.Char("Woo Template Id")
    exported_in_woo=fields.Boolean("Exported In Woo")
    woo_product_ids=fields.One2many("woo.product.product.ept","woo_template_id","Products")
    woo_gallery_image_ids=fields.One2many("woo.product.image.ept","woo_product_tmpl_id","Images")    
    created_at=fields.Datetime("Created At")
    updated_at=fields.Datetime("Updated At")           
    taxable=fields.Boolean("Taxable",default=True)    
    website_published=fields.Boolean('Available in the website', copy=False)    
    description=fields.Html("Description")
    short_description=fields.Html("Short Description")
    total_variants_in_woo=fields.Integer("Total Varaints in Woo",default=0,help="Total Variants in WooCommerce,\nDisplay after sync products")
    total_sync_variants=fields.Integer("Total Sync Variants",compute="get_total_sync_variants",store=True)
    
    
    @api.onchange("product_tmpl_id")
    def on_change_product(self):
        for record in self:
            record.name=record.product_tmpl_id.name            

    @api.multi
    def woo_unpublished(self):
        instance=self.woo_instance_id
        wcapi = instance.connect_in_woo()
        transaction_log_obj=self.env['woo.transaction.log']
        if self.woo_tmpl_id:
            info = {'status':'draft'}
            data = info
            if instance.woo_version == 'old':
                data = {'product':info}                       
            res = wcapi.put('products/%s'%(self.woo_tmpl_id),data)
            if not isinstance(res,requests.models.Response):               
                transaction_log_obj.create({'message': "Unpublish Product \nResponse is not in proper format :: %s"%(res),
                                             'mismatch_details':True,
                                             'type':'product',
                                             'woo_instance_id':instance.id
                                            })
                return True
            if res.status_code not in [200,201]:
                transaction_log_obj.create(
                                    {'message':res.content,
                                     'mismatch_details':True,
                                     'type':'product',
                                     'woo_instance_id':instance.id
                                    })
                return True            
            response = res.json()
            if instance.woo_version == 'old':            
                errors = response.get('errors','')
                if errors:
                    message = errors[0].get('message')
                    transaction_log_obj.create(
                                                {'message':"Can not Unpublish Template,  %s"%(message),
                                                 'mismatch_details':True,
                                                 'type':'product',
                                                 'woo_instance_id':instance.id
                                                })
                else:                    
                    self.write({'website_published':False})
            elif instance.woo_version == 'new':
                if response.get('data',{}) and response.get('data',{}).get('status') not in [200,201]:
                    message = response.get('message')
                    transaction_log_obj.create(
                                                {'message':"Can not Unpublish Template,  %s"%(message),
                                                 'mismatch_details':True,
                                                 'type':'product',
                                                 'woo_instance_id':instance.id
                                                })
                else:                                            
                    self.write({'website_published':False})
        return True           

    @api.multi
    def woo_published(self):
        instance=self.woo_instance_id
        wcapi = instance.connect_in_woo()
        transaction_log_obj=self.env['woo.transaction.log']
        if self.woo_tmpl_id:
            info = {'status':'publish'}
            data = info
            if instance.woo_version == 'old':
                data = {'product':info}
            res = wcapi.put('products/%s'%(self.woo_tmpl_id),data)
            if not isinstance(res,requests.models.Response):                
                transaction_log_obj.create({'message': "Publish Product \nResponse is not in proper format :: %s"%(res),
                                             'mismatch_details':True,
                                             'type':'product',
                                             'woo_instance_id':instance.id
                                            })
                return True
            if res.status_code not in [200,201]:
                transaction_log_obj.create(
                                    {'message':res.content,
                                     'mismatch_details':True,
                                     'type':'product',
                                     'woo_instance_id':instance.id
                                    })
                return True            
            response =res.json()
            if instance.woo_version == 'old':            
                errors = response.get('errors','')
                if errors:
                    message = errors[0].get('message')
                    transaction_log_obj.create(
                                                {'message':"Can not Publish Template,  %s"%(message),
                                                 'mismatch_details':True,
                                                 'type':'product',
                                                 'woo_instance_id':instance.id
                                                })
                else:                    
                    self.write({'website_published':True})
                    
            elif instance.woo_version == 'new':
                if response.get('data',{}) and response.get('data',{}).get('status') not in [200,201]:
                    message = response.get('message')
                    transaction_log_obj.create(
                                                {'message':"Can not Publish Template,  %s"%(message),
                                                 'mismatch_details':True,
                                                 'type':'product',
                                                 'woo_instance_id':instance.id
                                                })
                else:                    
                    self.write({'website_published':True})
        return True
    
    @api.multi
    def sync_new_woo_categ_with_product(self,wcapi,instance,woo_categories):
        obj_woo_product_categ=self.env['woo.product.categ.ept']
        categ_ids = []
        for woo_category in woo_categories:
            woo_product_categ = obj_woo_product_categ.search([('woo_categ_id','=',woo_category.get('id')),('woo_instance_id','=',instance.id)],limit=1)
            if not woo_product_categ:
                woo_product_categ = obj_woo_product_categ.search([('slug','=',woo_category.get('slug')),('woo_instance_id','=',instance.id)],limit=1)
            if woo_product_categ:
                woo_product_categ.write({'woo_categ_id':woo_category.get('id'),'name':woo_category.get('name'),'display':woo_category.get('display'),'slug':woo_category.get('slug'),'exported_in_woo':True})
                obj_woo_product_categ.sync_product_category(instance,woo_product_categ=woo_product_categ)
                categ_ids.append(woo_product_categ.id)                                                   
            else:
                woo_product_categ = obj_woo_product_categ.create({'woo_categ_id':woo_category.get('id'),'name':woo_category.get('name'),'display':woo_category.get('display'),'slug':woo_category.get('slug'),'woo_instance_id':instance.id,'exported_in_woo':True})
                obj_woo_product_categ.sync_product_category(instance,woo_product_categ=woo_product_categ)
                woo_product_categ and categ_ids.append(woo_product_categ.id)                        
        return categ_ids
    
    @api.multi
    def sync_new_woo_tags_with_product(self,wcapi,instance,woo_tags):
        obj_woo_product_tags=self.env['woo.tags.ept']        
        tag_ids = []
        for woo_tag in woo_tags:
            woo_product_tag = obj_woo_product_tags.search([('woo_tag_id','=',woo_tag.get('id')),('woo_instance_id','=',instance.id)],limit=1)
            if not woo_product_tag:
                woo_product_tag = obj_woo_product_tags.search([('slug','=',woo_tag.get('slug')),('woo_instance_id','=',instance.id)],limit=1)
            if woo_product_tag:
                woo_product_tag.write({'name':woo_tag.get('name'),'slug':woo_tag.get('slug'),'exported_in_woo':True})
                obj_woo_product_tags.sync_product_tags(instance,woo_product_tag=woo_product_tag)
                tag_ids.append(woo_product_tag.id)
            else:
                woo_product_tag = obj_woo_product_tags.create({'woo_tag_id':woo_tag.get('id'),'name':woo_tag.get('name'),'slug':woo_tag.get('slug'),'woo_instance_id':instance.id,'exported_in_woo':True})
                obj_woo_product_tags.sync_product_tags(instance,woo_product_tag=woo_product_tag)
                woo_product_tag and tag_ids.append(woo_product_tag.id)
        return tag_ids   
    
    @api.multi
    def sync_woo_categ_with_product(self,wcapi,instance,woo_categories):
        woo_product_categ=self.env['woo.product.categ.ept']
        categ_ids = []
        for woo_category in woo_categories:
            ctg = woo_category.lower().replace('\'','\'\'')
            self._cr.execute("select id from woo_product_categ_ept where LOWER(name) = '%s' and woo_instance_id = %s limit 1"%(ctg,instance.id))
            woo_product_categ_id = self._cr.dictfetchall()
            woo_categ=False
            if woo_product_categ_id:
                woo_categ = woo_product_categ.browse(woo_product_categ_id[0].get('id'))                
                categ_ids.append(woo_categ.id)                
                woo_categ = woo_product_categ.sync_product_category(instance,woo_product_categ=woo_categ)                    
            else:
                woo_categ = woo_product_categ.sync_product_category(instance,woo_product_categ_name=woo_category)
                woo_categ and categ_ids.append(woo_categ.id)                        
        return categ_ids
    
    @api.multi
    def sync_woo_tags_with_product(self,wcapi,instance,woo_tags):
        transaction_log_obj=self.env['woo.transaction.log']
        woo_product_tags=self.env['woo.tags.ept']        
        tag_ids = []
        for woo_tag in woo_tags:
            tag = woo_tag.lower().replace('\'','\'\'')
            self._cr.execute("select id from woo_tags_ept where LOWER(name) = '%s' and woo_instance_id = %s limit 1"%(tag,instance.id))
            woo_product_tag_id = self._cr.dictfetchall()
            woo_product_tag=False
            if woo_product_tag_id:
                woo_product_tag = woo_product_tags.browse(woo_product_tag_id[0].get('id'))
                tag_ids.append(woo_product_tag.id)                                                  
            else:
                tag_res=wcapi.get("products/tags?fields=id,name")
                if not isinstance(tag_res,requests.models.Response):                    
                    transaction_log_obj.create({'message': "Get Product Tags\nResponse is not in proper format :: %s"%(tag_res),
                                             'mismatch_details':True,
                                             'type':'product',
                                             'woo_instance_id':instance.id
                                            })
                    continue
                if tag_res.status_code not in [200,201]:
                    transaction_log_obj.create(
                                        {'message':tag_res.content,
                                         'mismatch_details':True,
                                         'type':'product',
                                         'woo_instance_id':instance.id
                                        })
                    continue                
                tag_response = tag_res.json()                
                product_tags = tag_response.get('product_tags')
                if isinstance(product_tags,dict):
                    product_tags = [product_tags]
                for product_tag in product_tags:
                    tag_name = product_tag.get('name')
                    if tag_name == woo_tag:
                        single_tag_res = wcapi.get("products/tags/%s"%(product_tag.get('id')))
                        if not isinstance(single_tag_res,requests.models.Response):                            
                            transaction_log_obj.create({'message': "Get Product Tags\nResponse is not in proper format :: %s"%(single_tag_res),
                                             'mismatch_details':True,
                                             'type':'product',
                                             'woo_instance_id':instance.id
                                            })
                            continue
                        single_tag_response = single_tag_res.json()
                        single_tag = single_tag_response.get('product_tag')
                        
                        tag_vals = {'name':woo_tag,'woo_instance_id':instance.id,'description':single_tag.get('description'),'exported_in_woo':True,'woo_tag_id':single_tag.get('id')}
                            
                        woo_product_tag = woo_product_tags.create(tag_vals)
                        woo_product_tag and tag_ids.append(woo_product_tag.id)
                        break        
        return tag_ids    
    
    def import_all_draft_products(self,wcapi,instance,transaction_log_obj,page):
        res=wcapi.get('products?filter[post_status]=draft&page=%s'%(page))
        if not isinstance(res,requests.models.Response):            
            transaction_log_obj.create({'message': "Get All Draft Products\nResponse is not in proper format :: %s"%(res),
                                             'mismatch_details':True,
                                             'type':'product',
                                             'woo_instance_id':instance.id
                                            })
            return []
        if res.status_code not in [200,201]:
            transaction_log_obj.create(
                                {'message':res.content,
                                 'mismatch_details':True,
                                 'type':'product',
                                 'woo_instance_id':instance.id
                                })            
            return []
        response = res.json()                   
        return response.get('products')    
    
    def import_all_products(self,wcapi,instance,transaction_log_obj,page):
        res=wcapi.get('products?page=%s'%(page))
        if not isinstance(res,requests.models.Response):            
            transaction_log_obj.create({'message': "Get All Products\nResponse is not in proper format :: %s"%(res),
                                             'mismatch_details':True,
                                             'type':'product',
                                             'woo_instance_id':instance.id
                                            })
            return []
        if res.status_code not in [200,201]:
            transaction_log_obj.create(
                                {'message':res.content,
                                 'mismatch_details':True,
                                 'type':'product',
                                 'woo_instance_id':instance.id
                                })            
            return []
        response = res.json()
        if instance.woo_version == 'old':
            errors = response.get('errors','')
            if errors:
                message = errors[0].get('message')
                transaction_log_obj.create(
                                            {'message':message,
                                             'mismatch_details':True,
                                             'type':'product',
                                             'woo_instance_id':instance.id
                                            })
                return []
            return response.get('products')
        elif instance.woo_version == 'new':            
            return response
   
    @api.multi
    def sync_products(self,instance,woo_tmpl_id=False,update_price=False,update_templates=True):
        woo_product_obj=self.env['woo.product.product.ept']
        transaction_log_obj=self.env["woo.transaction.log"]
        woo_product_img = self.env['woo.product.image.ept']        
        odoo_product_obj=self.env['product.product']                       
        wcapi = instance.connect_in_woo()
        
        categ_ids = []
        tag_ids = []
        
        if woo_tmpl_id:
            res=wcapi.get('products/%s'%(woo_tmpl_id))
        else:
            res=wcapi.get('products')            
            
        if not isinstance(res,requests.models.Response):                                 
            transaction_log_obj.create({'message': "Get Products\nResponse is not in proper format :: %s"%(res),
                                         'mismatch_details':True,
                                         'type':'product',
                                         'woo_instance_id':instance.id
                                        })
            return True
        if res.status_code not in [200,201]:
            transaction_log_obj.create(
                                {'message':res.content,
                                 'mismatch_details':True,
                                 'type':'product',
                                 'woo_instance_id':instance.id
                                })
            return True                                    
        total_pages = res.headers.get('X-WC-TotalPages')        
        res = res.json()        
        if not isinstance(res, dict):
            transaction_log_obj.create(
                                        {'message':"Sync Products, Response is not in proper format",
                                         'mismatch_details':True,
                                         'type':'product',
                                         'woo_instance_id':instance.id
                                        })
            return True
                    
        errors = res.get('errors','')
        if errors:
            message = errors[0].get('message')
            transaction_log_obj.create(
                                        {'message':message,
                                         'mismatch_details':True,
                                         'type':'product',
                                         'woo_instance_id':instance.id
                                        })
            return True
        
        if woo_tmpl_id:
            response = res.get('product')
            results = [response]
        else:
            results = res.get('products')
            draft_res=wcapi.get('products?filter[post_status]=draft')
            if not isinstance(draft_res,requests.models.Response):                                 
                transaction_log_obj.create({'message': "Get Draft Products\nResponse is not in proper format :: %s"%(draft_res),
                                             'mismatch_details':True,
                                             'type':'product',
                                             'woo_instance_id':instance.id
                                            })            
            if draft_res.status_code not in [200,201]:
                transaction_log_obj.create(
                                    {'message':draft_res.content,
                                     'mismatch_details':True,
                                     'type':'product',
                                     'woo_instance_id':instance.id
                                    })                                                
            draft_total_pages = draft_res.headers.get('X-WC-TotalPages')        
            draft_res = draft_res.json()        
            if not isinstance(draft_res, dict):
                transaction_log_obj.create(
                                            {'message':"Sync Draft Products,Response is not in proper format",
                                             'mismatch_details':True,
                                             'type':'product',
                                             'woo_instance_id':instance.id
                                            })
            results = results + draft_res.get('products')
            if draft_total_pages >=2:
                for page in range(2,int(draft_total_pages)+1):            
                    results = results + self.import_all_draft_products(wcapi,instance,transaction_log_obj,page)
        if total_pages >=2:
            for page in range(2,int(total_pages)+1):            
                results = results + self.import_all_products(wcapi,instance,transaction_log_obj,page)
                
                
        for result in results:
            woo_product=False
            odoo_product=False
                                        
            woo_tmpl_id = result.get('id')
            template_title = result.get('title')
            template_created_at = result.get('created_at')
            template_updated_at = result.get('updated_at')
            
            if template_created_at.startswith('-'):
                template_created_at = template_created_at[1:]                 
            if template_updated_at.startswith('-'):
                template_updated_at = template_updated_at[1:]
            
            short_description = result.get('short_description')
            description = result.get('description')
            status = result.get('status')
            taxable = result.get('taxable')            

            website_published = False
            if status == 'publish':
                website_published = True
                            
            tmpl_info = {'name':template_title,'created_at':template_created_at,'updated_at':template_updated_at,
                         'short_description':short_description,'description':description,
                         'website_published':website_published,'taxable':taxable}            
            
            woo_template = self.search([('woo_tmpl_id','=',woo_tmpl_id),('woo_instance_id','=',instance.id)],limit=1)
            if woo_template and not update_templates:
                continue
            updated_template=False                        
            for variation in result.get('variations'):                
                variant_id = variation.get('id')
                sku = variation.get('sku').split("!")[0]                                            
                                
                woo_product = woo_product_obj.search([('variant_id','=',variant_id),('woo_instance_id','=',instance.id)],limit=1)
                if not woo_product:
                    woo_product=woo_product_obj.search([('default_code','=',sku),('woo_instance_id','=',instance.id)],limit=1)
                if not woo_product:
                    woo_product=woo_product_obj.search([('product_id.default_code','=',sku),('woo_instance_id','=',instance.id)],limit=1)                                    
                if not woo_product:
                    odoo_product=odoo_product_obj.search([('default_code','=',sku)],limit=1)                    
                if not odoo_product and not woo_product:
                    message="%s Product  Not found for sku %s"%(template_title,sku)                    
                    transaction_log_obj.create(
                                                {'message':message,
                                                 'mismatch_details':True,
                                                 'type':'product',
                                                 'woo_instance_id':instance.id
                                                })
                    continue
                
                variant_info = {}                               
                var_img = False
                price = variation.get('sale_price') or variation.get('regular_price')
                var_images =  variation.get('image')
                var_image_src = ''
                var_image_id = False                
                for var_image in var_images:
                    if str(var_image.get('title').encode('utf-8')) == 'Placeholder' or not var_image.get('id'):
                        continue
                    if var_image.get('position') == 0:                        
                        var_image_src = var_image.get('src')
                        var_image_id = var_image.get('id')
                        if not instance.is_image_url and var_image_src:
                            try:
                                res_img = requests.get(var_image_src,stream=True,verify=False,timeout=10)
                                if res_img.status_code == 200:
                                    var_img = base64.b64encode(res_img.content)                                                                                       
                            except Exception:
                                pass                        
                            
                created_at = variation.get('created_at')
                updated_at = variation.get('updated_at')
                if created_at.startswith('-'):
                    created_at = created_at[1:]                 
                if updated_at.startswith('-'):
                    updated_at = updated_at[1:]
                    
                variant_info = {'name':template_title,'default_code':sku,'created_at':created_at,'updated_at':updated_at}
                if instance.is_image_url:
                    variant_info.update({'response_url':var_image_src,'woo_image_id':var_image_id})
                                                                                       
                if not woo_product:                                       
                    if not woo_template:
                        woo_categories=result.get('categories')
                        categ_ids = self.sync_woo_categ_with_product(wcapi,instance,woo_categories)
                                                    
                        woo_tags=result.get('tags')
                        tag_ids = self.sync_woo_tags_with_product(wcapi,instance,woo_tags)                                                                                                                    
                        tmpl_info.update({'product_tmpl_id':odoo_product.product_tmpl_id.id,'woo_instance_id':instance.id,
                                     'woo_tmpl_id':woo_tmpl_id,'taxable':taxable,                                     
                                     'exported_in_woo':True,'woo_categ_ids':[(6, 0, categ_ids)],
                                     'woo_tag_ids':[(6, 0, tag_ids)],
                                     'total_variants_in_woo':len(result.get('variations'))                                     
                                     })
                        
                        woo_template=self.create(tmpl_info)                                                                
                    variant_info.update({'product_id':odoo_product.id,
                             'name':template_title,
                             'variant_id':variant_id,
                             'woo_template_id':woo_template.id,                                 
                             'woo_instance_id':instance.id,                                                                 
                             'exported_in_woo':True,                                 
                             })               
                    woo_product = woo_product_obj.create(variant_info)
                    if not instance.is_image_url:
                        odoo_product.image = var_img if woo_product else None
                    if update_price:
                        odoo_product.write({'list_price':price})
                else:
                    if not updated_template:
                        woo_categories=result.get('categories')
                        categ_ids = self.sync_woo_categ_with_product(wcapi,instance,woo_categories)
                                                    
                        woo_tags=result.get('tags')
                        tag_ids = self.sync_woo_tags_with_product(wcapi,instance,woo_tags)                        
                        tmpl_info.update({
                                     'woo_tmpl_id':woo_tmpl_id,'taxable':taxable,                                     
                                     'exported_in_woo':True,
                                     'woo_categ_ids':[(6, 0, categ_ids)],
                                     'woo_tag_ids':[(6, 0, tag_ids)],
                                     'total_variants_in_woo':len(result.get('variations'))                                     
                                     })                                                                                                                                                                                                                               
                        updated_template=True                        
                        if not woo_template:
                            woo_template=woo_product.woo_template_id                            

                        woo_template.write(tmpl_info)                                            
                    variant_info.update({                             
                             'variant_id':variant_id,
                             'woo_template_id':woo_template.id,                                 
                             'woo_instance_id':instance.id,                                                                 
                             'exported_in_woo':True,                                 
                             })     
                    woo_product.write(variant_info)
                    if not instance.is_image_url:
                        woo_product.product_id.image = var_img if woo_product else None                        
            if not result.get('variations'):
                sku=result.get('sku').split("!")[0]
                price = result.get('sale_price') or result.get('regular_price')
                woo_product = woo_product_obj.search([('variant_id','=',woo_tmpl_id),('woo_instance_id','=',instance.id)],limit=1)
                if not woo_product:
                    woo_product=woo_product_obj.search([('default_code','=',sku),('woo_instance_id','=',instance.id)],limit=1)
                if not woo_product:
                    woo_product=woo_product_obj.search([('product_id.default_code','=',sku),('woo_instance_id','=',instance.id)],limit=1)                        
                if not woo_product:
                    odoo_product=odoo_product_obj.search([('default_code','=',sku)],limit=1)                    
                if not odoo_product and not woo_product:
                    message="%s Product  Not found for sku %s"%(template_title,sku)                    
                    transaction_log_obj.create(
                                                {'message':message,
                                                 'mismatch_details':True,
                                                 'type':'product',
                                                 'woo_instance_id':instance.id
                                                })
                    continue
                woo_categories=result.get('categories')
                categ_ids = self.sync_woo_categ_with_product(wcapi,instance,woo_categories)
                                            
                woo_tags=result.get('tags')
                tag_ids = self.sync_woo_tags_with_product(wcapi,instance,woo_tags)
                if not woo_product:                                       
                    if not woo_template:                                                                                      
                        tmpl_info.update({'product_tmpl_id':odoo_product.product_tmpl_id.id,'woo_instance_id':instance.id,
                                     'woo_tmpl_id':woo_tmpl_id,'taxable':taxable,
                                     'woo_categ_ids':[(6, 0, categ_ids)],
                                     'woo_tag_ids':[(6, 0, tag_ids)],                                     
                                     'exported_in_woo':True,
                                     'total_variants_in_woo':1                                     
                                     })
                        
                        woo_template=self.create(tmpl_info)                        
                    variant_info = {'name':template_title,'default_code':sku,'created_at':template_created_at,
                                    'updated_at':template_updated_at,'product_id':odoo_product.id,                             
                                    'variant_id':woo_tmpl_id,'woo_template_id':woo_template.id,                                 
                                    'woo_instance_id':instance.id,'exported_in_woo':True}               
                    woo_product = woo_product_obj.create(variant_info)                    
                    if update_price:
                        odoo_product.write({'list_price':price})
                else:
                    if not updated_template:                        
                        tmpl_info.update({
                                     'woo_tmpl_id':woo_tmpl_id,'taxable':taxable,
                                     'woo_categ_ids':[(6, 0, categ_ids)],
                                     'woo_tag_ids':[(6, 0, tag_ids)],                                     
                                     'exported_in_woo':True,
                                     'total_variants_in_woo':1                                     
                                     })                                                                                                                                                                                                                               
                        updated_template=True                        
                        if not woo_template:
                            woo_template=woo_product.woo_template_id                            

                        woo_template.write(tmpl_info)                                            
                    variant_info = {'name':template_title,'default_code':sku,'created_at':template_created_at,'updated_at':template_updated_at,
                                    'variant_id':woo_tmpl_id,'woo_template_id':woo_template.id,'woo_instance_id':instance.id,                                                                 
                                    'exported_in_woo':True}     
                    woo_product.write(variant_info)                    
            variant_info = {}
            tmpl_info = {}
                                                                                              
            images = result.get('images')
            
            existing_gallery_img_keys = {}
            if not instance.is_image_url:                
                for gallery_img in woo_template.woo_gallery_image_ids:
                    if not gallery_img.image:
                        continue
                    key=hashlib.md5(gallery_img.image).hexdigest()
                    if not key:
                        continue
                    existing_gallery_img_keys.update({key:gallery_img})                        
            for image in images:                
                if str(image.get('title').encode('utf-8')) == 'Placeholder' or not image.get('id'):
                    continue
                image_id = image.get('id')
                res_image_src = image.get('src')
                position = image.get('position')
                binary_img_data = False
                if not instance.is_image_url and res_image_src:                    
                    try:
                        res_img = requests.get(res_image_src,stream=True,verify=False,timeout=10)
                        if res_img.status_code == 200:
                            binary_img_data = base64.b64encode(res_img.content)
                            key=hashlib.md5(binary_img_data).hexdigest()
                            if existing_gallery_img_keys.has_key(key):
                                gallery_image = existing_gallery_img_keys.get(key)
                                gallery_image.write({'sequence':position,'woo_image_id':image_id})
                                continue
                            if position == 0:
                                if not instance.is_image_url and not result.get('variations'):                
                                    woo_template.woo_product_ids.product_id.image = binary_img_data
                                    continue                                                                                       
                    except Exception:
                        pass                    
                
                if res_image_src:
                    if position == 0:
                        if not instance.is_image_url and not result.get('variations'):                
                            woo_template.woo_product_ids.product_id.image = binary_img_data
                            continue
                    woo_product_tmp_img= woo_product_img.search([('woo_product_tmpl_id','=',woo_template.id),('woo_instance_id','=',instance.id),('woo_image_id','=',image_id)],limit=1)
                    if woo_product_tmp_img:
                        if instance.is_image_url:
                            woo_product_tmp_img.write({'response_url':res_image_src,'sequence':position})
                        else:
                            woo_product_tmp_img.write({'image':binary_img_data,'sequence':position})                        
                    else:                                                                      
                        if instance.is_image_url:
                            woo_product_img.create({'woo_instance_id':instance.id,'sequence':position,'woo_product_tmpl_id':woo_template.id,'response_url':res_image_src,'woo_image_id':image_id})
                        else:
                            woo_product_img.create({'woo_instance_id':instance.id,'sequence':position,'woo_product_tmpl_id':woo_template.id,'image':binary_img_data,'woo_image_id':image_id})            
            self._cr.commit()                
        return True
    
    @api.multi
    def sync_new_products(self,instance,woo_tmpl_id=False,update_price=False,update_templates=True):
        woo_product_obj=self.env['woo.product.product.ept']
        transaction_log_obj=self.env["woo.transaction.log"]
        woo_product_img = self.env['woo.product.image.ept']        
        odoo_product_obj=self.env['product.product']                       
        wcapi = instance.connect_in_woo()
        
        categ_ids = []
        tag_ids = []
        
        if woo_tmpl_id:
            res=wcapi.get('products/%s'%(woo_tmpl_id))            
        else:
            res=wcapi.get('products')                               
        if not isinstance(res,requests.models.Response):                                                         
            transaction_log_obj.create({'message': "Get Products\nResponse is not in proper format :: %s"%(res),
                                         'mismatch_details':True,
                                         'type':'product',
                                         'woo_instance_id':instance.id
                                        })
            return True
        if res.status_code not in [200,201]:
            transaction_log_obj.create(
                                {'message':res.content,
                                 'mismatch_details':True,
                                 'type':'product',
                                 'woo_instance_id':instance.id
                                })
            return True
        total_pages = res.headers.get('x-wp-totalpages')                
        res = res.json()                
        
        if woo_tmpl_id:            
            results = [res]
        else:
            results = res
        if total_pages >=2:
            for page in range(2,int(total_pages)+1):            
                results = results + self.import_all_products(wcapi,instance,transaction_log_obj,page)
        for result in results:
            woo_product=False
            odoo_product=False
                                        
            woo_tmpl_id = result.get('id')
            template_title = result.get('name')
            template_created_at = result.get('date_created')
            template_updated_at = result.get('date_modified')
            
            if template_created_at and template_created_at.startswith('-'):
                template_created_at = template_created_at[1:]                 
            if template_updated_at and template_updated_at.startswith('-'):
                template_updated_at = template_updated_at[1:]
            
            short_description = result.get('short_description')
            description = result.get('description')
            status = result.get('status')
            tax_status = result.get('tax_status')
            
            taxable = True
            if tax_status != 'taxable':             
                taxable = False
            website_published = False
            if status == 'publish':
                website_published = True
                            
            tmpl_info = {'name':template_title,'created_at':template_created_at or False,
                         'updated_at':template_updated_at or False,
                         'short_description':short_description,'description':description,
                         'website_published':website_published,'taxable':taxable}            
            
            woo_template = self.search([('woo_tmpl_id','=',woo_tmpl_id),('woo_instance_id','=',instance.id)],limit=1)
            if woo_template and not update_templates:
                continue
            updated_template=False                        
            for variation in result.get('variations'):                
                variant_id = variation.get('id')
                sku = variation.get('sku').split("!")[0]                                               
                                
                woo_product = woo_product_obj.search([('variant_id','=',variant_id),('woo_instance_id','=',instance.id)],limit=1)
                if not woo_product:
                    woo_product=woo_product_obj.search([('default_code','=',sku),('woo_instance_id','=',instance.id)],limit=1)
                if not woo_product:
                    woo_product=woo_product_obj.search([('product_id.default_code','=',sku),('woo_instance_id','=',instance.id)],limit=1)                                    
                if not woo_product:
                    odoo_product=odoo_product_obj.search([('default_code','=',sku)],limit=1)                    
                if not odoo_product and not woo_product:
                    message="%s Product  Not found for sku %s"%(template_title,sku)                    
                    transaction_log_obj.create(
                                                {'message':message,
                                                 'mismatch_details':True,
                                                 'type':'product',
                                                 'woo_instance_id':instance.id
                                                })
                    continue
                
                variant_info = {}                               
                var_img = False
                price = variation.get('sale_price') or variation.get('regular_price')
                var_images =  variation.get('image')
                var_image_src = ''
                var_image_id = False                
                for var_image in var_images:
                    if str(var_image.get('name').encode('utf-8')) == 'Placeholder' or not var_image.get('id'):
                        continue
                    if var_image.get('position') == 0:                        
                        var_image_src = var_image.get('src')
                        var_image_id = var_image.get('id')
                        if not instance.is_image_url and var_image_src:
                            try:
                                res_img = requests.get(var_image_src,stream=True,verify=False,timeout=10)
                                if res_img.status_code == 200:
                                    var_img = base64.b64encode(res_img.content)                                                                                       
                            except Exception:
                                pass                        
                            
                created_at = variation.get('date_created')
                updated_at = variation.get('date_modified')
                if created_at and created_at.startswith('-'):
                    created_at = created_at[1:]                 
                if updated_at and updated_at.startswith('-'):
                    updated_at = updated_at[1:]
                    
                variant_info = {'name':template_title,'default_code':sku,'created_at':created_at or False,'updated_at':updated_at or False}
                if instance.is_image_url:
                    variant_info.update({'response_url':var_image_src,'woo_image_id':var_image_id})
                                                                                       
                if not woo_product:                                       
                    if not woo_template:
                        woo_categories=result.get('categories')
                        categ_ids = self.sync_new_woo_categ_with_product(wcapi,instance,woo_categories)
                                                    
                        woo_tags=result.get('tags')
                        tag_ids = self.sync_new_woo_tags_with_product(wcapi,instance,woo_tags)                                                                                                                    
                        tmpl_info.update({'product_tmpl_id':odoo_product.product_tmpl_id.id,'woo_instance_id':instance.id,
                                     'woo_tmpl_id':woo_tmpl_id,'taxable':taxable,                                     
                                     'exported_in_woo':True,'woo_categ_ids':[(6, 0, categ_ids)],
                                     'woo_tag_ids':[(6, 0, tag_ids)],
                                     'total_variants_in_woo':len(result.get('variations'))                                     
                                     })
                        
                        woo_template=self.create(tmpl_info)                                                                
                    variant_info.update({'product_id':odoo_product.id,
                             'name':template_title,
                             'variant_id':variant_id,
                             'woo_template_id':woo_template.id,                                 
                             'woo_instance_id':instance.id,                                                                 
                             'exported_in_woo':True,                                 
                             })               
                    woo_product = woo_product_obj.create(variant_info)
                    if not instance.is_image_url:
                        odoo_product.image = var_img if woo_product else None
                    if update_price:
                        odoo_product.write({'list_price':price})
                else:
                    if not updated_template:
                        woo_categories=result.get('categories')
                        categ_ids = self.sync_new_woo_categ_with_product(wcapi,instance,woo_categories)
                                                    
                        woo_tags=result.get('tags')
                        tag_ids = self.sync_new_woo_tags_with_product(wcapi,instance,woo_tags)                        
                        tmpl_info.update({
                                     'woo_tmpl_id':woo_tmpl_id,'taxable':taxable,                                     
                                     'exported_in_woo':True,
                                     'woo_categ_ids':[(6, 0, categ_ids)],
                                     'woo_tag_ids':[(6, 0, tag_ids)],
                                     'total_variants_in_woo':len(result.get('variations'))                                     
                                     })                                                                                                                                                                                                                               
                        updated_template=True                        
                        if not woo_template:
                            woo_template=woo_product.woo_template_id                            

                        woo_template.write(tmpl_info)                                            
                    variant_info.update({                             
                             'variant_id':variant_id,
                             'woo_template_id':woo_template.id,                                 
                             'woo_instance_id':instance.id,                                                                 
                             'exported_in_woo':True,                                 
                             })     
                    woo_product.write(variant_info)
                    if not instance.is_image_url:
                        woo_product.product_id.image = var_img if woo_product else None                        
            if not result.get('variations'):
                sku=result.get('sku').split("!")[0]
                price = result.get('sale_price') or result.get('regular_price')
                woo_product = woo_product_obj.search([('variant_id','=',woo_tmpl_id),('woo_instance_id','=',instance.id)],limit=1)
                if not woo_product:
                    woo_product=woo_product_obj.search([('default_code','=',sku),('woo_instance_id','=',instance.id)],limit=1)
                if not woo_product:
                    woo_product=woo_product_obj.search([('product_id.default_code','=',sku),('woo_instance_id','=',instance.id)],limit=1)                        
                if not woo_product:
                    odoo_product=odoo_product_obj.search([('default_code','=',sku)],limit=1)                    
                if not odoo_product and not woo_product:
                    message="%s Product  Not found for sku %s"%(template_title,sku)                    
                    transaction_log_obj.create(
                                                {'message':message,
                                                 'mismatch_details':True,
                                                 'type':'product',
                                                 'woo_instance_id':instance.id
                                                })
                    continue
                woo_categories=result.get('categories')
                categ_ids = self.sync_new_woo_categ_with_product(wcapi,instance,woo_categories)
                                            
                woo_tags=result.get('tags')
                tag_ids = self.sync_new_woo_tags_with_product(wcapi,instance,woo_tags)
                if not woo_product:                                       
                    if not woo_template:                                                                                      
                        tmpl_info.update({'product_tmpl_id':odoo_product.product_tmpl_id.id,'woo_instance_id':instance.id,
                                     'woo_tmpl_id':woo_tmpl_id,'taxable':taxable,
                                     'woo_categ_ids':[(6, 0, categ_ids)],
                                     'woo_tag_ids':[(6, 0, tag_ids)],                                     
                                     'exported_in_woo':True,
                                     'total_variants_in_woo':1                                     
                                     })
                        
                        woo_template=self.create(tmpl_info)                        
                    variant_info = {'name':template_title,'default_code':sku,'created_at':template_created_at,
                                    'updated_at':template_updated_at,'product_id':odoo_product.id,                             
                                    'variant_id':woo_tmpl_id,'woo_template_id':woo_template.id,                                 
                                    'woo_instance_id':instance.id,'exported_in_woo':True}               
                    woo_product = woo_product_obj.create(variant_info)                    
                    if update_price:
                        odoo_product.write({'list_price':price})
                else:
                    if not updated_template:                        
                        tmpl_info.update({
                                     'woo_tmpl_id':woo_tmpl_id,'taxable':taxable,
                                     'woo_categ_ids':[(6, 0, categ_ids)],
                                     'woo_tag_ids':[(6, 0, tag_ids)],                                     
                                     'exported_in_woo':True,
                                     'total_variants_in_woo':1                                     
                                     })                                                                                                                                                                                                                               
                        updated_template=True                        
                        if not woo_template:
                            woo_template=woo_product.woo_template_id                            

                        woo_template.write(tmpl_info)                                            
                    variant_info = {'name':template_title,'default_code':sku,'created_at':template_created_at,'updated_at':template_updated_at,
                                    'variant_id':woo_tmpl_id,'woo_template_id':woo_template.id,'woo_instance_id':instance.id,                                                                 
                                    'exported_in_woo':True}     
                    woo_product.write(variant_info)                    
            variant_info = {}
            tmpl_info = {}
                                                                                              
            images = result.get('images')
            existing_gallery_img_keys = {}
            if not instance.is_image_url:                
                for gallery_img in woo_template.woo_gallery_image_ids:
                    if not gallery_img.image:
                        continue
                    key=hashlib.md5(gallery_img.image).hexdigest()
                    if not key:
                        continue
                    existing_gallery_img_keys.update({key:gallery_img})            
            for image in images:
                if str(image.get('name').encode('utf-8')) == 'Placeholder' or not image.get('id'):
                    continue                
                image_id = image.get('id')
                res_image_src = image.get('src')
                position = image.get('position')
                binary_img_data = False
                if not instance.is_image_url and res_image_src:                    
                    try:
                        res_img = requests.get(res_image_src,stream=True,verify=False,timeout=10)
                        if res_img.status_code == 200:
                            binary_img_data = base64.b64encode(res_img.content)
                            key=hashlib.md5(binary_img_data).hexdigest()
                            if existing_gallery_img_keys.has_key(key):
                                gallery_image = existing_gallery_img_keys.get(key)
                                gallery_image.write({'sequence':position,'woo_image_id':image_id})
                                continue
                            if position == 0:
                                if not instance.is_image_url and not result.get('variations'):                
                                    woo_template.woo_product_ids.product_id.image = binary_img_data
                                    continue                                                                                       
                    except Exception:
                        pass                    
                
                if res_image_src:
                    if position == 0:
                        if not instance.is_image_url and not result.get('variations'):                
                            woo_template.woo_product_ids.product_id.image = binary_img_data
                            continue
                    woo_product_tmp_img= woo_product_img.search([('woo_product_tmpl_id','=',woo_template.id),('woo_instance_id','=',instance.id),('woo_image_id','=',image_id)],limit=1)
                    if woo_product_tmp_img:
                        if instance.is_image_url:
                            woo_product_tmp_img.write({'response_url':res_image_src,'sequence':position})
                        else:
                            woo_product_tmp_img.write({'image':binary_img_data,'sequence':position})                        
                    else:                                                                      
                        if instance.is_image_url:
                            woo_product_img.create({'woo_instance_id':instance.id,'sequence':position,'woo_product_tmpl_id':woo_template.id,'response_url':res_image_src,'woo_image_id':image_id})
                        else:
                            woo_product_img.create({'woo_instance_id':instance.id,'sequence':position,'woo_product_tmpl_id':woo_template.id,'image':binary_img_data,'woo_image_id':image_id})
            self._cr.commit()                            
        return True
            
    @api.model
    def update_products_in_woo(self,instance,templates,update_image=True):
        transaction_log_obj=self.env['woo.transaction.log']
        woo_product_img = self.env['woo.product.image.ept']
        wcapi = instance.connect_in_woo()
        for template in templates:
            categ_ids = []
            tag_ids = []
            odoo_template = template.product_tmpl_id                                         
            
            if template.product_tmpl_id:
                woo_product = self.env['product.product'].search([('product_tmpl_id','=',template.product_tmpl_id.id)], limit=1)
                if woo_product:
                    if not template.product_tmpl_id.short_name:
                        raise except_orm(_('UserError'), _("Please define short name for %s!") % (woo_product.name_template,)) 
                    
                    woo_instance_obj=self.env['woo.instance.ept']
                    instance=woo_instance_obj.search([('state','=','confirmed')], limit=1)
                    if instance:
                        full_name_wcapi = instance.connect_for_point_in_woo() 
                        full_name_data = woo_product.name_template                                 
                        full_name_wcapi.post('product-fullname/%s'%(template.woo_tmpl_id),full_name_data)
            
            data = {'title':template.product_tmpl_id.short_name,'enable_html_description':True,'enable_html_short_description':True,'description':template.description or '',
                    'weight':template.product_tmpl_id.weight,'short_description':template.short_description or '','taxable':template.taxable and 'true' or 'false'}
            
            tmpl_images=[]                           
            position = 0
            
            if not odoo_template.attribute_line_ids and template.woo_tmpl_id == template.woo_product_ids[0].variant_id:
                position = 1
#             if update_image:
#                 gallery_img_keys={}
#                 key = False    
#                 for br_gallery_image in template.woo_gallery_image_ids:                               
#                     img_url = ''
#                     if instance.is_image_url:
#                         if br_gallery_image.response_url:
#                             try:
#                                 img = requests.get(br_gallery_image.response_url,stream=True,verify=False,timeout=10)
#                                 if img.status_code == 200:
#                                     img_url = br_gallery_image.response_url
#                                 elif br_gallery_image.url:
#                                     img_url = br_gallery_image.url
#                             except Exception:
#                                 img_url = br_gallery_image.url or ''                        
#                         elif br_gallery_image.url:
#                             img_url = br_gallery_image.url
#                     else:
#                         res = {}            
#                         if br_gallery_image.image:
#                             key=hashlib.md5(br_gallery_image.image).hexdigest()
#                             if not key:
#                                 continue
#                             if gallery_img_keys.has_key(key):
#                                 continue
#                             else:
#                                 gallery_img_keys.update({key:br_gallery_image.id})
#                             res = img_file_upload.upload_image(instance,br_gallery_image.image,"%s_%s_%s"%(odoo_template.name,odoo_template.categ_id.name,odoo_template.id))
#                         img_url = res and res.get('id',False) or ''
#                     if img_url:
#                         if instance.is_image_url:
#                             tmpl_images.append({'src':img_url,'position': position})
#                         else:
#                             tmpl_images.append({'id':img_url,'position': position})
#                         position += 1
#             tmpl_images and data.update({"images":tmpl_images})                                                                   
            for woo_categ in template.woo_categ_ids:
                if not woo_categ.woo_categ_id:                    
                    woo_categ.sync_product_category(instance,woo_product_categ=woo_categ)
                    woo_categ.woo_categ_id and categ_ids.append(woo_categ.woo_categ_id)
                else:
                    categ_res = wcapi.get("products/categories/%s"%(woo_categ.woo_categ_id))
                    if not isinstance(categ_res,requests.models.Response):               
                        transaction_log_obj.create({'message': "Get Product Category\nResponse is not in proper format :: %s"%(categ_res),
                                                     'mismatch_details':True,
                                                     'type':'product',
                                                     'woo_instance_id':instance.id
                                                    })
                        continue
                    categ_res = categ_res.json()
                    woo_product_category = categ_res.get('product_category')
                    if woo_product_category.get('id'): 
                        categ_ids.append(woo_categ.woo_categ_id)
                    else:
                        woo_categ.export_product_categs(instance,[woo_categ])
                        woo_categ.woo_categ_id and categ_ids.append(woo_categ.woo_categ_id)
            if categ_ids:
                data.update({'categories':list(set(categ_ids))})
                
            for woo_tag in template.woo_tag_ids:
                if not woo_tag.woo_tag_id:
                    woo_tag.export_product_tags(instance,[woo_tag])
                    woo_tag.woo_tag_id and tag_ids.append(woo_tag.woo_tag_id)
                else:
                    tag_res = wcapi.get("products/tags/%s"%(woo_tag.woo_tag_id))
                    if not isinstance(tag_res,requests.models.Response):               
                        transaction_log_obj.create({'message': "Get Product Tags\nResponse is not in proper format :: %s"%(tag_res),
                                                     'mismatch_details':True,
                                                     'type':'product',
                                                     'woo_instance_id':instance.id
                                                    })
                        continue
                    tag_res = tag_res.json()
                    woo_product_tag = tag_res.get('product_tag')
                    if woo_product_tag.get('id'):
                        tag_ids.append(woo_tag.woo_tag_id)
                    else:                         
                        woo_tag.export_product_tags(instance,[woo_tag])
                        woo_tag.woo_tag_id and tag_ids.append(woo_tag.woo_tag_id)
                    
            if tag_ids:
                data.update({'tags':list(set(tag_ids))})                                                               
            
            tmpl_res = wcapi.put('products/%s'%(template.woo_tmpl_id),{'product':data})
            if not isinstance(tmpl_res,requests.models.Response):
                transaction_log_obj.create({'message': "Update Products\nResponse is not in proper format :: %s"%(tmpl_res),
                                         'mismatch_details':True,
                                         'type':'product',
                                         'woo_instance_id':instance.id
                                        })
                continue
            if tmpl_res.status_code not in [200,201]:
                transaction_log_obj.create(
                                    {'message':tmpl_res.content,
                                     'mismatch_details':True,
                                     'type':'product',
                                     'woo_instance_id':instance.id
                                    })
                continue
            response = tmpl_res.json()
            if not isinstance(response, dict):
                transaction_log_obj.create(
                                            {'message':"Update Products\nResponse is not in proper format",
                                             'mismatch_details':True,
                                             'type':'product',
                                             'woo_instance_id':instance.id
                                            })
                continue
            errors = response.get('errors','')
            if errors:
                message = errors[0].get('message')
                transaction_log_obj.create(
                                            {'message':message,
                                             'mismatch_details':True,
                                             'type':'product',
                                             'woo_instance_id':instance.id
                                            })
                continue
            tmpl_update_response = response.get('product')
            offset = 0
            for tmpl_gallery_image in tmpl_update_response.get('images'):
                tmpl_image_data = {}
                response_image_id = tmpl_gallery_image.get('id')
                response_image_position = tmpl_gallery_image.get('position')
                if not odoo_template.attribute_line_ids and response_image_position == 0:
                    continue                
                if instance.is_image_url:
                    response_image_url = tmpl_gallery_image.get('src')                    
                    tmpl_image_data.update({'response_url':response_image_url})                
                tmpl_image_data.update({'woo_image_id':response_image_id,'sequence':response_image_position})
                woo_product_tmp_img = woo_product_img.search([('woo_product_tmpl_id','=',template.id),('woo_instance_id','=',instance.id)],offset=offset,limit=1)
                woo_product_tmp_img and woo_product_tmp_img.write(tmpl_image_data)
                offset +=1
                
            variant_img_keys = {}
            key = False    
            for variant in template.woo_product_ids:
                if not variant.variant_id:
                    continue
                info= {}
                info.update({'sku':variant.default_code,'weight':variant.product_id.weight})
                var_url = ''
#                 if update_image:
#                     if instance.is_image_url:                
#                         if variant.response_url:
#                             try:
#                                 img = requests.get(variant.response_url,stream=True,verify=False,timeout=10)
#                                 if img.status_code == 200:
#                                     var_url = variant.response_url
#                                 elif variant.woo_variant_url or variant.product_id.image_url :
#                                     var_url = variant.woo_variant_url or variant.product_id.image_url or ''
#                             except Exception:
#                                 var_url = variant.woo_variant_url or variant.product_id.image_url or ''
#                         else:
#                             var_url = variant.woo_variant_url or variant.product_id.image_url or ''
#                     else:
#                         res = {}
#                         if variant.product_id.image:
#                             key=hashlib.md5(variant.product_id.image).hexdigest()                                                                          
#                             if not variant_img_keys.has_key(key):
#                                 res = img_file_upload.upload_image(instance,variant.product_id.image,"%s_%s"%(variant.name,variant.id))
#                                 var_url = res and res.get('id',False) or ''
#                                 variant_img_keys.update({key:var_url})
#                             else:
#                                 var_url = variant_img_keys.get(key)                
#                 if var_url:
#                     if instance.is_image_url:
#                         info.update({"images":[{'src':var_url,'position': 0}]})
#                     else:
#                         info.update({"images":[{'id':var_url,'position': 0}]})
                var_res = wcapi.put('products/%s'%(variant.variant_id),{'product':info})
                if not isinstance(var_res,requests.models.Response):
                    transaction_log_obj.create(
                                                {'message':"Update Product\n Response is not in proper format :: %s"%(var_res),
                                                 'mismatch_details':True,
                                                 'type':'product',
                                                 'woo_instance_id':instance.id
                                                })
                    continue
                if var_res.status_code not in [200,201]:
                    transaction_log_obj.create(
                                        {'message':var_res.content,
                                         'mismatch_details':True,
                                         'type':'product',
                                         'woo_instance_id':instance.id
                                        })
                    continue
                var_response =var_res.json()
                if not isinstance(var_response, dict):
                    transaction_log_obj.create(
                                                {'message':"Update Product\n Response is not in proper format :: %s"%(var_response),
                                                 'mismatch_details':True,
                                                 'type':'product',
                                                 'woo_instance_id':instance.id
                                                })
                    continue
                errors = var_response.get('errors','')
                if errors:
                    message = errors[0].get('message')
                    transaction_log_obj.create(
                                                {'message':message,
                                                 'mismatch_details':True,
                                                 'type':'product',
                                                 'woo_instance_id':instance.id
                                                })
                    continue
                if instance.is_image_url:
                    update_response =var_response.get('product')
                    update_response_images = update_response.get('images')
                    variant_image_url = update_response_images and update_response_images[0].get('src')
                    variant_image_id = update_response_images and update_response_images[0].get('id')
                    variant.write({'response_url':variant_image_url,'woo_image_id':variant_image_id})                                                 
        return True

    @api.model
    def update_new_products_in_woo(self,instance,templates,update_image=True):
        transaction_log_obj=self.env['woo.transaction.log']                              
        wcapi = instance.connect_in_woo()
        
        batches = []
        woo_templates_ids = templates.ids
        total_woo_templates = len(woo_templates_ids)
        
        start,end=0,100
        if total_woo_templates > 100:
            while True:                                
                w_templates_ids = woo_templates_ids[start:end]
                if not w_templates_ids:
                    break
                temp=end+100
                start,end=end,temp
                if w_templates_ids:
                    woo_templates = self.browse(w_templates_ids)
                    batches.append(woo_templates)
        else:
            batches.append(templates)
                
        for templates in batches:                
            batch_update = {'update':[]}
            batch_update_data = []
        
            for template in templates:
                categ_ids = []
                tag_ids = []
                odoo_template = template.product_tmpl_id                                         
                
                data = {'id':template.woo_tmpl_id,'variations':[],'name':template.name,'enable_html_description':True,
                        'enable_html_short_description':True,'description':template.description or '',
                        'short_description':template.short_description or '','weight':str(template.product_tmpl_id.weight),
                        'taxable':template.taxable and 'true' or 'false'}
                
                flag= False
                tmpl_images=[]                           
                position = 0
                
                if not odoo_template.attribute_line_ids and template.woo_tmpl_id == template.woo_product_ids[0].variant_id:
                    position = 1
                if update_image:
                    gallery_img_keys={}
                    key = False  
                    for br_gallery_image in template.woo_gallery_image_ids:                               
                        img_url = ''
                        if instance.is_image_url:
                            if br_gallery_image.response_url:
                                try:
                                    img = requests.get(br_gallery_image.response_url,stream=True,verify=False,timeout=10)
                                    if img.status_code == 200:
                                        img_url = br_gallery_image.response_url
                                    elif br_gallery_image.url:
                                        img_url = br_gallery_image.url
                                except Exception:
                                    img_url = br_gallery_image.url or ''                        
                            elif br_gallery_image.url:
                                img_url = br_gallery_image.url
                        else:
                            res = {}            
                            if br_gallery_image.image:
                                key=hashlib.md5(br_gallery_image.image).hexdigest()
                                if not key:
                                    continue
                                if gallery_img_keys.has_key(key):
                                    continue
                                else:
                                    gallery_img_keys.update({key:br_gallery_image.id})
                                res = img_file_upload.upload_image(instance,br_gallery_image.image,"%s_%s_%s"%(odoo_template.name,odoo_template.categ_id.name,odoo_template.id))
                            img_url = res and res.get('id',False) or ''
                        if img_url:
                            if instance.is_image_url:
                                tmpl_images.append({'src':img_url,'position': position})
                            else:
                                tmpl_images.append({'id':img_url,'position': position})
                            position += 1
                if tmpl_images:    
                    data.update({"images":tmpl_images})
                    flag=True
                for woo_categ in template.woo_categ_ids:
                    if not woo_categ.woo_categ_id:                    
                        woo_categ.sync_product_category(instance,woo_product_categ=woo_categ)
                        woo_categ.woo_categ_id and categ_ids.append(woo_categ.woo_categ_id)
                    else:
                        categ_res = wcapi.get("products/categories/%s"%(woo_categ.woo_categ_id))
                        if not isinstance(categ_res,requests.models.Response):
                            transaction_log_obj.create({'message':"Get Product Category \n Response is not in proper format :: %s"%(categ_res),
                                                         'mismatch_details':True,
                                                         'type':'product',
                                                         'woo_instance_id':instance.id
                                                        })
                            continue
                        woo_product_category = categ_res.json()                     
                        if woo_product_category.get('id'): 
                            categ_ids.append(woo_categ.woo_categ_id)
                        else:
                            woo_categ.export_product_categs(instance,[woo_categ])
                            woo_categ.woo_categ_id and categ_ids.append(woo_categ.woo_categ_id)
                if categ_ids:
                    categ_ids = list(set(categ_ids))
                    categ_ids = [{'id':cat_id} for cat_id in categ_ids]
                    data.update({'categories':categ_ids})
                    
                for woo_tag in template.woo_tag_ids:
                    if not woo_tag.woo_tag_id:
                        woo_tag.export_product_tags(instance,[woo_tag])
                        woo_tag.woo_tag_id and tag_ids.append(woo_tag.woo_tag_id)
                    else:
                        tag_res = wcapi.get("products/tags/%s"%(woo_tag.woo_tag_id))
                        if not isinstance(tag_res,requests.models.Response):
                            transaction_log_obj.create({'message':"Get Product Tags \n Response is not in proper format :: %s"%(tag_res),
                                                         'mismatch_details':True,
                                                         'type':'product',
                                                         'woo_instance_id':instance.id
                                                        })
                            continue
                        woo_product_tag = tag_res.json()                     
                        if woo_product_tag.get('id'):
                            tag_ids.append(woo_tag.woo_tag_id)
                        else:                         
                            woo_tag.export_product_tags(instance,[woo_tag])
                            woo_tag.woo_tag_id and tag_ids.append(woo_tag.woo_tag_id)
                        
                if tag_ids:
                    tag_ids = list(set(tag_ids))
                    tag_ids = [{'id':tag_id} for tag_id in tag_ids]
                    data.update({'tags':tag_ids})
                
                variant_img_keys = {}
                key = False    
                for variant in template.woo_product_ids:
                    if not variant.variant_id:
                        continue
                    info= {}
                    info.update({'id':variant.variant_id,'weight':str(variant.product_id.weight)})
                    var_url = ''
                    if update_image:                        
                        if instance.is_image_url:                
                            if variant.response_url:
                                try:
                                    img = requests.get(variant.response_url,stream=True,verify=False,timeout=10)
                                    if img.status_code == 200:
                                        var_url = variant.response_url
                                    elif variant.woo_variant_url or variant.product_id.image_url :
                                        var_url = variant.woo_variant_url or variant.product_id.image_url or ''
                                except Exception:
                                    var_url = variant.woo_variant_url or variant.product_id.image_url or ''
                            else:
                                var_url = variant.woo_variant_url or variant.product_id.image_url or ''
                        else:
                            res = {}
                            if variant.product_id.image:
                                key=hashlib.md5(variant.product_id.image).hexdigest()
                                if not variant_img_keys.has_key(key):
                                    res = img_file_upload.upload_image(instance,variant.product_id.image,"%s_%s"%(variant.name,variant.id))
                                    var_url = res and res.get('id',False) or ''
                                    variant_img_keys.update({key:var_url})
                                else:
                                    var_url = variant_img_keys.get(key)
                        if var_url:
                            if instance.is_image_url:
                                info.update({"image":[{'src':var_url,'position': 0}]})
                            else:
                                info.update({"image":[{'id':var_url,'position': 0}]})
                    if template.woo_tmpl_id != variant.variant_id:                                                               
                        data.get('variations').append(info)                        
                        flag = True
                    elif template.woo_tmpl_id == variant.variant_id:
                        del data['variations']
                        if var_url:
                            if instance.is_image_url:
                                if data.get('images'):
                                    data.get('images').insert(0,{'src':var_url,'position': 0})
                                else:
                                    data.update({'images':[{'src':var_url,'position': 0}]})
                            else:
                                if data.get('images'):
                                    data.get('images').insert(0,{'id':var_url,'position': 0})
                                else:
                                    data.update({'images':[{'id':var_url,'position': 0}]})
                        flag = True
                flag and batch_update_data.append(data)
            if batch_update_data:
                batch_update.update({'update':batch_update_data})
                res = wcapi.put('products/batch',batch_update)
                if not isinstance(res,requests.models.Response):               
                    transaction_log_obj.create({'message': "Update Product \nResponse is not in proper format :: %s"%(res),
                                                 'mismatch_details':True,
                                                 'type':'product',
                                                 'woo_instance_id':instance.id
                                                })
                    continue
                if res.status_code not in [200,201]:
                    transaction_log_obj.create(
                                        {'message':"Update Product \n%s"%(res.content),
                                         'mismatch_details':True,
                                         'type':'product',
                                         'woo_instance_id':instance.id
                                        })
                    continue
                response = res.json()
                if response.get('data',{}) and response.get('data',{}).get('status') != 200:
                    message = response.get('message')
                    transaction_log_obj.create(
                                                {'message':"Update Product \n%s"%(message),
                                                 'mismatch_details':True,
                                                 'type':'product',
                                                 'woo_instance_id':instance.id
                                                })
                    continue                              
        return True
    
    @api.model
    def auto_update_stock_ept(self):
        woo_product_tmpl_obj=self.env['woo.product.template.ept']
        ctx = dict(self._context) or {}
        woo_instance_id = ctx.get('woo_instance_id',False)
        if woo_instance_id:
            woo_templates=woo_product_tmpl_obj.search([('woo_instance_id','=',woo_instance_id),('exported_in_woo','=',True)])
            instance = self.env['woo.instance.ept'].browse(woo_instance_id)
            if instance and instance.woo_version == 'old':
                self.update_stock_in_woo(instance,woo_templates)
            elif instance and instance.woo_version == 'new':
                self.update_new_stock_in_woo(instance,woo_templates)
        return True            
            
    @api.model
    def update_stock_in_woo(self,instance=False,products=False):
        transaction_log_obj=self.env['woo.transaction.log']
        instances=[]
        if not instance:
            instances=self.env['woo.instance.ept'].search([('stock_auto_export','=',True),('state','=','confirmed')])
        else:
            instances.append(instance)
        for instance in instances:  
            location_ids=instance.warehouse_id.lot_stock_id.child_ids.ids
            location_ids.append(instance.warehouse_id.lot_stock_id.id)
            woo_products = []            
            if not products:
                woo_products=self.search([('woo_instance_id','=',instance.id),('exported_in_woo','=',True)])      
            else:
                woo_products=self.search([('woo_instance_id','=',instance.id),('exported_in_woo','=',True),('id','in',products.ids)])      
                
            wcapi = instance.connect_in_woo()
            
            for template in woo_products:                
                res = wcapi.get('products/%s'%(template.woo_tmpl_id))
                if not isinstance(res,requests.models.Response):               
                    transaction_log_obj.create({'message': "Get Product \nResponse is not in proper format :: %s"%(res),
                                                 'mismatch_details':True,
                                                 'type':'stock',
                                                 'woo_instance_id':instance.id
                                                })
                    continue                                          
                response =res.json()                
                errors = response.get('errors','')
                if errors:
                    message = errors[0].get('message')
                    transaction_log_obj.create(
                                                {'message':message,
                                                 'mismatch_details':True,
                                                 'type':'stock',
                                                 'woo_instance_id':instance.id
                                                })
                    continue                                   
                for variant in template.woo_product_ids:
                    if  variant.variant_id:                        
                        quantity=self.get_stock(variant,instance.warehouse_id.id,instance.stock_field.name)                                                                       
                        data = {'product':{'managing_stock':True,'stock_quantity':int(quantity)}}                        
                        res = wcapi.put('products/%s'%(variant.variant_id),data)
                        if not isinstance(res,requests.models.Response):               
                            transaction_log_obj.create({'message': "Update Product Stock \nResponse is not in proper format :: %s"%(res),
                                                         'mismatch_details':True,
                                                         'type':'stock',
                                                         'woo_instance_id':instance.id
                                                        })
                            continue
                        if res.status_code not in [200,201]:
                            transaction_log_obj.create(
                                                {'message':res.content,
                                                 'mismatch_details':True,
                                                 'type':'stock',
                                                 'woo_instance_id':instance.id
                                                })
                            continue                        
                        response = res.json()                                               
                        errors = response.get('errors','')
                        if errors:
                            message = errors[0].get('message')
                            transaction_log_obj.create(
                                                        {'message':message,
                                                         'mismatch_details':True,
                                                         'type':'stock',
                                                         'woo_instance_id':instance.id
                                                        })
                            continue                
            if not self._context.get('process')=='update_stock':       
                instance.write({'last_inventory_update_time':datetime.now()})
        return True
    
    @api.model
    def update_new_stock_in_woo(self,instance=False,products=False):
        transaction_log_obj=self.env['woo.transaction.log']
        instances=[]
        if not instance:
            instances=self.env['woo.instance.ept'].search([('stock_auto_export','=',True),('state','=','confirmed')])
        else:
            instances.append(instance)
        for instance in instances:  
            location_ids=instance.warehouse_id.lot_stock_id.child_ids.ids
            location_ids.append(instance.warehouse_id.lot_stock_id.id)
            woo_products = []            
            if not products:
                woo_products=self.search([('woo_instance_id','=',instance.id),('exported_in_woo','=',True)])      
            else:
                woo_products=self.search([('woo_instance_id','=',instance.id),('exported_in_woo','=',True),('id','in',products.ids)])      
            if not woo_products:
                continue    
            wcapi = instance.connect_in_woo()
            
            batches = []
            woo_products_ids = woo_products.ids
            total_woo_products = len(woo_products_ids)
            
            start,end=0,100
            if total_woo_products > 100:
                while True:                                
                    w_products_ids = woo_products_ids[start:end]
                    if not w_products_ids:
                        break
                    temp=end+100
                    start,end=end,temp
                    if w_products_ids:
                        woo_products = self.browse(w_products_ids)
                        batches.append(woo_products)
            else:
                batches.append(woo_products)
                    
            for woo_products in batches:            
                batch_update = {'update':[]}
                batch_update_data = []
                for template in woo_products:
                    info = {'id':template.woo_tmpl_id,'variations':[]}
                    flag= False                                                                  
                    for variant in template.woo_product_ids:
                        if  variant.variant_id:                        
                            quantity=self.get_stock(variant,instance.warehouse_id.id,instance.stock_field.name)
                            if template.woo_tmpl_id != variant.variant_id:
                                info.get('variations').append({'id':variant.variant_id,'manage_stock':True,'stock_quantity':int(quantity)})
                                flag = True
                            elif template.woo_tmpl_id == variant.variant_id:
                                del info['variations']
                                info.update({'manage_stock':True,'stock_quantity':int(quantity)})
                                flag = True                                                                                             
                    flag and batch_update_data.append(info)
                if batch_update_data:
                    batch_update.update({'update':batch_update_data})
                    res = wcapi.put('products/batch',batch_update)
                    if not isinstance(res,requests.models.Response):               
                        transaction_log_obj.create({'message': "Update Product Stock \nResponse is not in proper format :: %s"%(res),
                                                     'mismatch_details':True,
                                                     'type':'stock',
                                                     'woo_instance_id':instance.id
                                                    })
                        continue
                    if res.status_code not in [200,201]:
                        transaction_log_obj.create(
                                            {'message':res.content,
                                             'mismatch_details':True,
                                             'type':'stock',
                                             'woo_instance_id':instance.id
                                            })
                        continue
                    response = res.json()
                    if response.get('data',{}) and response.get('data',{}).get('status') != 200:
                        message = response.get('message')
                        transaction_log_obj.create(
                                                    {'message':message,
                                                     'mismatch_details':True,
                                                     'type':'stock',
                                                     'woo_instance_id':instance.id
                                                    })
                        continue    
            if not self._context.get('process')=='update_stock':       
                instance.write({'last_inventory_update_time':datetime.now()})
        return True    

    @api.model
    def update_price_in_woo(self,instance,woo_templates):
        transaction_log_obj=self.env['woo.transaction.log']
        wcapi = instance.connect_in_woo()                     
        for woo_template in woo_templates:                                                                   
            for variant in woo_template.woo_product_ids:
                if  variant.variant_id:                                                      
                    price=instance.pricelist_id.with_context(uom=variant.product_id.uom_id.id).price_get(variant.product_id.id,1.0,partner=False,context=self._context)[instance.pricelist_id.id]                                                                                                                
                    data = {'product':{'regular_price':price,'sale_price':price}}
                    res = wcapi.put('products/%s'%(variant.variant_id),data)
                    if not isinstance(res,requests.models.Response):               
                        transaction_log_obj.create({'message': "Update Product Price \nResponse is not in proper format :: %s"%(res),
                                                     'mismatch_details':True,
                                                     'type':'price',
                                                     'woo_instance_id':instance.id
                                                    })
                        continue
                    if res.status_code not in [200,201]:
                        transaction_log_obj.create(
                                            {'message':res.content,
                                             'mismatch_details':True,
                                             'type':'price',
                                             'woo_instance_id':instance.id
                                            })
                        continue
                    response =res.json()                    
                    errors = response.get('errors','')
                    if errors:
                        message = errors[0].get('message')
                        transaction_log_obj.create(
                                                    {'message':message,
                                                     'mismatch_details':True,
                                                     'type':'price',
                                                     'woo_instance_id':instance.id
                                                    })
                        continue                    
        return True
    
    @api.model
    def update_new_price_in_woo(self,instance,woo_templates):
        transaction_log_obj=self.env['woo.transaction.log']
        wcapi = instance.connect_in_woo()
        batch_update = {'update':[]}
        batch_update_data = []
        for woo_template in woo_templates:            
            info = {'id':woo_template.woo_tmpl_id,'variations':[]}
            flag= False                                            
            for variant in woo_template.woo_product_ids:
                if  variant.variant_id:                                                      
                    price=instance.pricelist_id.with_context(uom=variant.product_id.uom_id.id).price_get(variant.product_id.id,1.0,partner=False,context=self._context)[instance.pricelist_id.id]                    
                    if woo_template.woo_tmpl_id != variant.variant_id:
                        info.get('variations').append({'id':variant.variant_id,'regular_price':str(price),'sale_price':str(price)})
                        flag = True
                    elif woo_template.woo_tmpl_id == variant.variant_id:
                        del info['variations']
                        info.update({'regular_price':str(price),'sale_price':str(price)})
                        flag = True                                                                           
            flag and batch_update_data.append(info)                
        if batch_update_data:
            batch_update.update({'update':batch_update_data})
            res = wcapi.put('products/batch',batch_update)
            if not isinstance(res,requests.models.Response):               
                transaction_log_obj.create({'message': "Update Product Price \nResponse is not in proper format :: %s"%(res),
                                             'mismatch_details':True,
                                             'type':'price',
                                             'woo_instance_id':instance.id
                                            })
                return True
            if res.status_code not in [200,201]:
                transaction_log_obj.create(
                                    {'message':res.content,
                                     'mismatch_details':True,
                                     'type':'price',
                                     'woo_instance_id':instance.id
                                    })
                return True
            response = res.json()
            if response.get('data',{}) and response.get('data',{}).get('status') != 200:
                message = response.get('message')
                transaction_log_obj.create(
                                            {'message':message,
                                             'mismatch_details':True,
                                             'type':'price',
                                             'woo_instance_id':instance.id
                                            })
        return True            
            
    @api.multi
    def get_stock(self,woo_product,warehouse_id,stock_type='virtual_available'):
        actual_stock=0.0
        product=self.env['product.product'].with_context(warehouse=warehouse_id).browse(woo_product.product_id.id)
        actual_stock=getattr(product, stock_type)
        if actual_stock >= 1.00:
            if woo_product.fix_stock_type=='fix':
                if woo_product.fix_stock_value >=actual_stock:
                    return actual_stock
                else:
                    return woo_product.fix_stock_value  
                              
            elif woo_product.fix_stock_type == 'percentage':
                quantity = int(actual_stock * woo_product.fix_stock_value)
                if quantity >= actual_stock:
                    return actual_stock
                else:
                    return quantity
        return actual_stock                 

    @api.model
    def export_products_in_woo(self,instance,woo_templates,update_price,update_stock,publish,update_image=False):
        transaction_log_obj=self.env['woo.transaction.log']
        wcapi = instance.connect_in_woo()        
        woo_product_product_ept = self.env['woo.product.product.ept']
        woo_product_img = self.env['woo.product.image.ept']
        for woo_template in woo_templates:
            template = woo_template.product_tmpl_id
            categ_ids = []
            tag_ids = []
            single_var_url = ''
                                         
            data = {'enable_html_description':True,'enable_html_short_description':True,'type': 'variable',
                    'title':woo_template.name,'description':woo_template.description or '','weight':template.weight,
                    'short_description':woo_template.short_description or '','taxable':woo_template.taxable and 'true' or 'false',
                    'shipping_required':'true'}          
            for woo_categ in woo_template.woo_categ_ids:
                if not woo_categ.woo_categ_id:
                    woo_categ.sync_product_category(instance,woo_product_categ=woo_categ)
                    woo_categ.woo_categ_id and categ_ids.append(woo_categ.woo_categ_id)
                else:
                    categ_res = wcapi.get("products/categories/%s"%(woo_categ.woo_categ_id))
                    if not isinstance(categ_res,requests.models.Response):               
                        transaction_log_obj.create({'message': "Get Product Category \nResponse is not in proper format :: %s"%(categ_res),
                                                     'mismatch_details':True,
                                                     'type':'product',
                                                     'woo_instance_id':instance.id
                                                    })
                        continue
                    categ_res = categ_res.json()
                    woo_product_category = categ_res.get('product_category')
                    if woo_product_category and woo_product_category.get('id'): 
                        categ_ids.append(woo_categ.woo_categ_id)
                    else:
                        woo_categ.sync_product_category(instance,woo_product_categ=woo_categ)
                        woo_categ.woo_categ_id and categ_ids.append(woo_categ.woo_categ_id)
            if categ_ids:
                data.update({'categories':list(set(categ_ids))})
                
            for woo_tag in woo_template.woo_tag_ids:
                if not woo_tag.woo_tag_id:
                    woo_tag.export_product_tags(instance,[woo_tag])
                    woo_tag.woo_tag_id and tag_ids.append(woo_tag.woo_tag_id)
                else:
                    tag_res = wcapi.get("products/tags/%s"%(woo_tag.woo_tag_id))
                    if not isinstance(tag_res,requests.models.Response):               
                        transaction_log_obj.create({'message': "Get Product Tags \nResponse is not in proper format :: %s"%(tag_res),
                                                     'mismatch_details':True,
                                                     'type':'product',
                                                     'woo_instance_id':instance.id
                                                    })
                        continue
                    tag_res = tag_res.json()
                    woo_product_tag = tag_res.get('product_tag')
                    if woo_product_tag and woo_product_tag.get('id'):
                        tag_ids.append(woo_tag.woo_tag_id)
                    else:                         
                        woo_tag.export_product_tags(instance,[woo_tag])
                        woo_tag.woo_tag_id and tag_ids.append(woo_tag.woo_tag_id)
                    
            if tag_ids:
                data.update({'tags':list(set(tag_ids))})
                                               
            
            if publish:
                data.update({'status':'publish'})                
            else:
                data.update({'status':'draft'})
            attributes = []
            position = 0
            for attribute_line in template.attribute_line_ids:
                options = []
                for option in attribute_line.value_ids:
                    options.append(option.name)
                attribute_data = {'name':attribute_line.attribute_id.name,
                                  'slug':attribute_line.attribute_id.name.lower(),
                                  'position':position,
                                  'visible': True,
                                  'variation': True,
                                  'options':options}
                position += 1
                attributes.append(attribute_data)                           
            if template.attribute_line_ids:                                               
                variations = []
                default_att = []
                variant_img_keys = {}
                key = False
                for variant in woo_template.woo_product_ids:                
                    variation_data = {}
                    if update_image:                                        
                        var_url = ''
                        if instance.is_image_url:                    
                            if variant.response_url:
                                try:
                                    img = requests.get(variant.response_url,stream=True,verify=False,timeout=10)
                                    if img.status_code == 200:                                
                                        var_url = variant.response_url
                                    elif variant.woo_variant_url or variant.product_id.image_url:
                                        var_url = variant.woo_variant_url or variant.product_id.image_url or ''                                
                                except Exception:
                                    var_url = variant.woo_variant_url or variant.product_id.image_url or ''
                            elif variant.woo_variant_url or variant.product_id.image_url:
                                var_url = variant.woo_variant_url or variant.product_id.image_url or ''
                        else:
                            res = {}
                            if variant.product_id.image:
                                key=hashlib.md5(variant.product_id.image).hexdigest()
                                if not variant_img_keys.has_key(key):
                                    res = img_file_upload.upload_image(instance,variant.product_id.image,"%s_%s"%(variant.name,variant.id))
                                    var_url = res and res.get('id',False) or ''
                                    variant_img_keys.update({key:var_url})
                                else:
                                    var_url = variant_img_keys.get(key)                            
                        if var_url:
                            if instance.is_image_url:
                                variation_data.update({"image":[{'src':var_url,'position': 0}]})
                            else:
                                variation_data.update({"image":[{'id':var_url,'position': 0}]})
                    att = []                                
                    for attribute_value in variant.product_id.attribute_value_ids:
                        att_data ={'name':attribute_value.attribute_id.name,'option':attribute_value.name}
                        att.append(att_data)                                            
                    variation_data.update({'attributes':att,'sku':variant.default_code,'weight':variant.product_id.weight})                    
#                     if update_price:                     
#                         price=instance.pricelist_id.with_context(uom=variant.product_id.uom_id.id).price_get(variant.product_id.id,1.0,partner=False,context=self._context)[instance.pricelist_id.id]
#                         variation_data.update({'regular_price':variant.product_id.product_tmpl_id.ecommerce_price,'sale_price':variant.product_id.product_tmpl_id.ecommerce_price})
                    if update_stock:                        
                        quantity=self.get_stock(variant,instance.warehouse_id.id,instance.stock_field.name)
                        variation_data.update({'managing_stock':True,'stock_quantity':int(quantity)})
                    variations.append(variation_data)
                default_att =  variations and variations[0].get('attributes') or []
                data.update({'attributes':attributes,'default_attributes':default_att,'variations':variations})
            else:
                variant = woo_template.woo_product_ids
                if update_image:
                    if instance.is_image_url:                    
                        if variant.response_url:
                            try:
                                img = requests.get(variant.response_url,stream=True,verify=False,timeout=10)
                                if img.status_code == 200:                                
                                    single_var_url = variant.response_url
                                elif variant.woo_variant_url or variant.product_id.image_url:
                                    single_var_url = variant.woo_variant_url or variant.product_id.image_url or ''                                
                            except Exception:
                                single_var_url = variant.woo_variant_url or variant.product_id.image_url or ''
                        elif variant.woo_variant_url or variant.product_id.image_url:
                            single_var_url = variant.woo_variant_url or variant.product_id.image_url or ''
                    else:
                        res = {}
                        if variant.product_id.image:
                            res = img_file_upload.upload_image(instance,variant.product_id.image,"%s_%s"%(variant.name,variant.id))
                        single_var_url = res and res.get('id',False) or ''
                data.update({'type': 'simple','sku':variant.default_code,'weight':variant.product_id.weight})
#                 if update_price:
#                     price=instance.pricelist_id.with_context(uom=variant.product_id.uom_id.id).price_get(variant.product_id.id,1.0,partner=False,context=self._context)[instance.pricelist_id.id]
#                     data.update({'regular_price':variant.product_id.product_tmpl_id.ecommerce_price,'sale_price':variant.product_id.product_tmpl_id.ecommerce_price})
                if update_stock:                        
                    quantity=self.get_stock(variant,instance.warehouse_id.id,instance.stock_field.name)
                    data.update({'managing_stock':True,'stock_quantity':int(quantity)})
            
            tmpl_images=[]                
            position = 0
            if not template.attribute_line_ids and single_var_url and update_image:
                if instance.is_image_url:
                    tmpl_images.append({'src':single_var_url,'position': 0})
                else:
                    tmpl_images.append({'id':single_var_url,'position': 0})
                position += 1
            if update_image:
                gallery_img_keys={}
                key = False      
                for br_gallery_image in woo_template.woo_gallery_image_ids:                                
                    img_url = ''
                    if instance.is_image_url:
                        if br_gallery_image.response_url:
                            try:
                                img = requests.get(br_gallery_image.response_url,stream=True,verify=False,timeout=10)
                                if img.status_code == 200:                                
                                    img_url = br_gallery_image.response_url
                                elif br_gallery_image.url:
                                    img_url = br_gallery_image.url
                            except Exception:
                                img_url = br_gallery_image.url or ''
                        elif br_gallery_image.url:
                            img_url = br_gallery_image.url
                    else:
                        res = {}            
                        if br_gallery_image.image:
                            key=hashlib.md5(br_gallery_image.image).hexdigest()
                            if not key:
                                continue
                            if gallery_img_keys.has_key(key):
                                continue
                            else:
                                gallery_img_keys.update({key:br_gallery_image.id})
                            res = img_file_upload.upload_image(instance,br_gallery_image.image,"%s_%s_%s"%(template.name,template.categ_id.name,template.id))
                        img_url = res and res.get('id',False) or ''
                    if img_url:
                        if instance.is_image_url:
                            tmpl_images.append({'src':img_url,'position': position})
                        else:
                            tmpl_images.append({'id':img_url,'position': position})
                        position += 1                
            tmpl_images and data.update({"images":tmpl_images})  
            new_product = wcapi.post('products',{'product':data})
            if not isinstance(new_product,requests.models.Response):               
                transaction_log_obj.create({'message': "Export Product \nResponse is not in proper format :: %s"%(new_product),
                                             'mismatch_details':True,
                                             'type':'product',
                                             'woo_instance_id':instance.id
                                            })
                continue
            if new_product.status_code not in [200,201]:
                transaction_log_obj.create(
                                    {'message':new_product.content,
                                     'mismatch_details':True,
                                     'type':'product',
                                     'woo_instance_id':instance.id
                                    })
                continue
            response = new_product.json()
            if not isinstance(response, dict):
                transaction_log_obj.create({'message':"Response is not in proper format :: %s"%(response),
                                             'mismatch_details':True,
                                             'type':'product',
                                             'woo_instance_id':instance.id
                                            })
                continue
            errors = response.get('errors','')
            if errors:
                message = errors[0].get('message')
                code = errors[0].get('code')
                if code == 'woocommerce_api_product_sku_already_exists':
                    message = "%s, SKU ==> %s"%(message,data.get('title')) 
                transaction_log_obj.create(
                                            {'message':message,
                                             'mismatch_details':True,
                                             'type':'product',
                                             'woo_instance_id':instance.id
                                            })
                continue
            response = response.get('product')            
            response_variations = response.get('variations')
            for response_variation in response_variations:
                response_variant_data = {}
                variant_sku = response_variation.get('sku')
                variant_id = response_variation.get('id')
                if instance.is_image_url:
                    variant_image = response_variation.get('image')
                    variant_image_id = variant_image and variant_image[0].get('id') or False
                    variant_image_url = variant_image and variant_image[0].get('src') or ''
                    response_variant_data.update({'woo_image_id':variant_image_id,'response_url':variant_image_url})
                variant_created_at = response_variation.get('created_at')
                variant_updated_at = response_variation.get('updated_at')
                if variant_created_at.startswith('-'):
                    variant_created_at = variant_created_at[1:]                 
                if variant_updated_at.startswith('-'):
                    variant_updated_at = variant_updated_at[1:]
                woo_product = woo_product_product_ept.search([('default_code','=',variant_sku),('woo_template_id','=',woo_template.id),('woo_instance_id','=',instance.id)])
                response_variant_data.update({'variant_id':variant_id,'created_at':variant_created_at,'updated_at':variant_updated_at,'exported_in_woo':True})
                woo_product and woo_product.write(response_variant_data) 
            woo_tmpl_id = response.get('id')                        
            if variant.product_id.product_tmpl_id.ecommerce_uom_id:
                woo_instance_obj=self.env['woo.instance.ept']
                instance=woo_instance_obj.search([('state','=','confirmed')], limit=1)
                if instance:
                    uom_wcapi = instance.connect_for_point_in_woo() 
                    uom_data = variant.product_id.product_tmpl_id.ecommerce_uom_id.id                    
                    uom_wcapi.post('insert-uom/%s'%(woo_tmpl_id),uom_data)                
            if variant.product_id.product_tmpl_id.barcode_no:
                woo_instance_obj=self.env['woo.instance.ept']
                instance=woo_instance_obj.search([('state','=','confirmed')], limit=1)
                if instance:
                    barcode_wcapi = instance.connect_for_point_in_woo() 
                    barcode_data = variant.product_id.product_tmpl_id.barcode_no                                    
                    barcode_wcapi.post('insert-barcode/%s'%(woo_tmpl_id),barcode_data) 
            if variant.product_id.product_tmpl_id.uom_ratio:
                woo_instance_obj=self.env['woo.instance.ept']
                instance=woo_instance_obj.search([('state','=','confirmed')], limit=1)
                if instance:
                    packing_size_wcapi = instance.connect_for_point_in_woo() 
                    packing_size_data = variant.product_id.product_tmpl_id.uom_ratio                                 
                    packing_size_wcapi.post('insert-packsize/%s'%(woo_tmpl_id),packing_size_data) 
            if variant.product_id.name_template:
                woo_instance_obj=self.env['woo.instance.ept']
                instance=woo_instance_obj.search([('state','=','confirmed')], limit=1)
                if instance:
                    full_name_wcapi = instance.connect_for_point_in_woo() 
                    full_name_data = variant.product_id.name_template                                 
                    full_name_wcapi.post('product-fullname/%s'%(woo_tmpl_id),full_name_data)     
            tmpl_images = response.get('images')
            offset = 0
            for tmpl_image in tmpl_images:
                tmpl_image_data = {}
                img_id = tmpl_image.get('id')
                position = tmpl_image.get('position')
                if not template.attribute_line_ids and position == 0:
                    continue
                if instance.is_image_url:                                                       
                    res_img_url = tmpl_image.get('src')
                    tmpl_image_data.update({'response_url':res_img_url})                
                tmpl_image_data.update({'woo_image_id':img_id,'sequence':position})
                self._cr.execute("select id from woo_product_image_ept where woo_product_tmpl_id='%s' and woo_instance_id='%s' limit 1 offset '%s'"%(woo_template.id,instance.id,offset))
                image_id = self._cr.fetchall()
                if image_id and isinstance(image_id,list):
                    woo_product_tmp_img = woo_product_img.browse(image_id[0][0])
                    woo_product_tmp_img.write(tmpl_image_data)
                offset +=1
            created_at = response.get('created_at')
            updated_at = response.get('updated_at')
            if created_at.startswith('-'):
                created_at = created_at[1:]                 
            if updated_at.startswith('-'):
                updated_at = updated_at[1:]
            if not template.attribute_line_ids:
                woo_product = woo_template.woo_product_ids
                woo_product.write({'variant_id':woo_tmpl_id,'created_at':created_at,'updated_at':updated_at,'exported_in_woo':True})
            tmpl_data= {'woo_tmpl_id':woo_tmpl_id,'created_at':created_at,'updated_at':updated_at,'exported_in_woo':True}
            tmpl_data.update({'website_published':True}) if publish else tmpl_data.update({'website_published':False})
            woo_template.write(tmpl_data)    
            woo_template.product_tmpl_id.write({'is_sync_ecommerce': True})         
            self._cr.commit()
        return True
    
    @api.model
    def export_new_products_in_woo(self,instance,woo_templates,update_price,update_stock,publish,update_image=True):
        transaction_log_obj=self.env['woo.transaction.log']
        wcapi = instance.connect_in_woo()        
        woo_product_product_ept = self.env['woo.product.product.ept']
        woo_product_img = self.env['woo.product.image.ept']
        for woo_template in woo_templates:
            template = woo_template.product_tmpl_id
            categ_ids = []
            tag_ids = []
            single_var_url = ''
                                         
            data = {'enable_html_description':True,'enable_html_short_description':True,'type': 'variable',
                    'name':woo_template.name,'description':woo_template.description or '',
                    'short_description':woo_template.short_description or '','weight':str(template.weight),
                    'taxable':woo_template.taxable and 'true' or 'false','shipping_required':'true'}          
            for woo_categ in woo_template.woo_categ_ids:
                if not woo_categ.woo_categ_id:
                    woo_categ.sync_product_category(instance,woo_product_categ=woo_categ)
                    woo_categ.woo_categ_id and categ_ids.append(woo_categ.woo_categ_id)
                else:
                    categ_res = wcapi.get("products/categories/%s"%(woo_categ.woo_categ_id))
                    if not isinstance(categ_res,requests.models.Response):               
                        transaction_log_obj.create({'message': "Get Product Category \nResponse is not in proper format :: %s"%(categ_res),
                                                     'mismatch_details':True,
                                                     'type':'product',
                                                     'woo_instance_id':instance.id
                                                    })
                        continue
                    woo_product_category = categ_res.json()
                    if woo_product_category and woo_product_category.get('id'): 
                        categ_ids.append(woo_categ.woo_categ_id)
                    else:
                        woo_categ.sync_product_category(instance,woo_product_categ=woo_categ)
                        woo_categ.woo_categ_id and categ_ids.append(woo_categ.woo_categ_id)
            if categ_ids:
                categ_ids = list(set(categ_ids))
                categ_ids = [{'id':cat_id} for cat_id in categ_ids]
                data.update({'categories':categ_ids})
                
            for woo_tag in woo_template.woo_tag_ids:
                if not woo_tag.woo_tag_id:
                    woo_tag.export_product_tags(instance,[woo_tag])
                    woo_tag.woo_tag_id and tag_ids.append(woo_tag.woo_tag_id)
                else:
                    tag_res = wcapi.get("products/tags/%s"%(woo_tag.woo_tag_id))
                    if not isinstance(tag_res,requests.models.Response):               
                        transaction_log_obj.create({'message': "Get Product Tags \nResponse is not in proper format :: %s"%(tag_res),
                                                     'mismatch_details':True,
                                                     'type':'product',
                                                     'woo_instance_id':instance.id
                                                    })
                        continue
                    woo_product_tag = tag_res.json()                                                      
                    if woo_product_tag and woo_product_tag.get('id'):
                        tag_ids.append(woo_tag.woo_tag_id)
                    else:                         
                        woo_tag.export_product_tags(instance,[woo_tag])
                        woo_tag.woo_tag_id and tag_ids.append(woo_tag.woo_tag_id)
                    
            if tag_ids:
                tag_ids = list(set(tag_ids))
                tag_ids = [{'id':tag_id} for tag_id in tag_ids]
                data.update({'tags':tag_ids})
                                               
            
            if publish:
                data.update({'status':'publish'})                
            else:
                data.update({'status':'draft'})
            attributes = []
            position = 0
            for attribute_line in template.attribute_line_ids:
                options = []
                for option in attribute_line.value_ids:
                    options.append(option.name)
                attribute_data = {'name':attribute_line.attribute_id.name,
                                  'slug':attribute_line.attribute_id.name.lower(),
                                  'position':position,
                                  'visible': True,
                                  'variation': True,
                                  'options':options}
                position += 1
                attributes.append(attribute_data)                           
            if template.attribute_line_ids:                                               
                variations = []
                default_att = []
                variant_img_keys = {}
                key = False
                for variant in woo_template.woo_product_ids:                
                    variation_data = {}
                    if update_image:                                        
                        var_url = ''
                        if instance.is_image_url:                    
                            if variant.response_url:
                                try:
                                    img = requests.get(variant.response_url,stream=True,verify=False,timeout=10)
                                    if img.status_code == 200:                                
                                        var_url = variant.response_url
                                    elif variant.woo_variant_url or variant.product_id.image_url:
                                        var_url = variant.woo_variant_url or variant.product_id.image_url or ''                                
                                except Exception:
                                    var_url = variant.woo_variant_url or variant.product_id.image_url or ''
                            elif variant.woo_variant_url or variant.product_id.image_url:
                                var_url = variant.woo_variant_url or variant.product_id.image_url or ''
                        else:
                            res = {}
                            if variant.product_id.image:
                                key=hashlib.md5(variant.product_id.image).hexdigest()
                                if not variant_img_keys.has_key(key):
                                    res = img_file_upload.upload_image(instance,variant.product_id.image,"%s_%s"%(variant.name,variant.id))
                                    var_url = res and res.get('id',False) or ''
                                    variant_img_keys.update({key:var_url})
                                else:
                                    var_url = variant_img_keys.get(key)
                            
                        if var_url:
                            if instance.is_image_url:
                                variation_data.update({"image":[{'src':var_url,'position': 0}]})
                            else:
                                variation_data.update({"image":[{'id':var_url,'position': 0}]})                                        
                    att = []                                
                    for attribute_value in variant.product_id.attribute_value_ids:
                        att_data ={'name':attribute_value.attribute_id.name,'option':attribute_value.name}
                        att.append(att_data)                                            
                    variation_data.update({'attributes':att,'sku':str(variant.default_code),'weight':str(variant.product_id.weight)})                    
                    if update_price:                     
                        price=instance.pricelist_id.with_context(uom=variant.product_id.uom_id.id).price_get(variant.product_id.id,1.0,partner=False,context=self._context)[instance.pricelist_id.id]
                        variation_data.update({'regular_price':str(price),'sale_price':str(price)})
                    if update_stock:                        
                        quantity=self.get_stock(variant,instance.warehouse_id.id,instance.stock_field.name)
                        variation_data.update({'manage_stock':True,'stock_quantity':int(quantity)})
                    variations.append(variation_data)
                default_att =  variations and variations[0].get('attributes') or []
                data.update({'attributes':attributes,'default_attributes':default_att,'variations':variations})
            else:
                variant = woo_template.woo_product_ids
                if update_image:
                    if instance.is_image_url:                    
                        if variant.response_url:
                            try:
                                img = requests.get(variant.response_url,stream=True,verify=False,timeout=10)
                                if img.status_code == 200:                                
                                    single_var_url = variant.response_url
                                elif variant.woo_variant_url or variant.product_id.image_url:
                                    single_var_url = variant.woo_variant_url or variant.product_id.image_url or ''                                
                            except Exception:
                                single_var_url = variant.woo_variant_url or variant.product_id.image_url or ''
                        elif variant.woo_variant_url or variant.product_id.image_url:
                            single_var_url = variant.woo_variant_url or variant.product_id.image_url or ''
                    else:
                        res = {}
                        if variant.product_id.image:
                            res = img_file_upload.upload_image(instance,variant.product_id.image,"%s_%s"%(variant.name,variant.id))
                        single_var_url = res and res.get('id',False) or ''
                data.update({'type': 'simple','sku':str(variant.default_code),'weight':str(variant.product_id.weight)})
                if update_price:                    
                    price=instance.pricelist_id.with_context(uom=variant.product_id.uom_id.id).price_get(variant.product_id.id,1.0,partner=False,context=self._context)[instance.pricelist_id.id]
                    data.update({'regular_price':str(price),'sale_price':str(price)})
                if update_stock:                        
                    quantity=self.get_stock(variant,instance.warehouse_id.id,instance.stock_field.name)
                    data.update({'manage_stock':True,'stock_quantity':int(quantity)})
            
            tmpl_images=[]                
            position = 0
            if not template.attribute_line_ids and single_var_url and update_image:
                if instance.is_image_url:
                    tmpl_images.append({'src':single_var_url,'position': 0})
                else:
                    tmpl_images.append({'id':single_var_url,'position': 0})
                position += 1
            if update_image:
                gallery_img_keys={}
                key = False  
                for br_gallery_image in woo_template.woo_gallery_image_ids:                                
                    img_url = ''
                    if instance.is_image_url:
                        if br_gallery_image.response_url:
                            try:
                                img = requests.get(br_gallery_image.response_url,stream=True,verify=False,timeout=10)
                                if img.status_code == 200:                                
                                    img_url = br_gallery_image.response_url
                                elif br_gallery_image.url:
                                    img_url = br_gallery_image.url
                            except Exception:
                                img_url = br_gallery_image.url or ''
                        elif br_gallery_image.url:
                            img_url = br_gallery_image.url
                    else:
                        res = {}            
                        if br_gallery_image.image:
                            key=hashlib.md5(br_gallery_image.image).hexdigest()
                            if not key:
                                continue
                            if gallery_img_keys.has_key(key):
                                continue
                            else:
                                gallery_img_keys.update({key:br_gallery_image.id})
                            res = img_file_upload.upload_image(instance,br_gallery_image.image,"%s_%s_%s"%(template.name,template.categ_id.name,template.id))
                        img_url = res and res.get('id',False) or ''
                    if img_url:
                        if instance.is_image_url:
                            tmpl_images.append({'src':img_url,'position': position})
                        else:
                            tmpl_images.append({'id':img_url,'position': position})
                        position += 1                
            tmpl_images and data.update({"images":tmpl_images})            
            new_product = wcapi.post('products',data)
            if not isinstance(new_product,requests.models.Response):               
                transaction_log_obj.create({'message': "Export Product\nResponse is not in proper format :: %s"%(new_product),
                                             'mismatch_details':True,
                                             'type':'product',
                                             'woo_instance_id':instance.id
                                            })
                continue
            if new_product.status_code not in [200,201]:
                transaction_log_obj.create(
                                    {'message':new_product.content,
                                     'mismatch_details':True,
                                     'type':'product',
                                     'woo_instance_id':instance.id
                                    })
                continue
            response = new_product.json()
            if response.get('data',{}) and response.get('data',{}).get('status') not in [200,201]:
                message = response.get('message')
                if response.get('code') == 'woocommerce_rest_product_sku_already_exists':                   
                    message = "%s, ==> %s"%(message,data.get('name'))
                transaction_log_obj.create(
                                            {'message':message,
                                             'mismatch_details':True,
                                             'type':'product',
                                             'woo_instance_id':instance.id
                                            })
                continue
            if not isinstance(response, dict):
                transaction_log_obj.create(
                                            {'message':"Export Product, Response is not in proper format",
                                             'mismatch_details':True,
                                             'type':'product',
                                             'woo_instance_id':instance.id
                                            })
                continue                      
            response_variations = response.get('variations')
            for response_variation in response_variations:
                response_variant_data = {}
                variant_sku = response_variation.get('sku')
                variant_id = response_variation.get('id')
                if instance.is_image_url:
                    variant_image = response_variation.get('image')
                    variant_image_id = variant_image and variant_image[0].get('id') or False
                    variant_image_url = variant_image and variant_image[0].get('src') or ''
                    response_variant_data.update({'woo_image_id':variant_image_id,'response_url':variant_image_url})
                variant_created_at = response_variation.get('date_created')
                variant_updated_at = response_variation.get('date_modified')
                if variant_created_at.startswith('-'):
                    variant_created_at = variant_created_at[1:]                 
                if variant_updated_at.startswith('-'):
                    variant_updated_at = variant_updated_at[1:]
                woo_product = woo_product_product_ept.search([('default_code','=',variant_sku),('woo_template_id','=',woo_template.id),('woo_instance_id','=',instance.id)])
                response_variant_data.update({'variant_id':variant_id,'created_at':variant_created_at,'updated_at':variant_updated_at,'exported_in_woo':True})
                woo_product and woo_product.write(response_variant_data) 
            woo_tmpl_id = response.get('id')
            tmpl_images = response.get('images')
            offset = 0
            for tmpl_image in tmpl_images:
                tmpl_image_data = {}
                img_id = tmpl_image.get('id')
                position = tmpl_image.get('position')
                if not template.attribute_line_ids and position == 0:
                    continue
                if instance.is_image_url:                                                       
                    res_img_url = tmpl_image.get('src')
                    tmpl_image_data.update({'response_url':res_img_url})                
                tmpl_image_data.update({'woo_image_id':img_id,'sequence':position})
                woo_product_tmp_img = woo_product_img.search([('woo_product_tmpl_id','=',woo_template.id),('woo_instance_id','=',instance.id)],offset=offset,limit=1)                
                woo_product_tmp_img and woo_product_tmp_img.write(tmpl_image_data)
                offset +=1
            created_at = response.get('date_created')
            updated_at = response.get('date_modified')
            if created_at and created_at.startswith('-'):
                created_at = created_at[1:]                 
            if updated_at and updated_at.startswith('-'):
                updated_at = updated_at[1:]
            if not template.attribute_line_ids:
                woo_product = woo_template.woo_product_ids
                woo_product.write({'variant_id':woo_tmpl_id,'created_at':created_at or False,'updated_at':updated_at or False,'exported_in_woo':True})
            tmpl_data= {'woo_tmpl_id':woo_tmpl_id,'created_at':created_at or False,'updated_at':updated_at or False,'exported_in_woo':True}
            tmpl_data.update({'website_published':True}) if publish else tmpl_data.update({'website_published':False})
            woo_template.write(tmpl_data)             
            self._cr.commit()
        return True    
    
class woo_product_product_ept(models.Model):
    _name="woo.product.product.ept"
    _order='product_id'
    
    @api.one
    def set_image(self):
        for variant_image in self:
            if variant_image.woo_instance_id.is_image_url:
                if variant_image.response_url:
                    try:  
                        img = requests.get(variant_image.response_url,stream=True,verify=False,timeout=10)
                        if img.status_code == 200:                        
                            variant_image.url_image=base64.b64encode(img.content)
                        else:
                            img = requests.get(variant_image.woo_variant_url,stream=True,verify=False,timeout=10)
                            if img.status_code == 200:                        
                                variant_image.url_image=base64.b64encode(img.content)
                    except Exception:
                        try:  
                            img = requests.get(variant_image.woo_variant_url,stream=True,verify=False,timeout=10)
                            variant_image.url_image=base64.b64encode(img.content)
                        except Exception:
                            pass
                
                elif variant_image.woo_variant_url:          
                    try:  
                        img = requests.get(variant_image.woo_variant_url,stream=True,verify=False,timeout=10)
                        if img.status_code == 200:
                            variant_image.url_image=base64.b64encode(img.content)
                    except Exception:
                        pass          
    
    name=fields.Char("Title")    
    woo_instance_id=fields.Many2one("woo.instance.ept","Instance",required=1)
    default_code=fields.Char("Default Code")
    product_id=fields.Many2one("product.product","Product",required=1)
    woo_template_id=fields.Many2one("woo.product.template.ept","Woo Template",required=1,ondelete="cascade")
    exported_in_woo=fields.Boolean("Exported In Woo")
    variant_id=fields.Char("Variant Id")
    fix_stock_type =  fields.Selection([('fix','Fix'),('percentage','Percentage')], string='Fix Stock Type')
    fix_stock_value = fields.Float(string='Fix Stock Value',digits=dp.get_precision("Product UoS"))
    created_at=fields.Datetime("Created At")
    updated_at=fields.Datetime("Updated At")
    is_image_url=fields.Boolean("Is Image Url ?",related="woo_instance_id.is_image_url")
    woo_variant_url = fields.Char(size=600, string='Image URL')
    response_url = fields.Char(size=600, string='Response URL',help="URL from WooCommerce")
    url_image=fields.Binary("Image",compute=set_image,store=False)
    woo_image_id=fields.Char("Image Id",help="WooCommerce Image Id")