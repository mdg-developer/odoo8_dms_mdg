from openerp.osv import fields, osv
from openerp.tools.translate import _
import time
import math
from datetime import datetime
from datetime import datetime,date, timedelta
import calendar
#import datetime

class hr_payslip(osv.osv):

    _inherit = 'hr.payslip'
    
    def saturday_count(self, cr, uid,context=None):
        cr.execute("update attendance_data_import set normal = 1,realtime =1  where timetable ='Morning' and extract('ISODOW' FROM date)= 6 and EXTRACT(MONTH FROM  date) = EXTRACT(month FROM CURRENT_DATE) ") 
        cr.execute("update attendance_data_import set normal = 0,realtime =0  where timetable ='Afternoon' and extract('ISODOW' FROM date)= 6 and EXTRACT(MONTH FROM  date) = EXTRACT(month FROM CURRENT_DATE)")
        cr.execute("update attendance_data_import set realtime =0.0  where timetable ='Morning' and absent = true and extract('ISODOW' FROM date)= 6 and EXTRACT(MONTH FROM  date) = EXTRACT(month FROM CURRENT_DATE)")
        cr.execute("update attendance_data_import set realtime =0.0  where timetable ='Afternoon' and absent = true and extract('ISODOW' FROM date)= 6   and EXTRACT(MONTH FROM  date) = EXTRACT(month FROM CURRENT_DATE)")

   
   
    