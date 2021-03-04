from openerp.osv import osv, fields
from openerp import tools
from openerp.tools.translate import _
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
        'partner_latitude': fields.float('Geo Latitude', digits=(16, 5)),
        'partner_longitude': fields.float('Geo Longitude', digits=(16, 5)),
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
        'isexclusive':fields.boolean('Exclusive'),
        'ctax_registration_no':fields.char('C Tax Registration No'),
        'address_title':fields.char('Address Title'),
        'contact_note': fields.text('Note'),
    }
    _defaults = {
               'start_time':'01',
               'end_time':'01',
               'start_rate':'am',
               'end_rate':'pm',
               
    }
    
    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if isinstance(ids, (int, long)):
            ids = [ids]
        res = []
        for record in self.browse(cr, uid, ids, context=context):
            name = record.name
            if record.parent_id and not record.is_company:
                name = "%s, %s" % (record.parent_name, name)
            if context.get('show_address_only'):
                name = self._display_address(cr, uid, record, without_company=True, context=context)
            if context.get('show_address'):
                name = name + "\n" + self._display_address(cr, uid, record, without_company=True, context=context)
            name = name.replace('\n\n','\n')
            name = name.replace('\n\n','\n')
            if context.get('show_email') and record.email:
                name = "%s <%s>" % (name, record.email)
            if record.customer_code:
                name = "[" + record.customer_code + "] " + record.name
            res.append((record.id, name))            
        return res
    
    def name_search(self, cr, uid, name, args=None, operator='ilike',
                    context=None, limit=100):
        if not args:
            args = []
        args = args[:]
        ids = []
        if name:
            ids = self.search(cr, uid,
                              [('customer_code', '=like', name + "%")] + args,
                              limit=limit)
            if not ids:
                ids = self.search(cr, uid,
                                  [('name', operator, name)] + args,
                                  limit=limit)
        else:
            ids = self.search(cr, uid, args, context=context, limit=limit)
        return self.name_get(cr, uid, ids, context=context)
    
