'''
Created on Aug 1, 2014

@author:  Khaing Myat
'''
from openerp.osv import fields, osv
from datetime import date, datetime
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
from dateutil.relativedelta import * 
class res_company(osv.osv):
    _inherit = 'res.company'
    _columns = {
                'over_target_amount': fields.float('Over Target Amount'),
                'worker_w1_hit_ration': fields.float('Worker W1 Ratio'),
                'worker_w2_hit_ration': fields.float('Worker W2 Ratio'),
                'worker_w3_hit_ration': fields.float('Worker W3 Ratio'),
                'worker_w4_hit_ration': fields.float('Worker W4 Ratio'),
                
                'factory_w1_hit_ration': fields.float('Factory W1 Ratio'),
                'factory_w2_hit_ration': fields.float('Factory W2 Ratio'),
                'factory_w3_hit_ration': fields.float('Factory W3 Ratio'),
                'factory_w4_hit_ration': fields.float('Factory W4 Ratio'),
    }
res_company()