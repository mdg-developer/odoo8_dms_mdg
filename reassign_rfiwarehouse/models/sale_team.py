from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
from datetime import datetime, timedelta
import calendar
from openerp import tools
class crm_case_section(osv.osv):
    _inherit = 'crm.case.section'
    _columns = {
                'assign_warehouse_lines': fields.one2many('section.warehouse','section_id','Warehouses'),
                }
        
    
class crm_case_section_assign(osv.osv):
    _name = 'section.warehouse'
    
    _columns = {
                'section_id': fields.many2one('crm.case.section','Sale Team'),
                'location_id':fields.many2one('stock.location','Reassign Warehouse'),
                'assign': fields.boolean('Assign', default=False),    
                'name':fields.char(related='location_id.name', store=True, readonly=True, copy=False),

                }
    
crm_case_section_assign()