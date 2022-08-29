from openerp.osv import fields, osv

class crm_case_section(osv.osv):
    _inherit = 'crm.case.section'

    _columns = {
        'competitor_product_ids': fields.many2many('competitor.product'),
    }