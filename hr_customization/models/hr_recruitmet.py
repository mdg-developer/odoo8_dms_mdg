from openerp.osv import fields, osv
from openerp import tools
from datetime import date,datetime
from dateutil import parser
from openerp.tools.translate import _


class hr_applicant_inherit(osv.osv):
    _inherit = 'hr.applicant'
    
    def _get_identification_id(self, cr, uid, ids, fields, arg, context):
                     
        data = self.browse(cr, uid, ids)[0]         
        nrc_prefix_id = data.nrc_prefix_id.name
        nrc_number = data.nrc_number      
        
                        
        res = {}      
        identification = ''
        if nrc_prefix_id:
            identification = nrc_prefix_id + nrc_number
        
                     
        for data in self.browse(cr, uid, ids, context):
            res[data.id] = identification
        return res
    
    _columns = {
              'nrc_prefix_id': fields.many2one('hr.nrc.prefix', 'NRC Prefix', required=True),
              'nrc_number': fields.char('NRC Number', required=True),  
              'dob':fields.date('Date of Birth'),
              #'identification_id':fields.char('NRC No')
              'identification_id' : fields.function(_get_identification_id, string="NRC ID", store=True, type="char"),
              'section_id': fields.many2one('hr.section', 'Section'),
              'initial_employment_date': fields.date('Initial Date of Employment', groups=False),
              }            
        
    def create(self, cr, uid, vals, context=None):
        current_date = datetime.now()
        current_year = current_date.year
        current_month = current_date.month
        if vals['dob']:
            birth_date = parser.parse(vals['dob'])
            age = current_year - birth_date.year
            if age < 18:
                raise osv.except_osv(_('Invalid Action!'), _('This date of birth is too Young!'))
            elif age == 18 and birth_date.month > current_month:  
                raise osv.except_osv(_('Invalid Action!'), _('This date of birth is too Young!'))
            if age > 60:
                raise osv.except_osv(_('Invalid Action!'), _('This date of birth is too Old!'))
            elif age == 60 and birth_date.month < current_month:
                raise osv.except_osv(_('Invalid Action!'), _('This date of birth is too Old!'))
        nrc_obj = self.pool.get('hr.nrc.prefix')
        identification_id = nrc_prefix_id = prefix = number = None
        if vals['nrc_prefix_id']:
            nrc_prefix_id = vals['nrc_prefix_id']
            nrc_id = nrc_obj.browse(cr,uid,nrc_prefix_id,context=None)
            if nrc_id:
                prefix = nrc_id.name
        if vals['nrc_number']:
            number =  vals['nrc_number']
            
        identification_id =  prefix + number
                  
        if number is not None:
            cr.execute("""select ht.name,hr.name,he.name_related,he.identification_id,he.nrc_number 
            from hr_employee_termination ht,hr_employee_termination_reason hr,hr_employee he
            where ht.employee_id = he.id and ht.reason_id=hr.id and ht.state = 'done'
            and he.nrc_number =%s 
            and (lower(hr.name) ='black list' or lower(hr.name) ='resigned without noticed'
            or lower(hr.name) ='resigned without full service')
            """,(number,))
            data = cr.fetchall()
            if data:
                data_count = data[0][0]
                if data_count > 0:             
                    raise osv.except_osv(_('Alert!:'), _("'%s' with %s already exist \n Reason: %s Date: %s")% (data[0][2],data[0][3],data[0][1],data[0][0]))
#             cr.execute('select id,length_of_service,name_related,identification_id from hr_employee WHERE nrc_number =%s',(number,))
#             service_data = cr.fetchone()
#             if service_data:
#                 if service_data[1] < 12:
#                     raise osv.except_osv(_('Alert!'), _("'%s' with %s already exist \n This employee worked less than 12 months")% (service_data[2],service_data[3]))
            cr.execute('select name_related,identification_id from hr_employee WHERE nrc_number =%s',(number,))
            nrc_data = cr.fetchone()
            if nrc_data:
                raise osv.except_osv(_('Alert!'), _("'%s' with %s already exist!")% (nrc_data[0],nrc_data[1]))       
        new_id = super(hr_applicant_inherit, self).create(cr, uid, vals, context=context)
        return new_id   
    
    def create_employee_from_applicant(self, cr, uid, ids, context=None):
        """ Create an hr.employee from the hr.applicants """
        if context is None:
            context = {}
        hr_employee = self.pool.get('hr.employee')
        model_data = self.pool.get('ir.model.data')
        act_window = self.pool.get('ir.actions.act_window')
        emp_id = False
        for applicant in self.browse(cr, uid, ids, context=context):
            address_id = contact_name = False
            if applicant.initial_employment_date is False:
                raise osv.except_osv(_('Alert!'), _("Please Choose Initial Date of Employment."))
            if applicant.partner_id:
                address_id = self.pool.get('res.partner').address_get(cr, uid, [applicant.partner_id.id], ['contact'])['contact']
                contact_name = self.pool.get('res.partner').name_get(cr, uid, [applicant.partner_id.id])[0][1]
            if applicant.job_id and (applicant.partner_name or contact_name):
                applicant.job_id.write({'no_of_hired_employee': applicant.job_id.no_of_hired_employee + 1})
                create_ctx = dict(context, mail_broadcast=True)
                emp_id = hr_employee.create(cr, uid, {'name': applicant.partner_name or contact_name,
                                                     'job_id': applicant.job_id.id,
                                                     'fingerprint_id': applicant.partner_name,
                                                     'address_home_id': address_id,
                                                     'department_id': applicant.department_id.id or False,
                                                     'section_id': applicant.section_id.id or False,
                                                     'nrc_prefix_id': applicant.nrc_prefix_id.id or False,
                                                     'nrc_number': applicant.nrc_number or False,
                                                     'initial_employment_date':applicant.initial_employment_date or False,
                                                     'birthday': applicant.dob or False,
                                                     'address_id': applicant.company_id and applicant.company_id.partner_id and applicant.company_id.partner_id.id or False,
                                                     'work_email': applicant.department_id and applicant.department_id.company_id and applicant.department_id.company_id.email or False,
                                                     'work_phone': applicant.department_id and applicant.department_id.company_id and applicant.department_id.company_id.phone or False,
                                                     }, context=create_ctx)
                self.write(cr, uid, [applicant.id], {'emp_id': emp_id}, context=context)
                self.pool['hr.job'].message_post(
                    cr, uid, [applicant.job_id.id],
                    body=_('New Employee %s Hired') % applicant.partner_name if applicant.partner_name else applicant.name,
                    subtype="hr_recruitment.mt_job_applicant_hired", context=context)
            else:
                raise osv.except_osv(_('Warning!'), _('You must define an Applied Job and a Contact Name for this applicant.'))

        action_model, action_id = model_data.get_object_reference(cr, uid, 'hr', 'open_view_employee_list')
        dict_act_window = act_window.read(cr, uid, [action_id], [])[0]
        if emp_id:
            dict_act_window['res_id'] = emp_id
        dict_act_window['view_mode'] = 'form,tree'
        return dict_act_window     
hr_applicant_inherit()

class hr_job(osv.osv):
    _inherit = 'hr.job'
     
    _columns = {              
              'section_id': fields.many2one('hr.section', 'Section'),
              }
     
hr_job()        
        