'''
Created on Jul 22, 2015

@author: Naw Zar
'''
from openerp import tools
from openerp.osv import fields, osv
from openerp import workflow
from docutils.nodes import target

##=======================================Direct Productivity Bonus Starting===============================================##
MONTH_SELECTION = [('1','Jan'),
            ('2','Feb'),
            ('3', 'Mar'),
            ('4','Apr'),
            ('5 ','May'),
            ('6','Jun'),
            ('7','Jul'),
            ('8','Aug'),
            ('9','Sep'),
            ('10','Oct'),
            ('11','Nov'),
            ('12','Dec')]

class hr_total_productivity_bonus(osv.osv):
    _name='hr.total.productivity.bonus'
    _columns={'bonus_id':fields.many2one('productivity.bonus.entry','Bonus'),
              'employee_id':fields.integer('Employee'),
             'position':fields.char('Position'),
             'performance':fields.float('Performance'),
             'abnormal':fields.float('Abnormal'),
             'contribution':fields.float('Contribution'),
             'total_percent':fields.float('Total Percent'),
             'total_amount':fields.float('Total Amount')
             }
hr_total_productivity_bonus()

class hr_indirect_productivity_bonus(osv.osv):
    _name='hr.indirect.productivity.bonus'
    _columns={'direct_id':fields.many2one('productivity.bonus.entry','Bonus'),
             'employee_id':fields.integer('Employee'),
             'position':fields.char('Position'),
             'performance':fields.float('Performance'),
             'abnormal':fields.float('Abnormal'),
             'contribution':fields.float('Contribution'),
             'total_percent':fields.float('Total Percent'),
             'total_amount':fields.float('Total Amount')
             }
hr_total_productivity_bonus()


class productivity_bonus_entry(osv.osv):
    _name = "productivity.bonus.entry"
    _description = "Productivity Bonus Entry"

    _columns = {
                'date':fields.date('Date'),
                'month':fields.selection(MONTH_SELECTION,'Month'),
                'name':fields.selection([('direct','Direct'),
                                       ('indirect','InDirect'),
                                        ],'Type',required=True),
                'week1':fields.many2one('setting.week', 'Week1'),
                'week2':fields.many2one('setting.week', 'Week2'),
                'week3':fields.many2one('setting.week', 'Week3'),
                'week4':fields.many2one('setting.week', 'Week4'),
                'w1_show':fields.char('.',readonly=True),
                'w2_show':fields.char('.',readonly=True),
                'w3_show':fields.char('.',readonly=True),
                'w4_show':fields.char('.',readonly=True),                
                'target1':fields.float('Target'),
                'target2':fields.float('Target'),
                'target3':fields.float('Target'),
                'target4':fields.float('Target'),
                'actual1':fields.float('Actual'),
                'actual2':fields.float('Actual'),
                'actual3':fields.float('Actual'),
                'actual4':fields.float('Actual'),
                'a_rate1':fields.char('Achieve Rate'),
                'a_rate2':fields.char('Achieve Rate'),
                'a_rate3':fields.char('Achieve Rate'),
                'a_rate4':fields.char('Achieve Rate'),
                'grade1':fields.char('Grade'),
                'grade2':fields.char('Grade'),
                'grade3':fields.char('Grade'),
                'grade4':fields.char('Grade'),
                'p_bonus1':fields.float('Productivity Bonus'),
                'p_bonus2':fields.float('Productivity Bonus'),
                'p_bonus3':fields.float('Productivity Bonus'),
                'p_bonus4':fields.float('Productivity Bonus'),
                'department_id':fields.many2one('hr.department','Department'),
                'bc_grade':fields.char('BC Grade %'),
                'bc_amount':fields.float('BC Amount'), 
                'o_target':fields.boolean('Over Target'),
                'o_target_amount':fields.float('Over Target Amount'),
                'a_rate':fields.float('Achieve Rate'),
                'grade':fields.char('Grade'),
                'productivity_bounus':fields.float('Productivity Bonus'),
                'department_id':fields.many2one('hr.department','Department'),
                'detail_line_id':fields.one2many('hr.total.productivity.bonus','bonus_id','Total Productivity Bonus'),
                'indirect_line_id':fields.one2many('hr.indirect.productivity.bonus','direct_id','Indirect Productivity Bonus'),
                'state': fields.selection([
                ('draft','draft'),                   
                ('direct_confirm', 'Confirm'),
                ('done', 'Success'),
                ], 'Status', readonly=True, copy=False, help="Gives the status of the quotation or sales order.\
                  \nThe exception status is automatically set when a cancel operation occurs \
                  in the invoice validation (Invoice Exception) or in the picking list process (Shipping Exception).\nThe 'Waiting Schedule' status is set when the invoice is confirmed\
                   but waiting for the scheduler to run on the order date.", select=True),
                }
    _defaults = {
        'state': 'draft', 
        'name' :'direct',     
        }
    
    def onchange_week1(self,cr,uid,ids,week1,w1,context=None):
            print 'onchange'
            result={}
            if not week1:
                print 'No Week'
                return True
    #         select *From product_template t ,product_product p where t.id=p.product_tmpl_id
            else:
                cr.execute('select from_date,to_date from setting_week where id=%s',(week1,))
                week_list = cr.fetchone()
                print 'price record',week_list
                from_date = week_list[0]
                to_date = week_list[0]
                week_name= from_date + '/' + to_date
                if w1=='w1' : 
                    result.update({'w1_show':week_name})
                elif w1=='w2' :
                    result.update({'w2_show':week_name})
                elif w1=='w3' :
                    result.update({'w3_show':week_name})
                else :
                    result.update({'w4_show':week_name})
                return{'value' : result}
        
    def onchange_achieve_rate(self,cr,uid,ids,target,actual,w,context=None):
            print 'onchange'
            result={}
            if target == 0.0:
                print 'No Week'
                return True
            else:
                real_target = target
                real_actual = actual
                achieve_rate = (actual/target)*100 
                actual_achieve_rate= "{0:.2f}".format(achieve_rate)+'%'
                cr.execute('select to_percentage from hite_rate where from_percentage<=0.0 and rate_id = (select id from productivity_bonus where name=%s)',('direct',))
                to_percentage_list= cr.fetchone()
                to_percentage = to_percentage_list[0]
                print "To Percentage",to_percentage
                cr.execute('select from_percentage from hite_rate where to_percentage<=0.0 and rate_id = (select id from productivity_bonus where name=%s)',('direct',))
                from_percentage_list = cr.fetchone()
                from_percentage= from_percentage_list[0]
                print "From Percentage",from_percentage
                if achieve_rate <= to_percentage:
                    cr.execute('select grade,productivity_bonus from hite_rate hr, productivity_bonus pb where from_percentage<=0.0 and to_percentage>=%s and hr.rate_id = pb.id and pb.name= %s',(achieve_rate,'direct',))
                elif achieve_rate>=from_percentage :
                    cr.execute('select grade,productivity_bonus from hite_rate hr, productivity_bonus pb where from_percentage<=%s and to_percentage<=0.0 and hr.rate_id = pb.id and pb.name= %s',(achieve_rate,'direct',))
                else :
                    cr.execute('select grade,productivity_bonus from hite_rate hr, productivity_bonus pb where from_percentage<=%s and to_percentage>=%s and hr.rate_id = pb.id and pb.name= %s',(achieve_rate,achieve_rate,'direct',))
                hit_rate_list = cr.fetchone()
                print 'hit rate list',hit_rate_list
                grade = hit_rate_list[0]
                productivity_bonus = hit_rate_list[1]
                
                if w=='w1' :
                    print "ONchange Print 1"
                    result.update({'a_rate1':actual_achieve_rate,'grade1':grade ,'p_bonus1':productivity_bonus})
                elif w=='w2':
                    print "ONchange Print 2"
                    result.update({'a_rate2':actual_achieve_rate,'grade2':grade ,'p_bonus2':productivity_bonus})
                elif w=='w3':
                    result.update({'a_rate3':actual_achieve_rate,'grade3':grade ,'p_bonus3':productivity_bonus})
                else:
                    result.update({'a_rate4':actual_achieve_rate,'grade4':grade ,'p_bonus4':productivity_bonus})
                return{'value' : result}
    
    def onchange_bonus(self,cr,uid,ids,p_bonus,context=None): 
        print "onchange bonus",p_bonus
        result={}
        if p_bonus:
            cr.execute ('select bc_amount from bc_grade where from_percentage >=%s and to_percentage<=%s and bc_line_id = (select id from productivity_bonus where name= %s)',(p_bonus,p_bonus,'direct'))
            amount_list = cr.fetchone()
            amount = amount_list[0]
            result.update({'bc_amount':amount,})
            return {'value':result}
        else:
            print 'No Bonus'
            return True
    
    def onchange_target(self,cr,uid,ids,o_target,context=None): 
        print "onchange bonus",o_target
        result={}
        if o_target:
            cr.execute ('select over_target_amount from hr_emp_bonus_settings')
            amount_list = cr.fetchone()
            if amount_list:
                amount = amount_list[0]
                result.update({'o_target_amount':amount,})
                return {'value':result}
        else:
            print 'No Bonus'
            return True
                
    def confirm(self, cr, uid, ids, context=None):
        print "id", ids
        bonus_val=ids[0]  
        # Get Monthly Bonus for worker
        cr.execute('select  (p_bonus1 + bc_amount * hs.worker_w1_hit_ration/100) +(p_bonus2+bc_amount * hs.worker_w2_hit_ration/100)+(p_bonus3+bc_amount * hs.worker_w3_hit_ration/100) +(p_bonus4+bc_amount *hs.worker_w4_hit_ration/100)+ pb.o_target_amount as p4,pb.department_id,pb.month from productivity_bonus_entry pb, hr_emp_bonus_settings hs where pb.id=%s',(ids[0],))
        worker_bonus_list= cr.fetchone()
        if worker_bonus_list :
            worker_bonus=worker_bonus_list[0]
            department_id = worker_bonus_list[1]
            month = worker_bonus_list[2]
            print "department_id",department_id
        #Get Monthly Bonus for Supervisor
        cr.execute('select  ((p_bonus1 + bc_amount) * (hs.factory_w1_hit_ration/100)) +((p_bonus2 + bc_amount) * (hs.factory_w2_hit_ration/100)) +((p_bonus3 + bc_amount) * (hs.factory_w3_hit_ration/100)) +((p_bonus4 + bc_amount) * (hs.factory_w4_hit_ration/100))+ pb.o_target_amount as p4,pb.department_id,pb.bc_amount from productivity_bonus_entry pb, hr_emp_bonus_settings hs where pb.id=%s',(ids[0],))
        supplier_bonus_list = cr.fetchone()
        if worker_bonus_list :
            supplier_bonus= supplier_bonus_list[0]
            print 'supplier bonus',supplier_bonus
        #Insert Into Employee_performance Table
        cr.execute('select employee_id,(abnormal+performance+contribution)as total_percentage,(%s * ((abnormal+performance+contribution)/100)),abnormal,performance,contribution,employee_id,%s from employee_performance where department_id=%s and emp_type=%s and month=%s and type=%s',(supplier_bonus,'Supervisor',department_id,'t',month,'direct',))
        supervisor_performance_list = cr.fetchall()
                
        cr.execute('select employee_id,(abnormal+performance+contribution)as total_percentage,(%s * ((abnormal+performance+contribution)/100)),abnormal,performance,contribution,employee_id,%s from employee_performance where department_id=%s and emp_type=%s and month=%s and type=%s',(worker_bonus,'Employee',department_id,'f',month,'direct',)) 
        worker_performance_list = cr.fetchall()
        
        cr.execute('select id, 100 as total_percentage, %s as total_amount, 0 as abnormal,100 as performance,0 as contribution,id,%s from hr_employee he where he.id not in (select employee_id from employee_performance where month=%s and type=%s) and department_id=%s and he.supervisor=%s and he.employee_type=%s',(supplier_bonus,'Supervisor',month,'direct',department_id,'t','direct'))
        supervisor_noperformance_list = cr.fetchall()
        
        cr.execute('select id, 100 as total_percentage, %s as total_amount, 0 as abnormal,100 as performance,0 as contribution,id,%s from hr_employee he where he.id not in (select employee_id from employee_performance where month=%s and type=%s) and department_id=%s and he.supervisor=%s and he.employee_type=%s',(worker_bonus,'Employee',month,'direct',department_id,'f','direct'))
        worker_noperformance_list = cr.fetchall()        
        
        total_performance_list = supervisor_performance_list + worker_performance_list + supervisor_noperformance_list + worker_noperformance_list  
        print 'performance list',total_performance_list
        hr_total_bonus_pool=self.pool.get('hr.total.productivity.bonus')
        if total_performance_list:
            self.write(cr, uid, [ids[0]], {'state': 'direct_confirm',})
            for result in total_performance_list:
                print 'result',result
                emp_id = result[0]
                print 'emp_id',emp_id
                value={'bonus_id':bonus_val,
                       'employee_id':result[0],
                       'position':result[7],
                       'performance':result[4],
                       'abnormal':result[3],
                       'contribution':result[5],
                       'total_percent':result[1],
                       'total_amount':result[2],
                     }
                hr_total_bonus_pool.create(cr,uid,value,context=context)
#                 cr.execute('update hr_employee set productivity_bonus=%s where id=%s',(result[2],emp_id))

                
    def onchange_grade(self,cr,uid,ids,achieve_rate,context=None):
            print 'onchange'
            result={}
            if target == 0.0:
                print 'No Week'
                return True
            else:
                cr.execute('select to_percentage from hite_rate hr,productivity_bonus pb where from_percentage<=0.0 and rate_id = (select id from productivity_bonus where name=%s)',('indirect',))
                to_percentage_list= cr.fetchone()
                if to_percentage_list :                 
                    to_percentage = to_percentage_list[0]
                    print "To Percentage",to_percentage
                cr.execute('select from_percentage from hite_rate where to_percentage<=0.0 and rate_id = (select id from productivity_bonus where name=%s)',('indirect',))
                from_percentage_list = cr.fetchone()
                from_percentage= from_percentage_list[0]
                print "From Percentage",from_percentage
#                 if achieve_rate <= to_percentage:
# #                      cr.execute('select grade,productivity_bonus from hite_rate hr, productivity_bonus pb where from_percentage<=%s and to_percentage>=%s and hr.rate_id = pb.id and pb.name= %s',(achieve_rate,achieve_rate,'direct',))
#                     cr.execute('select grade,productivity_bonus from hite_rate hr, productivity_bonus pb where from_percentage<=0.0 and to_percentage>=%s and hr.rate_id = pb.id and pb.name= %s',(achieve_rate,'indirect',))
                if achieve_rate >= from_percentage :
                    cr.execute('select grade,productivity_bonus from hite_rate hr, productivity_bonus pb where from_percentage<=%s and to_percentage<=0.0 and hr.rate_id = pb.id and pb.name= %s',(achieve_rate,'indirect',))
                else :
                    cr.execute('select grade,productivity_bonus from hite_rate hr, productivity_bonus pb where from_percentage<=%s and to_percentage>=%s and hr.rate_id = pb.id and pb.name= %s',(achieve_rate,achieve_rate,'indirect',))
                hit_rate_list = cr.fetchone()
                print 'hit rate list',hit_rate_list
                if hit_rate_list :
                    grade = hit_rate_list[0]
                    productivity_bonus = hit_rate_list[1]
                    result.update({'grade':grade ,'productivity_bounus':productivity_bonus})
                return{'value' : result}
                
    def indirect_confirm(self, cr, uid, ids, context=None):
        print "id", ids
        print "indirect form"
        bonus_val=ids[0]
       
        # Get Monthly Bonus for worker
        cr.execute('select pb.productivity_bounus, pb.department_id,pb.month, CASE WHEN pb.grade = %s THEN grade_a_emp WHEN pb.grade = %s THEN grade_b_emp WHEN pb.grade = %s THEN grade_c_emp WHEN pb.grade = %s THEN grade_d_emp ELSE NULL END as worker_bonus From productivity_bonus_entry pb,hr_emp_bonus_settings hb where pb.id=%s',('A','B','C','D',ids[0],))
        worker_bonus_list= cr.fetchone()
        if worker_bonus_list :
            productivity_bonus=worker_bonus_list[0]
            department_id = worker_bonus_list[1]
            month=worker_bonus_list[2]
            grade_percent = worker_bonus_list[3]
            worker_bonus = productivity_bonus * grade_percent/100
            
            print "departmant_id",worker_bonus
        # Get Monthly Bonus for supervisor
#         cr.execute('select pb.productivity_bounus, pb.department_id, CASE WHEN pb.grade = %s THEN grade_a_emp WHEN pb.grade = %s THEN grade_b_emp WHEN pb.grade = %s THEN grade_c_emp WHEN pb.grade = %s THEN grade_d_emp ELSE NULL END as worker_bonus From productivity_bonus_entry pb,hr_emp_bonus_settings hb where pb.id=%s',('A','B','C','D',ids[0],))
#         worker_bonus_list= cr.fetchone()
#         if worker_bonus_list :
#             productivity_bonus=worker_bonus_list[0]
#             grade_percent = worker_bonus_list[2]
#             worker_bonus = productivity_bonus * grade_percent/100
#             
#             print "departmant_id",worker_bonus
        #Insert Into Employee_performance Table
        cr.execute('select pb.productivity_bounus, pb.department_id, CASE WHEN pb.grade = %s THEN grade_a_sup WHEN pb.grade = %s THEN grade_b_sup WHEN pb.grade = %s THEN grade_c_sup WHEN pb.grade = %s THEN grade_d_sup ELSE NULL END as worker_bonus From productivity_bonus_entry pb,hr_emp_bonus_settings hb where pb.id=%s',('A','B','C','D',ids[0],))
        supervisor_bonus_list= cr.fetchone()
        if supervisor_bonus_list :
            sup_product_bonus=supervisor_bonus_list[0]
            sup_grade_percent = supervisor_bonus_list[2]
            supervisor_bonus = sup_product_bonus * sup_grade_percent/100
            
            print "departmant_id",supervisor_bonus
        cr.execute('select employee_id,(abnormal+performance+contribution)as total_percentage,(%s * ((abnormal+performance+contribution)/100)),abnormal,performance,contribution,employee_id,%s from employee_performance where department_id=%s and emp_type=%s and month=%s and type=%s',(worker_bonus,'Employee',department_id,'f',month,'indirect',)) 
        worker_performance_list = cr.fetchall()
        
        cr.execute('select employee_id,(abnormal+performance+contribution)as total_percentage,(%s * ((abnormal+performance+contribution)/100)),abnormal,performance,contribution,employee_id,%s from employee_performance where department_id=%s and emp_type=%s and month=%s and type=%s',(supervisor_bonus,'Supervisor',department_id,'t',month,'indirect',))
        supervisor_performance_list = cr.fetchall()
        
        cr.execute('select id, 100 as total_percentage, %s as total_amount, 0 as abnormal,100 as performance,0 as contribution,id,%s from hr_employee he where he.id not in (select employee_id from employee_performance where month=%s and type=%s) and department_id=%s and he.supervisor=%s and he.employee_type=%s',(supervisor_bonus,'Supervisor',month,'indirect',department_id,'t','indirect'))
        supervisor_noperformance_list = cr.fetchall() 
        
        cr.execute('select id, 100 as total_percentage, %s as total_amount, 0 as abnormal,100 as performance,0 as contribution,id,%s from hr_employee he where he.id not in (select employee_id from employee_performance where month=%s and type=%s) and department_id=%s and he.supervisor=%s and he.employee_type=%s',(worker_bonus,'Employee',month,'indirect',department_id,'f','indirect',))
        worker_noperformance_list = cr.fetchall()  
#         cr.execute('select id,(abnormal+performance+contribution)as total_percentage,(%s * ((abnormal+performance+contribution)/100)),abnormal,performance,contribution,employee_id,job_id from employee_performance where department_id=%s and job_id=%s',(worker_bonus,department_id,'Worker',)) 
#         worker_performance_list = cr.fetchall()
        
        total_performance_list = worker_performance_list +supervisor_performance_list+ supervisor_noperformance_list+worker_noperformance_list
        print 'performance list',total_performance_list
        hr_total_bonus_pool=self.pool.get('hr.indirect.productivity.bonus')
        if total_performance_list:
            self.write(cr, uid, [ids[0]], {'state': 'direct_confirm',})
            for result in total_performance_list:
                print 'result',result
                emp_id = result[0]
                print 'emp_id',emp_id
                value={'direct_id':bonus_val,
                       'employee_id':result[0],
                       'position':result[7],
                       'performance':result[4],
                       'abnormal':result[3],
                       'contribution':result[5],
                       'total_percent':result[1],
                       'total_amount':result[2],
                     }
                hr_total_bonus_pool.create(cr,uid,value,context=context)
#                 cr.execute('update hr_employee set productivity_bonus=%s where id=%s',(result[2],emp_id))
    
    def done(self, cr, uid, ids, context=None):
        print "done";   
        self.write(cr, uid, [ids[0]], {'state': 'done',})   
         
##=======================================Direct Productivity Bonus End===============================================##

class indirect_productivity_bonus(osv.osv):
        _name = "indirect.productivity.bonus"
        _description = "Indirect Productivity Bonus"
        _columns = {
                    'direct_id':fields.many2one('productivity.bonus.entry','Direct'),
                    'a_rate':fields.char('Achieve Rate',required=True),
                    'grade':fields.float('Productivity Bonus'),
                    'productivity_bounus':fields.float('.',required=True),
                    'department_id':fields.many2one('hr.department','Department'),
                    'detail_line_id':fields.one2many('hr.total.productivity.bonus','bonus_id','Total Productivity Bonus'),
                    }
        
        def onchange_achieve_rate(self,cr,uid,ids,achieve_rate,context=None):
            print 'onchange'
            result={}
            if target == 0.0:
                print 'No Week'
                return True
            else:
                cr.execute('select to_percentage from hite_rate where from_percentage<=0.0')
                to_percentage_list= cr.fetchone()
                to_percentage = to_percentage_list[0]
                print "To Percentage",to_percentage
                cr.execute('select from_percentage from hite_rate where to_percentage<=0.0')
                from_percentage_list = cr.fetchone()
                from_percentage= from_percentage_list[0]
                print "From Percentage",from_percentage
                if achieve_rate <= to_percentage:
                    cr.execute('select grade,productivity_bonus from hite_rate where from_percentage<=0.0 and to_percentage>=%s',(achieve_rate,))
                elif achieve_rate>=from_percentage :
                    cr.execute('select grade,productivity_bonus from hite_rate where from_percentage<=%s and to_percentage<=0.0',(achieve_rate,))
                else :
                    cr.execute('select grade,productivity_bonus from hite_rate where from_percentage<=%s and to_percentage>=%s',(achieve_rate,achieve_rate,))
                hit_rate_list = cr.fetchone()
                print 'hit rate list',hit_rate_list
                grade = hit_rate_list[0]
                productivity_bonus = hit_rate_list[1]                
                result.update({'grade':grade ,'productivity_bounus':productivity_bonus})
                return{'value' : result}