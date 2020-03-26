from openerp.osv import fields, osv

class crm_case_section(osv.osv):
    _inherit = 'crm.case.section'    
  
    _columns = {                
                'sale_group_id': fields.many2one('sales.group', 'Sales Group'),
        }
      
crm_case_section()
