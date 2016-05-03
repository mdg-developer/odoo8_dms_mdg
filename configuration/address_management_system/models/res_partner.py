'''
Created on Jan 6, 2016

@author: 7th Computing
'''
from openerp.osv import fields, osv

class res_partner(osv.osv):
    _inherit = 'res.partner'
    _columns = {               
             
            'city':fields.many2one('res.city','City'),
            'township':fields.many2one('res.township','Township'),
                                  
    } 
    
    def _display_address(self, cr, uid, address, without_company=False, context=None):
    
        '''
        The purpose of this function is to build and return an address formatted accordingly to the
        standards of the country where it belongs.

        :param address: browse record of the res.partner to format
        :returns: the address formatted in a display that fit its country habits (or the default ones
            if not country is specified)
        :rtype: string
        '''

        # get the information that will be injected into the display format
        # get the address format
        address_format = address.country_id.address_format or \
              "%(street)s\n%(street2)s\n%(city)s %(state_code)s %(zip)s\n%(country_name)s"
        args = {
            'city': address.city.name or '',
            'state_code': address.state_id.code or '',
            'state_name': address.state_id.name or '',
            'country_code': address.country_id.code or '',
            'country_name': address.country_id.name or '',
            'company_name': address.parent_name or '',
        }
        for field in self._address_fields(cr, uid, context=context):
            args[field] = getattr(address, field) or ''
        if without_company:
            args['company_name'] = ''
        elif address.parent_id:
            address_format = '%(company_name)s\n' + address_format
        city_obj=args['city'].name
        if city_obj:
            args['city'] =city_obj 
        return address_format % args  
    
res_partner()

    