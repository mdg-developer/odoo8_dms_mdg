from openerp.osv import fields
from openerp.osv import osv
class account_invoice_line(osv.osv):
 
    def _get_main_group(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        if context is None:
            context = {}       
        for line in self.browse(cr, uid, ids, context=context):
            gin_data = self.browse(cr, uid, line.id, context=context)
            if gin_data:
                main_group=gin_data.product_id.product_tmpl_id.main_group.id
                res[gin_data.id] = main_group            
        return res     
    
    _inherit = 'account.invoice.line'    
    _columns = {
        'promotion_id': fields.many2one('promos.rules', 'Promotion', readonly=False),
        'edit_promotion':fields.boolean('Edit Promotion Data Line',default=False),
        'main_group': fields.function(_get_main_group,
                                      string='Principle',
                                      type='many2one',relation="product.maingroup",
                                      readonly=True, store=False
                                      ),
    }
    