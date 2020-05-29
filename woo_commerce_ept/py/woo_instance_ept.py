from openerp import models,fields,api,_
from openerp.exceptions import Warning
from .. import woocommerce
import requests
class woo_instance_ept(models.Model):
    _name="woo.instance.ept"
    
    name = fields.Char(size=120, string='Name', required=True)
    company_id = fields.Many2one('res.company',string='Company', required=True)
    warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse')
    pricelist_id = fields.Many2one('product.pricelist', string='Pricelist')
    lang_id = fields.Many2one('res.lang', string='Language')
    order_prefix = fields.Char(size=10, string='Order Prefix')
    import_order_status_ids = fields.Many2many('import.order.status','woo_instance_order_status_rel','instance_id','status_id',"Import Order Status",help="Selected status orders will be imported from WooCommerce")
    order_auto_import = fields.Boolean(string='Auto Order Import?')
    order_auto_update=fields.Boolean(string="Auto Order Update ?")
    stock_auto_export=fields.Boolean(string="Stock Auto Export?")    
    fiscal_position_id = fields.Many2one('account.fiscal.position', string='Fiscal Position')
    stock_field = fields.Many2one('ir.model.fields', string='Stock Field')
    country_id=fields.Many2one("res.country","Country")
    host=fields.Char("Host",required=True)    
    consumer_key=fields.Char("Consumer Key",required=True)
    consumer_secret=fields.Char("Consumer Secret",required=True)
    verify_ssl=fields.Boolean("Verify SSL",default=False,help="Check this if your WooCommerce site is using SSL certificate")      
    shipment_charge_product_id=fields.Many2one("product.product","Shipment Fee",domain=[('type','=','service')])
    section_id=fields.Many2one('crm.case.section', 'Sales Team')
    payment_term_id = fields.Many2one('account.payment.term', string='Payment Term')    
    discount_product_id=fields.Many2one("product.product","Discount",domain=[('type','=','service')])    
    fee_line_id=fields.Many2one("product.product","Fees",domain=[('type','=','service')])
    last_inventory_update_time=fields.Datetime("Last Inventory Update Time")
    state=fields.Selection([('not_confirmed','Not Confirmed'),('confirmed','Confirmed')],default='not_confirmed')
    is_image_url = fields.Boolean("Is Image URL?",help="Check this if you use Images from URL\nKepp as it is if you use Product images")
    admin_username=fields.Char("Username", help="Used to Export/Import Image Files.")
    admin_password=fields.Char("Password", help="Used to Export/Import Image Files.")
    woo_version = fields.Selection([('new','2.6+'),('old','<=2.6')],default='old',string="WooCommerce Version")        
    product_auto_import = fields.Boolean(string='Auto Product Import?')
    
    @api.multi
    def test_woo_connection(self):              
        wcapi = self.connect_in_woo()
        r = wcapi.get("products")
        if not isinstance(r,requests.models.Response):
            raise Warning(_("Response is not in proper format :: %s"%(r)))
        if r.status_code != 200:
            raise Warning(_("%s\n%s"%(r.status_code,r.reason)))        
        else:
            raise Warning('Service working properly')
        return True
        
    @api.multi
    def reset_to_confirm(self):
        self.write({'state':'not_confirmed'})
        return True
    
    @api.multi
    def confirm(self):        
        wcapi = self.connect_in_woo()
        r = wcapi.get("products")
        if not isinstance(r,requests.models.Response):
            raise Warning(_("Response is not in proper format :: %s"%(r)))
        if r.status_code != 200:
            raise Warning(_("%s\n%s"%(r.status_code,r.reason)))
        else:            
            self.write({'state':'confirmed'})
        return True              
        
    @api.model
    def connect_in_woo(self):
        host = self.host
        consumer_key = self.consumer_key
        consumer_secret = self.consumer_secret
        wp_api = True if self.woo_version == 'new' else False
        version = "wc-api/v1" if wp_api else "v3"
        wcapi = woocommerce.api.API(url=host, consumer_key=consumer_key,
                    consumer_secret=consumer_secret,verify_ssl=self.verify_ssl,wp_api=wp_api,version=version,query_string_auth=True)
        return wcapi                 