try:
    import simplejson as json
except ImportError:
    import json  # noqa
import urllib

from openerp.osv import fields, osv
from openerp import tools
from openerp.tools.translate import _

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
    _columns = {
                'name':fields.char('Outlet Name'),
                }

    
outlet_type()

class res_partner(osv.osv):

    _inherit = 'res.partner'
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
    _columns = {  
                'customer_code':fields.char('Code', required=False),
                'outlet_type': fields.many2one('outlettype.outlettype', 'Outlet Type', required=True),
                'temp_customer':fields.char('Contact Person'),
                'class_id':fields.many2one('sale.class', 'Class'),
                'old_code': fields.char('Old Code'),
                'sales_channel':fields.many2one('sale.channel', 'Sale Channels'),
                'address':fields.char('Address'),
                'branch_id':fields.many2one('sale.branch', 'Branch'),
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

 } 
    _defaults = {
        'is_company': True,
        'pending' : None,
        'idle' : None,
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
                     A.zip,A.state_name,A.partner_latitude,A.partner_longitude  from (

                     select RP.id,RP.name,RP.image,RP.is_company,
                     RP.image_small,RP.street,RP.street2,RP.city,RP.website,
                     RP.phone,RP.township,RP.mobile,RP.email,RP.company_id,RP.customer, 
                     RP.customer_code,RP.mobile_customer,RP.shop_name ,RP.address,RP.territory,
                     RP.village,RP.branch_code,RP.zip ,RP.partner_latitude,RP.partner_longitude,RS.name as state_name
                     from sale_plan_day SPD ,
                                            res_partner_sale_plan_day_rel RPS , res_partner RP ,res_country_state RS
                                            where SPD.id = RPS.sale_plan_day_id 
                                            and  RS.id = RP.state_id
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
                        and SPT.sale_team = %s
                        )A 
                        where A.shop_name is not null
                    and A.customer_code is not null 
            ''', (section_id, section_id,))
        datas = cr.fetchall()
        cr.execute
        return datas
# kzo Eidt
    def res_partners_return_day(self, cr, uid, section_id, day_id , context=None, **kwargs):
        cr.execute('''                    
                     select A.id,A.name,A.image,A.is_company, A.image_small,A.street,A.street2,A.city,A.website,
                     A.phone,A.township,A.mobile,A.email,A.company_id,A.customer, 
                     A.customer_code,A.mobile_customer,A.shop_name ,
                     A.address,A.territory,A.village,A.branch_code,
                     A.zip,A.state_name,A.partner_latitude,A.partner_longitude,A.sale_plan_day_id,A.image_medium,A.credit_limit,
                     A.credit_allow,A.sales_channel,A.branch_id,A.pricelist_id,A.payment_term_id  from (

                     select RP.id,RP.name,'' as image,RP.is_company,RPS.sale_plan_day_id,
                     '' as image_small,RP.street,RP.street2,RC.name as city,RP.website,
                     RP.phone,RT.name as township,RP.mobile,RP.email,RP.company_id,RP.customer, 
                     RP.customer_code,RP.mobile_customer,OT.name as shop_name,RP.address,RP.territory,
                     RP.village,RP.branch_code,RP.zip ,RP.partner_latitude,RP.partner_longitude,RS.name as state_name,
                     substring(replace(cast(RP.image_medium as text),'/',''),1,5) as image_medium,RP.credit_limit,RP.credit_allow,
                     RP.sales_channel,RP.branch_id,RP.pricelist_id,RP.payment_term_id
                     from sale_plan_day SPD ,outlettype_outlettype OT,
                                            res_partner_sale_plan_day_rel RPS , res_partner RP ,res_country_state RS, res_city RC,res_township RT
                                            where SPD.id = RPS.sale_plan_day_id 
                                            and  RS.id = RP.state_id
                                            and RP.township =RT.id
                                            and RP.city = RC.id
                                            and RP.outlet_type = OT.id
                                            and RPS.partner_id = RP.id 
                                            and SPD.sale_team = %s
                                            and RPS.sale_plan_day_id = %s
                                            
                        )A 
                        where A.customer_code is not null
            ''', (section_id, day_id,))
        datas = cr.fetchall()
        return datas
# kzo Edit add Sale Plan Trip and Day ID
    def res_partners_return_trip(self, cr, uid, section_id, day_id , context=None, **kwargs):
        cr.execute('''        
                    select A.id,A.name,A.image,A.is_company,
                     A.image_small,A.street,A.street2,A.city,A.website,
                     A.phone,A.township,A.mobile,A.email,A.company_id,A.customer, 
                     A.customer_code,A.mobile_customer,A.shop_name ,
                     A.address,A.territory,A.village,A.branch_code,
                     A.zip,A.state_name,A.partner_latitude,A.partner_longitude,A.sale_plan_trip_id,A.image_medium,
                     A.credit_limit,A.credit_allow,A.sales_channel,A.branch_id,A.pricelist_id,A.payment_term_id 
                      from (
                     select RP.id,RP.name,'' as image,RP.is_company,
                     '' as image_small,RP.street,RP.street2,RC.name as city,RP.website,
                     RP.phone,RT.name as township,RP.mobile,RP.email,RP.company_id,RP.customer, 
                     RP.customer_code,RP.mobile_customer,OT.name as shop_name ,RP.address,RP.territory ,RPT.sale_plan_trip_id,
                     RP.village,RP.branch_code,RP.zip ,RP.partner_latitude,RP.partner_longitude,RS.name as state_name
                      ,substring(replace(cast(RP.image_medium as text),'/',''),1,5) as image_medium ,RP.credit_limit,RP.credit_allow,
                    ,RP.sales_channel,RP.branch_id,RP.pricelist_id,RP.payment_term_id
                     from sale_plan_trip SPT , res_partner_sale_plan_trip_rel RPT , res_partner RP ,res_country_state RS ,
                     res_city RC, res_township RT,outlettype_outlettype OT 
                     where SPT.id = RPT.sale_plan_trip_id 
                     and RPT.partner_id = RP.id 
                     and  RS.id = RP.state_id
                     and RP.outlet_type = OT.id
                     and  RP.city = RC.id
                     and RP.township = RT.id
                     and SPT.sale_team = %s
                     and RPT.sale_plan_trip_id = %s
                        )A 
                    where A.customer_code is not null 
            ''', (section_id, day_id,))
        datas = cr.fetchall()
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
                                codeResult = {'city_id':cityId.id, 'township_id':townshipId.id, 'sale_channel_id':channelId.id, 'nextnumber':1, 'padding':4}
                                codeId = codeObj.create(cr, uid, codeResult, context=context)
                                code = codeObj.generateCode(cr, uid, codeId, context=context)
                if code:
                    self.write(cr, uid, ids, {'customer_code':code}, context=context)
            return True
res_partner()
class res_partner_asset(osv.Model):

    _description = 'Partner Tags'
    _name = 'res.partner.asset'
    _columns = {
                        'partner_id': fields.many2one('res.partner', 'Partner', select=True, ondelete='cascade'),
                        'name':fields.char('Asset Name'),
                        'date':fields.date('Date'),
                        'type':fields.selection ([('rent', 'Rent'), ('give', 'Giving')],
                                                    'Type', required=True, default='rent'),
                        'asset_type':fields.many2one('asset.type','Asset Type'),
                       'qty':fields.integer('Qty'),
                        'image': fields.binary("Image"),
  }
    _defaults = {
        'date': fields.datetime.now,
                    }
    
class asset_type(osv.Model):

    _description = 'Asset Type'
    _name = 'asset.type'
    _columns = {
                'name':fields.char('Asset Type Name'),
                }