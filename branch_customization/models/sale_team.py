from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp

class crm_case_section(osv.osv):
    _inherit = 'crm.case.section'
    _columns = {
                'branch_id': fields.many2one('res.branch', 'Branch'),    
                }