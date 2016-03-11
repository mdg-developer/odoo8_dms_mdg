from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp

class crm_case_section(osv.osv):
    _inherit = 'crm.case.section'
    _columns = {
                'region': fields.char('Region'),
                'channel_ids':fields.many2many('sale.channel'),
                'code': fields.char('Code',required = True),
                'product_ids':fields.many2many('product.template'),
                'warehouse_id': fields.many2one('stock.warehouse', 'Warehouse',required = True),
                'location_id': fields.many2one('stock.location', 'Location',required = True),
                'analytic_account_id': fields.many2one('account.analytic.account', 'Analytic Account'),

                'demarcation_ids':fields.many2many('sale.demarcation'),
                'van_id':fields.char('Vehicle No'),
                'main_group_id': fields.many2many('product.maingroup'),
               }
    _sql_constraints = [
        ('code_uniq', 'unique (code)', 'The code of the sales team must be unique !')
    ]    
crm_case_section()