try:
    import simplejson as json
except ImportError:
    import json     # noqa
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
    _columns = {  
                'customer_code':fields.char('Code', required=True),  
                'outlet_type': fields.many2one('outlettype.outlettype', 'Outlet Type', required=True),                
                'temp_customer':fields.char('Contact Person'),                
                'class_id':fields.many2one('sale.class', 'Class'),  
                'old_code': fields.char('Old Code'), 
                'sales_channel':fields.many2one('sale.channel', 'Sale Channels'),
                'address':fields.char('Address'),   
                'branch_id':fields.many2one('sale.branch', 'Branch'),               
                'demarcation_id': fields.many2one('sale.demarcation', 'Demarcation'),                 
                'mobile_customer': fields.boolean('Mobile Customer', help="Check this box if this contact is a mobile customer. If it's not checked, purchase people will not see it when encoding a purchase order."),
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
                print 'result',result
                print 'result_latitude',result[0]
                print 'resul_longitude',result[1]
                self.write(cr, uid, [partner.id], {
                    'partner_latitude': result[0],
                    'partner_longitude': result[1],
                    'date_localization': fields.date.context_today(self, cr, uid, context=context)
                }, context=context)
        return True
res_partner()



  





     


    
    
    
