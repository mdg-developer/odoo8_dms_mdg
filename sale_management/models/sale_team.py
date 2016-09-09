from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp

class crm_case_section(osv.osv):
    _inherit = 'crm.case.section'

    def _get_total_invoice_data(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        if context is None:
            context = {}
        for line in self.browse(cr, uid, ids, context=context):
            cr.execute("select count(id) from account_invoice  where state not in ('draft','cancel') and section_id = %s and date_due = %s" , (line.id, line.date,))
            data = cr.fetchone()[0]
            res[line.id] = data
        return res        
    
    def _get_total_sku_data(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        if context is None:
            context = {}
        for line in self.browse(cr, uid, ids, context=context):
            cr.execute("   select count(st.id) from sales_target st ,sales_target_line stl where st.id=stl.sale_ids  and stl.product_uom_qty !=0.0 and sale_team_id =  %s and date= %s " , (line.id, line.date,))
            data = cr.fetchone()[0]
            res[line.id] = data
        return res       
    def _get_total_sku_invoice_percent(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        data = 0
        if context is None:
            context = {}
        for line in self.browse(cr, uid, ids, context=context):
            # cr.execute("   select count(st.id) from sales_target st ,sales_target_line stl where st.id=stl.sale_ids  and stl.product_uom_qty !=0.0 and sale_team_id =  %s and date= %s " ,( line.id,line.date,))
            # data=cr.fetchone()[0]
            res[line.id] = data
        return res        
 
    def _get_total_rout_plan(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        data = 0
        if context is None:
            context = {}
        for line in self.browse(cr, uid, ids, context=context):
            # cr.execute("   select count(st.id) from sales_target st ,sales_target_line stl where st.id=stl.sale_ids  and stl.product_uom_qty !=0.0 and sale_team_id =  %s and date= %s " ,( line.id,line.date,))
            # data=cr.fetchone()[0]
            res[line.id] = data
        return res       
 
    def _get_total_customer_visit(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        data = 0
        if context is None:
            context = {}
        for line in self.browse(cr, uid, ids, context=context):
            # cr.execute("   select count(st.id) from sales_target st ,sales_target_line stl where st.id=stl.sale_ids  and stl.product_uom_qty !=0.0 and sale_team_id =  %s and date= %s " ,( line.id,line.date,))
            # data=cr.fetchone()[0]
            res[line.id] = data
        return res      

    def _get_total_pre_sale(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        data = 0
        if context is None:
            context = {}
        for line in self.browse(cr, uid, ids, context=context):
            # cr.execute("select count(st.id) from sales_target st ,sales_target_line stl where st.id=stl.sale_ids  and stl.product_uom_qty !=0.0 and sale_team_id =  %s and date= %s " ,( line.id,line.date,))
            # data=cr.fetchone()[0]
            res[line.id] = data
        return res         
    
    def _get_sale_today(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        data = 0
        if context is None:
            context = {}
        for line in self.browse(cr, uid, ids, context=context):
            # cr.execute("   select count(st.id) from sales_target st ,sales_target_line stl where st.id=stl.sale_ids  and stl.product_uom_qty !=0.0 and sale_team_id =  %s and date= %s " ,( line.id,line.date,))
            # data=cr.fetchone()[0]
            res[line.id] = data
        return res         
    def _get_sale_month(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        data = 0
        if context is None:
            context = {}
        for line in self.browse(cr, uid, ids, context=context):
            # cr.execute("   select count(st.id) from sales_target st ,sales_target_line stl where st.id=stl.sale_ids  and stl.product_uom_qty !=0.0 and sale_team_id =  %s and date= %s " ,( line.id,line.date,))
            # data=cr.fetchone()[0]
            res[line.id] = data
        return res  
    
    def _get_sale_confirm(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        data = 0
        if context is None:
            context = {}
        for line in self.browse(cr, uid, ids, context=context):
            # cr.execute("   select count(st.id) from sales_target st ,sales_target_line stl where st.id=stl.sale_ids  and stl.product_uom_qty !=0.0 and sale_team_id =  %s and date= %s " ,( line.id,line.date,))
            # data=cr.fetchone()[0]
            res[line.id] = data
        return res  
    
    def _get_sale_work(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        data = 0
        if context is None:
            context = {}
        for line in self.browse(cr, uid, ids, context=context):
            # cr.execute("   select count(st.id) from sales_target st ,sales_target_line stl where st.id=stl.sale_ids  and stl.product_uom_qty !=0.0 and sale_team_id =  %s and date= %s " ,( line.id,line.date,))
            # data=cr.fetchone()[0]
            res[line.id] = data
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
            # cr.execute("   select count(st.id) from sales_target st ,sales_target_line stl where st.id=stl.sale_ids  and stl.product_uom_qty !=0.0 and sale_team_id =  %s and date= %s " ,( line.id,line.date,))
            # data=cr.fetchone()[0]
            res[line.id] = data
        return res
  
    _columns = {
                'region': fields.char('Region'),
                'channel_ids':fields.many2many('sale.channel'),
                'code': fields.char('Code', required=True),
                'product_ids':fields.many2many('product.product'),
                'warehouse_id': fields.many2one('stock.warehouse', 'Warehouse', required=True),
                'location_id': fields.many2one('stock.location', 'Location', required=True),
                'analytic_account_id': fields.many2one('account.analytic.account', 'Analytic Account'),
                'sale_channel_id':fields.many2many('sale.channel', 'sale_team_channel_rel', 'sale_team_id', 'sale_channel_id', string='Sale Channel'),
                'demarcation_ids':fields.many2many('sale.demarcation'),
                'van_id':fields.char('Vehicle No'),
                'vehicle_id':fields.many2one('fleet.vehicle', 'Vehicle No'),

                'main_group_id': fields.many2many('product.maingroup'),
                                'date':fields.date('Date'),
                'delivery_team_id': fields.many2one('crm.case.section', 'Delivery Team'),
                'total_invoice': fields.function(_get_total_invoice_data, digits_compute=dp.get_precision('Product Price'),
                type='float', readonly=True,
                string='Total Invoice'),
                'date':fields.date('Date'),
                'total_sku': fields.function(_get_total_sku_data, digits_compute=dp.get_precision('Product Price'),
                type='float', readonly=True,
                string='Total SKU'),
                 'total_sku_inv': fields.function(_get_total_sku_invoice_percent, digits_compute=dp.get_precision('Product Price'),
                type='float', readonly=True,
                string='Invoice/SKU %'),
                'total_sku': fields.function(_get_total_invoice_data, digits_compute=dp.get_precision('Product Price'),
                type='float', readonly=True,
                string='Total Invoice'),
                'date':fields.date('Date'),
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
        }
    _sql_constraints = [
        ('code_uniq', 'unique (code)', 'The code of the sales team must be unique !')
    ]    
    _defaults = {
        'date': fields.datetime.now,
        }   
crm_case_section()
