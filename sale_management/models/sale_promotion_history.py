from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp

class sale_promotion(osv.osv):
    
    _name = "sales.promotion.history"
    _description = "Sale Promotion"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _columns = {                
        'date':fields.date('Date'),
        'section_id':fields.many2one('crm.case.section', 'Sales Team '),
        'user_id':fields.many2one('res.users', 'Salesman'),
        'promotion_id':fields.many2one('promos.rules', string='Promotion'),     
        'partner_id': fields.many2one('res.partner', 'Customer'),
        'note':fields.text("Note"),

  }

sale_promotion()