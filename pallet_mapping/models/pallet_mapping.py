from openerp.osv import fields, osv
from openerp.tools.translate import _

class pallet_mapping(osv.osv):

    _name = "pallet.mapping"    
    
    def product_id_change(self, cr, uid, ids, product_id, context=None):
        if not product_id:
            return {}
        
        prod = self.pool.get('product.product').read(cr, uid, [product_id], ['code', 'name', 'product_tmpl_id'])
        product_tmpl_id = prod[0]['product_tmpl_id'][0]
        temp = self.pool.get('product.template').read(cr, uid, [product_tmpl_id], ['list_price'])
        product = self.pool.get('product.product').browse(cr, uid, product_id, context=context)                                                  
        uom_id = product.product_tmpl_id.uom_id and product.product_tmpl_id.uom_id.id or False,
        big_uom_id = product.product_tmpl_id.big_uom_id and product.product_tmpl_id.big_uom_id.id or False,
        categ_id = product.product_tmpl_id.categ_id.id,
        product_tmpl_id = product.product_tmpl_id and product.product_tmpl_id.id or False,
        cr.execute("""SELECT uom.id FROM product_product pp 
                      LEFT JOIN product_template pt ON (pp.product_tmpl_id=pt.id)
                      LEFT JOIN product_template_product_uom_rel rel ON (rel.product_template_id=pt.id)
                      LEFT JOIN product_uom uom ON (rel.product_uom_id=uom.id)
                      WHERE pp.id = %s""", (product.id,))
        uom_list = cr.fetchall()
        domain = {'small_uom_id': [('id', 'in', uom_list)], 'big_uom_id': [('id', 'in', uom_list)]}

        if prod[0]['code']:
            return {'value': { 'small_uom_id':uom_id, 'big_uom_id':big_uom_id}
                    , 'domain': domain}
        return {}    
    
    def _get_smaller_qty(self, cr, uid, ids, fields, arg, context):
                     
        data = self.browse(cr, uid, ids)[0]         
        unit_per_cartoon = data.unit_per_cartoon
        ctn = data.standard_layer_per_pallet_ctn    
        layer = data.standard_layer_per_pallet_layer
        total = 0                        
        res = {}      
        total = unit_per_cartoon * ctn * layer
        
                      
        for data in self.browse(cr, uid, ids, context):
            res[data.id] = total
        return res   
    
    _columns = {
        'product_id': fields.many2one('product.product', 'Product', required=True),
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
    
    def _get_branch(self, cr, uid, context=None, uid2=False):
        if not uid2:
            uid2 = uid
        user = self.pool.get('res.users').read(cr, uid, uid2, ['branch_id'], context)
        branch_id = user.get('branch_id', False)
        return branch_id and branch_id[0] or False    
    
    _columns = {
        'branch_ids':fields.many2many('res.branch', 'res_branch_users_rel', 'user_id', 'bid', 'Branches', required=True),
    }
res_users()

    
