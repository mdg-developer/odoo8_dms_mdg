from openerp import models,fields,api,_
from openerp.exceptions import Warning
from .. import woocommerce
import requests
from datetime import datetime
from dateutil.relativedelta import relativedelta

_intervalTypes = {
    'work_days': lambda interval: relativedelta(days=interval),
    'days': lambda interval: relativedelta(days=interval),
    'hours': lambda interval: relativedelta(hours=interval),
    'weeks': lambda interval: relativedelta(days=7*interval),
    'months': lambda interval: relativedelta(months=interval),
    'minutes': lambda interval: relativedelta(minutes=interval),
}

class woo_instance_config(models.TransientModel):
    _name = 'res.config.woo.instance'
    
    name = fields.Char("Instance Name")
    consumer_key=fields.Char("Consumer Key",required=True)
    consumer_secret=fields.Char("Consumer Secret",required=True)    
    host=fields.Char("Host",required=True)
    verify_ssl=fields.Boolean("Verify SSL",default=False,help="Check this if your WooCommerce site is using SSL certificate")
    country_id = fields.Many2one('res.country',string = "Country",required=True)
    is_image_url = fields.Boolean("Is Image URL?",help="Check this if you use Images from URL\nKepp as it is if you use Product images")
    admin_username=fields.Char("Username", help="Used to Export/Import Image Files.")
    admin_password=fields.Char("Password", help="Used to Export/Import Image Files.")
    woo_version = fields.Selection([('new','2.6+'),('old','<=2.6')],default='old',string="WooCommerce Version")    
        
    
    @api.multi
    def test_woo_connection(self):
        host = self.host
        consumer_key = self.consumer_key
        consumer_secret = self.consumer_secret
        wp_api = True if self.woo_version == 'new' else False
        version = "wc/v1" if wp_api else "v3"        
        wcapi = woocommerce.api.API(url=host, consumer_key=consumer_key,
                    consumer_secret=consumer_secret,verify_ssl=self.verify_ssl,wp_api=wp_api,version=version,query_string_auth=True)        
        r = wcapi.get("products")
        if not isinstance(r,requests.models.Response):
            raise Warning(_("Response is not in proper format :: %s"%(r)))
        if r.status_code != 200:
            raise Warning(_("%s\n%s"%(r.status_code,r.reason)))
        else:    
            self.env['woo.instance.ept'].create({'name':self.name,
                                                 'consumer_key':self.consumer_key,                                                 
                                                 'consumer_secret':self.consumer_secret,                                                 
                                                 'host':self.host,
                                                 'verify_ssl':self.verify_ssl,
                                                 'country_id':self.country_id.id,
                                                 'company_id':self.env.user.company_id.id,
                                                 'is_image_url':self.is_image_url,
                                                 'woo_version':self.woo_version,
                                                 'admin_username':self.admin_username,
                                                 'admin_password':self.admin_password                                                                                                                                                
                                                 })        
        return True
    
class woo_config_settings(models.TransientModel):
    _name = 'woo.config.settings'
    _inherit = 'res.config.settings'
    
    @api.model
    def _default_instance(self):
        instances = self.env['woo.instance.ept'].search([])
        return instances and instances[0].id or False
    
   
    @api.model
    def _get_default_company(self):
        company_id = self.env.user._get_company()
        if not company_id:
            raise Warning(_('There is no default company for the current user!'))
        return company_id
        
    woo_instance_id = fields.Many2one('woo.instance.ept', 'Instance', default=_default_instance)
    warehouse_id = fields.Many2one('stock.warehouse',string = "Warehouse")
    company_id = fields.Many2one('res.company',string='Company')
    country_id = fields.Many2one('res.country',string = "Country")
    lang_id = fields.Many2one('res.lang', string='Language')
    order_prefix = fields.Char(size=10, string='Order Prefix')
    import_order_status_ids = fields.Many2many('import.order.status','woo_config_settings_order_status_rel','woo_config_id','status_id',"Import Order Status",help="Select Order Status of the type of orders you want to import from WooCommerce.")           

    stock_field = fields.Many2one('ir.model.fields', string='Stock Field')
    
    pricelist_id = fields.Many2one('product.pricelist', string='Pricelist')
    payment_term_id = fields.Many2one('account.payment.term', string='Payment Term')    
    section_id=fields.Many2one('crm.case.section', 'Sales Team')
        
    shipment_charge_product_id=fields.Many2one("product.product","Shipment Fee",domain=[('type','=','service')])
    discount_product_id=fields.Many2one("product.product","Discount",domain=[('type','=','service')],required=False)
    fee_line_id=fields.Many2one("product.product","Fees",domain=[('type','=','service')],required=False,help="Any Extra fees applicable under specific condition(s) (e.g., Extra $20 if payment method is COD).")
    fiscal_position_id = fields.Many2one('account.fiscal.position', string='Fiscal Position')                
    
       
    order_auto_import = fields.Boolean(string='Auto Order Import?')
    order_import_interval_number = fields.Integer('Import Order Interval Number',help="Repeat every x.")
    order_import_interval_type = fields.Selection( [('minutes', 'Minutes'),
            ('hours','Hours'), ('work_days','Work Days'), ('days', 'Days'),('weeks', 'Weeks'), ('months', 'Months')], 'Import Order Interval Unit')
    order_import_next_execution = fields.Datetime('Next Execution', help='Next execution time')
    
    
    order_auto_update=fields.Boolean(string="Auto Order Update ?")
    order_update_interval_number = fields.Integer('Update Order Interval Number',help="Repeat every x.")
    order_update_interval_type = fields.Selection( [('minutes', 'Minutes'),
            ('hours','Hours'), ('work_days','Work Days'), ('days', 'Days'),('weeks', 'Weeks'), ('months', 'Months')], 'Update Order Interval Unit')               
    order_update_next_execution = fields.Datetime('Next Execution', help='Next execution time')
    
    stock_auto_export=fields.Boolean('Stock Auto Update.', default=False)
    update_stock_interval_number = fields.Integer('Update Order Interval Number',help="Repeat every x.")
    update_stock_interval_type = fields.Selection( [('minutes', 'Minutes'),
            ('hours','Hours'), ('work_days','Work Days'), ('days', 'Days'),('weeks', 'Weeks'), ('months', 'Months')], 'Update Order Interval Unit')
    update_stock_next_execution = fields.Datetime('Next Execution', help='Next execution time')
    
    product_auto_import = fields.Boolean(string='Auto Product Import?')
    product_import_interval_number = fields.Integer('Import Product Interval Number',help="Repeat every x.")
    product_import_interval_type = fields.Selection( [('minutes', 'Minutes'),
            ('hours','Hours'), ('work_days','Work Days'), ('days', 'Days'),('weeks', 'Weeks'), ('months', 'Months')], 'Import Order Interval Unit')
    product_import_next_execution = fields.Datetime('Next Execution', help='Next execution time')    
    
    @api.onchange('woo_instance_id')
    def onchange_instance_id(self):        
        instance = self.woo_instance_id or False
        self.company_id=instance and instance.company_id and instance.company_id.id or False
        self.warehouse_id = instance and instance.warehouse_id and instance.warehouse_id.id or False
        self.country_id = instance and instance.country_id and instance.country_id.id or False
        self.lang_id = instance and instance.lang_id and instance.lang_id.id or False
        self.order_prefix = instance and instance.order_prefix or ''
        self.import_order_status_ids = instance and instance.import_order_status_ids.ids
        self.stock_field = instance and instance.stock_field and instance.stock_field.id or False
        self.pricelist_id = instance and instance.pricelist_id and instance.pricelist_id.id or False
        self.payment_term_id = instance and instance.payment_term_id and instance.payment_term_id.id or False 
        self.shipment_charge_product_id = instance and instance.shipment_charge_product_id and instance.shipment_charge_product_id.id or False
        self.fiscal_position_id = instance and instance.fiscal_position_id and instance.fiscal_position_id.id or False
        self.discount_product_id=instance and instance.discount_product_id and instance.discount_product_id.id or False
        self.fee_line_id=instance and instance.fee_line_id and instance.fee_line_id.id or False        
        self.order_auto_import=instance and instance.order_auto_import
        self.stock_auto_export=instance and instance.stock_auto_export
        self.order_auto_update=instance and instance.order_auto_update
        self.section_id=instance and instance.section_id and instance.section_id.id or False
        self.product_auto_import=instance and instance.product_auto_import
       
        try:
            inventory_cron_exist = instance and self.env.ref('woo_commerce_ept.ir_cron_update_woo_stock_instance_%d'%(instance.id),raise_if_not_found=False)
        except:
            inventory_cron_exist=False
        if inventory_cron_exist:
            self.update_stock_interval_number=inventory_cron_exist.interval_number or False
            self.update_stock_interval_type=inventory_cron_exist.interval_type or False
            self.update_stock_next_execution = inventory_cron_exist.nextcall or False
             
        try:
            order_import_cron_exist = instance and self.env.ref('woo_commerce_ept.ir_cron_import_woo_orders_instance_%d'%(instance.id),raise_if_not_found=False)
        except:
            order_import_cron_exist=False
        if order_import_cron_exist:
            self.order_import_interval_number = order_import_cron_exist.interval_number or False
            self.order_import_interval_type = order_import_cron_exist.interval_type or False
            self.order_import_next_execution = order_import_cron_exist.nextcall or False
        try:
            order_update_cron_exist = instance and self.env.ref('woo_commerce_ept.ir_cron_update_woo_order_status_instance_%d'%(instance.id),raise_if_not_found=False)
        except:
            order_update_cron_exist=False
        if order_update_cron_exist:
            self.order_update_interval_number = order_update_cron_exist.interval_number or False
            self.order_update_interval_type = order_update_cron_exist.interval_type or False
            self.order_update_next_execution = order_update_cron_exist.nextcall or False
            
        try:
            product_import_cron_exist = instance and self.env.ref('woo_commerce_ept.ir_cron_import_woo_product_instance_%d'%(instance.id),raise_if_not_found=False)
        except:
            product_import_cron_exist=False
        if product_import_cron_exist:
            self.product_import_interval_number = product_import_cron_exist.interval_number or False
            self.product_import_interval_type = product_import_cron_exist.interval_type or False
            self.product_import_next_execution = product_import_cron_exist.nextcall or False   
    
    @api.multi
    def execute(self):
        instance = self.woo_instance_id
        values = {}
        res = super(woo_config_settings,self).execute()
        if instance:
            values['company_id'] = self.company_id and self.company_id.id or False
            values['warehouse_id'] = self.warehouse_id and self.warehouse_id.id or False
            values['country_id'] = self.country_id and self.country_id.id or False
            values['lang_id'] = self.lang_id and self.lang_id.id or False
            values['order_prefix'] = self.order_prefix and self.order_prefix
            values['import_order_status_ids'] = [(6,0,self.import_order_status_ids.ids)]           
            values['stock_field'] = self.stock_field and self.stock_field.id or False
            values['pricelist_id'] = self.pricelist_id and self.pricelist_id.id or False
            values['payment_term_id'] = self.payment_term_id and self.payment_term_id.id or False 
            values['shipment_charge_product_id'] = self.shipment_charge_product_id and self.shipment_charge_product_id.id or False
            values['fiscal_position_id'] = self.fiscal_position_id and self.fiscal_position_id.id or False
            values['discount_product_id']=self.discount_product_id.id or False
            values['fee_line_id']=self.fee_line_id.id or False            
            values['order_auto_import']=self.order_auto_import
            values['stock_auto_export']=self.stock_auto_export
            values['order_auto_update']=self.order_auto_update
            values['section_id']=self.section_id and self.section_id.id or False
            values['product_auto_import']=self.product_auto_import
            instance.write(values)
            self.setup_order_import_cron(instance)
            self.setup_order_status_update_cron(instance)                             
            self.setup_update_stock_cron(instance) 
            self.setup_product_import_cron(instance) 
        return res

    @api.multi   
    def setup_order_import_cron(self,instance):
        if self.order_auto_import:
            try:
                cron_exist = self.env.ref('woo_commerce_ept.ir_cron_import_woo_orders_instance_%d'%(instance.id),raise_if_not_found=False)
            except:
                cron_exist=False
            nextcall = datetime.now()
            nextcall += _intervalTypes[self.order_import_interval_type](self.order_import_interval_number)
            vals = {
                    'active' : True,
                    'interval_number':self.order_import_interval_number,
                    'interval_type':self.order_import_interval_type,
                    'nextcall':nextcall.strftime('%Y-%m-%d %H:%M:%S'),
                    'args':"([{'woo_instance_id':%d}])"%(instance.id)}
                    
            if cron_exist:
                vals.update({'name' : cron_exist.name})
                cron_exist.write(vals)
            else:
                try:
                    import_order_cron = self.env.ref('woo_commerce_ept.ir_cron_import_woo_orders')
                except:
                    import_order_cron=False
                if not import_order_cron:
                    raise Warning('Core settings of WooCommerce are deleted, please upgrade WooCommerce Connector module to back this settings.')
                
                name = instance.name + ' : ' +import_order_cron.name
                vals.update({'name' : name})
                new_cron = import_order_cron.copy(default=vals)
                self.env['ir.model.data'].create({'module':'woo_commerce_ept',
                                                  'name':'ir_cron_import_woo_orders_instance_%d'%(instance.id),
                                                  'model': 'ir.cron',
                                                  'res_id' : new_cron.id,
                                                  'noupdate' : True
                                                  })
        else:
            try:
                cron_exist = self.env.ref('woo_commerce_ept.ir_cron_import_woo_orders_instance_%d'%(instance.id))
            except:
                cron_exist=False
            
            if cron_exist:
                cron_exist.write({'active':False})
        return True                                                                                                                
        
    
    @api.multi   
    def setup_order_status_update_cron(self,instance):
        if self.order_auto_update:
            try:
                cron_exist = self.env.ref('woo_commerce_ept.ir_cron_update_woo_order_status_instance_%d'%(instance.id))
            except:
                cron_exist=False
            nextcall = datetime.now()
            nextcall += _intervalTypes[self.order_update_interval_type](self.order_update_interval_number)
            vals = {'active' : True,
                    'interval_number':self.order_update_interval_number,
                    'interval_type':self.order_update_interval_type,
                    'nextcall':nextcall.strftime('%Y-%m-%d %H:%M:%S'),
                    'args':"([{'woo_instance_id':%d}])"%(instance.id)}
                    
            if cron_exist:
                vals.update({'name' : cron_exist.name})
                cron_exist.write(vals)
            else:
                try:
                    update_order_cron = self.env.ref('woo_commerce_ept.ir_cron_update_woo_order_status')
                except:
                    update_order_cron=False
                if not update_order_cron:
                    raise Warning('Core settings of WooCommerce are deleted, please upgrade WooCommerce Connector module to back this settings.')
                
                name = instance.name + ' : ' +update_order_cron.name
                vals.update({'name' : name}) 
                new_cron = update_order_cron.copy(default=vals)
                self.env['ir.model.data'].create({'module':'woo_commerce_ept',
                                                  'name':'ir_cron_update_woo_order_status_instance_%d'%(instance.id),
                                                  'model': 'ir.cron',
                                                  'res_id' : new_cron.id,
                                                  'noupdate' : True
                                                  })
        else:
            try:
                cron_exist = self.env.ref('woo_commerce_ept.ir_cron_update_woo_order_status_instance_%d'%(instance.id))
            except:
                cron_exist=False
            if cron_exist:
                cron_exist.write({'active':False})
        return True
    
    @api.multi   
    def setup_update_stock_cron(self,instance):
        if self.stock_auto_export:
            try:                
                cron_exist = self.env.ref('woo_commerce_ept.ir_cron_update_woo_stock_instance_%d'%(instance.id))
            except:
                cron_exist=False
            nextcall = datetime.now()
            nextcall += _intervalTypes[self.update_stock_interval_type](self.update_stock_interval_number)
            vals = {'active' : True,
                    'interval_number':self.update_stock_interval_number,
                    'interval_type':self.update_stock_interval_type,
                    'nextcall':nextcall.strftime('%Y-%m-%d %H:%M:%S'),
                    'args':"([{'woo_instance_id':%d}])"%(instance.id)}
            if cron_exist:
                vals.update({'name' : cron_exist.name})
                cron_exist.write(vals)
            else:
                try:                    
                    update_stock_cron = self.env.ref('woo_commerce_ept.ir_cron_update_woo_stock')
                except:
                    update_stock_cron=False
                if not update_stock_cron:
                    raise Warning('Core settings of WooCommerce are deleted, please upgrade WooCommerce Connector module to back this settings.')
                
                name = instance.name + ' : ' +update_stock_cron.name
                vals.update({'name':name})
                new_cron = update_stock_cron.copy(default=vals)
                self.env['ir.model.data'].create({'module':'woo_commerce_ept',
                                                  'name':'ir_cron_update_woo_stock_instance_%d'%(instance.id),
                                                  'model': 'ir.cron',
                                                  'res_id' : new_cron.id,
                                                  'noupdate' : True
                                                  })
        else:
            try:
                cron_exist = self.env.ref('woo_commerce_ept.ir_cron_update_woo_stock_instance_%d'%(instance.id))
            except:
                cron_exist=False
            if cron_exist:
                cron_exist.write({'active':False})        
        return True
    
    api.multi   
    def setup_product_import_cron(self,instance):
        if self.product_auto_import:
            try:
                cron_exist = self.env.ref('woo_commerce_ept.ir_cron_import_woo_product_instance_%d'%(instance.id),raise_if_not_found=False)
            except:
                cron_exist=False
            nextcall = datetime.now()
            nextcall += _intervalTypes[self.product_import_interval_type](self.product_import_interval_number)
            vals = {
                    'active' : True,
                    'interval_number':self.product_import_interval_number,
                    'interval_type':self.product_import_interval_type,
                    'nextcall':nextcall.strftime('%Y-%m-%d %H:%M:%S'),
                    'args':"([{'woo_instance_id':%d}])"%(instance.id)}
                    
            if cron_exist:
                vals.update({'name' : cron_exist.name})
                cron_exist.write(vals)
            else:
                try:
                    import_product_cron = self.env.ref('woo_commerce_ept.ir_cron_import_woo_product')
                except:
                    import_product_cron=False
                if not import_product_cron:
                    raise Warning('Product Core settings of WooCommerce are deleted, please upgrade WooCommerce Connector module to back this settings.')
                
                name = instance.name + ' : ' +import_product_cron.name
                vals.update({'name' : name})
                new_cron = import_product_cron.copy(default=vals)
                self.env['ir.model.data'].create({'module':'woo_commerce_ept',
                                                  'name':'ir_cron_import_woo_product_instance_%d'%(instance.id),
                                                  'model': 'ir.cron',
                                                  'res_id' : new_cron.id,
                                                  'noupdate' : True
                                                  })
        else:
            try:
                cron_exist = self.env.ref('woo_commerce_ept.ir_cron_import_woo_product_instance_%d'%(instance.id))
            except:
                cron_exist=False
            
            if cron_exist:
                cron_exist.write({'active':False})
        return True
    
    