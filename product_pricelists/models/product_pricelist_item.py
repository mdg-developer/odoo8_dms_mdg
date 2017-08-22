from openerp.osv import fields, osv


class product_pricelist_item(osv.osv):
    _inherit = "product.pricelist.item"
    _columns = {
                    'product_uom_id':fields.many2one('product.uom', string='Product UoM')
                        }
    
product_pricelist_item()
