from openerp.osv import fields, osv
from openerp.tools.translate import _
#from datetime import date,datetime
from dateutil import parser
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as OE_DATEFORMAT

class hr_employee(osv.osv):
    _inherit = "hr.employee"
    
    def _get_employed_months(self, cr, uid, ids, field_name, arg, context=None):

        res = dict.fromkeys(ids, 0.0)        
        _res = self.get_months_service_to_date(cr, uid, ids, context=context)
        for k, v in _res.iteritems():
            res[k] = v[0]
        return res
    
    def get_months_service_to_date(self, cr, uid, ids, dToday=None, context=None):    
        '''Returns a dictionary of floats. The key is the employee id, and the value is
        number of months of employment.'''
        
        res = dict.fromkeys(ids, 0)
        if dToday == None:
            dToday = date.today()

        for ee in self.pool.get('hr.employee').browse(cr, uid, ids, context=context):

            delta = relativedelta(dToday, dToday)
            contracts = self._get_contracts_list(ee)
            if len(contracts) == 0:
                res[ee.id] = (0.0, False)
                continue

            dInitial = datetime.strptime(
                contracts[0].date_start, OE_DATEFORMAT).date()

            if ee.initial_employment_date:
                #dFirstContract = dInitial
                dFirstContract =datetime.strptime(
                    ee.initial_employment_date, '%Y-%m-%d').date()
                dInitial = datetime.strptime(
                    ee.initial_employment_date, '%Y-%m-%d').date()
                
                if dFirstContract != dInitial:
                    raise osv.except_osv(_('Employment Date mismatch!'),
                                         _('Initial Employment Date must be the same with Trial Start Date and Duration Start Date.\nEmployee: %s')% ee.name)

                delta = relativedelta(dFirstContract, dInitial)

            for c in contracts:
                if c.state != 'contract_ending' and c.state != 'pending_done' and c.state != 'done':
                #if c.state != 'draft':
                    #dStart = datetime.strptime(c.date_start, '%Y-%m-%d').date()
                    dStart = datetime.strptime(
                    ee.initial_employment_date, '%Y-%m-%d').date()
                    if dStart >= dToday:
                        continue
    
                    # If the contract doesn't have an end date, use today's date
                    # If the contract has finished consider the entire duration of
                    # the contract, otherwise consider only the months in the
                    # contract until today.
                    #
                    if c.date_end:
                        dEnd = datetime.strptime(c.date_end, '%Y-%m-%d').date()
                    else:
                        dEnd = dToday
                    if dEnd > dToday:
                        dEnd = dToday
    
                    delta += relativedelta(dEnd, dStart)

            # Set the number of months the employee has worked
            date_part = float(delta.days) / float(
                self._get_days_in_month(dInitial))
            res[ee.id] = (
                float((delta.years * 12) + delta.months) + date_part, dInitial)

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
        contract_obj = self.pool.get('hr.contract')
        for data in self.browse(cr, uid, ids):
            effective_date = None
            contract_ids = contract_obj.search(cr,uid,[('employee_id', '=',data.id )], context=context)
            if contract_ids:
                for contract_id in contract_ids:
                    contract = contract_obj.browse(cr,uid,contract_id,context=context)
                    if contract:
                        effective_date = contract.effective_date
                res[data.id] = effective_date 
            else:
                res[data.id] = effective_date      
#         res={}
#         termination_obj =self.pool.get('hr.employee.termination')
#         for record in self.browse(cr, uid, ids):
#             effective_date = None
#             termination_ids=termination_obj.search(cr,uid,[('employee_id','=',record.id)], context=context)
#             if termination_ids:
#                 for termination_id in termination_ids:
#                     termination= termination_obj.browse(cr, uid, termination_id, context=context)
#                     if termination:
#                         effective_date = termination.name
#                         res[record.id] = effective_date
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
    def _set_remaining_days(self, cr, uid, empl_id, name, value, arg, context=None):
        employee = self.browse(cr, uid, empl_id, context=context)
        diff = value - employee.remaining_leaves
        type_obj = self.pool.get('hr.holidays.status')
        holiday_obj = self.pool.get('hr.holidays')
        # Find for holidays status
        status_ids = type_obj.search(cr, uid, [('limit', '=', False)], context=context)
        if len(status_ids) != 1 :
            raise osv.except_osv(_('Warning!'),_("The feature behind the field 'Remaining Legal Leaves' can only be used when there is only one leave type with the option 'Allow to Override Limit' unchecked. (%s Found). Otherwise, the update is ambiguous as we cannot decide on which leave type the update has to be done. \nYou may prefer to use the classic menus 'Leave Requests' and 'Allocation Requests' located in 'Human Resources \ Leaves' to manage the leave days of the employees if the configuration does not allow to use this field.") % (len(status_ids)))
        status_id = status_ids and status_ids[0] or False
        if not status_id:
            return False
        if diff > 0:
            leave_id = holiday_obj.create(cr, uid, {'name': _('Allocation for %s') % employee.name, 'employee_id': employee.id, 'holiday_status_id': status_id, 'type': 'add', 'holiday_type': 'employee', 'number_of_days_temp': diff}, context=context)
        elif diff < 0:
            raise osv.except_osv(_('Warning!'), _('You cannot reduce validated allocation requests'))
        else:
            return False
        for sig in ('confirm', 'validate', 'second_validate'):
            holiday_obj.signal_workflow(cr, uid, [leave_id], sig)
        return True
    
    def _get_remaining_days(self, cr, uid, ids, name, args, context=None):
        current_year = datetime.now().year
        cr.execute("""SELECT
                sum(h.number_of_days) as days,
                h.employee_id
            from
                hr_holidays h
                join hr_holidays_status s on (s.id=h.holiday_status_id)
            where
                h.state='validate' and
                s.limit=False and
                h.employee_id in %s and
                (DATE_PART('year', date_from::date)=%s or DATE_PART('year', expiry_date::date)=%s)
            group by h.employee_id""", (tuple(ids),current_year,current_year,))
        res = cr.dictfetchall()
        remaining = {}
        for r in res:
            remaining[r['employee_id']] = r['days']
        for employee_id in ids:
            if not remaining.get(employee_id):
                remaining[employee_id] = 0.0
        return remaining
    
    _columns = {
        'remaining_leaves': fields.function(_get_remaining_days, string='Remaining Legal Leaves', fnct_inv=_set_remaining_days, type="float", help='Total number of legal leaves allocated to this employee, change this value to create allocation/leave request. Total based on all the leave types without overriding limit.'),
        'trial_end_date' : fields.function(_trial_end_date_availabe, method=True, string="Trial End Date", type='date', store=True),
        'date_end' : fields.function(_contract_end_availabe, method=True, string="Contract End Date", type='date', store=True),        
        'wage' : fields.function(_contract_wage_availabe, method=True, string="Wage", store=True),
        'struct_id' : fields.function(_contract_structure_availabe, method=True, string="Salary Structure",type='char', store=True),
        'effective_date' : fields.function(_effective_date_available, type='date', method=True, groups=False,string="Effective Date"),
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
        'gender': fields.selection([('male', 'Male'), ('female', 'Female')], 'Gender'),
        'marital': fields.selection([('single', 'Single'), ('married', 'Married'), ('widower', 'Widower'), ('divorced', 'Divorced')], 'Marital Status'),
        'length_of_service': fields.function(_get_employed_months, type='float', method=True, 
                                             groups=False,
                                             string='Length of Service',store=True),
                
    }
    

    def work_service(self, cr, uid, ids, dToday=None, context=None):
        '''Returns a dictionary of floats. The key is the employee id, and the value is
        number of months of employment.'''
        
        res = dict.fromkeys(ids, 0)
        work_service=""
        if dToday == None:
            dToday = date.today()

        for ee in self.pool.get('hr.employee').browse(cr, uid, ids, context=context):

            delta = relativedelta(dToday, dToday)
            contracts = self._get_contracts_list(ee)
            if len(contracts) == 0:
                res[ee.id] = (0.0, False)
                continue

            dInitial = datetime.strptime(
                contracts[0].date_start, OE_DATEFORMAT).date()

            if ee.initial_employment_date:
                dFirstContract = dInitial
                dInitial = datetime.strptime(
                    ee.initial_employment_date, '%Y-%m-%d').date()
                print 'dFirstContract',dFirstContract
                print 'dInitial',dInitial
                if dFirstContract != dInitial:
#                     raise osv.except_osv(_('Employment Date mismatch!'),
#                                          _('Initial Employment Date must be the same with Trial Start Date and Duration Start Date.\nEmployee: %s')% ee.name)

                    delta = relativedelta(dFirstContract, dInitial)

            for c in contracts:
                if c.state != 'contract_ending' and c.state != 'pending_done' and c.state != 'done':
                #if c.state != 'draft' :
                    #dStart = datetime.strptime(c.date_start, '%Y-%m-%d').date()
                    dStart = datetime.strptime(
                    ee.initial_employment_date, '%Y-%m-%d').date()
                    if dStart >= dToday:
                        continue
    
                    # If the contract doesn't have an end date, use today's date
                    # If the contract has finished consider the entire duration of
                    # the contract, otherwise consider only the months in the
                    # contract until today.
                    #
                    if c.date_end:
                        dEnd = datetime.strptime(c.date_end, '%Y-%m-%d').date()
                    else:
                        dEnd = dToday
                    if dEnd > dToday:
                        dEnd = dToday
    
                    delta += relativedelta(dEnd, dStart)
                   
                    print 'delta',delta
                    if delta.years>0:
                        if delta.years==1:
                            work_service=work_service+str(delta.years)+' year  '
                        else:
                            work_service=work_service+str(delta.years)+' years  '
                    if delta.months>0:
                        if delta.months==1:
                            work_service=work_service+str(delta.months)+' month  '
                        else:
                            work_service=work_service+str(delta.months)+' months  '
                    if delta.days>0:
                        if delta.days==1:
                            work_service=work_service+str(delta.days)+' day'   
                        else:
                            work_service=work_service+str(delta.days)+' days'                   
                   
                
            # Set the number of months the employee has worked           
            res[ee.id] = work_service     
        return res
    
    def write(self, cr, uid, ids, vals, context=None):
        changes = ''           
        if vals.get('employee_id'):
            changes = ' Badge ID,'
            
        if vals.get('fingerprint_id'):        
            changes += ' FingerPrint ID,'
            if ids:
                emp = self.browse(cr, uid, ids, context=context)
                vals['employee_id']=vals['fingerprint_id']
            
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
    
    def check_nrc(self, cr, uid, ids, context=None):
        identification_id = None
        if ids:
            emp = self.browse(cr, uid, ids, context=context)
            identification_id = emp.nrc_prefix_id.name + str(emp.nrc_number)
            emp_id = self.search(cr, uid, ['&',('identification_id', '=', identification_id),('id', '!=', ids[0])], order='id', limit=1, context=context)
            if len(emp_id) > 0:
                emp_obj = self.browse(cr, uid,emp_id,context=context ) 
                self.unlink(cr, uid, ids, context=context)
                cr.execute("delete from hr_employee where id=%s",(ids[0],))  
                raise osv.except_osv(_('Warning!'), _('This NRC number already exist with %s!') %emp_obj.name_related)
                
        return True  
#*****************CLOSE COMMENT BY PHYO HSU*******************************************          
#     def create(self, cr, uid, vals, context=None):
#         current_date = datetime.now()
#         current_year = current_date.year
#         current_month = current_date.month
#         if vals['birthday']:
#             birth_date = parser.parse(vals['birthday'])
#             age = current_year - birth_date.year
#             if age < 18:
#                 raise osv.except_osv(_('Invalid Action!'), _('This date of birth is too Young!'))
#             elif age == 18 and birth_date.month > current_month:  
#                 raise osv.except_osv(_('Invalid Action!'), _('This date of birth is too Young!'))
#             if age > 60:
#                 raise osv.except_osv(_('Invalid Action!'), _('This date of birth is too Old!'))
#             elif age == 60 and birth_date.month < current_month:
#                 raise osv.except_osv(_('Invalid Action!'), _('This date of birth is too Old!'))
#******************* END***********************************************************
       
#         new_id = False
#         identification_id = None
#         if vals.get('nrc_prefix_id'):
#             #identification_id = vals.get('nrc_prefix_id')
#             nrc = self.pool.get('hr.nrc.prefix').browse(cr,uid,vals.get('nrc_prefix_id'),context=context)
#             identification_id = nrc.name
#         if vals.get('nrc_number'):
#             identification_id += str(vals.get('nrc_number'))    
#             emp_id = self.search(cr, uid, [('identification_id', '=', identification_id)], context=context)
#             if len(emp_id) > 0:
#                 new_id = super(hr_employee, self).create(cr, uid, vals, context=context)
#                 mod_obj = self.pool.get('ir.model.data')
#                 wiz_view = mod_obj.get_object_reference(cr, uid, 'hr_customization', 'employee_warning_form')
#                 view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'hr_customization', 'employee_warning_form')
#                 ctx = {
#                  'identification_id': identification_id,
#                  'emp_id': new_id,
#                  }
#                 act_import = {
#                         'name': _('employee.yes.no.form'),
#                         'view_type': 'form',
#                         'view_mode': 'form',
#                         'res_model': 'employee.yes.no',
#                         'view_id': [wiz_view[1]],
#                         'nodestroy': False,
#                         'target': 'new',
#                         #'views': [(wiz_view[1], 'form')],
#                         'type': 'ir.actions.act_window',
#                         'context': ctx,#vals,
#                 }
#                 
#                 return act_import
# 
#                  
#                  
#             else:    
#                 new_id = super(hr_employee, self).create(cr, uid, vals, context=context)
#              
#         return new_id 
 
#**************CLOSE COMMENT BY PHYO HSU****************************************  
#         new_id = super(hr_employee, self).create(cr, uid, vals, context=context)
#         return new_id
#**************END**************************************************************
hr_employee()     