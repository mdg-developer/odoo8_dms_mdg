from openerp import tools
from openerp.osv import fields, osv

class product_pricelist_new(osv.osv):
 
    _name = "product.pricelist.new"
    _auto = False
     
    _columns = {
                'pricelist_version': fields.char('Pricelist Version', readonly=True),
                'pricelist': fields.char('Pricelist', readonly=True),
                'product_id': fields.many2one('product.product','Product'),
                'product_tmpl_id': fields.many2one('product.template', 'Product Template'),                
                'product_uom_id':fields.many2one('product.uom', string='Product UoM'),
                'price_surcharge': fields.float('Price Surcharge'),
            }
     
    _order = "product_id"

    def init(self, cr):
        tools.sql.drop_view_if_exists(cr, 'product_pricelist_new')
        cr.execute("""
            CREATE or REPLACE VIEW product_pricelist_new as
              (select distinct i.product_id,  i.id as id,
                p.name pricelist,
                v.name pricelist_version,
                i.price_surcharge,
                pp.name_template product,
                pt.name product_template,
                u.name uom,
                i.product_tmpl_id,
                i.product_uom_id
                from product_pricelist p, product_pricelist_version v, 
                product_pricelist_item i,product_product pp,
                product_template pt,product_uom u
                where p.id=v.pricelist_id and v.id=i.price_version_id 
                and i.product_id=pp.id and i.product_tmpl_id=pt.id 
                and i.product_uom_id=u.id
                and v.active='t' and p.active='t'
              )      
    
        """)

product_pricelist_new()