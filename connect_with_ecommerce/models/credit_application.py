from openerp.osv import fields, osv
import time
import datetime
from openerp import models, api, _
class credit_application(osv.osv):
    _name = 'credit.application'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _columns = {
                    'name': fields.char('Company Registration Number', required=True),
                    'date_of_application': fields.date('Date of Application'),                    
                    'sole_proprietor': fields.boolean('Sole Proprietor', default=False),
                    'corporation': fields.boolean('Corporation', default=False),
                    'others': fields.boolean('Others', default=False),
                    'date_received': fields.date('Date Received'),                    
                    'registration_date': fields.date('Registration Date',default=datetime.datetime.today()), 
                    'number_of_employees': fields.integer('Number of Employees'),
                    'company_register_name': fields.char('Company Register Name'),
                    'trade_brand_name': fields.char('Trade Name/Brand Name'),
                    'company_street': fields.char('Street'),
                    'company_street2': fields.char('Street2'),      
                    'company_city_id': fields.many2one('res.city', 'City'),
                    'company_state_id': fields.many2one("res.country.state", 'State'),
                    'company_country_id': fields.many2one('res.country', 'Country'),       
                    'company_township_id':fields.many2one('res.township','Township'),
                    'company_zip': fields.char('Zip', size=24),
                    'company_phone': fields.char('Phone'), 
                    'residence_street': fields.char('Street'),
                    'residence_street2': fields.char('Street2'),      
                    'residence_city_id': fields.many2one('res.city', 'City'),
                    'residence_state_id': fields.many2one("res.country.state", 'State'),
                    'residence_country_id': fields.many2one('res.country', 'Country'),       
                    'residence_township_id':fields.many2one('res.township','Township'),
                    'residence_zip': fields.char('Zip', size=24),
                    'residence_phone': fields.char('Phone'),
                    'company_nrc': fields.char("Customer's NRC(For Individual/Sole Propprietor)"), 
                    'customer_email': fields.char('Customer Email Address'),
                    'phone': fields.char('Phone'),
                    'mobile': fields.char('Mobile'),
                    'business_phone': fields.boolean('Business', default=False),
                    'residential_phone': fields.boolean('Residential', default=False),
                    'viber': fields.boolean('Viber', default=False),
                    'wechat': fields.boolean('Wechat', default=False),
                    'whatsapp': fields.boolean('WhatsApp', default=False),
                    'owner': fields.char('Owner/Managing Director'),
                    'owner_email': fields.char('E-mail Address'),
                    'owner_phone': fields.char('Telephone Number'),
                    'owner_mobile': fields.char('Mobile Phone'),
                    'purchasing_manager': fields.char('Purchasing Manager/In-Charge'),
                    'pm_email': fields.char('E-mail Address'),
                    'pm_phone': fields.char('Telephone Number'),
                    'pm_mobile': fields.char('Mobile Phone'),
                    'operation_manager': fields.char('Operations Manager/In-Charge'),
                    'om_email': fields.char('E-mail Address'),
                    'om_phone': fields.char('Telephone Number'),
                    'om_mobile': fields.char('Mobile Phone'),
                    'finance_manager': fields.char('Finance Manager/In-Charge'),
                    'fm_email': fields.char('E-mail Address'),
                    'fm_phone': fields.char('Telephone Number'),
                    'fm_mobile': fields.char('Mobile Phone'),
                    'cash': fields.boolean('Cash', default=False),
                    'bank': fields.boolean('Bank Deposit/Transfer', default=False),
                    'company_cheque': fields.boolean('Company Cheque', default=False),
                    'other_specify': fields.char('Other(Specify)'),
                    'date_of_opening': fields.date('Date of Account Opening/Number of Years Banking'),
                    'bank_name': fields.char('Bank Name'),
                    'bank_register_street': fields.char('Street'),
                    'bank_register_street2': fields.char('Street2'),      
                    'bank_register_city_id': fields.many2one('res.city', 'City'),
                    'bank_register_state_id': fields.many2one("res.country.state", 'State'),
                    'bank_register_country_id': fields.many2one('res.country', 'Country'),       
                    'bank_register_township_id':fields.many2one('res.township','Township'),'bank_register_street': fields.char('Street'),
                    'bank_register_zip': fields.char('Zip', size=24),
                    'bank_officer': fields.char('Bank Officer/Manager'),
                    'bank_officer_email': fields.char('Email Address'),
                    'bank_officer_phone': fields.char('Telephone Number'),
                    'bank_officer_mobile': fields.char('Mobile Phone'),
                    'customer_id': fields.many2one('res.partner', 'Customer', track_visibility='onchange'),
                    'appiled_amount': fields.float('Appiled Amount',track_visibility='onchange'),
                    'approved_amount': fields.float('Approved Amount',track_visibility='onchange'),
                    'state': fields.selection([('draft', 'Draft'),('approved', 'Approved')],'Status', required=True, readonly="1", track_visibility='onchange', default='draft'),
                    'effective_date': fields.date('Effective Date', track_visibility='onchange'),
     
               }

    @api.multi
    def set_to_draft(self):
        update = self.write({
            'state': 'draft',
            'approved_amount': False,
            'effective_date': False,            
        })
        print("update",update)
        return update


    @api.multi
    def action_confirm(self):
        module = __name__.split('addons.')[1].split('.')[0]
        view = self.env.ref('%s.view_credit_application_approval_form' % module)
        return {
            'name': _('Approve'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'credit.application.approval',
            'view_id': view.id,
            'target': 'new',
            'type': 'ir.actions.act_window',
        }

    def create_from_woo(self, cr, uid, ids, vals, context=None):
        country_obj = self.pool.get('res.country')
        township_obj = self.pool.get('res.township')
        city_obj = self.pool.get('res.city')
        state_obj = self.pool.get('res.country.state')
        partner_obj = self.pool.get('res.partner')

        #Company
        if vals.get("company_country_id"):
            country_value = country_obj.search(cr, uid, [('name', '=ilike', vals['company_country_id'])], context=context)
            if country_value:
                country = country_obj.browse(cr, uid, country_value, context=context)
                vals['company_country_id'] = country.id
        if vals.get("company_state_id"):
            state_value = state_obj.search(cr, uid, [('name', '=ilike', vals['company_state_id'])], context=context)
            if state_value:
                state = state_obj.browse(cr, uid, state_value, context=context)
                vals['company_state_id'] = state.id
        if vals.get("company_city_id"):
            city_value = city_obj.search(cr, uid, [('name', '=ilike', vals['company_city_id'])], context=context)
            if city_value:
                city = city_obj.browse(cr, uid, city_value, context=context)
                vals['company_city_id'] = city.id
        if vals.get("company_township_id"):
            township_value = township_obj.search(cr, uid, [('name', '=ilike', vals['company_township_id'])], context=context)
            if township_value:
                township = township_obj.browse(cr, uid, township_value, context=context)
                vals['company_township_id'] = township.id
        
        #Customer
        if vals.get('customer_id'):
            customer_value = partner_obj.search(cr, uid, [('customer_code','=',vals['customer_id'])], context=context)
            if customer_value:
                customer = partner_obj.browse(cr, uid, customer_value, context=context)
                vals['customer_id'] = customer.id
        
        # Residence
        if vals.get("residence_country_id"):
            country_value = country_obj.search(cr, uid, [('name', '=ilike', vals['residence_country_id'])], context=context)
            if country_value:
                country = country_obj.browse(cr, uid, country_value, context=context)
                vals['residence_country_id'] = country.id
        if vals.get("residence_state_id"):
            state_value = state_obj.search(cr, uid, [('name', '=ilike', vals['residence_state_id'])], context=context)
            if state_value:
                state = state_obj.browse(cr, uid, state_value, context=context)
                vals['residence_state_id'] = state.id
        if vals.get("residence_city_id"):
            city_value = city_obj.search(cr, uid, [('name', '=ilike', vals['residence_city_id'])], context=context)
            if city_value:
                city = city_obj.browse(cr, uid, city_value, context=context)
                vals['residence_city_id'] = city.id
        if vals.get("residence_township_id"):
            township_value = township_obj.search(cr, uid, [('name', '=ilike', vals['residence_township_id'])], context=context)
            if township_value:
                township = township_obj.browse(cr, uid, township_value, context=context)
                vals['residence_township_id'] = township.id

        # Bank
        if vals.get("bank_register_country_id"):
            country_value = country_obj.search(cr, uid, [('name', '=ilike', vals['bank_register_country_id'])], context=context)
            if country_value:
                country = country_obj.browse(cr, uid, country_value, context=context)
                vals['bank_register_country_id'] = country.id
        if vals.get("bank_register_state_id"):
            state_value = state_obj.search(cr, uid, [('name', '=ilike', vals['bank_register_state_id'])], context=context)
            if state_value:
                state = state_obj.browse(cr, uid, state_value, context=context)
                vals['bank_register_state_id'] = state.id
        if vals.get("bank_register_city_id"):
            city_value = city_obj.search(cr, uid, [('name', '=ilike', vals['bank_register_city_id'])], context=context)
            if city_value:
                city = city_obj.browse(cr, uid, city_value, context=context)
                vals['bank_register_city_id'] = city.id
        if vals.get("bank_register_township_id"):
            township_value = township_obj.search(cr, uid, [('name', '=ilike', vals['bank_register_township_id'])], context=context)
            if township_value:
                township = township_obj.browse(cr, uid, township_value, context=context)
                vals['bank_register_township_id'] = township.id                


        result = self.create(cr, uid, vals, context=context)
        return result


class credit_application_approval(models.TransientModel):
    _name = 'credit.application.approval'

    _columns = {
        'name': fields.char('Company Registration Number', required=True),
        'customer_id': fields.many2one('res.partner',string='customer'),
        'appiled_amount': fields.float('Appiled Amount'),
        'approved_amount': fields.float('Approved Amount'),
        'effective_date': fields.date('Effective Date'),
    }

    @api.model
    def default_get(self, fields):
        res = super(credit_application_approval, self).default_get(fields)
        credit_app_ids = self.env.context.get('active_ids', [])
        data = {}
        credit_app = self.env['credit.application'].search([('id','=', credit_app_ids[0])])
        data['name'] = credit_app.name
        data['customer_id'] = credit_app.customer_id.id if credit_app.customer_id else False
        data['appiled_amount'] = credit_app.appiled_amount
        data['approved_amount'] = credit_app.approved_amount
        data['effective_date'] = credit_app.effective_date
        res.update(data)
        return res

    @api.multi
    def confirm_credit_application(self):
        credit_app_ids = self.env.context.get('active_ids', [])
        credit_app = self.env['credit.application'].search([('id','=', credit_app_ids[0])])
        credit_app.write({
            'state': 'approved',
            'approved_amount': self.approved_amount,
            'effective_date': self.effective_date,
        })
        return True
    