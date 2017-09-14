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
#         if nrc_number:
#             cr.execute("""select ht.name,hr.name,he.name_related,he.identification_id,he.nrc_number 
#                 from hr_employee_termination ht,hr_employee_termination_reason hr,hr_employee he
#                 where ht.employee_id = he.id and ht.reason_id=hr.id and ht.state = 'done'
#                 and he.nrc_number =%s 
#                 and (lower(hr.name) ='black list' or lower(hr.name) ='resigned without noticed'
#                 or lower(hr.name) ='resigned without full service')
#             """,(nrc_number,))
#             data1 = cr.fetchall()
#             if data1:
#                 data_count = data1[0][0]
#                 if data_count > 0:             
#                raise osv.except_osv(_('Alert!:'), _("'%s' with %s already exist \n Reason: %s Date: %s")% (data1[0][2],data1[0][3],data1[0][1],data1[0][0]))
#             cr.execute('select name_related,identification_id,nrc_number from hr_employee WHERE nrc_number =%s',(nrc_number,))
#             nrc_data = cr.fetchone()
#             if nrc_data:
#                 raise osv.except_osv(_('Alert!'), _("'%s' with %s already exist!")% (nrc_data[0],nrc_data[1]))                
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
    def _contract_wage_availabe(self, cr, uid, ids, fields, arg, context):

        res={}
        contract_obj = self.pool.get('hr.contract')
        for data in self.browse(cr, uid, ids):
    
            contract_wage = None
            
            contract_ids = contract_obj.search(cr,uid,[('employee_id', '=',data.id )], context=context)
            if contract_ids:
                for contract_id in contract_ids:
                    contract = contract_obj.browse(cr,uid,contract_id,context=context)
                    if contract:
                        contract_wage = contract.wage
                res[data.id] = contract_wage          
        return res  
  
    _columns = {
        #'trial_end_date' : fields.function(_trial_end_date_availabe, method=True, string="Trial End Date", type='date', store=True),        
        #'wage' : fields.function(_contract_wage_availabe, method=True, string="Wage", store=True),
        'nrc_prefix_id': fields.many2one('hr.nrc.prefix', 'NRC Prefix'),
        'nrc_number': fields.char('NRC Number'),
        #'labour_card': fields.char('Labour Card'),
        #'ssb': fields.char('SSB'),
        'identification_id' : fields.function(_get_identification_id, string="NRC ID", store=True, type="char"),
    }
  
hr_employee()     