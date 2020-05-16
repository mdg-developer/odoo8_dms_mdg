#from firebase import firebase
from firebase.firebase import FirebaseApplication, FirebaseAuthentication
from openerp import models, fields, api
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

class product_product(models.Model):
    _inherit = 'product.product' 
    
    def sync_cloud_filestore(self):
        cred = credentials.Certificate('/opt/odoo/customs/custom_addons_new/firebase_cloud_filestore_sync/json/tabletsales-1373-firebase-adminsdk-12xpb-9cafccb3de.json')
        firebase_admin.initialize_app(cred)
        
        db = firestore.client()
        
        #get product
        self._cr.execute("""select  pp.id,pt.list_price,coalesce(replace(pt.description,',',';'), ' ') as description,pt.categ_id,pc.name as categ_name,pp.default_code, 
            pt.name,substring(replace(cast(pt.image_small as text),'/',''),1,5) as image_small,pt.main_group,pt.uom_ratio,
            pp.product_tmpl_id,pt.is_foc,pp.sequence,pt.type,pt.uom_id,ccs.id section_id
            from product_sale_group_rel rel ,
            crm_case_section ccs ,product_template pt, product_product pp , product_category pc
            where pp.id = rel.product_id
            and pt.id = pp.product_tmpl_id
            and pt.active = true
            and pp.active = true
            and ccs.sale_group_id = rel.sale_group_id
            and pc.id = pt.categ_id""")
        for row in self._cr.dictfetchall():
            node = 'product_product_id_' + str(row['id'])
            doc_ref = db.collection('product_product').document(node)
            doc_ref.set(row)
        
        #get uom
        self._cr.execute("""select distinct uom_id,uom_name,ratio,template_id,product_id from(
                    select  pu.id as uom_id,pu.name as uom_name ,floor(round(1/factor,2)) as ratio,
                    pur.product_template_id as template_id,pp.id as product_id,ccs.id as section_id
                    from product_uom pu , product_template_product_uom_rel pur ,
                    product_product pp,
                    product_sale_group_rel rel,crm_case_section ccs
                    where pp.product_tmpl_id = pur.product_template_id
                    and rel.product_id = pp.id
                    and pu.id = pur.product_uom_id
                    and rel.sale_group_id=ccs.sale_group_id""")
        for row in self._cr.dictfetchall():
            node = 'uom_uom_id_' + str(row['uom_id'])
            doc_ref = db.collection('uom_uom').document(node)
            doc_ref.set(row)    

#     def sync_product_product(self):
#         
#         self._cr.execute("""select  pp.id,pt.list_price,coalesce(replace(pt.description,',',';'), ' ') as description,pt.categ_id,pc.name as categ_name,pp.default_code, 
#             pt.name,substring(replace(cast(pt.image_small as text),'/',''),1,5) as image_small,pt.main_group,pt.uom_ratio,
#             pp.product_tmpl_id,pt.is_foc,pp.sequence,pt.type,pt.uom_id,ccs.id section_id
#             from product_sale_group_rel rel ,
#             crm_case_section ccs ,product_template pt, product_product pp , product_category pc
#             where pp.id = rel.product_id
#             and pt.id = pp.product_tmpl_id
#             and pt.active = true
#             and pp.active = true
#             and ccs.sale_group_id = rel.sale_group_id
#             and pc.id = pt.categ_id""")
#         firebase = FirebaseApplication('https://tabletsales-1373.firebaseio.com', None)         
#         for row in self._cr.dictfetchall():
#             res = {
#                 'id': row['id'],
#                 'list_price': row['list_price'],
#                 'description': row['description'],                
#                 'categ_id': row['categ_id'] ,
#                 'categ_name': row['categ_name'],
#                 'default_code': row['default_code'],
#                 'name': row['name'],
#                 'image_small': row['image_small'],
#                 'main_group': row['main_group'],
#                 'uom_ratio':row['uom_ratio'],
#                 'product_tmpl_id':row['product_tmpl_id'],
#                 'is_foc':row['is_foc'],
#                 'sequence':row['sequence'],
#                 'type':row['type'],
#                 'uom_id':row['uom_id'],
#                 'section_id':row['section_id'],
#             }
#             snapshot = firebase.post('/product_product', res)    

#     def sync_user(self):
#         print "Hello Testing"
#         firebase = FirebaseApplication('https://tabletsales-1373.firebaseio.com', None)
#         #new_user1 = 'Ozgur Vatansever'
#         
#         #result = firebase.post('/_user', new_user1, {'print': 'pretty'}, {'X_FANCY_HEADER': 'VERY FANCY'})
#         #print result
#         data = {'name': 'Ozgur Vatansever', 'age': 26}
# 
#         snapshot = firebase.post('/users', data)
#         print(snapshot['name'])
#         data = {'name': 'Hello', 'age':27}
#         snapshot = firebase.post('/users',data)
        #new_user2 = 'Hello'
        #result = firebase.post('/test_user', new_user2, {'print': 'silent'}, {'X_FANCY_HEADER': 'VERY FANCY'})
        #print result == None
        #True
#     def sync_product(self):
#         
#         
#         db = firestore.client()
#         self._cr.execute("""select  pp.id,pt.list_price,coalesce(replace(pt.description,',',';'), ' ') as description,pt.categ_id,pc.name as categ_name,pp.default_code, 
#                     pt.name,substring(replace(cast(pt.image_small as text),'/',''),1,5) as image_small,pt.main_group,pt.uom_ratio,
#                     pp.product_tmpl_id,pt.is_foc,pp.sequence,pt.type,pt.uom_id,ccs.id section_id
#                     from product_sale_group_rel rel ,
#                     crm_case_section ccs ,product_template pt, product_product pp , product_category pc
#                     where pp.id = rel.product_id
#                     and pt.id = pp.product_tmpl_id
#                     and pt.active = true
#                     and pp.active = true
#                     and ccs.sale_group_id = rel.sale_group_id
#                     and pc.id = pt.categ_id""")
#         
#         for row in self._cr.dictfetchall():
#             
#             node_name = 'product_id_' + str(row['id'])
#             doc_ref = db.collection('product_product').document(node_name)
#             res = {
#                 'id': row['id'],
#                 'list_price': row['list_price'],
#                 'description': row['description'],                
#                 'categ_id': row['categ_id'] ,
#                 'categ_name': row['categ_name'],
#                 'default_code': row['default_code'],
#                 'name': row['name'],
#                 'image_small': row['image_small'],
#                 'main_group': row['main_group'],
#                 'uom_ratio':row['uom_ratio'],
#                 'product_tmpl_id':row['product_tmpl_id'],
#                 'is_foc':row['is_foc'],
#                 'sequence':row['sequence'],
#                 'type':row['type'],
#                 'uom_id':row['uom_id'],
#                 'section_id':row['section_id'],
#             }
#             doc_ref.set(res)
            
