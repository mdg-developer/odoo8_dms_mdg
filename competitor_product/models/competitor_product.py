from openerp.osv import fields, osv

class competitor_product(osv.osv):
    _name = 'competitor.product'

    _columns = {
        'name':fields.char(string='Name'),
        'image': fields.binary("Image"),
        'uom_ids': fields.many2many('product.uom', string='UoM'),
        'description': fields.text(string='Description'),
        'sequence': fields.integer(string='Sequence'),
    }