'''
Created on Jan 21, 2016

@author: NSM.7thcomputing
'''
from openerp.osv import fields, osv

class branch(osv.osv):
    _name = 'res.branch'
    _columns = {
                    'name': fields.char('Branch Name', required=True),
                    'branch_code': fields.char('Branch Code', required=True),  
                                        'name': fields.char('Branch Name', required=True),
                    'address': fields.text('Address'),  
                    'active': fields.boolean('Active')  ,
                    'res_company_id' : fields.many2one('res.company', 'Company'),
                    'branch_location_id' : fields.many2one('stock.location', 'Branch Location'),
                     #'p_line':fields.one2many('res.branch.line', 'line_id', 'Product Lines',copy=True),
                    'p_line': fields.one2many('res.branch.line', 'line_id', 'Order Lines'),           
               
                }
    
    def retrieve_data(self, cr, uid, ids, context=None):
        branch_line_obj = self.pool.get('res.branch.line')
        cr.execute('delete from res_branch_line where line_id=%s', (ids[0],))
        cr.execute('''select pp.id,pp.sequence from product_template pt,product_product pp where pt.id=pp.product_tmpl_id
            and pt.type!='service' and pt.sale_ok=True''')
        product_data=cr.fetchall()
        if product_data:                
            for val in product_data:
                product_id=val[0]    
                product_sequence =val[1]   
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
    
    _defaults = {
        'active': True,
 
    }
    _sql_constraints = [('Branch_code_uniq', 'unique(branch_code)',
    
                                     'Branch Code should not be same to others!')]
branch()
