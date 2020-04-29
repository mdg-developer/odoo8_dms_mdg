
try:
    import simplejson as json
except ImportError:
    import json  # noqa
import urllib
from openerp.osv import fields, osv
from openerp import tools
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
import calendar
from datetime import datetime
import time
from datetime import date
from dateutil import relativedelta

DEFAULT_SERVER_DATE_FORMAT = "%Y-%m-%d"
def geo_find(addr):
    url = 'https://maps.googleapis.com/maps/api/geocode/json?sensor=false&address='
    url += urllib.quote(addr.encode('utf8'))

    try:
        result = json.load(urllib.urlopen(url))
    except Exception, e:
        raise osv.except_osv(_('Network error'),
                             _('Cannot contact geolocation servers. Please make sure that your internet connection is up and running (%s).') % e)
    if result['status'] != 'OK':
        return None

    try:
        geo = result['results'][0]['geometry']['location']
        return float(geo['lat']), float(geo['lng'])
    except (KeyError, ValueError):
        return None


def geo_query_address(street=None, zip=None, city=None, state=None, country=None):
    if country and ',' in country and (country.endswith(' of') or country.endswith(' of the')):
        # put country qualifier in front, otherwise GMap gives wrong results,
        # e.g. 'Congo, Democratic Republic of the' => 'Democratic Republic of the Congo'
        country = '{1} {0}'.format(*country.split(',', 1))
    return tools.ustr(', '.join(filter(None, [street,
                                              ("%s %s" % (zip or '', city or '')).strip(),
                                              state,
                                              country])))

class outlet_type(osv.osv):
    _name = 'outlettype.outlettype'
    
    def retrieve_data(self, cr, uid, ids, context=None):
        product_outlet_obj = self.pool.get('product.outlettype')
        cr.execute('delete from product_outlettype where outlettype_id=%s', (ids[0],))
        cr.execute('''select pp.id,pp.sequence from product_template pt,product_product pp where pt.id=pp.product_tmpl_id
            and pt.type!='service' and pt.sale_ok=True''')
        product_data=cr.fetchall()
        if product_data:                
            for val in product_data:
                product_id=val[0]    
                product_sequence =val[1]   
                product_outlet_obj.create(cr, uid, {'outlettype_id': ids[0],
                               'sequence':product_sequence,
                              'product_id': product_id,
                              'type':'none',
                        }, context=context)        
    _columns = {
                'name':fields.char('Outlet Name'),
                'outlet_product_line':fields.one2many('product.outlettype','outlettype_id','Outlet'),
                }

    
outlet_type()

class product_outlet(osv.osv):
    _name = 'product.outlettype'
    _columns = {
                'outlettype_id':fields.many2one('outlettype.outlettype','Outlet'),
                'product_id':fields.many2one('product.product','Product'),
                'sequence':fields.integer('Sequence'),         
                'type':fields.selection([('none', 'None'),
                                   ('must_sell','Must Sell'), # used by cash statements
                                   ('available', 'Available')],'Type', select=True),
                }
    
product_outlet()

class res_partner(osv.osv):

    _inherit = 'res.partner'
    _period_number = 5
    
    def _get_default_pricelist(self, cr, uid, ids, field_name, arg, context=None):
        result = {}
        for rec in self.browse(cr, uid, ids, context=context):
            result[rec.id] = rec.property_product_pricelist.id
        return result
    
    def _get_default_payment_term_id(self, cr, uid, ids, field_name, arg, context=None):
        result = {}
        for rec in self.browse(cr, uid, ids, context=context):
            result[rec.id] = rec.property_payment_term.id
        return result
    
    def _sale_order_count_pending(self, cr, uid, ids, field_name, arg, context=None):
        res = {} 
        print 'Pending>>>', ids    
        cr.execute("""select day from sale_order_configuration where customer_type='pending customer' order by id desc limit 1 """)
        day_number = cr.fetchall()
        print 'day_number>>>', day_number
        if day_number:
            day = day_number[0][0]
            print 'day>>>', day
            cr.execute("""select day from sale_order_configuration where customer_type='idle customer' order by id desc limit 1 """)
            largeday_number = cr.fetchall()
            if largeday_number:
                largeday = largeday_number[0][0]    
                cr.execute("""select DATE_PART('day',CURRENT_TIMESTAMP- max(date_order)) from sale_order where partner_id= %s GROUP BY partner_id
                HAVING COUNT(partner_id) > 1""", (ids[0],))
                order_day_number = cr.fetchall()
                print 'order_day_number>>>', order_day_number            
                if order_day_number:
                    order_day = order_day_number[0][0] 
                    print 'order_day>>>', order_day
                    print 'largeday>>>>>', largeday
                    print day <= order_day
                    print largeday >= order_day
                    if day <= order_day and largeday > order_day:
                        str_day = str(day) + ' days'                 
                        print 'condition>>>>>>>>>>'
                        cr.execute("""update res_partner set pending=%s where id=%s""", (str_day, ids[0],))
                    else:
                        # str_day = ''
                        str_day = None                         
                        cr.execute("""update res_partner set pending=NULL where id=%s""", (ids[0],))
                    print 'update>>pending', str_day                     
                    for partner in self.browse(cr, uid, ids, context):
                        print 'str_day>>>', str_day                            
                        res[partner.id] = str_day
                        
        return res
    
    def _sale_order_count_idle(self, cr, uid, ids, field_name, arg, context=None):
        res = {} 
        print 'Idel>>>', ids       
        cr.execute("""select day from sale_order_configuration where customer_type='idle customer' order by id desc limit 1 """)
        largeday_number = cr.fetchall()
        if largeday_number:
            largeday = largeday_number[0][0]    
            cr.execute("""select DATE_PART('day',CURRENT_TIMESTAMP- max(date_order)) from sale_order where partner_id= %s """, (ids[0],))
            order_day_number = cr.fetchall()
            print 'order_day_number>>>', order_day_number            
            if order_day_number:
                order_day = order_day_number[0][0] 
                print 'order_day>>>', order_day
                    
                if largeday <= order_day:
                    str_day = str(largeday) + ' days'                   
                    cr.execute("""update res_partner set idle=%s where id=%s""", (str_day, ids[0],))
                else:
                    # str_day = ''
                    str_day = None 
                    cr.execute("""update res_partner set idle=NULL where id=%s""", (ids[0],))
                print 'update>>idle', str_day                      
                for partner in self.browse(cr, uid, ids, context):
                    print 'str_day>>>', str_day                            
                    res[partner.id] = str_day
                        
        return res  
    def _sale_order_count_week(self, cr, uid, ids, field_name, arg, context=None):
        
        res = {} 
               
        cr.execute("""select DATE_PART('day',max(date_order)- min(date_order)) from sale_order where partner_id= %s """, (ids[0],))
        day_number = cr.fetchall()
        
        if day_number:
            day = day_number[0][0]    
            cr.execute('select count(id) from sale_order where partner_id=%s ', (ids[0],))
            so_number = cr.fetchall()
            
            if so_number:
                so_count = so_number[0][0]                                 
                if day > 6.0:
                    week_num = day / 7
                    
                else:
                    week_num = 1                   
                    
                if week_num > 0.0 :
                    if so_count > 0:
                        for partner in self.browse(cr, uid, ids, context):
                            
                            res[partner.id] = round(so_count / week_num, 2)
                        
        return res           
    
    def _get_total_sale_data(self, cr, uid, ids, field_name, arg, context=None):
        res = dict(map(lambda x: (x,0), ids))
        sale_obj=self.pool.get('sale.order')
        month_begin = date.today().replace(day=1)
        to_date = month_begin.replace(day=calendar.monthrange(month_begin.year, month_begin.month)[1]).strftime(tools.DEFAULT_SERVER_DATE_FORMAT)
        from_date=time.strftime('%Y-%m-01')
        # The current user may not have access rights for sale orders
        try:
            for partner in self.browse(cr, uid, ids, context):
                sale_ids = sale_obj.search(cr, uid, [('date_order', '>', from_date), ('date_order', '<', to_date),('partner_id','=',partner.id)], context=context) 
                res[partner.id] = len(sale_ids)
        except:
            pass
        return res
    
    def _get_total_invoice_data(self, cr, uid, ids, field_name, arg, context=None):
        res = dict(map(lambda x: (x,0), ids))
        invoice_obj=self.pool.get('account.invoice')
        month_begin = date.today().replace(day=1)
        to_date = month_begin.replace(day=calendar.monthrange(month_begin.year, month_begin.month)[1]).strftime(tools.DEFAULT_SERVER_DATE_FORMAT)
        from_date=time.strftime('%Y-%m-01')
        # The current user may not have access rights for sale orders
        try:
            for partner in self.browse(cr, uid, ids, context):
                invoice_ids = invoice_obj.search(cr, uid, [('date_invoice', '>=', from_date), ('date_invoice', '<=', to_date),('partner_id','=',partner.id)], context=context) 
                res[partner.id] = len(invoice_ids)
        except:
            pass
        return res
    
    def _get_invoice_confirm(self, cr, uid, ids, field_name, arg, context=None):
        res = dict(map(lambda x: (x,0), ids))
        invoice_obj=self.pool.get('account.invoice')
        month_begin = date.today().replace(day=1)
        to_date = month_begin.replace(day=calendar.monthrange(month_begin.year, month_begin.month)[1]).strftime(tools.DEFAULT_SERVER_DATE_FORMAT)
        from_date=time.strftime('%Y-%m-01')
        # The current user may not have access rights for sale orders
        try:
            for partner in self.browse(cr, uid, ids, context):
                invoice_ids = invoice_obj.search(cr, uid, [('date_invoice', '>', from_date), ('date_invoice', '<', to_date),('partner_id','=',partner.id),('state','=','paid')], context=context) 
                res[partner.id] = len(invoice_ids)
        except:
            pass
        return res 

    def _get_last_purchase_date(self, cr, uid, ids, field_name, arg, context=None):
        res = dict(map(lambda x: (x,0), ids))
        last_order_date=False
        for data in self.browse(cr, uid, ids, context=context):
            cr.execute("select date_order::date from sale_order where partner_id =%s order by id desc", (data.id,))
            last_order = cr.fetchone()
            if last_order:
                last_order_date = last_order[0]
            else:
                last_order_date = False
            
            res[data.id] = last_order_date
        return res 

    def _get_last_visit_date(self, cr, uid, ids, field_name, arg, context=None):
        res = dict(map(lambda x: (x,0), ids))
        for data in self.browse(cr, uid, ids, context=context):
            cr.execute("select date from customer_visit where customer_id=%s order by id desc", (data.id,))
            last_visit = cr.fetchone()
            if last_visit:
                last_visit_date = last_visit[0]
            else:
                last_visit_date = False
            
            res[data.id] = last_visit_date
        return res 
    def _get_last_purchase_amount(self, cr, uid, ids, field_name, arg, context=None):
        res = dict(map(lambda x: (x,0), ids))
        last_order_amount=False
        for data in self.browse(cr, uid, ids, context=context):
            cr.execute("select amount_total from sale_order where partner_id =%s order by id desc", (data.id,))
            last_order = cr.fetchone()
            if last_order:
                last_order_amount = last_order[0]
            else:
                last_order_amount = 0.0
            
            res[data.id] = last_order_amount
        return res
    
    def _get_all_invoice_amount(self, cr, uid, ids, field_name, arg, context=None):
        res = dict(map(lambda x: (x,0), ids))
        amount_total=0.0
        for data in self.browse(cr, uid, ids, context=context):
            cr.execute("select sum(amount_total) from account_invoice where partner_id =%s", (data.id,))
            amount_total = cr.fetchone()
            if amount_total:
                amount_total = amount_total[0]
            else:
                amount_total = 0.0
            
            res[data.id] = amount_total
        return res 

    def _get_monthly_invoice_amount(self, cr, uid, ids, field_name, arg, context=None):
        res = dict(map(lambda x: (x,0), ids))
        m_amount_total=0.0
        m_date='2016-09-20'
        month_begin = date.today().replace(day=1)
        #month_begin =m_date().replace(day=1)
        to_date = month_begin.replace(day=calendar.monthrange(month_begin.year, month_begin.month)[1]).strftime(tools.DEFAULT_SERVER_DATE_FORMAT)
        from_date=time.strftime('%Y-%m-01') 
        print 'from_date',from_date,to_date               
        for data in self.browse(cr, uid, ids, context=context):
            cr.execute("select sum(amount_total) from account_invoice where partner_id =%s and date_invoice between %s and %s ", (data.id,from_date,to_date,))
            amount_total = cr.fetchone()
            if amount_total:
                m_amount_total = amount_total[0]
            else:
                m_amount_total = 0.0
            
            res[data.id] = m_amount_total
        return res 
           
    def default_image_one(self, cr, uid, ids, context=None):
        res = {}
        data = 0
        if context is None:
            context = {}
        for line in self.browse(cr, uid, ids, context=context):
            cr.execute("update res_partner set image_small=%s, image =%s,image_medium=%s where id = %s" , (line.image_one, line.image_one, line.image_one, line.id,))
        return True

    def default_image_two(self, cr, uid, ids, context=None):
        res = {}
        data = 0
        if context is None:
            context = {}
        for line in self.browse(cr, uid, ids, context=context):
            cr.execute("update res_partner set image_small=%s, image =%s,image_medium=%s where id = %s" , (line.image_two, line.image_two, line.image_two, line.id,))
        return True

    def default_image_three(self, cr, uid, ids, context=None):
        res = {}
        data = 0
        if context is None:
            context = {}
        for line in self.browse(cr, uid, ids, context=context):
            cr.execute("update res_partner set image_small=%s, image =%s,image_medium=%s where id = %s" , (line.image_three, line.image_three, line.image_three, line.id,))
        return True

    def default_image_four(self, cr, uid, ids, context=None):
        res = {}
        data = 0
        if context is None:
            context = {}
        for line in self.browse(cr, uid, ids, context=context):
            cr.execute("update res_partner set image_small=%s, image =%s,image_medium=%s where id = %s" , (line.image_four, line.image_four, line.image_four, line.id,))
        return True

    def default_image_five(self, cr, uid, ids, context=None):
        res = {}
        data = 0
        if context is None:
            context = {}
        for line in self.browse(cr, uid, ids, context=context):
            cr.execute("update res_partner set image_small=%s, image =%s,image_medium=%s where id = %s" , (line.image_five, line.image_five, line.image_five, line.id,))
        return True

    def _default_country(self,cr, uid, ids,context=None, uid2=False):
        if not uid2:
            uid2 = uid
        cr.execute("select id from res_country where name ='Myanmar'")
        country_id=cr.fetchone()[0]
        return country_id   
    
    def update_customer_target(self, cr, uid, ids, context=None):        
        customer_target_obj = self.pool.get('customer.target')
        for partner in self.browse(cr, uid, ids, context=context):
            customer_target_obj.create_customer_target_data(cr, uid, partner.id, context=context)            

    _columns = {  
                'customer_code':fields.char('Code', required=False,copy=False),
                'outlet_type': fields.many2one('outlettype.outlettype', 'Outlet Type'),
                'temp_customer':fields.char('Contact Person'),
                'class_id':fields.many2one('sale.class', 'Class'),
                'frequency_id':fields.many2one('plan.frequency','Frequency',required=False),
                'chiller':fields.boolean('Chiller'),
		       	'hamper':fields.boolean('Hamper'),

                'old_code': fields.char('Old Code'),
                'sales_channel':fields.many2one('sale.channel', 'Sale Channel'),
                'address':fields.char('Address'),
                'branch_id':fields.many2one('res.branch', 'Branch'),
                'demarcation_id': fields.many2one('sale.demarcation', 'Demarcation'),
                'mobile_customer': fields.boolean('Pending Customer', help="Check this box if this contact is a mobile customer. If it's not checked, purchase people will not see it when encoding a purchase order."),
                # 'sale_order_count_by_week': fields.function(sale_order_count_by_week, string='# of Sales Order by week', type='integer'),
#                 'pending_customer': fields.function(_sale_order_count_pending, string='Customer Type', type='char',readonly=True, store=True),               
#                 'idle_customer': fields.function(_sale_order_count_idle, string='Idle Customer', type='char',readonly=True, store=True),
                'pending': fields.char('Pending Customer', required=False),
                'idle': fields.char('Idle Customer', required=False),
                'pending_customer': fields.function(_sale_order_count_pending, string='Customer Type Function', type='char'),
                'idle_customer': fields.function(_sale_order_count_idle, string='Idle Customer Function', type='char'),
                'unit': fields.char('Unit', required=False),
                # 'avg_sale_order_ids': fields.one2many('sale.order','partner_id','Sales Order'),
                'pricelist_id':fields.function(_get_default_pricelist, type='many2one', relation='product.pricelist', string='Price List', store=True),
                'payment_term_id':fields.function(_get_default_payment_term_id, type='many2one', relation='account.payment.term', string='Payment Term', store=True),
                 'asset_ids': fields.one2many('res.partner.asset', 'partner_id', 'Asset'),
                 'space_ids': fields.one2many('sales.rental', 'partner_id', 'Space Rental'),
                'image_one': fields.binary("Image One",
                    help="This field holds the image used as avatar for this contact, limited to 1024x1024px"),
                'image_two': fields.binary("Image Two",
                    help="This field holds the image used as avatar for this contact, limited to 1024x1024px"),
                'image_three': fields.binary("Image Three",
                    help="This field holds the image used as avatar for this contact, limited to 1024x1024px"),
                'image_four': fields.binary("Image Four",
                    help="This field holds the image used as avatar for this contact, limited to 1024x1024px"),
                'image_five': fields.binary("Image Five",
                    help="This field holds the image used as avatar for this contact, limited to 1024x1024px"),
                 'month_sale': fields.function(_get_total_sale_data, digits_compute=dp.get_precision('Product Price'),
                type='float', readonly=True,
                string='Monthly Sale'),
                 'month_invoice': fields.function(_get_total_invoice_data,
                type='integer', readonly=True,
                string='Monthly Invoice'),
                'invoice_confirm': fields.function(_get_invoice_confirm, digits_compute=dp.get_precision('Product Price'),
                type='float', readonly=True,
                string='Invoice Confirm'),
                 'last_purchase_date': fields.function(_get_last_purchase_date,
                type='date', readonly=True,
                string='Last Purchase Date'),
                 'last_purchase_amount': fields.function(_get_last_purchase_amount,
                type='float', readonly=True,
                string='Last Purchase Amount'),                
                'all_invoice_amount': fields.function(_get_all_invoice_amount,
                type='float', readonly=True,
                string='All Invoice Amount'),  
                'month_invoice_amount': fields.function(_get_monthly_invoice_amount,
                type='float', readonly=True,
                string='Month Invoice Amount'),  
                'last_visit_date':fields.function(_get_last_visit_date,
                type='datetime', readonly=True,
                string='Lastest Visit Date'),                        
        'user_id': fields.many2one('res.users', 'Created By', help='The internal user that is in charge of communicating with this contact if any.'),
          
 } 
    _defaults = {
        'is_company': True,
        'pending' : None,
        'idle' : None,
        'country_id':_default_country,
    }
    _sql_constraints = [        
        ('customer_code_uniq', 'unique (customer_code)', 'Customer code must be unique !'),
    ]
    
     
    
    def geo_localize(self, cr, uid, ids, context=None):
        # Don't pass context to browse()! We need country names in english below
        for partner in self.browse(cr, uid, ids):
            if not partner:
                continue
            result = geo_find(geo_query_address(street=partner.street,
                                                zip=partner.zip,
                                                city=partner.city.name,
                                                state=partner.state_id.name,
                                                country=partner.country_id.name))
            if result:
                self.write(cr, uid, [partner.id], {
                    'partner_latitude': result[0],
                    'partner_longitude': result[1],
                    'date_localization': fields.date.context_today(self, cr, uid, context=context)
                }, context=context)
        return True
    
    def partner_id_from_sale_plan_day(self, cr, uid, sale_team_id , context=None, **kwargs):
        cr.execute('select RP.id from sale_plan_day SPD , res_partner_sale_plan_day_rel RPS , res_partner RP where SPD.id = RPS.sale_plan_day_id and RPS.res_partner_id = RP.id and SPD.sale_team = %s ', (sale_team_id,))
        datas = cr.fetchall()
        cr.execute
        return datas
    def partner_id_from_sale_plan_trip(self, cr, uid, sale_team_id , context=None, **kwargs):
        cr.execute('select RP.id from sale_plan_trip SPT , res_partner_sale_plan_trip_rel RPT , res_partner RP where SPT.id = RPT.sale_plan_trip_id and RPT.res_partner_id = RP.id and SPT.sale_team =  %s ', (sale_team_id,))
        datas = cr.fetchall()
        cr.execute
        return datas
    def partner_id_from_section_id(self, cr, uid, section_id , context=None, **kwargs):
        cr.execute('select id from res_partner where section_id = %s ', (section_id,))
        datas = cr.fetchall()
        cr.execute
        return datas
    
    def res_partners_return(self, cr, uid, section_id , context=None, **kwargs):
        cr.execute('''
                    

             select A.id,A.name,A.image,A.is_company,
                     A.image_small,A.street,A.street2,A.city,A.website,
                     A.phone,A.township,A.mobile,A.email,A.company_id,A.customer, 
                     A.customer_code,A.mobile_customer,A.shop_name ,
                     A.address,A.territory,A.village,A.branch_code,
                     A.zip,A.state_name,A.partner_latitude,A.partner_longitude,is_consignment  from (

                     select RP.id,RP.name,RP.image,RP.is_company,RP.is_consignment,
                     RP.image_small,RP.street,RP.street2,RP.city,RP.website,
                     RP.phone,RP.township,RP.mobile,RP.email,RP.company_id,RP.customer, 
                     RP.customer_code,RP.mobile_customer,RP.shop_name ,RP.address,RP.territory,
                     RP.village,RP.branch_code,RP.zip ,RP.partner_latitude,RP.partner_longitude,RS.name as state_name
                     from sale_plan_day SPD ,
                                            res_partner_sale_plan_day_rel RPS , res_partner RP ,res_country_state RS
                                            where SPD.id = RPS.sale_plan_day_id 
                                            and  RS.id = RP.state_id
                                            and RP.active = true
                                            and RPS.res_partner_id = RP.id 
                                            and SPD.sale_team = %s
                                            union

                                            select RP.id,RP.name,RP.image,RP.is_company,
                     RP.image_small,RP.street,RP.street2,RP.city,RP.website,
                     RP.phone,RP.township,RP.mobile,RP.email,RP.company_id,RP.customer, 
                     RP.customer_code,RP.mobile_customer,RP.shop_name ,RP.address,RP.territory ,
                     RP.village,RP.branch_code,RP.zip ,RP.partner_latitude,RP.partner_longitude,RS.name as state_name
                     from sale_plan_trip SPT , res_partner_sale_plan_trip_rel RPT , res_partner RP ,res_country_state RS 
                                            where SPT.id = RPT.sale_plan_trip_id 
                        and RPT.res_partner_id = RP.id 
                        and  RS.id = RP.state_id
                        and RP.active = true
                        and SPT.sale_team = %s
                        )A 
                        where A.shop_name is not null
                    and A.customer_code is not null 
            ''', (section_id, section_id,))
        datas = cr.fetchall()
        cr.execute
        return datas
    
    # MMK
    def generate_customercode(self, cr, uid, ids, val, context=None):
            codeObj = self.pool.get('res.code')
            cityId = townshipId = channelId = codeId = code = None
            codeResult = {}
            if ids:
                for resVal in self.browse(cr, uid, ids, context=context):
                    if resVal:
                        cityId = resVal.city
                        townshipId = resVal.township
                        channelId = resVal.sales_channel
                        if cityId and townshipId and channelId:
                            codeId = codeObj.search(cr, uid, [('city_id', '=', cityId.id), ('township_id', '=', townshipId.id), ('sale_channel_id', '=', channelId.id)])
                            if codeId:
                                code = codeObj.generateCode(cr, uid, codeId[0], context=context)
                            else:
                                codeResult = {'city_id':cityId.id, 'township_id':townshipId.id, 'sale_channel_id':channelId.id, 'nextnumber':1, 'padding':6}
                                codeId = codeObj.create(cr, uid, codeResult, context=context)
                                code = codeObj.generateCode(cr, uid, codeId, context=context)
                if code:
                    from datetime import datetime
                    cr.execute("update res_partner set customer_code=%s ,date_partnership=now()::date ,mobile_customer=False ,write_uid =%s ,write_date =now() where id=%s",(code,uid,ids[0], ))
                    cr.execute("select a.category_id from res_partner_res_partner_category_rel a , res_partner_category b where a.category_id = b.id and partner_id =%s",(ids[0], ))
                    category_data=cr.fetchone()
                    if not category_data:
                        cr.execute("INSERT INTO res_partner_res_partner_category_rel(category_id,partner_id) VALUES(%s,%s)",(2,ids[0],))

                    #self.write(cr, uid, ids, {'customer_code':code,'date_partnership':datetime.now().date(),'mobile_customer':False}, context=context)
            return True
res_partner()
class res_partner_asset(osv.Model):

    _description = 'Partner Tags'
    _name = 'res.partner.asset'
    _columns = {
                        'partner_id': fields.many2one('res.partner', 'Customer', select=True, ondelete='cascade',required=True),                        
                        'township_id': fields.related(
                                            'partner_id', 'township',
                                            type='many2one',
                                            relation='res.township',
                                            string="Township",store=True), 
                        'name':fields.char('Asset Name',required=True),
                        'date':fields.date('Date',required=True),
                        'type':fields.selection ([('rent', 'Rent'), ('give', 'Giving')],
                                                    'Type', required=True, default='rent'),
                        'asset_type':fields.many2one('asset.type', 'Asset Type',required=True),
                       'qty':fields.integer('Qty',required=True),
                        'image': fields.binary("Image"),
                        'note':fields.text('Note'),
  }
    _defaults = {
        'date': fields.datetime.now,
                    }
    
class asset_type(osv.Model):

    _description = 'Asset Type'
    _name = 'asset.type'
    _columns = {
                'name':fields.char('Name',required=True),
                }
