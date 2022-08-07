from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp

class mobile_sale_display(osv.osv):
    
    _name = "sales.display"
    _description = "Mobile Sales Display"
   
    _columns = {
        'displayname': fields.char('Display Name'),
        'customer':fields.many2one('res.partner', 'Customer'),
        'category_id':fields.many2one('product.category', 'Category'),
        'sale_team_id':fields.many2one('crm.case.section', 'Sale Team'),
        'quantity':fields.integer('Quantity'),
        'date':fields.date('Date'),
        'description':fields.text('Description'),
        'sub_group':fields.many2one('product.group', 'Sub Group'),
        'display_line':fields.one2many('sales.display.line', 'display_ids', string='Sale Display Line', copy=True),
        'user_id': fields.many2one('res.users', 'Salesman Name', help='The internal user that is in charge of communicating with this contact if any.'),        
  }
mobile_sale_display()

class sale_display_line(osv.osv):
    
    _name = 'sales.display.line'
    _columns = {
                'display_ids': fields.many2one('sales.display', 'Sales Display'),
                'product_id':fields.many2one('product.product','Product',required=True),
                'product_uom':fields.many2one('product.uom','UOM',required=True),
                'product_uom_qty':fields.integer('Quantity', required=True),              
                }
sale_display_line()    