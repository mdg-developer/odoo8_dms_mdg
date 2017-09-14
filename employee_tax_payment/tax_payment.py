'''
Created on Jun 12, 2015

@author: Administrator
'''
import time

from openerp import netsvc
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
from datetime import datetime
from dateutil.relativedelta import relativedelta
from operator import attrgetter
from openerp.osv import fields, osv

class tax_payment(osv.osv):
    _name = "tax.payment"
    _description = "Tax Payment Form"
    _order = "id desc"

    _columns = {
         'employee_id':fields.many2one('hr.employee','Employee', required=True),
         'description':fields.char('Description'),
         'amount':fields.float('Amount'),
         'from_date':fields.date('From Date'),
         'to_date':fields.date('To Date'),
         'job':fields.char('Job'),
         'date':fields.date('Date'),
    }
    
    def onchange_job(self,cr,uid,ids,employee_id,context=None):
        result={}
        print 'employee_id',employee_id
        if not employee_id:
            print 'No Product'
            return True
#         select *From product_template t ,product_product p where t.id=p.product_tmpl_id
        else: 
            cr.execute('select hd.name from hr_job hd where hd.id = (select job_id from hr_employee he where he.id = %s)',(employee_id,))
            price_rec = cr.fetchone()
            print 'price record',price_rec
            job = price_rec[0]
            result.update({'job':job})
            return{'value' : result}
   
  
   
    