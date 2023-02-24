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
        'viss_value': fields.float('Viss',compute='_compute_viss_value'),
        'cbm_value': fields.float('CBM'),
        'ctn_pallet': fields.float('Ctn/Pallet'),
        'barcode_no': fields.char('Barcode'),
        'ctn_weight': fields.float('Carton Weight'),
        'ctn_height': fields.float('Carton Height'),
        'inbound_shelf_life': fields.float('Inbound Shelf Life'),
        'image_medium' : fields.binary("Product Image"),
        'state': fields.selection([('draft', 'Draft'),('done', 'Confirmed')], 'Status'),
        'confirm_date': fields.datetime('Confirm Date'),
        'confirm_by':fields.many2one('res.users', 'Confirm By'),
        'carton_image': fields.binary("Carton Image"),
        'barcode_ids': fields.one2many('product.multi.barcode', 'product_info_id', string='Barcodes'),
        'description':fields.char('Product Description'),
        'default_code':fields.char('Internal Referencce')

    }

    _defaults = {
        'state': 'draft',
    }

    @api.one
    @api.onchange('product_tmpl_id')
    def onchange_product_id(self):
        self.ti = self.product_tmpl_id.ti
        self.hi = self.product_tmpl_id.hi
        self.viss_value = self.product_tmpl_id.viss_value
        self.cbm_value = self.product_tmpl_id.cbm_value
        self.ctn_pallet = self.product_tmpl_id.ctn_pallet
        self.barcode_no = self.product_tmpl_id.barcode_no
        self.carton_image = self.product_tmpl_id.carton_image
        self.image_medium = self.product_tmpl_id.image_medium
        self.barcode_ids = self.product_tmpl_id.barcode_ids
        self.ctn_weight = self.product_tmpl_id.ctn_weight
        self.ctn_height = self.product_tmpl_id.ctn_height
        self.inbound_shelf_life = self.product_tmpl_id.inbound_shelf_life
        self.description = self.product_tmpl_id.description
        self.default_code = self.product_tmpl_id.default_code

    def confirm(self, cr, uid, ids, context=None):
        for flag in self.browse(cr, uid, ids, context=context):
            flag.product_tmpl_id.sudo().update({
                'ti':flag.ti,
                'hi':flag.hi,
                'viss_value':flag.viss_value,
                'cbm_value':flag.cbm_value,
                'ctn_pallet':flag.ctn_pallet,
                'barcode_no':flag.barcode_no,
                'image_medium':flag.image_medium,
                'carton_image': flag.carton_image,
                'ctn_weight': flag.ctn_weight,
                'ctn_height': flag.ctn_height,
                'inbound_shelf_life': flag.inbound_shelf_life,
                'description':flag.description,
                'default_code':flag.default_code,
            })

            flag.update({'state':'done'})
        return True