from openerp.osv import fields,osv

class res_branch(osv.osv):
    _inherit = 'res.branch'
    
    _columns = {
        'branch_warehouse_id' : fields.many2one('stock.warehouse', 'Default Warehouse'),
    }
    