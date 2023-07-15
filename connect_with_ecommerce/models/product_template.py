from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
from openerp.osv.fields import _column
import xmlrpclib
from openerp import api
import re

import logging

_logger = logging.getLogger(__name__)

class product_product(osv.osv):
    _inherit = "product.product"
    _columns = {
         'is_sync_ecommerce':fields.boolean('Is Sync Ecommerce',default=False),

        }    
class product_template(osv.osv):
    _inherit = 'product.template' 
    _order = 'sequence asc'
    _columns = {
        'is_sync_ecommerce': fields.related('product_variant_ids', 'is_sync_ecommerce', type='boolean', string='Is Sync Ecommerce', required=False),
        'short_name': fields.char('Product Short Name', size=45),
        'myanmar_name': fields.char('Product Myanmar Name', size=33),
        'city_lines':fields.many2many('res.city'),
#         'ecommerce_price': fields.float('Price'),
        'ecommerce_uom_id': fields.many2one('product.uom', 'UOM'),
        'delivery_id':fields.many2one('delivery.group', 'Delivery Group',required=False),
        'brand_id': fields.many2one('product.brand', 'Product Brand'),
        'tag_ids': fields.many2many('product.tag', 'product_template_tags_rel', 'product_template_id', 'tag_id',
                                    "Product Tag"),
        'ecommerce_supplier_id': fields.many2one('product.supplier', 'Product Supplier'),
        'ecommerce_department_id': fields.many2one('product.department', 'Product Department'),
        'is_generated_code':fields.boolean('Is Generated Code'),
        'is_generated_int_ref': fields.boolean('Is Generated Internal Reference',default=False),
            }

    def default_get(self, cr, uid, fields, context=None):
        res = super(product_template, self).default_get(cr, uid, fields, context=context)
        res['type'] = 'product'
        res['cost_method'] = 'real'
        res['valuation'] = 'real_time'
        # not work
        res['taxes_id'] = [(6, 0, [1])] 
        return res
    # helper function
    def generate_product_code_old(self, cr, uid, ids, context=None):
        records = []
        sorted_records = []
        product_code = ''
        for rec in self.browse(cr, uid, ids, context=None):
            categ_id = rec.categ_id.id
            uom_ratio = rec.uom_ratio
            categ_data = self.pool.get('product.category').browse(cr, uid, categ_id, context=context)
            cr.execute(""" select uom_ratio from product_template where categ_id = %s order by uom_ratio asc;""",(categ_id,))
            res = cr.fetchall()
            if res:
                records = [i[0] for i in res]
            _logger.info('--------------------')
            _logger.info('records>>>>>> %s',records)
            # stripped_records = [re.sub(r'[a-wy-zA-WY-Z]+', '', item).replace('*', 'x').replace('X','x').replace(' ','') for item in records if item is not None]
            stripped_records = [re.sub(r'[^x\d]', '', re.sub(r'[X*]', 'x', item)) for item in records if item is not None]
            _logger.info('--------------------')
            _logger.info('stripped_records>>>>>> %s',stripped_records)
            # for record in stripped_records:
            #     right_side = record.partition('x')[2].rstrip(')')
            #     try:
            #         if right_side.isdigit():
            #             sorted_records.append((record, int(right_side)))
            #         else:
            #             sorted_records.append((record, float(right_side)))
            #     except ValueError as v:
            #         _logger.info('Error >>>>>> %s',v)
            sorted_records = sorted(stripped_records, key=lambda x: int(x.partition('x')[2].rstrip(')')) if x.partition('x')[2].rstrip(')').isdigit() else (float(x.partition('x')[2].rstrip(')')) if x.partition('x')[2].rstrip(')').isdigit() else float('inf')))
            _logger.info('--------------------')
            _logger.info('sorted_records>>>>>> %s',sorted_records)
            if uom_ratio:
                stripped_uom_ratio = re.sub(r'[a-wy-zA-WY-Z]+', '', uom_ratio).replace('*', 'x').replace('X','x')
                if stripped_uom_ratio in sorted_records:
                    index = sorted_records.index(stripped_uom_ratio) + 1
                    sku_code = "%03d" % index
                    categ_code = categ_data.code
                    # cr.execute("""insert into principal_category_code (principal_code,category_code,category_id) values (%s,%s,%s)""",(rec['principal_code'],category_code,category.id,))
                    if categ_code:
                        product_code = categ_code + '-' + sku_code
                    else:
                        raise Warning('Please Define Category Code for: %s',categ_data.name)
            return self.write(cr, uid, ids, {'default_code':product_code})
    
    def generate_product_code(self, cr, uid, ids, context=None):
        vals = {}
        product_code = 0
        for rec in self.browse(cr, uid, ids, context=None):
            categ_id = rec.categ_id.id
            categ_code = rec.categ_id.code
            if categ_code:
                _logger.info('categ_id--------------%s',categ_id)
                cr.execute(""" select id,sequence from product_template where categ_id = %s and is_generated_code=True order by sequence desc limit 1;""",(categ_id,))
                records = cr.dictfetchall()
                # sequence = '001'
                sku_code = '001'
                if records:
                    for rec in records:
                        if rec['sequence'] != None:
                            sequence = rec['sequence']
                            _logger.info('sequence--------------%s',sequence)
                            sequence = int(sequence) + 1
                        product_code = sequence
                else:
                    product_code = categ_code + sku_code
        vals.update({'sequence':product_code,'is_generated_code':True})
        return self.write(cr, uid, ids, vals)

    # Generate product internal reference only with ir.sequence
    # this button disappear when is_generated_int_ref True
    def generate_internal_ref(self, cr, uid, ids, context=None):
        vals = {}
        internal_ref = self.pool.get('ir.sequence').get(cr, uid, 'product.template.code') or '/'
        vals.update({'default_code':internal_ref,'is_generated_int_ref':True})
        return self.write(cr, uid, ids, vals)

    def on_change_uom_id(self, cr, uid, ids, uom_id, context=None):
        if uom_id:
            return {'value':{'uom_po_id': uom_id}}
    
    def onchange_report_uom_id(self, cr, uid, ids, uom_id, report_uom_id, context=None):
        domain = { }
        if uom_id and report_uom_id:
            base_uom = uom_id
            report_uom = report_uom_id
            domain['ecommerce_uom_id'] = [('id','in',[base_uom,report_uom])]
        return {'domain':domain}

class product_uom_price(osv.osv):
    _inherit = 'product.uom.price'
    
    _columns = {
        
        'for_ecommerce':fields.boolean('For E-Commerce' , default=True),

    }