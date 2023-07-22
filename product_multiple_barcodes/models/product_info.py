from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import api
from datetime import datetime

class product_info(osv.osv):
    _name = "product.info"
    _columns = {

        'product_tmpl_id': fields.many2one('product.template', 'Product'),
        'ti':fields.integer('TI'),
        'hi':fields.integer('HI'),
        'viss_value': fields.float('Viss'),
        'kg_value': fields.float('Kg'),
        'cbm_value': fields.float('CBM'),
        'ctn_pallet': fields.float('Ctn/Pallet'),
        'barcode_no': fields.char('Barcode'),
        'ctn_weight': fields.float('Carton Weight'),
        'ctn_height': fields.float('Carton Height'),
        'inbound_shelf_life': fields.float('Inbound Shelf Life'),
        'inbound_shelf_life_min': fields.float('Inbound Shelf Life (Min Days)'),
        'image_medium' : fields.binary("Product Image"),
        'state': fields.selection([('draft', 'Draft'),('done', 'Confirmed')], 'Status'),
        'confirm_date': fields.datetime('Confirm Date'),
        'confirm_by':fields.many2one('res.users', 'Confirm By'),
        'carton_image': fields.binary("Carton Image"),
        'barcode_ids': fields.one2many('product.multi.barcode', 'product_info_id', string='Barcodes'),
        'description':fields.char('Product Description'),
        'default_code':fields.char('Internal Referencce'),
        'ctn_pallet_pickface':fields.float('Ctn/Pallet'),
        'big_uom_length': fields.float('Big UOM (L) cm'),
        'big_uom_breadth': fields.float('Big UOM (B) cm'),
    }

    _defaults = {
        'state': 'draft',
    }

    def on_change_kg_value(self, cr, uid, ids, kg_value, context=None):
        viss_value = kg_value / 1.63
        return {'value':{'viss_value':viss_value}}
    
    @api.one
    @api.onchange('ctn_height')
    def on_change_lenght_breadth_height(self):
        cbm_value = self.big_uom_length * self.big_uom_breadth * self.ctn_height
        self.cbm_value = cbm_value

    @api.one
    @api.onchange('hi')
    def on_change_ti_hi(self):
        pallet_value = self.ti * self.hi
        self.ctn_pallet = pallet_value

    @api.one
    @api.onchange('product_tmpl_id')
    def onchange_product_id(self):
        self.ti = self.product_tmpl_id.ti
        self.hi = self.product_tmpl_id.hi
        self.viss_value = self.product_tmpl_id.viss_value
        self.kg_value = self.product_tmpl_id.ctn_weight
        self.big_uom_length =  self.product_tmpl_id.big_uom_length
        self.big_uom_breadth =  self.product_tmpl_id.big_uom_breadth
        self.ctn_height = self.product_tmpl_id.ctn_height
        self.cbm_value = self.product_tmpl_id.cbm_value
        self.ctn_pallet = self.product_tmpl_id.ctn_pallet
        self.ctn_pallet_pickface = self.product_tmpl_id.ctn_pallet_pickface
        self.barcode_no = self.product_tmpl_id.barcode_no
        self.carton_image = self.product_tmpl_id.carton_image
        self.image_medium = self.product_tmpl_id.image_medium
        self.barcode_ids = self.product_tmpl_id.barcode_ids
        self.inbound_shelf_life = self.product_tmpl_id.inbound_shelf_life
        self.inbound_shelf_life_min = self.product_tmpl_id.inbound_shelf_life_min
        self.description = self.product_tmpl_id.description
        self.default_code = self.product_tmpl_id.default_code

    def confirm(self, cr, uid, ids, context=None):
        for flag in self.browse(cr, uid, ids, context=context):
            flag.product_tmpl_id.sudo().update({
                'ti':flag.ti,
                'hi':flag.hi,
                'viss_value':flag.viss_value,
                'ctn_weight': flag.kg_value,
                'big_uom_length': flag.big_uom_length,
                'big_uom_breadth': flag.big_uom_breadth,
                'ctn_height': flag.ctn_height,
                'cbm_value':flag.cbm_value,
                'ctn_pallet':flag.ctn_pallet,
                'ctn_pallet_pickface':flag.ctn_pallet_pickface,
                'barcode_no':flag.barcode_no,
                'image_medium':flag.image_medium,
                'carton_image': flag.carton_image,
                'inbound_shelf_life': flag.inbound_shelf_life,
                'inbound_shelf_life_min': flag.inbound_shelf_life_min,
                'description':flag.description,
                'default_code':flag.default_code,
            })

            flag.update({'state':'done'})
        return True