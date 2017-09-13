from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
from datetime import datetime, timedelta
import calendar
from openerp import tools

OE_DATEFORMAT = "%Y-%m-%d"
class crm_case_section(osv.osv):
    _inherit = 'res.partner'
  
    _columns = {
        'iso': fields.selection([('yes','Yes'),('no','No'),('n/a','N/A')],'ISO'),       
        'import_fname_iso': fields.char('Filename', size=256),
        'import_file_iso':fields.binary('File'),
        'certify_product': fields.selection([('yes','Yes'),('no','No'),('n/a','N/A')],'Product Certification'),
        'import_fname_certify_product': fields.char('Filename', size=256),
        'import_file_certify_product':fields.binary('File'),  
        'legal_status': fields.boolean('Legal Status of your company(company registration)'), 
        'iso_certificate': fields.boolean('ISO 9001 certificate'), 
        'product_certificate': fields.boolean('Any product certification?Product Certificate.'), 
        'product_sample': fields.boolean('Product Sample'), 
        'reliable': fields.integer('Reliable'),
        'price': fields.integer('Price'),
        'delivery': fields.integer('Delivery'),
        'flexibility': fields.integer('Flexibility'),
        'communication': fields.integer('Communication'),
        'after_services': fields.integer('After Services'),
        'total_marks': fields.integer('Total Marks', readonly=True),
        #'remark': fields.char('Remark'),
        'remark': fields.selection([
                               ('accepted', 'Accepted'),
                               ('unaccepted', 'Unaccepted'),                           
                            ], 'Remark'),
        'is_distributor': fields.boolean('Is Distributor'), 
        'distributor_target_amount':fields.float('Distributor Target Amount'),
        }
    
    
    
    def onchange_calculate_total_marks(self, cr, uid, ids,reliable,price,delivery,flexibility,communication,after_services,context=None):       
        total = reliable+price+delivery+flexibility+communication+after_services
        if total < 12:
            remark = 'unaccepted'
        else:
            remark = 'accepted'
        result = {'value': {
            'total_marks': total,
            'remark':remark,
        }}
        return result 