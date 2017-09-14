from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import datetime,date, timedelta
import calendar

class attendance_data_import(osv.osv):

    _inherit = "attendance.data.import"    
    _columns = {
        'three_day_absent': fields.boolean('Three Days Absent'),
    }

    def threedays_absent(self, cr,uid,context=None):
        att_data_pool = self.pool.get("attendance.data.import")
        start_date = datetime.now().date().replace(month=1, day=1)    
        end_date = datetime.now().date().replace(month=12, day=31)
#         start_date=datetime.today()
#         start_date = start_date.replace(day=1)
#         _, days_in_month = calendar.monthrange(start_date.year, start_date.month)
#         end_date = start_date + timedelta(days=days_in_month)
        date_list=[];
        final_list=[];
        cr.execute("""SELECT distinct employee_id FROM attendance_data_import where absent='t' and date::date between %s and %s""",(start_date, end_date,))
        emp_res = cr.dictfetchall()
        date_ids=[]
        for e in emp_res:
            attemp_ids = att_data_pool.search(cr, uid, [('absent', '=', 't'), ('employee_id', '=', e['employee_id']), ], context=context)        
            cr.execute("""select date from attendance_data_import where id in %s Group by date Having count(date) =2
                        order by date""", (tuple(attemp_ids),))
            
            res_date = cr.dictfetchall()
              
            for d in res_date:
                if d['date'] not in date_list:
                    for i in range(0,3):                    
                        date = datetime.strptime(d['date'], "%Y-%m-%d")   
                        if i > 0:
                            date=date + timedelta(days=i)
                        date_final=date.date()
                        date_string = date_final.strftime('%Y-%m-%d')
                        date_list.append(date_string)
                        i=i+1
                          
                    cr.execute("""SELECT id FROM attendance_data_import 
                                where date in %s and absent='t' and employee_id=%s""", (tuple(date_list), e['employee_id']))
                    date_ids = cr.dictfetchall()          
  
                    if len(date_ids) == 6:
                        final_list.extend(date_ids)
                        del date_ids[:]
                        del date_list[:]
                    else:                        
                        del date_ids[:]
                        del date_list[:]
        final_ids=[]
        for f in final_list:
            final_ids.append(f['id'])                     
        self.write(cr, uid, final_ids, {'three_day_absent':True})
        print 'Success ...........................................'
        return {'absent_ids':final_ids}  	
#     _columns = {
#         'absent_ids': fields.function(threedays_absent, type='integer', string='Absent'),
#     }	
attendance_data_import()   



    