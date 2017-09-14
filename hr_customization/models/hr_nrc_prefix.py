from openerp.osv import fields, osv
from openerp.tools.translate import _

class hr_nrc_prefix(osv.osv):

    _name = "hr.nrc.prefix"
  
    _columns = {
        'name': fields.char('Name', required=True), 
    }
    _sql_constraints = [('name_uniq', 'unique(name)',
                                     'NRC prefix should not be same to others!')]
hr_nrc_prefix()


class hr_employee(osv.osv):

    _inherit = "hr.employee"
    
    def _get_identification_id(self, cr, uid, ids, fields, arg, context):
                     
        data = self.browse(cr, uid, ids)[0]         
        nrc_prefix_id = data.nrc_prefix_id.name
        nrc_number = data.nrc_number    
                                
        res = {}      
        identification = ''
        if nrc_prefix_id:
            identification = nrc_prefix_id + nrc_number
        
        cr.execute("""select count(*) from hr_employee_termination
            where reason_id in(select id from hr_employee_termination_reason where lower(name) ='black list')
            and employee_id in(select id from hr_employee where identification_id=%s)
            """,(identification,))
        data1 = cr.fetchall()
        if data1:
            data_count = data1[0][0]
            if data_count > 0:                
                raise osv.except_osv(_('Alert!:'), _("Black List Employee"))              
        for data in self.browse(cr, uid, ids, context):
            res[data.id] = identification
        return res   
    
    
    def _trial_end_date_availabe(self, cr, uid, ids, fields, arg, context):

        res={}
        contract_obj = self.pool.get('hr.contract')
        for record in self.browse(cr, uid, ids):
    
            trial_date_end = None
            
            contract_ids = contract_obj.search(cr,uid,[('employee_id', '=',record.id )], context=context)
            if contract_ids:
                for contract_id in contract_ids:
                    contract = contract_obj.browse(cr,uid,contract_id,context=context)
                    if contract:
                        trial_date_end = contract.trial_date_end
                res[record.id] = trial_date_end          

    
        return res 
  
    _columns = {
        'trial_end_date' : fields.function(_trial_end_date_availabe, method=True, string="Trial End Date", type='date', store=True),        
        
        'nrc_prefix_id': fields.many2one('hr.nrc.prefix', 'NRC Prefix'),
        'nrc_number': fields.char('NRC Number'),
        #'bus_stop': fields.char('Bus Stop'),
        'bus_stop_id': fields.many2one('hr.bus.stop', 'Bus Stop'),
        'labour_card': fields.char('Labour Card'),
        'identification_id' : fields.function(_get_identification_id, string="NRC ID", store=True, type="char"),
        #'trial_end_date' : fields.float('Trial End Date', compute='_trail_end_date')
    }
#     def create(self, cr, uid, vals, context=None):
#         
#         print 'start create', vals 
#         identification_id = None
#         
#         if vals['nrc_prefix_id']:
#            identification_id = str(vals['nrc_prefix_id'])
#         if vals['nrc_number']:    
#            identification_id += str(vals['nrc_number'])
#         if identification_id is not None:
#             cr.execute("""select count(*) from hr_employee_termination
#             where reason_id in(select id from hr_employee_termination_reason where lower(name) ='black list')
#             and employee_id in(select id from hr_employee where identification_id=%s)
#             """,(identification_id,))
#             data = cr.fetchall()
#             if data:
#                 data_count = data[0][0]
#                 if data_count > 0:                
#                     raise osv.except_osv(_('Alert!:'), _("Black List Person"))       
#         new_id = super(hr_employee, self).create(cr, uid, vals, context=context)
#         print 'new_id>>>', new_id
#         return new_id     
hr_employee()     