'''
Created on Auguest 31, 2016

@author: Administrator
'''
import time

from openerp.osv import fields , osv
from openerp.tools.translate import _


class stock_return_from_mobile(osv.osv):
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _name = "stock.return.mobile"
    _description = "Stock Return From Mobile"
    _order = "id desc"    
    
    _columns = {
        'sale_team_id':fields.many2one('crm.case.section', 'Sales Team' , required=True),
        'user_id':fields.many2one('res.users', 'Return From'  , required=True, select=True, track_visibility='onchange'),
         'return_date':fields.date('Date of Return'),
        'vehicle_id':fields.many2one('fleet.vehicle', 'Vehicle No'),
        'p_line':fields.one2many('stock.return.mobile.line', 'line_id', 'Product Lines',
                              copy=True),
               'branch_id':fields.many2one('res.branch', 'Branch'),
        'company_id':fields.many2one('res.company', 'Company'),

}
    _defaults = {
        'state' : 'draft',
    }     
            
class stock_return_from_mobile_line(osv.osv):
    _name = 'stock.return.mobile.line'
    _description = 'Return Line From Mobile'
    _columns = {                
        'line_id':fields.many2one('stock.return.mobile', 'Line', ondelete='cascade', select=True),
        'product_id': fields.many2one('product.product', 'Product', required=True),
        'return_quantity' : fields.float(string='Returned Qty', digits=(16, 0)),
        'sale_quantity' : fields.float(string='Sales Qty', digits=(16, 0)),
        'foc_quantity' : fields.float(string='FOC Qty', digits=(16, 0)),
        'product_uom': fields.many2one('product.uom', 'UOM', required=True),
    }
        
   
    
