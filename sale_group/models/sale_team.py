from openerp.osv import fields, osv


class crm_case_section(osv.osv):
    _inherit = 'crm.case.section'

    _columns = {
        'sale_group_id': fields.many2one('sales.group', 'Sales Group'),
        'sales_person_id': fields.many2one('sales.person.name', 'Sales Person Name'),
        'join_date': fields.date('Join Date'),
        'sales_supervisor_id': fields.many2one('sales.supervisor', 'Sales Supervisor'),
        'sales_manager_id': fields.many2one('sales.manager', 'Sales Manager'),
        'branch_manager_id': fields.many2one('branch.manager', 'Branch Manager'),
        'sales_rom_id': fields.many2one('sales.rom', 'ROM'),
        'sales_csm_id': fields.many2one('sales.csm', 'CSM'),
        'sales_nsm_id': fields.many2one('sales.nsm', 'NSM'),
    }


crm_case_section()
