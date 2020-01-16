# -*- coding: utf-8 -*-

import json
from openerp import SUPERUSER_ID
from openerp.addons.web import http
from openerp.addons.web.http import request
from openerp.tools import html_escape as escape
from openerp.addons.website.models.website import slug, unslug

class partner_map(http.Controller):
    '''
    This class generates on-the-fly partner maps that can be reused in every
    website page. To do so, just use an ``<iframe ...>`` whose ``src``
    attribute points to ``/google_map`` (this controller generates a complete
    HTML5 page).

    URL query parameters:
    - ``partner_ids``: a comma-separated list of ids (partners to be shown)
    - ``partner_url``: the base-url to display the partner
        (eg: if ``partner_url`` is ``/partners/``, when the user will click on
        a partner on the map, it will be redirected to <myodoo>.com/partners/<id>)

    In order to resize the map, simply resize the ``iframe`` with CSS
    directives ``width`` and ``height``.
    '''    
    
    @http.route(['/partner_map'], type='http', auth="public", website=True)
    def partner_map(self, *arg, **post):        
        cr, uid, context = request.cr, request.uid, request.context
        domain = [('is_company', '=', True)]
        partner_obj = request.registry['res.partner']
        partners = partner_obj.search(cr, SUPERUSER_ID, domain ,context=context)
        
        # filter real ints from query parameters and build a domain
        clean_ids = []
        for s in partners:
            print(s);
            try:
                i = int(s)
                clean_ids.append(i)
            except ValueError:
                pass

        # search for partners that can be displayed on a map
        domain = [
            ("id", "in", clean_ids), 
            ('website_published', '=', True), 
            ('is_company', '=', True),
            ('partner_latitude', '!=', False),
            ('partner_longitude', '!=', False),
            ('partner_latitude', '!=', 0.0),
            ('partner_longitude', '!=', 0.0),
            ]
#         partners_ids = partner_obj.search(cr, SUPERUSER_ID, domain, context=context)

        # browse and format data
        partner_data = {
        "counter": len(partners),
        "partners": []
        }
        
        partner_details =  partner_obj.browse(cr, SUPERUSER_ID, clean_ids,context = {'show_address': True})
#         print(partner_details);
        request.context.update({'show_address': True})
        for partner in partner_details:
            print(partner.name_get());
            partner_data["partners"].append({
                'id': partner.id,
                'name': escape(partner.name),
                'outlet_type': escape(partner.outlet_type.name or ''),
                'address': escape('\n'.join(partner.name_get()[0][1].split('\n')[1:])),
                'township': escape(partner.township.name or ''),
                'latitude': escape(str(partner.partner_latitude)),
                'longitude': escape(str(partner.partner_longitude)),
                })

        if 'customers' in post.get('partner_url', ''):
            partner_url = '/customers/'
        else:
            partner_url = '/partners/'

        # generate the map
        values = {
            'partner_url': partner_url,
            'partner_data': json.dumps(partner_data)
        }
        return request.website.render("partner_google_map.partner_map", values)
    
    @http.route(['/selected_partner_map'], type='http', auth="public", website=True)
    def get_selected_partners_map(self, *arg, **post):        
        cr, uid, context = request.cr, request.uid, request.context
        
        print(request.params);
        print(request.params['id']);
        id = request.params['id'];
        id = id.replace('[','')
        id = id.replace(']','')
        ids = id.split(',')
        domain = [('is_company', '=', True),('id', 'in', ids),('partner_latitude', '!=', False),
            ('partner_longitude', '!=', False),
            ('partner_latitude', '!=', 0.0),
            ('partner_longitude', '!=', 0.0)]
        partner_obj = request.registry['res.partner']
        partners = partner_obj.search(cr, SUPERUSER_ID, domain ,context=context)
        
        # filter real ints from query parameters and build a domain
        clean_ids = []
        for s in partners:
#             print(s);
            try:
                i = int(s)
                clean_ids.append(i)
            except ValueError:
                pass

        # search for partners that can be displayed on a map
        domain = [
            ("id", "in", clean_ids), 
            ('website_published', '=', True), 
            ('is_company', '=', True),
            ('partner_latitude', '!=', False),
            ('partner_longitude', '!=', False),
            ('partner_latitude', '!=', 0.0),
            ('partner_longitude', '!=', 0.0),
            ]
#         partners_ids = partner_obj.search(cr, SUPERUSER_ID, domain, context=context)

        # browse and format data
        partner_data = {
        "counter": len(partners),
        "partners": []
        }
        
        partner_details =  partner_obj.browse(cr, SUPERUSER_ID, clean_ids,context = {'show_address': True})
#         print(partner_details);
        request.context.update({'show_address': True})
        for partner in partner_details:
#             print(partner.name_get());
            print 'outlet_type>>>>>>>>>>',partner.outlet_type.name
            partner_data["partners"].append({
                'id': partner.id,
                'name': escape(partner.name),
                'outlet_type': escape(partner.outlet_type.name or ''),
                'address': escape('\n'.join(partner.name_get()[0][1].split('\n')[1:])),
                'township': escape(partner.township.name or ''),
                'latitude': escape(str(partner.partner_latitude)),
                'longitude': escape(str(partner.partner_longitude)),
                })

        if 'customers' in post.get('partner_url', ''):
            partner_url = '/customers/'
        else:
            partner_url = '/partners/'

        # generate the map
        values = {
            'partner_url': partner_url,
            'partner_data': json.dumps(partner_data)
        }
        return request.website.render("partner_google_map.partner_map", values)

    @http.route(['/partners_polygon_map'], type='http', auth="public", website=True)
    def get_polygon_map(self, *arg, **post):        
        cr, uid, context = request.cr, request.uid, request.context
        
        print('polygon request.params')
        print(request.params);
        print('polygon request.params[id]');
        print(request.params['id']);
        id = request.params['id'];
        id = id.replace('[','')
        id = id.replace(']','')
        ids = id.split(',')
        domain = [('is_company', '=', True),('id', 'in', ids),('partner_latitude', '!=', False),
            ('partner_longitude', '!=', False),
            ('partner_latitude', '!=', 0.0),
            ('partner_longitude', '!=', 0.0)]
        partner_obj = request.registry['res.partner']
        partners = partner_obj.search(cr, SUPERUSER_ID, domain ,context=context)
        
        # filter real ints from query parameters and build a domain
        clean_ids = []
        for s in partners:
#             print(s);
            try:
                i = int(s)
                clean_ids.append(i)
            except ValueError:
                pass

        # search for partners that can be displayed on a map
        domain = [
            ("id", "in", clean_ids), 
            ('website_published', '=', True), 
            ('is_company', '=', True),
            ('partner_latitude', '!=', False),
            ('partner_longitude', '!=', False),
            ]
#         partners_ids = partner_obj.search(cr, SUPERUSER_ID, domain, context=context)

        # browse and format data
        partner_data = {
        "counter": len(partners),
        "partners": []
        }
        
        #partner_details =  partner_obj.browse(cr, SUPERUSER_ID, clean_ids)
        partner_details =  partner_obj.browse(cr, SUPERUSER_ID, clean_ids , context = {'show_address': True})
        print('polygon partner_details')
        print(partner_details);
        request.context.update({'show_address': True})
        for partner in partner_details:
#             print(partner.name_get());
            partner_data["partners"].append({
                'id': partner.id,
                'name': escape(partner.name),
                'outlet_type': escape(partner.outlet_type.name or ''),
                'address': escape('\n'.join(partner.name_get()[0][1].split('\n')[1:])),
                'township': escape(partner.township.name or ''),
                'latitude': escape(str(partner.partner_latitude)),
                'longitude': escape(str(partner.partner_longitude)),
                })

        if 'customers' in post.get('partner_url', ''):
            partner_url = '/customers/'
        else:
            partner_url = '/partners/'

        # generate the map
        values = {
            'partner_url': partner_url,
            'partner_data': json.dumps(partner_data)
        }
        print 'map value>>>',values
        return request.website.render("partner_google_map.partners_polygon_map", values)