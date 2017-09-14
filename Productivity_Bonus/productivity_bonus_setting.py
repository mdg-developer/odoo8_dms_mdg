from openerp import tools
from openerp.osv import fields, osv
from openerp import workflow


class productivity_bonus(osv.osv):
    _name = "productivity.bonus"
    _description = "Productivity Bonus Setting"

    _columns = {
                'date':fields.date('Date'),
                'name':fields.selection([('direct','Direct'),
                                       ('indirect','InDirect'),
                                        ],'Type',required=True),
                'rate_line_ids': fields.one2many('hite.rate', 'rate_id', 'Hit Rate Inputs'),    
                'bc_line_ids': fields.one2many('bc.grade', 'bc_line_id', 'B/C Grade Inputs'),
                            
                }
    

class hite_rate(osv.osv):
    _name = 'hite.rate'
    _description = "Hit Rate"
     
    _columns = {
                'rate_id':fields.many2one('productivity.bonus', 'Hit Rate')  ,
                'department_id':fields.many2one('hr.department','Department'),
#                 'job_id':fields.many2one('hr.job','Employee Type',required=True),
                'emp_type':fields.selection([('supervisor','Supervisor'),
                                       ('employee','Employee'),
                                        ],'Employee Type',required=True),
                'from_percentage':fields.float('From Percentage(%)',required=True),
                'to_percentage':fields.float('To Percentage(%)',required=True),
#                 'week_id':fields.many2one('setting.week', 'Week', required=True),
                'grade':fields.char('Grade',required=True),
                'productivity_bonus':fields.float('Amount',required=True),
                'hite_rate_id':fields.many2one('setting.productivity','Hit Rate'),
                }
                
                
class bc_grade(osv.osv):
    _name = 'bc.grade'
    _description = "B/C Grade"
     
    _columns = {
               'from_percentage':fields.float('From Percentage(%)',required=True),
               'to_percentage':fields.float('To Percentage(%)',required=True),
               'bc_amount':fields.float('B/C Grade Amount',required=True),
               'bc_line_id':fields.many2one('productivity.bonus', 'B/C Grade'), 
               'emp_type':fields.selection([('supervisor','Supervisor'),
                                       ('employee','Employee'),
                                        ],'Employee Type',required=True),                           
                }
                
                
# class abnormal(osv.osv):
#     _name = 'abnormal'
#     _description = "Abnormal"
#      
#     _columns = {
# 
#                 'abnormal_id':fields.many2one('productivity.bonus', 'Abnormal')  ,
#                 'department_id':fields.many2one('hr.department','Department', required=True),
#                 'hite_rate_id':fields.many2one('setting.productivity','Value', required=True) ,
#                 }
#                   
                  
# class personal_performance(osv.osv):
#     _name = 'personal.performance'
#     _description = "Personal Performance"
#      
#     _columns = {
# 
#                 'performance_id':fields.many2one('productivity.bonus', 'Personal Performance')  ,
#                 'employee_id':fields.many2one('hr.employee','Employee', required=True),
#                 'hite_rate_id':fields.many2one('setting.productivity','Value', required=True) ,
#                 }              
                
        
                  
# class over_target(osv.osv):
#     _name = 'over.target'
#     _description = "Over Target"
#      
#     _columns = {
# 
#                 'target_id':fields.many2one('productivity.bonus', 'Over Target'),
#                 'employee_id':fields.many2one('hr.employee','Employee Type', required=True),
#                 'week_id':fields.many2one('setting.week', 'Weekly'),
#                 'percentage':fields.char('Percentage',required=True),
#                 'grade':fields.char('Grade',required=True),
#                 'amount':fields.char('Amount'),
#                 }   