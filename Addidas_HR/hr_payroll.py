from pytz import timezone, utc

import openerp.addons.decimal_precision as dp
from datetime import datetime, timedelta
from openerp import models, fields, api, _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as OE_DATEFORMAT
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as OE_DATETIMEFORMAT
from openerp.tools.translate import _
from openerp.osv import fields, osv

class hr_payslip_customize(osv.osv):
    '''
    Payslip Worked Time
    '''
    _name = 'hr.payslip'
    _inherit = "hr.payslip"
    def get_inputs(self, cr, uid, contract_ids, date_from, date_to, context=None):
        #get job_id  
        con_id=len(contract_ids)
        c_id=con_id-1
        print 'contract_ids',contract_ids[-c_id]
        contract_ids=contract_ids[-c_id]
        print 'contract_ids----------',contract_ids
        #seniority bonus input amount
        cr.execute('''SELECT (DATE_PART('month', current_date) - DATE_PART('month', date_start)) as length_month from hr_contract where id=%s''', (contract_ids,))
        mo= cr.fetchone()
        month=mo[0]
        cr.execute('select amount from hr_seniority where from_month <%s and to_month >%s',(month,month))
        se_amount=cr.fetchone()
        if se_amount:
           se_amount=se_amount[0];
        else:
            se_amount=0.0
           
        cr.execute('select employee_id from hr_contract where id = %s', (contract_ids,))
        employee_id= cr.fetchone()
        cr.execute('select skill_type_id,critical_grade_id,position_grade_id,language_grade_id,factory_driver_license_amt,electricity_certificate_amt,amount,special_amount from hr_bonus_entry where employee_id=%s and state=\'confirm\' and entry_date between %s and %s ', (employee_id,date_from,date_to))
        employee_data= cr.fetchone()
        if employee_data:
            skill_type=employee_data[0]
            cri_grade=employee_data[1]
            posi_grade=employee_data[2]
            lang_grade=employee_data[3]        
            dri_amt=employee_data[4]
            ceri_amt=employee_data[5]
            certifi_amount=employee_data[6]
            lang_amount=employee_data[7]
            #for performance*skill bonus(multi_skill and full_skill)
            cr.execute('''select * from (
            select pe.date,hb.employee_id,hb.performance from hr_total_productivity_bonus hb,productivity_bonus_entry pe
            where hb.bonus_id=pe.id
            union
            select pe.date,hb.employee_id,hb.performance from hr_indirect_productivity_bonus hb,productivity_bonus_entry pe
            where hb.direct_id=pe.id
            )A
            where date between %s and %s
            and employee_id=%s''',(date_from,date_to,employee_id,) ) 
            performance=cr.fetchone()
            skill_amount=0.0
            if(skill_type == 'multi_skill'):
                cr.execute('select multi_skill_amt from hr_bonus',)
                s_amount= cr.fetchone()
                if performance:
                   skill_amount=s_amount[0]*(performance[2]/100)    
            elif (skill_type == 'full_skill'):      
                cr.execute('select full_skill_amt from hr_bonus',)
                s_amount= cr.fetchone()
                if performance:
                   skill_amount=s_amount[0]*(performance[2]/100)   
            else:
                skill_amount=0.0   
      
    
            if(dri_amt is True): 
                cr.execute('select factory_driver_license_amt from hr_bonus',)
                amount= cr.fetchone() 
                dri_amount=amount[0]
            else:
                dri_amount=0.0
            if(ceri_amt is True): 
                cr.execute('select electricity_certificate_amt from hr_bonus',)
                amount= cr.fetchone() 
                ceri_amount=amount[0]
            else:
                ceri_amount=0.0          
            cr.execute('select language_bonus_amt from hr_language_input where id= %s', (lang_grade,))
            l_amount= cr.fetchone() 
            if l_amount:
                lan_amount=l_amount[0];
            else:
                lan_amount=0.0
            cr.execute('select critical_skill_amt from hr_critical_input where id= %s', (cri_grade,))
            c_amount= cr.fetchone() 
            if c_amount:
                cri_amount=c_amount[0];
            else:
                cri_amount=0.0 
            cr.execute('select job_position_amt from hr_position_input where id= %s', (posi_grade,))
            p_amount= cr.fetchone() 
            if p_amount:
                posi_amount=p_amount[0];
            else:
                posi_amount=0.0
        else:
            se_amount=0.0
            skill_amount=0.0
            dri_amount=0.0
            ceri_amount=0.0
            cri_amount=0.0
            lan_amount=0.0
            posi_amount=0.0
            lang_amount=0.0
            certifi_amount=0.0
        cr.execute('''select * from (
        select hb.total_amount,pe.date,hb.employee_id from hr_total_productivity_bonus hb,productivity_bonus_entry pe
        where hb.bonus_id=pe.id
        union
        select hb.total_amount,pe.date,hb.employee_id from hr_indirect_productivity_bonus hb,productivity_bonus_entry pe
        where hb.direct_id=pe.id
        )A
        where date between %s and %s
        and employee_id=%s''',(date_from,date_to,employee_id,) )      
        total_amount= cr.fetchone() 
        if total_amount:
           productivity_bonus=total_amount[0]
        else:
           productivity_bonus=0.0
                                                 
        res = []
        contract_obj = self.pool.get('hr.contract')
        rule_obj = self.pool.get('hr.salary.rule')
       
        structure_ids = contract_obj.get_all_structures(cr, uid, contract_ids, context=context)
        rule_ids = self.pool.get('hr.payroll.structure').get_all_rules(cr, uid, structure_ids, context=context)
        sorted_rule_ids = [id for id, sequence in sorted(rule_ids, key=lambda x:x[1])]

        for contract in contract_obj.browse(cr, uid, contract_ids, context=context):

            #print 'AAAAcontract_ids',contract_ids
            for rule in rule_obj.browse(cr, uid, sorted_rule_ids, context=context):
                if rule.input_ids:
                    for input in rule.input_ids:

#     
                        if input.code == 'SNB':
                            inputs = {
                               'name': input.name,
                               'code': input.code,
                               'amount':se_amount,
                               'contract_id': contract.id,
                              }
                        else:
                            inputs = {
                                     'name': input.name,
                                     'code': input.code,
                                     'amount':0.0,
                                     'contract_id': contract.id,
                                }
                        if input.code == 'EPB':
                            inputs = {
                               'name': input.name,
                               'code': input.code,
                               'amount':skill_amount,
                               'contract_id': contract.id,
                              }                            
                        if input.code == 'FDB':
                            inputs = {
                               'name': input.name,
                               'code': input.code,
                               'amount':dri_amount,
                               'contract_id': contract.id,
                              } 
                        if input.code == 'ECB':
                            inputs = {
                               'name': input.name,
                               'code': input.code,
                               'amount':ceri_amount,
                               'contract_id': contract.id,
                              } 
                        if input.code == 'CTB':
                            inputs = {
                               'name': input.name,
                               'code': input.code,
                               'amount':cri_amount,
                               'contract_id': contract.id,
                              } 
                        if input.code == 'LGB':
                            inputs = {
                               'name': input.name,
                               'code': input.code,
                               'amount':lan_amount,
                               'contract_id': contract.id,
                              } 
                        if input.code == 'POB':
                            inputs = {
                               'name': input.name,
                               'code': input.code,
                               'amount':posi_amount,
                               'contract_id': contract.id,
                              }
                        if input.code == 'SPA':
                            inputs = {
                               'name': input.name,
                               'code': input.code,
                               'amount':lang_amount,
                               'contract_id': contract.id,
                              }
                        if input.code == 'CFB':
                            inputs = {
                               'name': input.name,
                               'code': input.code,
                               'amount':certifi_amount,
                               'contract_id': contract.id,
                              }
                        if input.code == 'PDB':
                            inputs = {
                               'name': input.name,
                               'code': input.code,
                               'amount':productivity_bonus,
                               'contract_id': contract.id,
                              }                                                                                                                                                                                                                                       
                        res += [inputs]
                        #print 'inputs',res;
            return res 