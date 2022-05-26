from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
from openerp.osv.fields import _column
import xmlrpclib
from openerp.tools.translate import _
from openerp.osv.orm import except_orm

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
        consumer_product_data = ""
        product_data = ""
        if data.consumer == True or data.retail == True:
            woo_instance_obj = self.pool.get('woo.instance.ept')
            product_obj = self.pool.get('product.product')
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
                        product_code = pricelist_item.product_id.default_code
                        if not product_code:
                            raise except_orm(_('UserError'), _("Please define product code for %s!") % (pricelist_item.product_id.name_template,))
                        product=product_obj.browse(cr,uid,pricelist_item.product_id.id)
                        if not product.product_tmpl_id.ecommerce_uom_id:
                            raise except_orm(_('UserError'), _("Please define Ecommerce UOM  for %s!") % (pricelist_item.product_id.name_template,))
                        if product.product_tmpl_id.uom_id.id !=product.product_tmpl_id.ecommerce_uom_id.id:
                            product_uom = self.pool['product.uom'].search(cr,uid,[('id', '=', product.product_tmpl_id.ecommerce_uom_id.id)],context=None)
                            if product_uom:
                                product_uom = self.pool['product.uom'].browse(cr, uid, product_uom)
                                price = pricelist_item.new_price * product_uom.factor_inv
                        else:
                            price = pricelist_item.new_price
                        pricelist_id = data.id
                        if data.consumer == True:                                                    
                            price_info = product_code + "," + str(int(price)) + ",,"                                           
                            if consumer_product_data == "":
                                consumer_product_data = price_info
                            else:
                                consumer_product_data = consumer_product_data + "/ " + price_info
                        if data.retail == True and data.branch_id:
                            price_info = product_code + "," + str(int(price)) + "," + str(data.branch_id.name)
                            if product_data == "":
                                product_data = price_info
                            else:
                                product_data = product_data + "/ " + price_info
            if consumer_product_data:
                response = wcapi.put('dynamic-price-consumer-all-products', consumer_product_data)
                if response.status_code not in [200, 201]:
                    message = "Error in syncing response pricelist %s" % (response.content)
                    raise except_orm(_('UserError'), _("%s!") % (message,))
            if product_data:
                response = wcapi.put('insert-price-userrole-all-products',product_data)
                if response.status_code not in [200,201]:
                    message = "Error in syncing response pricelist %s"%(response.content)
                    raise except_orm(_('UserError'), _("%s!") % (message,))
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
            