from openerp import models,fields,api
import requests

class woo_departments_ept(models.Model):
    _name="woo.departments.ept"
    _order='name'

    name=fields.Char("Name")
    description=fields.Text('Description')
    woo_department_id = fields.Integer("Woo Department Id")
    slug = fields.Char(string='Slug',
                       help="The slug is the URL-friendly version of the name. It is usually all lowercase and contains only letters, numbers, and hyphens.")
    exported_in_woo = fields.Boolean("Exported In Woo", default=False)
    woo_instance_id = fields.Many2one("woo.instance.ept", "Instance", required=1)

    @api.model
    def export_product_departments(self, instance, woo_product_departments):
        transaction_log_obj = self.env['woo.transaction.log']
        wcapi = instance.connect_in_woo()
        for woo_product_department in woo_product_departments:
            row_data = {'name': woo_product_department.name, 'description': str(woo_product_department.description or '')}
            if woo_product_department.slug:
                row_data.update({'slug':str(woo_product_department.slug)})
            if instance.woo_version == 'old':
                data = {'product_department': row_data}
            elif instance.woo_version == 'new':
                data = row_data
            res = wcapi.post("products/departments", data)
            if not isinstance(res,requests.models.Response):
                transaction_log_obj.create({'message':"Export Product Departments \nResponse is not in proper format :: %s"%(res),
                                             'mismatch_details':True,
                                             'type':'tags',
                                             'woo_instance_id':instance.id
                                            })
                continue
            if res.status_code not in [200,201]:
                if res.status_code == 500:
                    response = res.json()
                    if isinstance(response,dict) and response.get('code')=='term_exists':
                        woo_product_department.write({'woo_department_id':response.get('data'),'exported_in_woo':True})
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
            product_department = False
            if instance.woo_version == 'old':
                errors = response.get('errors','')
                if errors:
                    message = errors[0].get('message')
                    message = "%s :: %s"%(message,woo_product_department.name)
                    transaction_log_obj.create(
                                                {'message':message,
                                                 'mismatch_details':True,
                                                 'type':'tags',
                                                 'woo_instance_id':instance.id
                                                })
                    continue
                product_department=response.get('product_department',False)
            elif instance.woo_version == 'new':
                product_department =response
            product_department_id = product_department and product_department.get('id', False)
            slug = product_department and product_department.get('slug', '')
            if product_department_id:
                woo_product_department.write({'woo_department_id': product_department_id, 'exported_in_woo': True, 'slug': slug})
        return True

    @api.model
    def update_product_departments_in_woo(self,instance,woo_product_departments):
        transaction_log_obj=self.env['woo.transaction.log']
        wcapi = instance.connect_in_woo()
        for woo_department in woo_product_departments:
            row_data = {'name':woo_department.name,'description':str(woo_department.description or '')}
            if woo_department.slug:
                row_data.update({'slug':str(woo_department.slug)})
            if instance.woo_version == 'old':
                data = {"product_department": row_data}
            elif instance.woo_version == 'new':
                data = row_data
            res = wcapi.put('products/departments/%s' % (woo_department.woo_department_id), data)
            if not isinstance(res, requests.models.Response):
                transaction_log_obj.create({'message':"Get Product Departments \nResponse is not in proper format :: %s"%(res),
                                             'mismatch_details':True,
                                             'type':'departments',
                                             'woo_instance_id':instance.id
                                            })
                continue
            if res.status_code not in [200,201]:
                transaction_log_obj.create(
                                                {'message':res.content,
                                                 'mismatch_details':True,
                                                 'type':'departments',
                                                 'woo_instance_id':instance.id
                                                })
                continue
            response = res.json()
            response_data = {}
            if not isinstance(response, dict):
                transaction_log_obj.create(
                                            {'message':"Response is not in proper format,Please Check Details",
                                             'mismatch_details':True,
                                             'type':'departments',
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
                                                 'type':'departments',
                                                 'woo_instance_id':instance.id
                                                })
                    continue
                else:
                    response_data = response.get('product_departments')
            else:
                response_data = response
            if response_data:
                woo_department.write({'slug':response_data.get('slug')})
        return True

    def import_all_departments(self,wcapi,instance,transaction_log_obj,page):
        res=wcapi.get('products/departments?page=%s'%(page))
        if not isinstance(res,requests.models.Response):
            transaction_log_obj.create({'message':"Get Product Departments \nResponse is not in proper format :: %s"%(res),
                                             'mismatch_details':True,
                                             'type':'departments',
                                             'woo_instance_id':instance.id
                                            })
            return []
        if res.status_code not in [200,201]:
            transaction_log_obj.create(
                                    {'message':res.content,
                                     'mismatch_details':True,
                                     'type':'departments',
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
                                             'type':'departments',
                                             'woo_instance_id':instance.id
                                            })
                return []
            return response.get('product_departments')
        elif instance.woo_version == 'new':
            return response


    @api.multi
    def sync_product_departments(self, instance, woo_product_department=False):
        transaction_log_obj=self.env["woo.transaction.log"]
        wcapi = instance.connect_in_woo()
        if woo_product_department and woo_product_department.exported_in_woo:
            res = wcapi.get("products/departments/%s"%(woo_product_department.woo_tag_id))
            if not isinstance(res,requests.models.Response):
                transaction_log_obj.create({'message':"Get Product Departments \nResponse is not in proper format :: %s"%(res),
                                                 'mismatch_details':True,
                                                 'type':'tags',
                                                 'woo_instance_id':instance.id
                                                })
                return True
            if res.status_code == 404:
                self.export_product_departments(instance, [woo_product_department])
                return True
            if res.status_code not in [200,201]:
                transaction_log_obj.create(
                                    {'message':res.content,
                                     'mismatch_details':True,
                                     'type':'departments',
                                     'woo_instance_id':instance.id
                                    })
                return True
            res = res.json()
            description = ''
            if instance.woo_version == 'old':
                description = res.get('product_department', {}).get('description', '')
            elif instance.woo_version == 'new':
                description = res.get('description')
            woo_product_department.write({'description': description})
        else:
            res = wcapi.get("products/departments")
            if not isinstance(res, requests.models.Response):
                transaction_log_obj.create({'message':"Get Product Departments \nResponse is not in proper format :: %s"%(res),
                                             'mismatch_details':True,
                                             'type':'departments',
                                             'woo_instance_id':instance.id
                                                })
                return True
            if res.status_code  not in [200,201]:
                transaction_log_obj.create({'message':"Get Product Departments \nResponse is not in proper format :: %s"%(res.content),
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
                                                 'type':'departments',
                                                 'woo_instance_id':instance.id
                                                })
                    return True
                results =  res.get('product_departments')
            elif instance.woo_version == 'new':
                results = res
            if total_pages >=2:
                for page in range(2,int(total_pages)+1):
                    results = results + self.import_all_tags(wcapi,instance,transaction_log_obj,page)

            for res in results:
                if not isinstance(res, dict):
                    continue
                department_id = res.get('id')
                name= res.get('name')
                description = res.get('description')
                slug = res.get('slug')
                woo_department = self.search([('woo_department_id','=',department_id),('woo_instance_id','=',instance.id)],limit=1)
                if not woo_department:
                    woo_department = self.search([('slug','=',slug),('woo_instance_id','=',instance.id)],limit=1)
                if woo_department:
                    woo_department.write({'woo_department_id':department_id,'name':name,'description':description,
                                   'slug':slug,'exported_in_woo':True})
                else:
                    self.create({'woo_department_id':department_id,'name':name,'description':description,
                                 'slug':slug,'woo_instance_id':instance.id,'exported_in_woo':True})
        return True















