from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
from openerp.osv.fields import _column
import xmlrpclib

class product_pricelist(osv.osv):
    _inherit = "product.pricelist"
    
    _columns = {
                'city_id':fields.many2one('res.city','City'),
                'township_id':fields.many2one('res.township','Township'),
                'retail':fields.boolean('Is Retail Pricelist' , default=False),
                'is_sync_woo':fields.boolean('Is Sync Woo', default=False),
            }   
    
    def write(self, cr, uid, ids, vals, context=None):  
        data = self.browse(cr,uid,ids[0])
        if data.is_sync_woo == True: 
            vals['is_sync_woo']=False
        res = super(product_pricelist, self).write(cr, uid, ids, vals, context=context)
        return res 
    
    def sync_to_woo(self, cr, uid, ids, context=None):
        
        data = self.browse(cr,uid,ids[0])
        if data.consumer == True or data.retail == True:
            woo_instance_obj = self.pool.get('woo.instance.ept')
            pricelist_item_obj = self.pool.get('product.pricelist.item')
            instance = woo_instance_obj.search(cr, uid, [('state','=','confirmed')], limit=1)
            if instance:
                instance_obj = woo_instance_obj.browse(cr,uid,instance)
                wcapi = instance_obj.connect_for_point_in_woo()   
            pricelist_version_ids = self.pool['product.pricelist.version'].search(cr,uid,[('pricelist_id','=',data.id)],context=None)
            if pricelist_version_ids:
                for version_id in pricelist_version_ids:
                    for version_item in self.pool['product.pricelist.item'].search(cr,uid,[('price_version_id','=',version_id)],context=None):
                        pricelist_item = pricelist_item_obj.browse(cr,uid,version_item)
                        if pricelist_item.product_uom_id.id == pricelist_item.product_id.product_tmpl_id.ecommerce_uom_id.id:
                            product_code = pricelist_item.product_id.product_tmpl_id.default_code
                            price = pricelist_item.new_price
                            pricelist_id = data.id
                            if product_code:
                                if data.consumer == True:                            
                                    price_info = product_code + "," + str(int(price)) + "," + str(pricelist_id) + ',consumer'                        
                                    wcapi.put('dynamic-price-consumer',price_info) 
                                if data.retail == True:
                                    price_info = product_code + "," + str(int(price)) + "," + str(pricelist_id) + ',retail'                      
                                    wcapi.put('dynamic-price-retailer',price_info)
            if data.is_sync_woo != True:
                self.write(cr, uid, ids, {'is_sync_woo': True}, context=context)
            
class product_pricelist_version(osv.osv):
    _inherit = 'product.pricelist.version'
    
    _columns = {
                'city_id' : fields.related('pricelist_id', 'city_id',
                                       type='many2one',
                                       readonly=True,
                                     relation='res.city',
                                       string='City'),
                'township_id' : fields.related('pricelist_id', 'township_id',
                                       type='many2one',
                                       readonly=True,
                                     relation='res.township',
                                       string='Township'),
                'is_sync_woo':fields.boolean('Is Sync Woo', default=False),
            }
    
    def write(self, cr, uid, ids, vals, context=None):  
        data = self.browse(cr,uid,ids[0])
        if data.is_sync_woo == True: 
            vals['is_sync_woo']=False
        res = super(product_pricelist_version, self).write(cr, uid, ids, vals, context=context)
        return res 
    
    def sync_to_woo(self, cr, uid, ids, context=None):
        
        data = self.browse(cr,uid,ids[0])
        data.pricelist_id.sync_to_woo()
        if data.is_sync_woo != True:
            self.write(cr, uid, ids, {'is_sync_woo': True}, context=context)
            