from openerp import models,fields,api
import requests
import logging
from requests.structures import CaseInsensitiveDict


_logger = logging.getLogger(__name__)

class woo_brands_ept(models.Model):
    _name="woo.brands.ept"
    _order='name'

    name=fields.Char("Name")
    description=fields.Text('Description')
    woo_brand_id = fields.Integer("Woo Brand Id")
    slug = fields.Char(string='Slug',
                       help="The slug is the URL-friendly version of the name. It is usually all lowercase and contains only letters, numbers, and hyphens.")
    exported_in_woo = fields.Boolean("Exported In Woo", default=False)
    woo_instance_id = fields.Many2one("woo.instance.ept", "Instance", required=1)

    @api.model
    def export_product_brands(self, instance, woo_product_brands):
        transaction_log_obj = self.env['woo.transaction.log']
        wcapi = instance.connect_in_woo()
        for woo_product_brand in woo_product_brands:
            row_data = {'name': woo_product_brand.name, 'description': str(woo_product_brand.description or '')}
            if woo_product_brand.slug:
                row_data.update({'slug':str(woo_product_brand.slug)})
            if instance.woo_version == 'old':
                data = {'product_brand': row_data}
            elif instance.woo_version == 'new':
                data = row_data
            url = instance.host+"/wp-json/product/v1/brands"
            headers = CaseInsensitiveDict()
            headers["Content-Type"] = "application/json"
            res = requests.post(url, json=row_data, headers=headers)
            if res.status_code not in [200,201]:
                if res.status_code == 500:
                    response = res.json()
                    if isinstance(response,dict) and response.get('code')=='term_exists':
                        woo_product_brand.write({'woo_brand_id':response.get('data'),'exported_in_woo':True})
                        continue
                    else:
                        message = res.content
                        transaction_log_obj.create(
                                                    {'message':message,
                                                     'mismatch_details':True,
                                                     'type':'tags',
                                                     'woo_instance_id':instance.id
                                                    })
                        continue
            response = res.json()
            if response:
                product_brand_id =response.get('id',False)
                slug = response.get('slug',False)
            if product_brand_id:
                woo_product_brand.write({'woo_brand_id': product_brand_id, 'exported_in_woo': True, 'slug':slug})
        return True

    @api.model
    def update_product_brands_in_woo(self,instance,woo_product_brands):
        transaction_log_obj=self.env['woo.transaction.log']
        wcapi = instance.connect_in_woo()
        for woo_brand in woo_product_brands:
            row_data = {'id':woo_brand.woo_brand_id,'name':woo_brand.name,'description':str(woo_brand.description or '')}
            if woo_brand.slug:
                row_data.update({'slug':str(woo_brand.slug)})
            if instance.woo_version == 'old':
                data = {"product_brand": row_data}
            elif instance.woo_version == 'new':
                data = row_data
            url = instance.host+"/wp-json/product/v1/brands_update/"
            headers = CaseInsensitiveDict()
            headers["Content-Type"] = "application/json"
            res = requests.post(url, json=row_data)
            response = res.json()
            if response:
                _logger.info('woo brand update complete')
        return True

    def import_all_brands(self,wcapi,instance,transaction_log_obj,page):
        res=wcapi.get('products/brands?page=%s'%(page))
        if not isinstance(res,requests.models.Response):
            transaction_log_obj.create({'message':"Get Product Brands \nResponse is not in proper format :: %s"%(res),
                                             'mismatch_details':True,
                                             'type':'brands',
                                             'woo_instance_id':instance.id
                                            })
            return []
        if res.status_code not in [200,201]:
            transaction_log_obj.create(
                                    {'message':res.content,
                                     'mismatch_details':True,
                                     'type':'brands',
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
                                             'type':'brands',
                                             'woo_instance_id':instance.id
                                            })
                return []
            return response.get('product_brands')
        elif instance.woo_version == 'new':
            return response


    @api.multi
    def sync_product_brands(self, instance, woo_product_brand=False):
        transaction_log_obj=self.env["woo.transaction.log"]
        wcapi = instance.connect_in_woo()
        if woo_product_brand and woo_product_brand.exported_in_woo:
            res = wcapi.get("products/brands/%s"%(woo_product_brand.woo_tag_id))
            if not isinstance(res,requests.models.Response):
                transaction_log_obj.create({'message':"Get Product Brands \nResponse is not in proper format :: %s"%(res),
                                                 'mismatch_details':True,
                                                 'type':'tags',
                                                 'woo_instance_id':instance.id
                                                })
                return True
            if res.status_code == 404:
                self.export_product_tags(instance, [woo_product_brand])
                return True
            if res.status_code not in [200,201]:
                transaction_log_obj.create(
                                    {'message':res.content,
                                     'mismatch_details':True,
                                     'type':'brands',
                                     'woo_instance_id':instance.id
                                    })
                return True
            res = res.json()
            description = ''
            if instance.woo_version == 'old':
                description = res.get('product_brand', {}).get('description', '')
            elif instance.woo_version == 'new':
                description = res.get('description')
            woo_product_brand.write({'description': description})
        else:
            res = wcapi.get("products/brands")
            if not isinstance(res, requests.models.Response):
                transaction_log_obj.create({'message':"Get Product Brands \nResponse is not in proper format :: %s"%(res),
                                             'mismatch_details':True,
                                             'type':'brands',
                                             'woo_instance_id':instance.id
                                                })
                return True
            if res.status_code  not in [200,201]:
                transaction_log_obj.create({'message':"Get Product Brands \nResponse is not in proper format :: %s"%(res.content),
                                                 'mismatch_details':True,
                                                 'type':'tags',
                                                 'woo_instance_id':instance.id
                                                })
                return True
            results = []
            total_pages = res and res.headers.get('x-wp-totalpages') or 1
            res = res.json()

            if instance.woo_version == 'old':
                errors = res.get('errors','')
                if errors:
                    message = errors[0].get('message')
                    transaction_log_obj.create(
                                                {'message':message,
                                                 'mismatch_details':True,
                                                 'type':'brands',
                                                 'woo_instance_id':instance.id
                                                })
                    return True
                results =  res.get('product_brands')
            elif instance.woo_version == 'new':
                results = res
            if total_pages >=2:
                for page in range(2,int(total_pages)+1):
                    results = results + self.import_all_tags(wcapi,instance,transaction_log_obj,page)

            for res in results:
                if not isinstance(res, dict):
                    continue
                brand_id = res.get('id')
                name= res.get('name')
                description = res.get('description')
                slug = res.get('slug')
                woo_brand = self.search([('woo_brand_id','=',brand_id),('woo_instance_id','=',instance.id)],limit=1)
                if not woo_brand:
                    woo_brand = self.search([('slug','=',slug),('woo_instance_id','=',instance.id)],limit=1)
                if woo_brand:
                    woo_brand.write({'woo_brand_id':brand_id,'name':name,'description':description,
                                   'slug':slug,'exported_in_woo':True})
                else:
                    self.create({'woo_brand_id':brand_id,'name':name,'description':description,
                                 'slug':slug,'woo_instance_id':instance.id,'exported_in_woo':True})
        return True