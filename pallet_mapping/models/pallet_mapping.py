from openerp.osv import fields, osv
from openerp.tools.translate import _

class pallet_mapping(osv.osv):

    _name = "pallet.mapping"    
    
    def _get_smaller_qty(self, cr, uid, ids, fields, arg, context):
                     
        data = self.browse(cr, uid, ids)[0]         
        unit_per_cartoon = data.unit_per_cartoon
        ctn = data.standard_layer_per_pallet_ctn    
        layer = data.standard_layer_per_pallet_layer
        total =0                        
        res = {}      
        total = unit_per_cartoon * ctn * layer
        
                      
        for data in self.browse(cr, uid, ids, context):
            res[data.id] = total
        return res   
    
    _columns = {
               
        
       
        'product_id': fields.many2one('product.product', 'Product',required=True),
        'small_uom_id': fields.many2one('product.uom', 'Smaller UOM'),
        'unit_per_cartoon': fields.integer('Standard Unit Per Carton'),
		'big_uom_id': fields.many2one('product.uom', 'Bigger UOM'),
		'weight_per_cartoon': fields.float('Standard Weight Per Ctns(kg)'),
		'weight_per_pallet_kg': fields.float('Standard Weight Per Pallet(kg)'),
		'standard_layer_per_pallet_ctn': fields.float('Standard Layer Per Pallet Ctns'),
		'standard_layer_per_pallet_layer': fields.float('Standard Layer Per Pallet Layer'),
		'number_of_ctns_pallet': fields.float('Numer of Ctns Per Pallet'),
        'smaller_qty' : fields.function(_get_smaller_qty, string="Smaller Total qty", store=True, type="float"),
    }
    
   
pallet_mapping()   



class res_users(osv.osv):
    _inherit = "res.users"
    _description = "Users"
    
    def _get_branch(self,cr, uid, context=None, uid2=False):
        if not uid2:
            uid2 = uid
        user = self.pool.get('res.users').read(cr, uid, uid2, ['branch_id'], context)
        branch_id = user.get('branch_id', False)
        return branch_id and branch_id[0] or False    
    
    _columns = {
        'branch_ids':fields.many2many('res.branch','res_branch_users_rel','user_id','bid','Branches',required=True),
    }
res_users()

    