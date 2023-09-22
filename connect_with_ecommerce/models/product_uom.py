from openerp.osv import fields, osv

class product_uom(osv.osv):
    _inherit = 'product.uom'

    def _factor_value(self, cursor, user, ids, name, arg, context=None):
        res = {}
        for uom in self.browse(cursor, user, ids, context=context):
            res[uom.id] = round(1/uom.factor,0)
        return res

    _columns = {
        'uom_myanmar':fields.char('Unit of Measure (Myanmar)'),
        'uom_description': fields.char('Unit of Measure Description'),
        'factor_value': fields.function(_factor_value, digits=0, string='Factor Value'),
        }

product_uom()
