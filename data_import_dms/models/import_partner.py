# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#
#    Copyright (c) 2014 Noviat nv/sa (www.noviat.com). All rights reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from __future__ import division
from openerp.osv import orm
from openerp.osv import fields, osv
from openerp.tools.translate import _
import base64, StringIO, csv
from xlrd import open_workbook
import logging
import datetime
_logger = logging.getLogger(__name__)
header_fields = ['sale channel', 'postal code', 'region', 'class', 'outlet id code', 'outlet name',
                 'outlet type', 'address', 'ward', 'district', 'township', 'city/town', 'village/ village group',
                 'telephone', 'contact person', 'rb code', 'selling brand', 'branch code', 'demarcation code', 'display',
                 'ka_tha', 'website', 'title', 'job position', 'old code', 'email', 'fax' , 'credit limit', 'credit allow',
                 'branch code','country','latitude','longitude']

class partner(osv.osv):
    _name = 'data_import.partner'
    _columns = {
              'name':fields.char('Description'),
              'import_date':fields.date('Import Date', readonly=True),
              'import_fname': fields.char('Filename', size=128),
              'import_file':fields.binary('File', required=True),
              'note':fields.text('Log'),
              'company_id': fields.many2one('res.company', 'Company', required=False),
              'state':fields.selection([
                ('draft', 'Draft'),
                ('completed', 'Completed'),
                ('error', 'Error'),
            ], 'States'),
              
              }
    _defaults = {
            'state':'draft',
            'import_date':datetime.date.today(),
                 }
    
    def _check_file_ext(self, cursor, user, ids):
        for import_file in self.browse(cursor, user, ids):
            if '.xls' in import_file.import_fname:return True
            else: return False
        return True
    
    _constraints = [(_check_file_ext, "Please import Excel file!", ['import_fname'])]
    
    def import_data(self, cr, uid, ids, context=None):
        partner_obj = self.pool.get('res.partner')
        outlet_obj = self.pool.get('outlettype.outlettype')
        branch_obj = self.pool.get('res.branch')
        sale_channel_obj = self.pool.get('sale.channel')
        state_obj = self.pool.get('res.country.state')
        township_obj = self.pool.get('res.township')
        demarcation_obj = self.pool.get('sale.demarcation')
        city_obj = self.pool.get('res.city')
        class_obj = self.pool.get('sale.class')
        title_obj = self.pool.get('res.partner.title')
        data = self.browse(cr, uid, ids)[0]
        company_id = data.company_id.id
        import_file = data.import_file
        import_filename = data.name

        err_log = ''
        header_line = False

        lines = base64.decodestring(import_file)
        wb = open_workbook(file_contents=lines)
        excel_rows = []
        for s in wb.sheets():
            # header
            headers = []
            header_row = 0
            for hcol in range(0, s.ncols):
                headers.append(s.cell(header_row, hcol).value)
            # add header
            excel_rows.append(headers)
            for row in range(header_row + 1, s.nrows):
                values = []
                for col in range(0, s.ncols):
                    cell = s.cell(row, col)
                    cell_value= cell.value
                    if cell.ctype in (2,3):
                        value_str = str(cell_value)
                        value_str = value_str.replace('.0', '') 
                    else:
                        value_str = str(cell.value.encode('utf-8'))
                    values.append(value_str)
                excel_rows.append(values)
        con_ls = []
        amls = []
        count = val = head_count = 0
        records = 0;
        for ln in excel_rows:
            # ln = [str(x).strip() for x in ln]
            if not ln or ln and ln in ['', '#']:
                continue
            # process header line
            
            if not header_line:
                for x in ln:
                    x = str(x).strip().lower()
                    if x in header_fields:
                        con_ls.append(x)
                        head_count = head_count + 1
                if head_count < 5:
                    head_count = 0
                    con_ls = []
                else:
                    if ln:
                        b3 = set(header_fields).difference(con_ls)
                        # check the columns without contained the header fields
                        if b3:
                            for l in b3:
                                ln.append(str(l))
                            val = len(b3)
                    header_line = True
                    credit_limit_i = credit_allow_i = website_i = title_i = job_position_i = old_code_i = email_i = fax_i = display_i = city_i = rb_code_i = postal_code_i = region_i = sale_channel_i = class_i = demarcation_i = customer_code_i = shop_name_i = shop_type_i = address_i = street_i = state_id_i = territory_i = township_i = village_i = phone_i = name_i = brand_i = branch_code_i = ka_tha_i = latitude_i = longitude_i = None
                    column_cnt = 0
                    for cnt in range(len(ln)):
                        if ln[cnt] == '':
                            column_cnt = cnt
                            break
                        elif cnt == len(ln) - 1:
                            column_cnt = cnt + 1
                            break
                    for i in range(column_cnt):
                        # header fields
                        header_field = ln[i].strip().lower()
                        if header_field not in header_fields:
                            err_log += '\n' + _("Invalid EXCEL File, Header Field '%s' is not supported !") % ln[i]
                        # required header fields : account, debit, credit
                
                        elif header_field == 'website':
                            website_i = i
                        elif header_field == 'title':
                            title_i = i
                        elif header_field == 'job position':
                            job_position_i = i
                        elif header_field == 'old code':
                            old_code_i = i
                        elif header_field == 'class':
                            class_i = i
                        elif header_field == 'postal code':
                            postal_code_i = i
                        elif header_field == 'email':
                            email_i = i
                        elif header_field == 'fax':
                            fax_i = i
                        elif header_field == 'region':
                            region_i = i
                        elif header_field =='division_code':
                            division_code_i=i
                        elif header_field == 'sale channel':
                            sale_channel_i = i
                        elif header_field == 'outlet id code':
                            customer_code_i = i
                        elif header_field == 'outlet name':
                            shop_name_i = i 
                        elif header_field == 'outlet type':
                            shop_type_i = i 
                        elif header_field == 'address':
                            address_i = i 
                        elif header_field == 'ward':
                            street_i = i 
                        elif header_field == 'district':
                            territory_i = i 
                        elif header_field == 'township':
                            township_i = i 
                        elif header_field == 'village/ village group':
                            village_i = i 
                        elif header_field == 'telephone':
                            phone_i = i 
                        elif header_field == 'contact person':
                            name_i = i 
                        elif header_field == 'rb code':
                            rb_code_i = i
                        elif header_field == 'city/town':
                            city_i = i
                        elif header_field == 'selling brand':
                            brand_i = i 
                        elif header_field == 'branch code':
                            branch_code_i = i
                        elif header_field == 'demarcation code':
                            demarcation_i = i
                        elif header_field == 'ka_tha':
                            ka_tha_i = i                            
                        elif header_field == 'display':
                            display_i = i          
                        elif header_field == 'credit allow':
                            credit_allow_i = i         
                        elif header_field == 'credit limit':
                            credit_limit_i = i
                        elif header_field == 'latitude':
                            latitude_i = i
                        elif header_field == 'longitude':
                            longitude_i = i                                     
                    for f in [(credit_allow_i, 'credit allow'), (credit_limit_i, 'credit limit'), (website_i, 'website'), (title_i, 'title'), (job_position_i, 'job position'), (old_code_i, 'old code'), (email_i, 'email'), (fax_i, 'fax'), (display_i, 'display'), (postal_code_i, 'postal_code'), (city_i, 'city'), (rb_code_i, 'rb_code'), (region_i, 'region'), (sale_channel_i, 'sale_channel'), (class_i, 'class'), (demarcation_i, 'demarcation'), (customer_code_i, 'customer_code'), (shop_name_i, 'shop_name'), (shop_type_i, 'shop_type'), (address_i, 'address'), (street_i, 'street'), (territory_i, 'territory'), (township_i, 'township'), (village_i, 'village'), (phone_i, 'phone'), (name_i, 'name'), (brand_i, 'brand'), (branch_code_i, 'branch_code'), (ka_tha_i, 'ka_tha'),(latitude_i, 'latitude'),(longitude_i, 'longitude')]:
                        
                        if not isinstance(f[0], int):
                            err_log += '\n' + _("Invalid EXCEL file, Header '%s' is missing !") % f[1]
                    # process data lines   
            else:
                # add the without value for without header fields columns
                for i in range(0, val):
                    ln.append('')
                if ln and ln[0] and ln[0][0] not in ['#', '']:
                    import_vals = {}
                    import_vals['website'] = ln[website_i]
                    import_vals['title'] = ln[title_i]
                    import_vals['job position'] = ln[job_position_i]
                    import_vals['old code'] = ln[old_code_i]
                    import_vals['email'] = ln[email_i]
                    import_vals['fax'] = ln[fax_i]
                    import_vals['sale channel'] = ln[sale_channel_i]
                    import_vals['class'] = ln[class_i]
                    import_vals['outlet id code'] = ln[customer_code_i]
                    import_vals['outlet name'] = ln[shop_name_i]
                    import_vals['outlet type'] = ln[shop_type_i]
                    import_vals['address'] = ln[address_i]
                    import_vals['ward'] = ln[street_i]
                    import_vals['district'] = ln[territory_i]
                    import_vals['township'] = ln[township_i]
                    import_vals['village/ village group'] = ln[village_i]
                    import_vals['telephone'] = ln[phone_i]
                    import_vals['selling brand'] = ln[brand_i]
                    import_vals['contact person'] = ln[name_i]
                    import_vals['rb code'] = ln[rb_code_i]
                    import_vals['city/town'] = ln[city_i]
                    import_vals['branch code'] = ln[branch_code_i]
                    import_vals['demarcation code'] = ln[demarcation_i]
                    import_vals['postal code'] = ln[postal_code_i]
                    import_vals['region'] = ln[region_i]
                    import_vals['ka_tha'] = ln[ka_tha_i]
                    import_vals['display'] = ln[display_i]
                    import_vals['credit allow'] = ln[credit_allow_i]
                    import_vals['credit limit'] = ln[credit_limit_i]
                    import_vals['latitude'] = ln[latitude_i]
                    import_vals['longitude'] = ln[longitude_i]
                    amls.append(import_vals)
        if err_log:
            self.write(cr, uid, ids[0], {'note': err_log})
            self.write(cr, uid, ids[0], {'state': 'error'})
        else:
            error_log = ''
            country_id = None
            if not country_id:  # no need to create or update country
                    cr.execute("""select id from res_country where lower(name) like %s""", ('myanmar',))
                    data = cr.fetchall()
                    if data:
                        country_id = data[0][0]
                    else:
                        country_id = None
                        
            for aml in amls:
                title_id = branch_id  = sale_channel_ids = township_ids = temp_id = demarcation_id = class_id = township_id = customize_id = sale_channel_id = branch_ids = city_id = sale_channel_id = city_id = shop_id = state_ids = shop_ids = state_id = partner_id = demarcation_ids = class_ids = division_code_ids = partner_ids = None
                value = []
                website = job_position = old_code = email = fax = title = region = postal_code = class_name = customer_code = shop_name = shop_type = address = street = territory = township =division= None
                village = phone = brand = contact = city = sale_channel = branch_code = demarcation = ka_tha = display = class_val = latitude = longitude = None
                credit_limit = 0
                credit_allow = False
                
                if aml['credit allow']:
                    try:
                        if str(aml['credit allow']).strip() == 'yes':
                            credit_allow = True
                        else:
                            credit_allow = False
                    except Exception, e:
                        credit_allow = False
                if aml['credit limit']:
                    credit_limit = float(aml['credit limit'])
                if aml['website']:
                    website = str(aml['website'])
                if aml['job position']:
                    job_position = str(aml['job position'])
                if aml['old code']:
                    old_code = str(aml['old code'])
                if aml['rb code']:
                    rb_code = str(aml['rb code'])   
                if aml['email']:
                    email = str(aml['email'])
                if aml['fax']:
                    fax = str(aml['fax'])
                if aml['title']:
                    title = str(aml['title'])
                if aml['region']:
                    region = str(aml['region'])
                if aml['postal code']:
                    postal_code = str(aml['postal code'])
                if aml['class']:
                    class_name = str(aml['class'])
                if aml['outlet id code']:
                    customer_code = str(aml['outlet id code'])  # #in this case i check the customer id with the customer_code not to be duplicated.i make that there's not contained customer_code ,I fill this blank with customer name + count++
                if aml['outlet name']:
                    shop_name = str(aml['outlet name'])
                if aml['outlet type']:
                    shop_type = str(aml['outlet type'])
                if  aml['address']:
                    address = str(aml['address'])
                if aml['ward']:
                    street = str(aml['ward'])
                if aml['district']:
                    territory = str(aml['district'])
                if aml['township']:
                    township = str(aml['township'])
                if aml['village/ village group']:
                    village = str(aml['village/ village group'])
                if aml['telephone']:
                    phone = str(aml['telephone'])
                if aml['selling brand']:
                    brand = str(aml['selling brand'])
                if aml['contact person']:
                    contact = str(aml['contact person'])
                if aml['city/town']:
                    city = str(aml['city/town'])
                if aml['sale channel']:
                    sale_channel = str(aml['sale channel'])
                if aml['branch code']:
                    branch_code = str(aml['branch code'])
                if aml['demarcation code']:
                    demarcation = str(aml['demarcation code'])
                if aml['ka_tha']:
                    ka_tha = str(aml['ka_tha'])
                if aml['display']:
                    display = str(aml['display'])
                if aml['class']:
                    class_val = str(aml['class'])
                if aml['latitude']:
                    latitude = aml['latitude']
                if aml['longitude']:
                    longitude = aml['longitude']   
                if website:
                    website = website.strip()
                    website = website.replace('.0', '')
                if job_position:
                    job_position = job_position.strip()
                    job_position = job_position.replace('.0', '')
                if old_code:
                    old_code = old_code.strip()
                    old_code = old_code.replace('.0', '')
                if rb_code:
                    rb_code = rb_code.strip()
                    rb_code = rb_code.replace('.0', '')
                if email:
                    email = email.strip()
                    email = email.replace('.0', '')
                if fax:
                    fax = fax.strip()
                    fax = fax.replace('.0', '')
                if title:
                    title = title.strip()
                    title = title.replace('.0', '')
                    cr.execute("""select id from res_partner_title where lower(name) like %s""", (title.lower(),))
                    data = cr.fetchall()
                    title_rel = {'name':title, 'shortcut':title, 'domain':'partner'}
                    if data:
                        title_id = data[0][0]
                    else:
                        title_id = title_obj.create(cr, uid, title_rel, context=context)
                if latitude:
                    latitude = latitude.strip()        
                if longitude:
                    longitude = longitude.strip()
                    
                        
                if display:
                    display = display.strip()
                if ka_tha:
                    ka_tha = ka_tha.strip()
                if branch_code:
                    branch_code = branch_code.strip()
                    branch_code = branch_code.replace('.0', '')
                if contact:
                    contact = contact.strip()
                if brand:
                    brand = brand.strip()
                if phone:
                    phone = phone.strip()
                    phone = phone.replace('.0', '')
                    
                if village:
                    village = village.strip()
                        
                if territory:
                    territory = territory.strip()
                    
                if street:
                    street = street.strip()
                    
                if address:
                    address = address.strip()
                    
                if shop_name:
                    shop_name = shop_name.strip()
                    shop_name = shop_name.replace('.0', '')
                    
                if customer_code:
                    customer_code = customer_code.strip()
                    
                if class_name:
                    class_name = class_name.strip()
                    
                if postal_code:
                    postal_code = postal_code.strip()
                    
                if class_val:  # no need to update
                    class_val = class_val.strip()
                    cr.execute("""select id from sale_class where lower(name) like %s""", (class_val.lower(),))
                    data = cr.fetchall()
                    if data:
                        class_id = data[0][0]
                        class_res = {'name':class_val, 'class_code':class_val.upper()}
                        if not class_id:
                            class_ids = class_obj.create(cr, uid, class_res, context)
                        else:
                            class_ids = class_id
                        
                if demarcation:  # no need to update
                    demarcation = demarcation.strip()
                    cr.execute("""select id from sale_demarcation where lower(name) like %s""", (demarcation.lower(),))
                    data = cr.fetchall()
                    if data:
                        demarcation_id = data[0][0]
                    demarcation_res = {'name':demarcation, 'demarcation_desc':demarcation}
                    if not demarcation_id:
                        demarcation_ids = demarcation_obj.create(cr, uid, demarcation_res, context)
                    else:
                        demarcation_ids = demarcation_id
                        
                if sale_channel:
                    if len(sale_channel) > 0:  # no need to update
                        sale_channel = sale_channel.strip()
                        cr.execute("""select id from sale_channel where lower(name) like %s""", (sale_channel.lower(),))
                        data = cr.fetchall()
                        if data:
                            sale_channel_id = data[0][0]
                        sale_channel = {
                                          'name':sale_channel, 'code':sale_channel.upper()}
                        if not sale_channel_id :
                            sale_channel_ids = sale_channel_obj.create(cr, uid, sale_channel, context)
                        else:
                            sale_channel_ids = sale_channel_id
                        
                if region:  # no need to update or create
                    region = region.strip()
                    cr.execute("""select id from res_country_state where lower(name) like %s""", (region.lower(),))
                    data = cr.fetchall()
                    if data:
                        state_ids = data[0][0]
                    else:
                        state_ids = self.pool.get('res.country').create(cr, uid, {
                                                                                                'code':region[:3],  # get first three words
                                                                                                'name':region,
                                                                                                'country_id':country_id
                                                                                                })

                    
                if city:  # no need to create or update city
                    city = city.strip()
                    cr.execute("""select id from res_city where lower(name) like %s """, (city.lower(),))
                    data = cr.fetchall()
                    if data:
                        city_id = data[0][0]
                    else:
                        city_id = self.pool.get('res.city').create(cr, uid, {
                                                                                                'code':city[:3],  # get first three words
                                                                                                'name':city,
                                                                                                'state_id':state_ids
                                                                                            }, context)
                    
                if township:  # no need to update or create township
                    township = township.strip()
                    cr.execute("""select id from res_township where lower(name) = %s""", (township.lower(),))
                    data = cr.fetchall()
                   
                    if data:
                        township_id = data[0][0]
                    else:
                        township_id = self.pool.get('res.township').create(cr, uid, {
                                                                                                'code':township,  # get first three words
                                                                                                'name':township,
                                                                                                'city_id':city_id
                                                                                            }, context)
                        
                if branch_code:  # no need to update
                    
                    branch_code = branch_code.strip()
                    cr.execute("""select id from res_branch where lower(branch_code) = %s """ , (branch_code.lower(),))
                    data = cr.fetchall()
                    if data:
                        branch_id = data[0][0]
                        
                    branch_res = {'branch_code':branch_code, 'name':branch_code}
                    if not branch_id:
                        branch_ids = branch_obj.create(cr, uid, branch_res, context)
                    else:
                        branch_ids = branch_id
                        
                        
                if shop_type:        
                    if len(shop_type) > 0:  # no need to update
                        shop_type = shop_type.strip()
                        cr.execute("""select id from outlettype_outlettype where lower(name) = %s """, (shop_type.lower(),))
                        data = cr.fetchall()
                        if data:
                            shop_id = data[0][0]
                        shop_res = {
                                      'name':shop_type}
                        if not shop_id:
    
                            shop_ids = outlet_obj.create(cr, uid, shop_res, context)
                        else:
                            shop_ids = shop_id
                        
                value = {
                       'customer_code':customer_code,
                       #'shop_name':shop_name,
                       'street2':address,
                       'street':street,
                       'outlet_type':shop_ids,
                       'district':territory,
                       'township':township_id,
                       'village':village,
                       'phone':phone,
                       'brand':brand,
                       'name':shop_name,
                       'country_id':country_id,
                       'state_id':state_ids,
                       'unit':postal_code,
                       'temp_customer':contact,
                       'branch_id':branch_ids,
                       'demarcation_id':demarcation_ids,
                       'sales_channel':sale_channel_ids,
                       'class_id':class_ids,
                       'ref':ka_tha,
                       'city':city_id,
                       'display':display,
                       'title':title_id,
                       'website':website,
                       'function':job_position,
                       'old_code':old_code,
                       'rb_code':rb_code,
                       'email':email,
                       'credit_allow':credit_allow,
                       'credit_limit':credit_limit,
                       'company_id':company_id,
                       'fax':fax,
                       'partner_latitude':latitude,
                       'partner_longitude':longitude}
                # ##below code is purpose for contained customer_code
#                 if shop_name or customer_code and shop_ids and sale_channel_ids:
                if shop_name:
                    if customer_code:
                        cr.execute("""select id from res_partner where lower(customer_code) like %s""", (customer_code.lower(),))
                        data = cr.fetchall()
                        if data:
                            partner_id = data[0][0]
                    if not partner_id:
                        try:
                            if customer_code:
                                value['customer_code'] = customer_code
                            records=records + 1
                            #print "record printed count:%s", records
                            print records,shop_name
                            partner_obj.create(cr, uid, value, context)
                        except Exception, e:
                            error_log += "error running"
                            
                    else:
                        partner_obj.write(cr, uid, partner_id, value)
                else:
                    error_log += ' ' + str(customer_code) + '\n'
                
            self.write(cr, uid, ids[0], {'state': 'completed', 'note':error_log})
