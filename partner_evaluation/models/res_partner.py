from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
from datetime import datetime, timedelta
import calendar
from openerp import tools

OE_DATEFORMAT = "%Y-%m-%d"
class crm_case_section(osv.osv):
    _inherit = 'res.partner'
    
    def _get_res_invoice_amount(self, cr, uid, ids, field_name, arg, context=None):
        res = dict(map(lambda x: (x, 0), ids))
        amount_total = 0.0
        currentYear = datetime.now().year
        print 'currentYearcurrentYear', currentYear
        for data in self.browse(cr, uid, ids, context=context):
            cr.execute("select COALESCE(sum(amount_total),0) from account_invoice where partner_id =%s and state !='cancel' and EXTRACT(YEAR FROM date_invoice)=%s", (data.id, currentYear,))
            amount_total = cr.fetchone()
            if amount_total:
                amount_total = amount_total[0]
            else:
                amount_total = 0.0
            cr.execute("update res_partner set  res_total_amount =%s where id=%s ", (amount_total, data.id,))
                
            res[data.id] = amount_total
        return res 
  
    _columns = {
        'iso': fields.selection([('yes', 'Yes'), ('no', 'No'), ('n/a', 'N/A')], 'ISO'),
        'import_fname_iso': fields.char('Filename', size=256),
        'import_file_iso':fields.binary('File'),
        'certify_product': fields.selection([('yes', 'Yes'), ('no', 'No'), ('n/a', 'N/A')], 'Product Certification'),
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
        # 'remark': fields.char('Remark'),
        'remark': fields.selection([
                               ('accepted', 'Accepted'),
                               ('unaccepted', 'Unaccepted'),
                            ], ''),
        'is_distributor': fields.boolean('Distributor'),
        'distributor_target_amount':fields.float('Distributor Target Amount'),
        'position': fields.char('Position'),
        'service_offered': fields.char('Products or Services Offered',),
        'major_customers': fields.char('Major Customers'),
        'approved_evalution': fields.boolean('Approved'),
        'dean_customer': fields.boolean('Dean'),
        'bw_customer': fields.boolean('BW'),
        'function_res_total_amount':fields.function(_get_res_invoice_amount,
        type='float', readonly=True,
        string='Total Invoice Amount'),
        'res_total_amount': fields.float(readonly=True,
        string='Total Invoice Amount'),
        'inter_company': fields.boolean('Inter Company', default=False),
        'property_account_payable': fields.property(
            type='many2one',
            relation='account.account',
            string="Account Payable",
            domain="[('type', '=', 'payable')]",
            help="This account will be used instead of the default one as the payable account for the current partner",
            required=True),
        'property_account_receivable': fields.property(
            type='many2one',
            relation='account.account',
            string="Account Receivable",
            domain="[('type', '=', 'receivable')]",
            help="This account will be used instead of the default one as the receivable account for the current partner",
            required=True),
        
        }
    
    _defaults = {
        'is_distributor': False,
        }
        
    
    
    def onchange_calculate_total_marks(self, cr, uid, ids, reliable, price, delivery, flexibility, communication, after_services, context=None):  
        if reliable > 3 or reliable < 0:
             raise osv.except_osv(('Error!'), ('Reliable must be greater than 0 and less than 3!'))
        if price > 3 or price < 0:
           raise osv.except_osv(('Error!'), ('Price must be greater than 0 and less than 3!'))            
        if delivery > 3 or delivery < 0: 
            raise osv.except_osv(('Error!'), ('Delivery must be greater than 0 and less than 3!'))
        if flexibility > 3 or flexibility < 0:
            raise osv.except_osv(('Error!'), ('Flexibility must be greater than 0 and less than 3!'))
        if communication > 3 or communication < 0: 
           raise osv.except_osv(('Error!'), ('Communication must be greater than 0 and less than 3!'))
        if after_services > 3 or after_services < 0:
          raise osv.except_osv(('Error!'), ('After Services must be greater than 0 and less than 3!'))
       
        total = reliable + price + delivery + flexibility + communication + after_services
        if total < 12:
            remark = 'unaccepted'
            approved = False
        else:
            remark = 'accepted'
            approved = True
        
        result = {'value': {
            'total_marks': total,
            'remark':remark,
            'approved_evalution':approved,
            'reliable' : reliable,
            'price' : price,
            'delivery' : delivery,
            'flexibility' : flexibility,
            'communication' : communication,
            'after_services' : after_services,
        }}
        return result 
