'''
Created on Jan 21, 2016

@author: NSM.7thcomputing
'''
from openerp.osv import fields, osv


class branch(osv.osv):
    _inherit = 'res.branch'
    _columns = {
                   
                    'branch_location_id' : fields.many2one('stock.location', 'Default Location'),
                    'p_line': fields.one2many('res.branch.line', 'line_id', 'Order Lines'),
                    'request_line': fields.one2many('branch.request.line', 'request_id', 'Order Lines'),
                    'requesting_line': fields.one2many('branch.requesting.line', 'requesting_id', 'Order Lines'),
                    'subdeal': fields.boolean('Subdeal', default=False),
                }
    
    def retrieve_data(self, cr, uid, ids, context=None):
        branch_line_obj = self.pool.get('res.branch.line')
        cr.execute('delete from res_branch_line where line_id=%s', (ids[0],))
        cr.execute('''select pp.id,pp.sequence from product_template pt,product_product pp where pt.id=pp.product_tmpl_id
            and pt.type!='service' and pt.sale_ok=True and pp.active=True''')
        product_data = cr.fetchall()
        if product_data:                
            for val in product_data:
                product_id = val[0]    
                product_sequence = val[1]   
                branch_line_obj.create(cr, uid, {'line_id': ids[0],
                               'sequence':product_sequence,
                              'product_id': product_id,
                              'assign':False,
                        }, context=context)        

          
class res_branch_line(osv.osv):
    _name = "res.branch.line"
    _columns = {
                'line_id': fields.many2one('res.branch', 'Line', required=True, ondelete='cascade'),
                'sequence':fields.integer('Sequence'),
                'product_id' : fields.many2one('product.product', 'Product'),
                'assign' : fields.boolean('Assigned'),
                }


class request_location_line(osv.osv):
    _name = "branch.request.line"
    _columns = {
                'request_id': fields.many2one('res.branch', 'Line', required=True, ondelete='cascade'),
                    'location_id' : fields.many2one('stock.location', 'Request Location'),
                }

    
class requesting_location_line(osv.osv):
    _name = "branch.requesting.line"
    _columns = {
                'requesting_id': fields.many2one('res.branch', 'Line', required=True, ondelete='cascade'),
                'transit_location_id' : fields.many2one('stock.location', 'Transit Location'),
                 'location_id' : fields.many2one('stock.location', 'Requesting Warehouse'),

                }

