from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
from datetime import datetime, timedelta
import calendar
from openerp import tools

OE_DATEFORMAT = "%Y-%m-%d"
class crm_case_section(osv.osv):
    _inherit = 'crm.case.section'

    def _get_total_invoice_data(self, cr, uid, ids, field_name, arg, context=None):
        res = dict(map(lambda x: (x, 0), ids))        
        for line in self.browse(cr, uid, ids, context=context):
            cr.execute("select count(id) from account_invoice where state not in ('draft','cancel') and section_id = %s and date_invoice = %s" , (line.id, line.date,))
            data = cr.fetchone()[0]
            res[line.id] = data
        return res        
    
    def _get_total_sku_data(self, cr, uid, ids, field_name, arg, context=None):
        res = dict(map(lambda x: (x, 0), ids))        
        # res = {}
        for line in self.browse(cr, uid, ids, context=context):            
            cr.execute("select count(st.id) from sales_target st ,sales_target_line stl where st.id=stl.sale_ids and stl.product_uom_qty !=0.0 and sale_team_id = %s and date= %s " , (line.id, line.date,))
            data = cr.fetchone()[0]
            res[line.id] = data
        return res       
    
    def _get_total_sku_invoice_percent(self, cr, uid, ids, field_name, arg, context=None):
        res = {}   
        data = 0
        total_invoice = 0
        total_sku = 0
        for line in self.browse(cr, uid, ids, context=context):
            total_invoice = line.total_invoice
            total_sku = line.total_sku
            if total_invoice != 0.0 and total_sku != 0.0:
                data = total_invoice / total_sku
            else:
                data = 0
            res[line.id] = data
        return res        
 
    def _get_total_rout_plan(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        data = 0
        if context is None:
            context = {}
        for line in self.browse(cr, uid, ids, context=context):
            cr.execute("select setting.partner_count from sale_plan_day_setting setting,sale_plan_day_sale_team_rel rel where rel.sale_plan_day_id=setting.id and rel.sale_team_id=%s  order by id desc" , (line.id,))
            partner_count = cr.fetchone()
            if partner_count:
                data = partner_count[0]
            else:
                data = 0
            res[line.id] = data
        return res       
 
    def _get_total_customer_visit(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        data = 0
        if context is None:
            context = {}
        for line in self.browse(cr, uid, ids, context=context):
            cr.execute(" select count(id) from customer_visit where sale_team_id=%s  and  (date+ '6 hour'::interval + '30 minutes'::interval)::date=%s" , (line.id, line.date,))
            data = cr.fetchone()[0]
            res[line.id] = data
        return res      

    def _get_total_pre_sale(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        data = 0
        if context is None:
            context = {}
        for line in self.browse(cr, uid, ids, context=context):
            cr.execute("select count(id) from sale_order where state ='draft' and section_id=%s and (date_order+ '6 hour'::interval + '30 minutes'::interval)::date=%s and pre_order ='t'" , (line.id, line.date,))
            pre_sale = cr.fetchone()[0]
            cr.execute("select count(id) from sale_order where state not in ('draft','cancel')  and section_id=%s and (date_order+ '6 hour'::interval + '30 minutes'::interval)::date=%s and pre_order ='f'" , (line.id, line.date,))
            sale_order = cr.fetchone()[0]
            if pre_sale != 0 and sale_order != 0:
                data = pre_sale / sale_order
            else:
                data = 0            
            res[line.id] = data
        return res         
    
    def _get_sale_today(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        data = 0
        if context is None:
            context = {}
        for line in self.browse(cr, uid, ids, context=context):
            cr.execute("select count(id) from sale_order where state not in ('draft','cancel')  and section_id=%s and (date_order+ '6 hour'::interval + '30 minutes'::interval)::date=%s and pre_order ='f'" , (line.id, line.date,))
            data = cr.fetchone()[0]
            res[line.id] = data
        return res
    
    def _get_sale_month(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        data = 0
        for line in self.browse(cr, uid, ids, context=context):
            team_date = line.date
            date_filter = datetime.strptime(team_date, OE_DATEFORMAT).date()                       
            month_begin = date_filter.replace(day=1)
            to_date = month_begin.replace(day=calendar.monthrange(month_begin.year, month_begin.month)[1]).strftime(tools.DEFAULT_SERVER_DATE_FORMAT)
            day_from = month_begin
            day_to = datetime.strptime(to_date, "%Y-%m-%d").date()
            nb_of_days = (day_to - day_from).days + 1
            cr.execute("select count(id) from hr_holidays_public_line where date between %s and %s", (day_from, day_to)) 
            day_count = cr.fetchone()
            if day_count:
                day_count = nb_of_days - day_count[0]
            else:
                day_count = nb_of_days
            cr.execute("select sum(amount_total) from sale_order where state not in ('draft','cancel')  and section_id=%s and (date_order+ '6 hour'::interval + '30 minutes'::interval)::date between %s and %s" , (line.id, day_from, day_to,))
            sale_value = cr.fetchone()
            if sale_value and sale_value[0] is not None:                
                sale_value = sale_value[0] / day_count
            else:
                sale_value = 0 / day_count                
            res[line.id] = sale_value
        return res  
    
    def _get_sale_confirm(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        data = 0
        if context is None:
            context = {}
        for line in self.browse(cr, uid, ids, context=context):
            cr.execute("select count(id) from sale_order where state ='progress' and section_id=%s and (date_order+ '6 hour'::interval + '30 minutes'::interval)::date=%s" , (line.id, line.date,))
            data = cr.fetchone()[0]
            res[line.id] = data
        return res  
    
    def _get_sale_work(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        data = 0
        for line in self.browse(cr, uid, ids, context=context):
            team_date = line.date
            date_filter = datetime.strptime(team_date, OE_DATEFORMAT).date()                       
            month_begin = date_filter.replace(day=1)
            to_date = month_begin.replace(day=calendar.monthrange(month_begin.year, month_begin.month)[1]).strftime(tools.DEFAULT_SERVER_DATE_FORMAT)
            day_from = month_begin
            day_to = datetime.strptime(to_date, "%Y-%m-%d").date()
            nb_of_days = (day_to - day_from).days + 1
            cr.execute("select count(id) from hr_holidays_public_line where date between %s and %s", (day_from, day_to)) 
            day_count = cr.fetchone()
            if day_count:
                day_count = nb_of_days - day_count[0]
            else:
                day_count = nb_of_days
            cr.execute("select count(id) from sale_order where state not in ('draft','cancel')  and section_id=%s and (date_order+ '6 hour'::interval + '30 minutes'::interval)::date between %s and %s" , (line.id, day_from, day_to,))
            sale_count = cr.fetchone()
            if sale_count:                
                sale_count = sale_count[0] / day_count
            else:
                sale_count = 0 / day_count
            res[line.id] = sale_count
        return res 
    
    def _get_sku_invoice(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        data = 0
        if context is None:
            context = {}
        for line in self.browse(cr, uid, ids, context=context):
            # cr.execute("   select count(st.id) from sales_target st ,sales_target_line stl where st.id=stl.sale_ids  and stl.product_uom_qty !=0.0 and sale_team_id =  %s and date= %s " ,( line.id,line.date,))
            # data=cr.fetchone()[0]
            res[line.id] = data
        return res
    
    def _get_product_invoice(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        data = 0
        if context is None:
            context = {}
        for line in self.browse(cr, uid, ids, context=context):
            # cr.execute("   select count(st.id) from sales_target st ,sales_target_line stl where st.id=stl.sale_ids  and stl.product_uom_qty !=0.0 and sale_team_id =  %s and date= %s " ,( line.id,line.date,))
            # data=cr.fetchone()[0]
            res[line.id] = data
        return res
    
    def _get_credit_sale(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        data = 0
        if context is None:
            context = {}
        for line in self.browse(cr, uid, ids, context=context):
            cr.execute(" select count(id) from sale_order where state not in ('draft','cancel') and payment_type='credit' and section_id=%s and (date_order+ '6 hour'::interval + '30 minutes'::interval)::date=%s" , (line.id, line.date,))
            data = cr.fetchone()[0]
            res[line.id] = data
        return res
  
    _columns = {
                'region': fields.char('Region'),
                'channel_ids':fields.many2many('sale.channel'),
                'code': fields.char('Code', size=15, required=True),

                'product_ids':fields.many2many('product.product'),
                'warehouse_id': fields.many2one('stock.warehouse', 'Car Warehouse', required=True),
                'location_id': fields.many2one('stock.location', ' Car Location', required=True),
                'issue_location_id': fields.many2one('stock.location', 'Issue location', required=True),
                'issue_warehouse_id': fields.many2one('stock.warehouse', 'Issue Warehouse', required=True),
                'temp_location_id': fields.many2one('stock.location', 'Temp location', required=True),
                'receiver':fields.char('Receiver'),
                'analytic_account_id': fields.many2one('account.analytic.account', 'Analytic Account'),
                'sale_channel_id':fields.many2many('sale.channel', 'sale_team_channel_rel', 'sale_team_id', 'sale_channel_id', string='Sale Channel'),
                'demarcation_ids':fields.many2many('sale.demarcation'),
                'van_id':fields.char('Vehicle No'),
                'pricelist_ids':fields.many2many('product.pricelist'),
                'vehicle_id':fields.many2one('fleet.vehicle', 'Vehicle No'),
                'main_group_id': fields.many2many('product.maingroup'),
                                'date':fields.date('Date'),
                'delivery_team_id': fields.many2one('crm.case.section', 'Delivery Team'),
                'date':fields.date('Date'),
                'total_invoice': fields.function(_get_total_invoice_data, digits_compute=dp.get_precision('Product Price'),
                type='float',
                string='Total Invoice'),
                'date':fields.date('Date'),
                'total_sku': fields.function(_get_total_sku_data, digits_compute=dp.get_precision('Product Price'),
                type='float',
                string='Total SKU'),
                 'total_sku_inv': fields.function(_get_total_sku_invoice_percent, digits_compute=dp.get_precision('Product Price'),
                type='float',
                string='Invoice/SKU %'),
                'total_rout_plan': fields.function(_get_total_rout_plan, digits_compute=dp.get_precision('Product Price'),
                type='float', readonly=True,
                string='Total Rout Plan'),
                  'total_customer_visit': fields.function(_get_total_customer_visit, digits_compute=dp.get_precision('Product Price'),
                type='float', readonly=True,
                string='Total Customer Visit'),
                    'total_pre_sale': fields.function(_get_total_pre_sale, digits_compute=dp.get_precision('Product Price'),
                type='float', readonly=True,
                string='Pre Order/Sale Order'),
               'sale_value': fields.function(_get_sale_today, digits_compute=dp.get_precision('Product Price'),
                type='float', readonly=True,
                string='Sale Today'),
                'sale_total_month': fields.function(_get_sale_month, digits_compute=dp.get_precision('Product Price'),
                type='float', readonly=True,
                string='Monthly Sale'),
                'sale_confirm_today': fields.function(_get_sale_confirm, digits_compute=dp.get_precision('Product Price'),
                type='float', readonly=True,
                string='Sale Confirm Today'),
                'sale_work_day': fields.function(_get_sale_work, digits_compute=dp.get_precision('Product Price'),
                type='float', readonly=True,
                string='Sale WorkDay'),
                'sku_invoice': fields.function(_get_sku_invoice, digits_compute=dp.get_precision('Product Price'),
                type='float', readonly=True,
                string='SKU/Invoice'),
                'product_invoice': fields.function(_get_product_invoice, digits_compute=dp.get_precision('Product Price'),
                type='float', readonly=True,
                string='Daily Average'),
                'credit_sale': fields.function(_get_credit_sale, digits_compute=dp.get_precision('Product Price'),
                type='float', readonly=True,
                string='Credit Outstanding'),
                'price_list_line': fields.one2many('price.list.line', 'team_id', 'Price List', copy=True),
                'branch_id':fields.many2one('res.branch', 'Branch'),
                'allow_foc':fields.boolean('Allow FOC'),
                'allow_tax':fields.boolean('Allow Tax'),
                'default_division':fields.many2one('res.country.state','Division'),
                'normal_return_location_id': fields.many2one('stock.location', 'Normal Return location', required=True),
                'exp_location_id': fields.many2one('stock.location', 'Expiry location', required=True),
                'near_exp_location_id': fields.many2one('stock.location', 'Near Expiry location', required=True),
                'damage_location_id': fields.many2one('stock.location', 'Damage location', required=True),
                'fresh_stock_not_good_location_id': fields.many2one('stock.location', 'Fresh stock minor damage location', required=True),
                'optional_issue_location_id': fields.many2one('stock.location', 'Optional Issue Location'),
                'is_supervisor':fields.boolean('Is Supervisor',default=False),
                'supervisor_team': fields.many2one('crm.case.section', 'Supervisor Team'),                
        }
    _sql_constraints = [
        ('code_uniq', 'unique (code)', 'The code of the sales team must be unique !')
    ]    
    _defaults = {
        'date': fields.datetime.now,
        'allow_foc':False,
         'allow_tax':False,

        }   
crm_case_section()
