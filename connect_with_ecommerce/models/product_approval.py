from openerp import api,fields, models, _
from openerp.osv import osv
import requests
import json
import logging
import ast
import re
from pyfcm import FCMNotification

_logger = logging.getLogger(__name__)

class product_approval(models.Model):
    _name = "product.approval"
    _description = "Product Approval"
    _inherit = ['mail.thread']

    state = fields.Selection([('draft', 'Draft'),('pending','Pending'),('approved','Approved'),('done','Done')], 'State', default='draft')
    product_name = fields.Char('Product Name',size=45)
    product_short_name = fields.Char('Product Short Name',size=45)
    product_myanmar_name = fields.Char('Product Myanmar Name', size=45)
    description =fields.Text('Product Description')
    product_type = fields.Selection([('product','Stockable'),('consu','Consumable'),('service','Service')], 'Product Type', default='product')
    image_medium =  fields.Binary('Product Image')
    carton_image =  fields.Binary('Carton Image')
    base_uom_id = fields.Many2one('product.uom','Base UOM')
    report_uom_id = fields.Many2one('product.uom','Report UOM')
    ecommerce_uom_id = fields.Many2one('product.uom','Ecommerce UOM')
    default_code = fields.Char('Internal Reference')
    # sequence = fields.Integer('Sequence')
    product_principal_id = fields.Many2one('product.maingroup','Product Principal')
    product_group_id = fields.Many2one('product.group','Burmart')
    product_category_id = fields.Many2one('product.category','MDG Category')
    barcode_no = fields.Char('Barcode')
    barcode_ids = fields.One2many('product.multi.barcode', 'product_approval_id', string='Barcodes')
    barcode_approval_ids = fields.One2many('product.multi.barcode.approval', 'product_approval_id', string="Product Multi Barcodes")
    uom_ratio = fields.Char('Packing Size')
    ctn_height = fields.Float('Carton Height')
    cbm_value = fields.Float('Big UOM (cm3)')
    ti =fields.Integer('Ti')
    hi =fields.Integer('Hi')
    ctn_weight = fields.Float('Big UOM Weight (Kg)')
    viss_value = fields.Float('Weight(Viss)')
    ctn_pallet = fields.Integer('Ctn/Pallet (Racking)')
    inbound_shelf_life = fields.Integer('Inbound Shelf Life(Days)')
    inbound_shelf_life_min = fields.Integer('Inbound Shelf Life(Minimum)')
    product_tmpl_id = fields.Many2one('product.template','Product', copy=False)
    is_prod_created = fields.Boolean('Is Product Created', copy=False)
    is_prod_changed = fields.Boolean('Is Product Changed', copy=False)
    small_uom_weight = fields.Float('Small UOM Weight (Kg)')
    big_uom_length = fields.Float('Big UOM (L) cm')
    big_uom_breadth = fields.Float('Big UOM (B) cm')
    big_uom_height = fields.Float('Big UOM (H) cm')
    ctn_pallet_pickface = fields.Integer('Ctn/Pallet (Pickface)')
    tag_ids = fields.Many2many('product.tag', 'product_template_tags_rel', 'product_template_id', 'tag_id',"Product Tag")
    brand_id = fields.Many2one('product.brand','Product Brand')
    supplier_id = fields.Many2one('product.supplier','Product Supplier')
    department_id = fields.Many2one('product.department','Product Department')
    uom_price_lines = fields.One2many('product.uom.price','product_approval_id','Uom Price Lines')
    uom_lines = fields.Many2many('product.uom')
    purchase_uom_id = fields.Many2one('product.uom','Purchase UOM')
    # updated_by = fields.Many2one('res.users', string="Last Updated By")
    # updated_time = fields.Datetime(string='Last Updated On')
    sale_description =fields.Text('Sale Description')


    def create(self, cr, uid, vals, context=None):
        # pattern = r"^\S[^!@#$%^*={}|[\]:';<>,.?/\\]*\S$"
        pattern = r'^(?!\s|\S.*\s$).+$'
        product_name = vals.get('product_name')
        short_name = vals.get('product_short_name')
        barcode = vals.get('barcode_no')
        if product_name:
            # approval_prod_name = self.env['product.approval'].search([('product_name','=',product_name)])
            # if product_name == approval_prod_name:
            #     raise osv.except_osv(_('Product Name Error!'), _('Cannot create Product because of duplicate Product Name!!!'))
            if not re.match(pattern, product_name):
                raise osv.except_osv(_('Product Name Error!'), _('Product Name Contains front/rear spaces %s!!!'% (product_name)))
        if short_name:
            if not re.match(pattern, short_name):
                raise osv.except_osv(_('Product Short Name Error!'), _('Product Short Name Contains front/rear spaces %s!!!'% (short_name)))
        if barcode:
            if not re.match(pattern, barcode):
                raise osv.except_osv(_('Barcode Error!'), _('Barcode Contains front/rear spaces %s!!!'% (barcode)))

        # vals['updated_time'] = fields.datetime.now()
        # vals['updated_by'] = uid
        return super(product_approval, self).create(cr, uid, vals, context=context)
    
    def write(self, cr, uid, ids, vals, context=None):
        # pattern = r"^\S[^!@#$%^*={}|[\]:';<>,.?/\\]*\S$"
        pattern = r'^(?!\s|\S.*\s$).+$'
        product_name = vals.get('product_name')
        short_name = vals.get('product_short_name')
        barcode = vals.get('barcode_no')
        if product_name:
            if not re.match(pattern, product_name):
                raise osv.except_osv(_('Product Name Error!'), _('Product Name Contains front/rear spaces %s!!!'% (product_name)))
        if short_name:
            if not re.match(pattern, short_name):
                raise osv.except_osv(_('Product Short Name Error!'), _('Product Short Name Contains front/rear spaces %s!!!'% (short_name)))
        if barcode:
            if not re.match(pattern, barcode):
                raise osv.except_osv(_('Barcode Error!'), _('Barcode Contains front/rear spaces %s!!!'% (barcode)))

        # vals['updated_time'] = fields.datetime.now()
        # vals['updated_by'] = uid
        return super(product_approval, self).write(cr, uid, ids, vals, context=context)

    @api.one
    @api.onchange('base_uom_id')
    def on_change_uom_id(self):
        if self.base_uom_id:
            self.purchase_uom_id = self.base_uom_id

    @api.one
    @api.onchange('ctn_weight')
    def onchange_ctn_weight(self):
        ctn_weight = self.ctn_weight or 0
        self.viss_value = ctn_weight/ 1.63

    @api.one
    @api.onchange('hi')
    def on_change_ti_hi(self):
        pallet_value = self.ti * self.hi
        self.ctn_pallet = pallet_value

    @api.onchange('report_uom_id')
    def onchange_report_uom_id(self):
        domain = { }
        if self.base_uom_id and self.report_uom_id:
            base_uom = self.base_uom_id.id
            report_uom = self.report_uom_id.id
            domain['ecommerce_uom_id'] = [('id','in',(base_uom,report_uom))]
        return {'domain':domain}

    @api.one
    @api.onchange('ctn_height')
    def on_change_lenght_breadth_height(self):
        cbm_value = self.big_uom_length * self.big_uom_breadth * self.ctn_height
        self.cbm_value = cbm_value
    
    @api.multi
    def action_done(self):
        vals = {}
        tag_list = []
        price_line_list = []
        uom_list = []
        barcode_list = []
        old_barcode_list = []
        new_barcode_list = []
        for item in self:
            for tag_id in item.tag_ids:
                tag_list.append(tag_id.id)
            for price_line in item.uom_price_lines:
                price_line_list.append(price_line.id)
            for uom in item.uom_lines:
                uom_list.append(uom.id)   
            vals.update({
                'name': item.product_name or '',
                'short_name': item.product_short_name or '',
                'myanmar_name': item.product_myanmar_name or '',
                'description': item.description or '',
                'description_sale': item.sale_description or '',
                'type': item.product_type or '',
                'image_medium': item.image_medium or '',
                'carton_image': item.carton_image or '',
                'uom_id': item.base_uom_id.id or '',
                'report_uom_id': item.report_uom_id.id or '',
                'default_code': item.default_code or '',
                'sequence': 0,
                'main_group': item.product_principal_id.id or '',
                'group': item.product_group_id.id or '',
                'categ_id': item.product_category_id.id or '',
                'barcode_no': item.barcode_no or '',
                # 'barcode_ids': [(6, 0, item.barcode_ids.ids)],
                'uom_ratio': item.uom_ratio or '', 
                'ctn_weight': item.ctn_weight or '',
                'ctn_height': item.ctn_height or '',
                'cbm_value': item.cbm_value or '',
                'ti': item.ti or '',
                'hi': item.hi or '',
                'viss_value': item.viss_value or '',
                'ctn_pallet': item.ctn_pallet or '',
                'inbound_shelf_life': item.inbound_shelf_life or '',
                'inbound_shelf_life_min': item.inbound_shelf_life_min or '',
                'small_uom_weight': item.small_uom_weight or '',
                'big_uom_length': item.big_uom_length or '',
                'big_uom_breadth': item.big_uom_breadth or '',
                'ctn_height': item.big_uom_height or '',
                'ctn_pallet_pickface': item.ctn_pallet_pickface or '',
                'ecommerce_uom_id': item.ecommerce_uom_id.id or '',
                'tag_ids': [(6, 0, tag_list)],
                'brand_id': item.brand_id.id,
                'ecommerce_supplier_id': item.supplier_id.id,
                'ecommerce_department_id': item.department_id.id,
                'weight': 0.0,
                'uom_price_lines':[(6,0,price_line_list)],
                'uom_lines': [(6, 0, uom_list)],
                'uom_po_id': item.purchase_uom_id.id,
                'write_uid': item.write_uid,
                'write_date': item.write_date,
            })

            if not item.is_prod_changed:
                try:
                    product_id = self.env['product.template'].create(vals)
                    if product_id:
                        self.state = 'done'
                        self.product_tmpl_id = product_id
                        self.is_prod_created = True
                        for barcode in item.barcode_approval_ids:
                            barcode_list.append((0,0,{'name':barcode.name,'product_tmpl_id':item.product_tmpl_id.id,'product_approval_id':item.id}))
                            item.write({'barcode_ids':barcode_list})
                            vals['barcode_ids'] = [(6, 0, item.barcode_ids.ids)]
                            product_tmpl_obj = self.env['product.template'].browse(product_id.id)
                            product_tmpl_obj.sudo().update({'barcode_ids':[(6, 0, item.barcode_ids.ids)]})
                except Exception as e:
                    raise osv.except_osv(_('Product Creation Failed!'), _('Here is why:  %s!!!'% (e)))
            else:
                try:
                    # remove existing
                    for org_barcode in item.barcode_ids:
                        old_barcode_list.append((2,org_barcode.id))
                    item.write({'barcode_ids':old_barcode_list})
                    # add new
                    for barcode in item.barcode_approval_ids:
                        new_barcode_list.append((0,0,{'name':barcode.name,'product_tmpl_id':item.product_tmpl_id.id,'product_approval_id':item.id}))
                    item.write({'barcode_ids':new_barcode_list})
                    vals['barcode_ids'] = [(6, 0, item.barcode_ids.ids)]
                    product_id = item.product_tmpl_id.sudo().update(vals)
                    self.state = 'done'
                    self.is_prod_changed = True
                except Exception as e:
                    raise osv.except_osv(_('Product Updating Failed!'), _('Here is why:  %s!!!'% (e)))

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

class product_multi_barcode_approval(models.Model):
    _name = 'product.multi.barcode.approval'
    _description = 'Product Multi Barcode Approval'

    name = fields.Char(string='Barcode',required=True)
    product_approval_id = fields.Many2one('product.approval', string='Product Approval Id', ondelete='cascade')

class product_uom_price(models.Model):
    _inherit = 'product.uom.price'

    product_approval_id = fields.Many2one('product.approval', string="Product Approval")
