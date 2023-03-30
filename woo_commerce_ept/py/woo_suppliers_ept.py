from openerp import models,fields,api
import requests

class woo_suppliers_ept(models.Model):
    _name="woo.suppliers.ept"
    _order='name'

    name=fields.Char("Name")
    description=fields.Text('Description')
    woo_supplier_id = fields.Integer("Woo Supplier Id")
    slug = fields.Char(string='Slug',
                       help="The slug is the URL-friendly version of the name. It is usually all lowercase and contains only letters, numbers, and hyphens.")
    exported_in_woo = fields.Boolean("Exported In Woo", default=False)
    woo_instance_id = fields.Many2one("woo.instance.ept", "Instance", required=1)

    @api.model
    def export_product_suppliers(self, instance, woo_product_suppliers):
        transaction_log_obj = self.env['woo.transaction.log']
        wcapi = instance.connect_in_woo()
        for woo_product_supplier in woo_product_suppliers:
            row_data = {'name': woo_product_supplier.name, 'description': str(woo_product_supplier.description or '')}
            if woo_product_supplier.slug:
                row_data.update({'slug':str(woo_product_supplier.slug)})
            if instance.woo_version == 'old':
                data = {'product_supplier': row_data}
            elif instance.woo_version == 'new':
                data = row_data
            res = wcapi.post("products/suppliers", data)
            if not isinstance(res,requests.models.Response):
                transaction_log_obj.create({'message':"Export Product Suppliers \nResponse is not in proper format :: %s"%(res),
                                             'mismatch_details':True,
                                             'type':'tags',
                                             'woo_instance_id':instance.id
                                            })
                continue
            if res.status_code not in [200,201]:
                if res.status_code == 500:
                    response = res.json()
                    if isinstance(response,dict) and response.get('code')=='term_exists':
                        woo_product_supplier.write({'woo_supplier_id':response.get('data'),'exported_in_woo':True})
                        continue
                    else:
                        message = res.content
                        transaction_log_obj.create(
                                                    {'message':message,
                                                     'mismatch_details':True,
                                                     'type':'suppliers',
                                                     'woo_instance_id':instance.id
                                                    })
                        continue
            response = res.json()
            product_supplier = False
            if instance.woo_version == 'old':
                errors = response.get('errors','')
                if errors:
                    message = errors[0].get('message')
                    message = "%s :: %s"%(message,woo_product_supplier.name)
                    transaction_log_obj.create(
                                                {'message':message,
                                                 'mismatch_details':True,
                                                 'type':'tags',
                                                 'woo_instance_id':instance.id
                                                })
                    continue
                product_supplier=response.get('product_supplier',False)
            elif instance.woo_version == 'new':
                product_supplier =response
            product_supplier_id = product_supplier and product_supplier.get('id', False)
            slug = product_supplier and product_supplier.get('slug', '')
            if product_supplier_id:
                woo_product_supplier.write({'woo_supplier_id': product_supplier_id, 'exported_in_woo': True, 'slug': slug})
        return True

    @api.model
    def update_product_suppliers_in_woo(self,instance,woo_product_suppliers):
        transaction_log_obj=self.env['woo.transaction.log']
        wcapi = instance.connect_in_woo()
        for woo_supplier in woo_product_suppliers:
            row_data = {'name':woo_supplier.name,'description':str(woo_supplier.description or '')}
            if woo_supplier.slug:
                row_data.update({'slug':str(woo_supplier.slug)})
            if instance.woo_version == 'old':
                data = {"product_supplier": row_data}
            elif instance.woo_version == 'new':
                data = row_data
            res = wcapi.put('products/suppliers/%s' % (woo_supplier.woo_supplier_id), data)
            if not isinstance(res, requests.models.Response):
                transaction_log_obj.create({'message':"Get Product Suppliers \nResponse is not in proper format :: %s"%(res),
                                             'mismatch_details':True,
                                             'type':'suppliers',
                                             'woo_instance_id':instance.id
                                            })
                continue
            if res.status_code not in [200,201]:
                transaction_log_obj.create(
                                                {'message':res.content,
                                                 'mismatch_details':True,
                                                 'type':'suppliers',
                                                 'woo_instance_id':instance.id
                                                })
                continue
            response = res.json()
            response_data = {}
            if not isinstance(response, dict):
                transaction_log_obj.create(
                                            {'message':"Response is not in proper format,Please Check Details",
                                             'mismatch_details':True,
                                             'type':'suppliers',
                                             'woo_instance_id':instance.id
                                            })
                continue
            if instance.woo_version == 'old':
                errors = response.get('errors','')
                if errors:
                    message = errors[0].get('message')
                    transaction_log_obj.create(
                                                {'message':message,
                                                 'mismatch_details':True,
                                                 'type':'suppliers',
                                                 'woo_instance_id':instance.id
                                                })
                    continue
                else:
                    response_data = response.get('product_suppliers')
            else:
                response_data = response
            if response_data:
                woo_supplier.write({'slug':response_data.get('slug')})
        return True

    def import_all_suppliers(self,wcapi,instance,transaction_log_obj,page):
        res=wcapi.get('products/suppliers?page=%s'%(page))
        if not isinstance(res,requests.models.Response):
            transaction_log_obj.create({'message':"Get Product Suppliers \nResponse is not in proper format :: %s"%(res),
                                             'mismatch_details':True,
                                             'type':'suppliers',
                                             'woo_instance_id':instance.id
                                            })
            return []
        if res.status_code not in [200,201]:
            transaction_log_obj.create(
                                    {'message':res.content,
                                     'mismatch_details':True,
                                     'type':'suppliers',
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
                                             'type':'suppliers',
                                             'woo_instance_id':instance.id
                                            })
                return []
            return response.get('product_suppliers')
        elif instance.woo_version == 'new':
            return response


    @api.multi
    def sync_product_suppliers(self, instance, woo_product_supplier=False):
        transaction_log_obj=self.env["woo.transaction.log"]
        wcapi = instance.connect_in_woo()
        if woo_product_supplier and woo_product_supplier.exported_in_woo:
            res = wcapi.get("products/suppliers/%s"%(woo_product_supplier.woo_tag_id))
            if not isinstance(res,requests.models.Response):
                transaction_log_obj.create({'message':"Get Product Suppliers \nResponse is not in proper format :: %s"%(res),
                                                 'mismatch_details':True,
                                                 'type':'tags',
                                                 'woo_instance_id':instance.id
                                                })
                return True
            if res.status_code == 404:
                self.export_product_suppliers(instance, [woo_product_supplier])
                return True
            if res.status_code not in [200,201]:
                transaction_log_obj.create(
                                    {'message':res.content,
                                     'mismatch_details':True,
                                     'type':'suppliers',
                                     'woo_instance_id':instance.id
                                    })
                return True
            res = res.json()
            description = ''
            if instance.woo_version == 'old':
                description = res.get('product_supplier', {}).get('description', '')
            elif instance.woo_version == 'new':
                description = res.get('description')
            woo_product_supplier.write({'description': description})
        else:
            res = wcapi.get("products/suppliers")
            if not isinstance(res, requests.models.Response):
                transaction_log_obj.create({'message':"Get Product Suppliers \nResponse is not in proper format :: %s"%(res),
                                             'mismatch_details':True,
                                             'type':'suppliers',
                                             'woo_instance_id':instance.id
                                                })
                return True
            if res.status_code  not in [200,201]:
                transaction_log_obj.create({'message':"Get Product Suppliers \nResponse is not in proper format :: %s"%(res.content),
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
                                                 'type':'suppliers',
                                                 'woo_instance_id':instance.id
                                                })
                    return True
                results =  res.get('product_suppliers')
            elif instance.woo_version == 'new':
                results = res
            if total_pages >=2:
                for page in range(2,int(total_pages)+1):
                    results = results + self.import_all_tags(wcapi,instance,transaction_log_obj,page)

            for res in results:
                if not isinstance(res, dict):
                    continue
                supplier_id = res.get('id')
                name= res.get('name')
                description = res.get('description')
                slug = res.get('slug')
                woo_supplier = self.search([('woo_supplier_id','=',supplier_id),('woo_instance_id','=',instance.id)],limit=1)
                if not woo_supplier:
                    woo_supplier = self.search([('slug','=',slug),('woo_instance_id','=',instance.id)],limit=1)
                if woo_supplier:
                    woo_supplier.write({'woo_supplier_id':supplier_id,'name':name,'description':description,
                                   'slug':slug,'exported_in_woo':True})
                else:
                    self.create({'woo_supplier_id':supplier_id,'name':name,'description':description,
                                 'slug':slug,'woo_instance_id':instance.id,'exported_in_woo':True})
        return True















