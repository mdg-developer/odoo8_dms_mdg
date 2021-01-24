from openerp.osv import osv, fields
from openerp import tools
from openerp.tools.translate import _
import logging
TIME_SELECTION = [
        ('01', '01'),
        ('02', '02'),
        ('03', '03'),
        ('04', '04'),
        ('05', '05'),
        ('06', '06'),
        ('07', '07'),
        ('08', '08'),
         ('09', '09'),
         ('10', '10'),
         ('11', '11'),
        ('12', '12'),
         ('13', '13'),
         ('14', '14'),
          ('15', '15'),
          ('16', '16'),
         ('17', '17'),
         ('18', '18'),
         ('19', '19'),
         ('20', '10'),
        ('21', '21'),
        ('22', '22'),
        ('23', '23'),
        ('24', '24'),
    ]
class res_partner(osv.osv):
    _inherit = "res.partner"
    _columns = {
                 'is_bank':fields.boolean('Bank Transfer'),
                'is_cheque':fields.boolean('Cheque'),
                'is_tax':fields.boolean('WithHolding Tax Allow'),
        'partner_latitude': fields.float('Geo Latitude', digits=(16, 5), readonly=True),
        'partner_longitude': fields.float('Geo Longitude', digits=(16, 5), readonly=True),
        'date_localization': fields.date('Geo Localization Date'),
        'contact_note': fields.text('Note'),
       'credit_allow':fields.boolean('Credit Approved'),
       'is_consignment':fields.boolean('Consignment'),
         'gain_account_id': fields.property(
            type='many2one',
            relation='account.account',
            string="Gain Account",
        #    domain="[('type', '=', 'receivable')]",
          ),
            'loss_account_id': fields.property(
            type='many2one',
            relation='account.account',
            string="Loss Account",
           # domain="[('type', '=', 'receivable')]",
          ),
         'start_time':fields.selection(TIME_SELECTION, 'Start Time'),
         'start_rate':fields.selection([('am', 'AM'), ('pm', 'PM')], string="Rate"),
         'end_time':fields.selection(TIME_SELECTION, 'End Time'),
         'end_rate':fields.selection([('am', 'AM'), ('pm', 'PM')], string="Rate"),
         'mon':fields.boolean('MON'),
         'tue':fields.boolean('TUE'),
         'wed':fields.boolean('WED'),
         'thur':fields.boolean('THURS'),
         'fri':fields.boolean('FRI'),
         'sat':fields.boolean('SAT'),
         'sun':fields.boolean('SUN'),
     'section_id':fields.many2many('crm.case.section', 'sale_team_customer_rel', 'partner_id', 'sale_team_id', string='Sales Team'),
     'is_exclusive':fields.boolean('Exclusive'),
     'collection_team':fields.many2one('crm.case.section','Collection Team'),
     'address_title':fields.char('Address Title'),
    }
    _defaults = {
               'start_time':'01',
               'end_time':'01',
               'start_rate':'am',
               'end_rate':'pm',
               'is_tax':False,
    }
    
    def swap_contact(self, cr, uid, ids, val, context=None):
        
        tmp_vals = {}
        customer_vals = {}
        for res in self.browse(cr, uid, ids, context=context):
            
            if res.parent_id:
                                
                if res.image:
                    #copy contact address into tmp vals
                    tmp_vals['image']= res.image   
                    #assign customer address into contact address     
                    res.image = res.parent_id.image     
                    #assign contact address into customer address
                    customer_vals['image']= tmp_vals['image']
                    
                if res.street:
                    tmp_vals['street']= res.street
                    res.street = res.parent_id.street
                    customer_vals['street']= tmp_vals['street']
                    
                if res.street2:                    
                    tmp_vals['street2']= res.street2
                    res.street2 = res.parent_id.street2
                    customer_vals['street2']= tmp_vals['street2']
                    
                if res.township:
                    tmp_vals['township']= res.township.id or None
                    res.township = res.parent_id.township.id or None
                    customer_vals['township']= tmp_vals['township']
                    
                if res.city:
                    tmp_vals['city']= res.city.id or None
                    res.city = res.parent_id.city.id or None
                    customer_vals['city']= tmp_vals['city']
                    
                if res.state_id:
                    tmp_vals['state_id']= res.state_id.id or None
                    res.state_id = res.parent_id.state_id.id or None
                    customer_vals['state_id']= tmp_vals['state_id']
                    
                if res.zip:
                    tmp_vals['zip']= res.zip
                    res.zip = res.parent_id.zip
                    customer_vals['zip']= tmp_vals['zip']
                    
                if res.country_id:
                    tmp_vals['country_id']= res.country_id.id or None
                    res.country_id = res.parent_id.country_id.id or None
                    customer_vals['country_id']= tmp_vals['country_id']
                    
                if res.mobile:
                    tmp_vals['mobile']= res.mobile or None
                    res.mobile = res.parent_id.mobile or None
                    customer_vals['mobile']= tmp_vals['mobile']
                
                if res.phone:
                    tmp_vals['phone']= res.phone or None
                    res.phone = res.parent_id.phone or None
                    customer_vals['phone']= tmp_vals['phone']
                    
                if res.name:
                    tmp_vals['name']= res.name or None
                    res.name = res.parent_id.temp_customer or 'null'  
                    logging.warning("Check tmp vals name: %s", tmp_vals['name'])                       
                    customer_vals['temp_customer']= tmp_vals['name']
                    
                if res.shop_name:
                    tmp_vals['shop_name']= res.shop_name or None
                    res.shop_name = res.parent_id.shop_name or None
                    customer_vals['shop_name']= tmp_vals['shop_name']
                    
                if res.gender:
                    tmp_vals['gender']= res.gender or None
                    res.gender = res.parent_id.gender or None
                    customer_vals['gender']= tmp_vals['gender']
                    
                if res.birthday:
                    tmp_vals['birthday']= res.birthday or None
                    res.birthday = res.parent_id.birthday or None
                    customer_vals['birthday']= tmp_vals['birthday']
                
                if res.outlet_type:
                    tmp_vals['outlet_type']= res.outlet_type.id or None
                    res.outlet_type = res.parent_id.outlet_type.id or None
                    customer_vals['outlet_type']= tmp_vals['outlet_type']
                    
                self.pool.get('res.partner').write(cr, uid, res.parent_id.id, customer_vals, context=context)                       
                return True
                