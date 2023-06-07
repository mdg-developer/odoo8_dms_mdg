from openerp.osv import fields, osv

class ProductMultiBarcode(osv.osv):
    _name = 'product.multi.barcode'
    
    _columns = {
                'name' : fields.char('Barcode', required=True),
                'product_tmpl_id' : fields.many2one('product.template', string="Product", required=True, ondelete='cascade'),
                'product_info_id': fields.many2one('product.info', string="Product Info", ondelete='cascade'),
                'product_approval_id': fields.many2one('product.approval', string="Product Approval", ondelete='cascade'),
    }

    def create(self, cursor, user, vals, context=None):
        if not "product_tmpl_id" in vals and "product_info_id" in vals:
            product_info_id = vals['product_info_id']
            product_tmpl_id = self.pool('product.info').browse(cursor,user,product_info_id).product_tmpl_id.id
            vals['product_tmpl_id']=product_tmpl_id

        return super(ProductMultiBarcode, self).create(cursor, user, vals, context=context)


    