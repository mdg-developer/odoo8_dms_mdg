from openerp import api, fields, models, _
from openerp.osv import osv
import requests
import json
import logging
import ast
from pyfcm import FCMNotification

_logger = logging.getLogger(__name__)


class product_approval(models.Model):
    _name = "product.approval"
    _description = "Product Approval"

    state = fields.Selection([('draft', 'Draft'), ('pending', 'Pending'), ('approved', 'Approved'), ('done', 'Done')],
                             'State', default='draft')
    product_name = fields.Char('Product Name', size=45)
    product_short_name = fields.Char('Product Short Name', size=45)
    description = fields.Char('Product Description')
    product_type = fields.Selection([('product', 'Stockable'), ('consu', 'Consumable'), ('service', 'Service')],
                                    'Product Type')
    image_medium = fields.Binary('Product Image')
    carton_image = fields.Binary('Carton Image')
    base_uom_id = fields.Many2one('product.uom', 'Base UOM')
    report_uom_id = fields.Many2one('product.uom', 'Report UOM')
    ecommerce_uom_id = fields.Many2one('product.uom', 'Ecommerce UOM')
    default_code = fields.Char('Internal Reference')
    sequence = fields.Integer('Sequence')
    product_principal_id = fields.Many2one('product.maingroup', 'Product Principal')
    product_group_id = fields.Many2one('product.group', 'Product Sub Group')
    product_category_id = fields.Many2one('product.category', 'Product Category')
    barcode_no = fields.Char('Barcode')
    barcode_ids = fields.One2many('product.multi.barcode', 'product_approval_id', string='Barcodes')
    uom_ratio = fields.Char('Packing Size')
    ctn_weight = fields.Float('Carton Weight')
    ctn_height = fields.Float('Carton Height')
    cbm_value = fields.Float('CBM(cm)')
    ti = fields.Float('Ti')
    hi = fields.Float('Hi')
    kg_value = fields.Float('Weight(Kg)')
    viss_value = fields.Float('Weight(Viss)')
    ctn_pallet = fields.Float('Ctn/Pallet')
    inbound_shelf_life = fields.Float('Inbound Shelf Life(Days)')
    inbound_shelf_life_min = fields.Float('Inbound Shelf Life(Minimum)')
    product_tmpl_id = fields.Many2one('product.template', 'Product', copy=False)
    is_prod_created = fields.Boolean('Is Product Created', copy=False)
    is_prod_changed = fields.Boolean('Is Product Changed', copy=False)

    @api.one
    @api.onchange('kg_value')
    def onchange_kg_value(self):
        kg_value = self.kg_value or 0
        self.viss_value = kg_value / 1.63

    @api.multi
    def action_done(self):
        vals = {}
        for item in self:
            vals.update({
                'name': item.product_name or '',
                'short_name': item.product_short_name or '',
                'description': item.description or '',
                'type': item.product_type or '',
                'image_medium': item.image_medium or '',
                'carton_image': item.carton_image or '',
                'uom_id': item.base_uom_id.id or '',
                'report_uom_id': item.report_uom_id.id or '',
                'default_code': item.default_code or '',
                'sequence': item.sequence or '',
                'main_group': item.product_principal_id.id or '',
                'group': item.product_group_id.id or '',
                'categ_id': item.product_category_id.id or '',
                'barcode_no': item.barcode_no or '',
                'barcode_ids': item.barcode_ids or '',
                'uom_ratio': item.uom_ratio or '',
                'ctn_weight': item.ctn_weight or '',
                'ctn_height': item.ctn_height or '',
                'cbm_value': item.cbm_value or '',
                'ti': item.ti or '',
                'hi': item.hi or '',
                'kg_value': item.kg_value or '',
                'viss_value': item.viss_value or '',
                'ctn_pallet': item.ctn_pallet or '',
                'inbound_shelf_life': item.inbound_shelf_life or '',
                'inbound_shelf_life_min': item.inbound_shelf_life_min or ''
            })
            if not item.is_prod_changed:
                try:
                    product_id = self.env['product.template'].create(vals)
                    if product_id:
                        self.state = 'done'
                        self.product_tmpl_id = product_id
                        self.is_prod_created = True
                except Exception as e:
                    raise osv.except_osv(_('Customer Creation Failed!'), _('Here is why:  %s!!!' % (e)))
            else:
                try:
                    product_id = item.product_tmpl_id.sudo().update(vals)
                    self.state = 'done'
                    self.is_prod_created = True
                except Exception as e:
                    raise osv.except_osv(_('Customer Updating Failed!'), _('Here is why:  %s!!!' % (e)))

    @api.multi
    def action_pending(self):
        self.state = 'pending'

    @api.multi
    def action_set_to_pending(self):
        self.state = 'pending'

    @api.multi
    def action_set_to_approved(self):
        self.state = 'approved'
        self.is_prod_changed = True

    @api.multi
    def action_approved(self):
        self.state = 'approved'

    # @api.multi
    # def write(self, vals, context=None):
    #     _logger.info('--------------write()---------')
    #     if self.state == 'done' and vals.get('state') == 'approved':
    #         self.action_approved
    #     return super(product_approval, self).write(vals)

