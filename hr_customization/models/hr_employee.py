from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import date,datetime
from dateutil import parser

class hr_employee(osv.osv):
    _inherit = "hr.employee"

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
    def _contract_end_availabe(self, cr, uid, ids, fields, arg, context):

        res={}
        contract_obj = self.pool.get('hr.contract')
        for record in self.browse(cr, uid, ids):
    
            contract_end_date = None
            
            contract_ids = contract_obj.search(cr,uid,[('employee_id', '=',record.id )], context=context)
            if contract_ids:
                for contract_id in contract_ids:
                    contract = contract_obj.browse(cr,uid,contract_id,context=context)
                    if contract:
                        contract_end_date = contract.date_end
                res[record.id] = contract_end_date          

    
        return res  
    
    def _effective_date_available(self, cr, uid, ids, fields, arg, context):
        res={}
        termination_obj =self.pool.get('hr.employee.termination')
        for record in self.browse(cr, uid, ids):
            effective_date = None
            termination_ids=termination_obj.search(cr,uid,[('employee_id','=',record.id)], context=context)
            if termination_ids:
                for termination_id in termination_ids:
                    termination= termination_obj.browse(cr, uid, termination_id, context=context)
                    if termination:
                        effective_date = termination.name
                        res[record.id] = effective_date
        return res
    
    def _contract_structure_availabe(self, cr, uid, ids, fields, arg, context):
        res={}
        contract_obj = self.pool.get('hr.contract')
        for data in self.browse(cr, uid, ids):
            contract_structure = None
            contract_ids = contract_obj.search(cr,uid,[('employee_id', '=',data.id )], context=context)
            if contract_ids:
                for contract_id in contract_ids:
                    contract = contract_obj.browse(cr,uid,contract_id,context=context)
                    if contract:
                        contract_structure = contract.struct_id.name
                res[data.id] = contract_structure          
        return res
    
    _columns = {
        'trial_end_date' : fields.function(_trial_end_date_availabe, method=True, string="Trial End Date", type='date', store=True),
        'date_end' : fields.function(_contract_end_availabe, method=True, string="Contract End Date", type='date', store=True),        
        'wage' : fields.function(_contract_wage_availabe, method=True, string="Wage", store=True),
        'struct_id' : fields.function(_contract_structure_availabe, method=True, string="Salary Structure",type='char', store=True),
        'effective_date' : fields.function(_effective_date_available, method=True, string="Effective Date", type='date', store=True),
        'nrc_prefix_id': fields.many2one('hr.nrc.prefix', 'NRC Prefix'),
        'nrc_number': fields.char('NRC Number'),
        'labour_card': fields.char('Labour Card'),
        'first_aider': fields.boolean('First Aider'),
        'fire_figher': fields.boolean('Fire Fighter'),
        'ohs': fields.boolean('OHS Member'),
        'restricted_allowed': fields.boolean('Allowed Restricted Area'),
        'ssb': fields.char('SSB'),
        'ssb_effective_date': fields.date('SSB Effective Date'),
        'labour_referenceno': fields.char('Labour Reference No'),
        'labour_card_release_date': fields.date('Labour Card Release Date'),
        'gender': fields.selection([('male', 'Male'), ('female', 'Female')], 'Gender',required=True),
        'marital': fields.selection([('single', 'Single'), ('married', 'Married'), ('widower', 'Widower'), ('divorced', 'Divorced')], 'Marital Status',required=True),
    }
    
    def write(self, cr, uid, ids, vals, context=None):
        print 'vals>>>>',vals   
        changes = ''  
        print 'len>>', len(changes)          
        if vals.get('employee_id'):
            changes = ' Badge ID,'
            
        if vals.get('fingerprint_id'):
            changes += ' FingerPrint ID,'
            
        if vals.get('name'):
            changes += ' Name,'
        
        if vals.get('nrc_prefix_id'):
            changes += ' NRC Prefix,'
        
        if vals.get('nrc_number'):
            changes += ' NRC Number,'
        
        if vals.get('birthday'):
            changes += ' Date of Birth,'
        
        if vals.get('initial_employment_date'):
            changes += ' Initial Date of Employment,' 
        
        if len(changes) > 0:
            print 'changes[:-1]>>>',changes[:-1]
            title =  'Employee updated' + '\n' + changes[:-1]
            self.message_post(cr, uid, ids, body=_(title), context=context)
                                                
        new_id = super(hr_employee, self).write(cr, uid, ids, vals, context=context)                
        return new_id
    
    def create(self, cr, uid, vals, context=None):
        current_date = datetime.now()
        current_year = current_date.year
        current_month = current_date.month
        if vals['birthday']:
            birth_date = parser.parse(vals['birthday'])
            age = current_year - birth_date.year
            if age < 18:
                raise osv.except_osv(_('Invalid Action!'), _('This date of birth is too Young!'))
            elif age == 18 and birth_date.month > current_month:  
                raise osv.except_osv(_('Invalid Action!'), _('This date of birth is too Young!'))
            if age > 60:
                raise osv.except_osv(_('Invalid Action!'), _('This date of birth is too Old!'))
            elif age == 60 and birth_date.month < current_month:
                raise osv.except_osv(_('Invalid Action!'), _('This date of birth is too Old!'))
            
        new_id = super(hr_employee, self).create(cr, uid, vals, context=context)
        return new_id
hr_employee()     