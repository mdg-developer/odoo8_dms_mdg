import itertools
from lxml import etree
from openerp.osv import fields, osv
from openerp import models, fields, api, _
from openerp.tools import float_compare
import openerp.addons.decimal_precision as dp

class PromotionRules(models.Model):

    _inherit = 'promos.rules'

    def create(self,cr,uid,ids,context=None):
        result = super(PromotionRules,self).create(cr,uid,ids,context=None)
        return result

# Conditions Class#
class PromotionsRulesConditionsExps(models.Model):

    _inherit = "promos.rules.conditions.exps"

    product_id = fields.Many2one('product.product', copy=True, string="Product")
    product_id_sub_total = fields.Many2one('product.product', copy=True, string="Product")
    product_ids = fields.Many2many('product.product', 'product_product_rel', 'condition_id', 'product_id',"Products", copy=True)
    uom_id = fields.Many2one('product.uom', string="Product UOM", copy=True)
    category_id = fields.Many2one('product.category', string="Product Category", copy=True)
    category_ids = fields.Many2many('product.category', 'product_category_rel', 'condition_id', 'category_id',"Product Categories", copy=True)
    sale_total = fields.Integer('Sales Total', copy=True)
    sale_total_for_fix_categ = fields.Integer('Sales Total', copy=True)
    sale_total_for_multi_prod = fields.Integer('Sales Total', copy=True)
    sale_total_for_sub_total = fields.Integer('Sales Total', copy=True)
    qty = fields.Integer('Qty', copy=True)
    minimum_qty = fields.Integer('Minimum Quantity', copy=True)
    quantity_total = fields.Integer('Total Quantity', copy=True)
    condition_line_ids = fields.One2many('promos.rules.conditions.exps.lines','condition_id','Products', copy=True)

    def on_change(self, cursor, user, ids=None,attribute=None, value=None, context=None):
        # result = super(PromotionsRulesConditionsExps,self).on_change(cursor,user,ids,attribute,value,context)
        result = ''
        return result

    # Helper Functions
    @api.multi
    @api.onchange('product_id')
    def onchange_product_id(self):
        domain = {}
        if self.product_id:
            base_uom = self.product_id.uom_id.id
            report_uom = self.product_id.report_uom_id.id
            domain['uom_id'] = [('id', 'in', (base_uom, report_uom))]
        else:
            domain['uom_id'] = []
        return {'domain': domain}

    # I play logic from onchange for different types of conditions
    ## Start onChange Blocks
    @api.onchange('condition_line_ids','quantity_total')
    def onChange_cond_lines_for_multi_uom(self):
        # This is for Multi UOM Promo Type
        code_place = ''
        uom_ratio_place = ''
        qty_place = ''
        format = ''
        total_qty = 0
        # format = 'p1';'p2';'p3' | p1_uom;p2_uom;p3_uom:0.00
        # format = code_place + '|' + uom_ratio_place + ':' + qty_place
        print('---------------quantity_total')
        print(self.quantity_total)
        if self.attribute:
            for line in self.condition_line_ids:
                code = line.default_code
                uom_ratio = line.uom_ratio
                if code:
                    if code_place:
                        code_place += ";'%s'" % code
                    else:
                        code_place += "'%s'" % code
                # Append the uom_ratio to uom_ratio_place
                if uom_ratio:
                    if uom_ratio_place:
                        uom_ratio_place += ";%d" % uom_ratio
                    else:
                        uom_ratio_place += "%d" % uom_ratio
                if self.quantity_total:
                    qty_place = self.quantity_total
                if code_place and uom_ratio_place and qty_place:
                    # Construct the final format string
                    format = "%s|%s:%s" % (code_place, uom_ratio_place, qty_place)
            self.value = format
    # @api.onchange('condition_line_ids')
    def onChange_cond_lines_for_multi_uom_old(self):
        code_place = ''
        uom_ratio_place = ''
        qty_place = ''
        format = ''
        total_qty = 0
        qty_values = []
        # format = 'p1';'p2';'p3' | p1_uom;p2_uom;p3_uom:0.00
        # format = code_place + '|' + uom_ratio_place + ':' + qty_place
        if self.attribute:
            for line in self.condition_line_ids:
                total_qty += line.qty
                code = line.default_code
                uom_ratio = line.uom_ratio
                qty = line.unit
                # Append the code to code_place
                if code:
                    if code_place:
                        code_place += ";'%s'" % code
                    else:
                        code_place += "'%s'" % code
                # Append the uom_ratio to uom_ratio_place
                if uom_ratio:
                    if uom_ratio_place:
                        uom_ratio_place += ";%d" % uom_ratio
                    else:
                        uom_ratio_place += "%d" % uom_ratio
                # Logic Change use
                if total_qty:
                    qty_values.append(str(total_qty))
                    qty_place = total_qty
            # Construct the final format string
            format = "%s|%s:%s" % (code_place, uom_ratio_place, qty_place)
            self.value = format
            self.total_qty = total_qty
    @api.onchange('product_id','uom_id','qty')
    def onChange_for_prod_qty(self):
        format = ''
        code_place = ''
        qty_place = ''
        if self.product_id and self.uom_id and self.qty:
            product_code = self.product_id.default_code
            uom_ratio = self.uom_id.factor_inv
            qty = self.qty
            cal_qty = int(uom_ratio * qty)
            if product_code:
                code_place += "'%s'" % product_code
            if uom_ratio:
                qty_place += str(cal_qty)
            format = "%s:%s" % (code_place,qty_place)
            self.value = format
    @api.onchange('category_id','sale_total')
    def onChange_for_cat_total(self):
        format = ''
        if self.category_id and self.sale_total:
            category_name = self.category_id.name
            sale_total = self.sale_total
            format = "'%s':%s" % (category_name, sale_total)
            self.value = format
    @api.onchange('category_ids','minimum_qty','sale_total_for_fix_categ')
    def onChange_for_fix_categ_qty(self):
        format = ''
        code_place = ''
        for line in self.category_ids:
            name = line.name
            if name:
                if code_place:
                    code_place += ";'%s'" % name
                else:
                    code_place += "'%s'" % name
            if code_place and self.minimum_qty and self.sale_total_for_fix_categ:
                format = "%s:%s|%s" % (code_place,self.minimum_qty,self.sale_total_for_fix_categ)
            self.value = format
    @api.onchange('product_ids','sale_total_for_multi_prod')
    def onChange_for_multi_prod_sale_amt(self):
        format = ''
        code_place = ''
        for line in self.product_ids:
            code = line.default_code
            if code:
                if code_place:
                    code_place += ";'%s'" % code
                else:
                    code_place += "'%s'" % code
            if code_place and self.sale_total_for_multi_prod:
                format = "%s:%s" % (code_place, self.sale_total_for_multi_prod)
            self.value = format
    @api.onchange('product_id_sub_total','sale_total_for_sub_total')
    def onChange_for_prod_sub_total(self):
        format = ''
        code = self.product_id_sub_total.default_code
        if code and self.sale_total_for_sub_total:
            format = "'%s':%s" % (code, self.sale_total_for_sub_total)
        self.value = format
    ## End onChange Blocks

# Condition Lines Class#
class PromotionsRulesConditionsExpsLines(models.Model):

    _name = 'promos.rules.conditions.exps.lines'

    category_id = fields.Many2one('product.category', 'Product Categories')
    product_id = fields.Many2one('product.product', 'Products')
    condition_id = fields.Many2one('promos.rules.conditions.exps', 'Promos Conditions')
    uom_id = fields.Many2one('product.uom', 'UOM')
    default_code = fields.Char(string="Product Codes", related='product_id.default_code')
    uom_ratio = fields.Float(string="Unit Ratio", related='uom_id.factor_inv')
    unit = fields.Integer(string="Unit") #user input field

    @api.onchange('product_id')
    def onChangeProduct_id(self):
        domain = {}
        if self.product_id:
            base_uom = self.product_id.uom_id.id
            report_uom = self.product_id.report_uom_id.id
            domain['uom_id'] = [('id', 'in', (base_uom, report_uom))]
        else:
            domain['uom_id'] = []
        return {'domain': domain}

    # @api.depends('uom_ratio','unit')
    # def _compute_qty(self):
    #     for record in self:
    #         record.qty = int(record.uom_ratio * record.unit)

    # @api.depends('qty')
    # def _compute_total_qty(self):
    #     for record in self:
    #         total_qty = sum(line.qty for line in self.search([]))
    #         record.total_qty = total_qty

# Action Class
class PromotionsRuleActions(models.Model):
    _inherit = 'promos.rules.actions'

    product_id = fields.Many2one('product.product',string="Product", copy=True)
    product_ids = fields.Many2many('product.product', 'product_action_rel', 'action_id', 'product_id',string="Products", copy=True)
    uom_id = fields.Many2one('product.uom',string="UOM", copy=True)
    qty = fields.Integer('Quantity', copy=True)
    discount_percentage = fields.Float('Discount Percentage(%)', copy=True)
    discount_product = fields.Many2one('product.product',string="Discount Product", copy=True)
    discount_amount = fields.Integer('Discount Amount', copy=True)
    foc_qty = fields.Integer('Foc Qty', copy=True)

    # Helper Functions
    @api.multi
    @api.onchange('product_id')
    def onchange_product_id(self):
        domain = {}
        if self.product_id:
            base_uom = self.product_id.uom_id.id
            report_uom = self.product_id.report_uom_id.id
            domain['uom_id'] = [('id', 'in', (base_uom, report_uom))]
        else:
            domain['uom_id'] = []
        return {'domain': domain}

    # I play logic from a set of onchange
    ## But their views and usecase are mix,So these on change will be mixing.
    ## Later I hope I will divide logic.
    @api.onchange('product_id','discount_percentage','discount_product')
    def onChange_first_logic(self):
        code_place = percent_prod_place = disc_prod_place = ''
        product_code = self.product_id.default_code
        disc_percentage = self.discount_percentage
        discount_code = self.discount_product.default_code
        if product_code:
            code_place = "'%s'" % product_code
            # populate
            self.product_code = code_place
        if disc_percentage:
            percent_prod_place = disc_percentage
            # populate
            self.arguments = percent_prod_place
        if discount_code:
            disc_prod_place = "'%s'" % discount_code
            # populate
            self.discount_product_code = disc_prod_place
    @api.onchange('qty','discount_amount')
    def onChange_second_logic(self):
        format = qty_place = amount_place = ''
        # Populate Arguments
        if self.qty and self.discount_amount:
            qty_place = self.qty
            amount_place = self.discount_amount
            format = "%s|%s" % (amount_place,qty_place)
            self.arguments = format
    @api.onchange('product_ids','qty','discount_amount')
    def onChange_third_logic(self):
        format = format2 = code_place = qty_place = amount_place = ''
        # Populate Product Code
        for line in self.product_ids:
            product_code = line.default_code
            if product_code:
                if code_place:
                    code_place += ":'%s'" % product_code
                else:
                    code_place += "'%s'" % product_code
            if code_place:
                format = "%s" % (code_place)
            self.product_code = format
        # Populate Arguments
        if self.discount_amount and self.qty:
            qty_place = self.qty
            amount_place = self.discount_amount
            format2 =  "%s|%s" % (amount_place,qty_place)
            self.arguments = format2
    @api.onchange('qty','foc_qty')
    def onChange_forth_logic(self):
        format = qty_place = foc_qty_place = ''
        if self.qty and self.foc_qty:
            qty_place = self.qty
            foc_qty_place = self.foc_qty
            format = "%s|%s" % (foc_qty_place, qty_place)
            self.arguments = format