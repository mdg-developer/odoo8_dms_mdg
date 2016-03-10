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
from openerp.osv import orm
from openerp.osv import fields, osv
from openerp.tools.translate import _
import base64, StringIO, csv
from xlrd import open_workbook
import logging
import datetime
_logger = logging.getLogger(__name__)
header_fields = [ 'sale channel', 'postal code', 'region', 'class', 'outlet id code', 'outlet name',
                 'outlet type', 'address', 'ward', 'district', 'township', 'city/town', 'village/ village group',
                 'telephone', 'contact person', 'rb code', 'selling brand', 'branch code', 'demarcation code', 'display', 'ka_tha']


class temp_customer(osv.osv):
    _name = 'temp.customer'
    _columns = {
              'name':fields.char('Name'),
              'display_name':fields.char('Display Name'),
              'temp_customer':fields.char('Temp Customer'),
              'sales_channel':fields.char('Sale Channel'),
              'class':fields.char('Class'),
              'shop_name':fields.char('Shop Name'),
              'address':fields.char('Address'),
              'customer_code':fields.char('Customer'),
              'branch_code':fields.char('Branch Code'),
              'street':fields.char('Street'),
              'street2':fields.char('Street2'),
              'shop_type':fields.char('Shop Type'),
              'territory':fields.char('Territory'),
              'township':fields.char('Township'),
              'village ':fields.char('Village'),
              'demarcation ':fields.char('Demarcation'),
              'brand':fields.char('Brand'),
              'phone':fields.char('Phone'),
              'zip':fields.char('Zip'),
              'region':fields.char('Region'),
              'postal_code':fields.char('Postal Code'),
              'state_id':fields.char('State ID'),
              'ka_tha':fields.char('Ka_Tha'),
              'display':fields.char('Display')
    
              }
temp_customer()

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
                'temp_customer':fields.many2one('temp.customer', 'Error Log')
              
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
        res_country_state_obj = self.pool.get('res.country.state')
        outlet_obj = self.pool.get('outlettype.outlettype')
        temp_customer_obj = self.pool.get('temp.customer')
        branch_obj = self.pool.get('sale.branch')
        sale_channel_obj = self.pool.get('sale.channel')
        state_obj = self.pool.get('res.country.state')
        township_obj = self.pool.get('res.township')
        demarcation_obj = self.pool.get('sale.demarcation')
        city_obj = self.pool.get('res.city')
        class_obj = self.pool.get('sale.class')
        cr.execute('DELETE from temp_customer')
        cr.execute('select id from res_country where name like %s', ('Myanmar',))
        country_id = cr.fetchall()[0]
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
                    values.append(s.cell(row, col).value)
                excel_rows.append(values)
        con_ls = []
        amls = []
        count = val = head_count = 0
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
                    display_i = city_i = rb_code_i = postal_code_i = region_i = sale_channel_i = class_i = demarcation_i = customer_code_i = shop_name_i = shop_type_i = address_i = street_i = state_id_i = territory_i = township_i = village_i = phone_i = name_i = brand_i = branch_code_i = ka_tha_i = None
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
                        elif header_field == 'class':
                            class_i = i
                        elif header_field == 'postal code':
                            postal_code_i = i
                        elif header_field == 'region':
                            region_i = i
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
                    for f in [(display_i, 'display'), (postal_code_i, 'postal_code'), (city_i, 'city'), (rb_code_i, 'rb_code'), (region_i, 'region'), (sale_channel_i, 'sale_channel'), (class_i, 'class'), (demarcation_i, 'demarcation'), (customer_code_i, 'customer_code'), (shop_name_i, 'shop_name'), (shop_type_i, 'shop_type'), (address_i, 'address'), (street_i, 'street'), (territory_i, 'territory'), (township_i, 'township'), (village_i, 'village'), (phone_i, 'phone'), (name_i, 'name'), (brand_i, 'brand'), (branch_code_i, 'branch_code'), (ka_tha_i, 'ka_tha')]:
                        
                        if not isinstance(f[0], int):
                            err_log += '\n' + _("Invalid EXCEL file, Header '%s' is missing !") % f[1]
                    # process data lines   
            else:
                # add the without value for without header fields columns
                for i in range(0, val):
                    ln.append('')
                if ln and ln[0] and ln[0][0] not in ['#', '']:
                    
                    import_vals = {}

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
                    
                    amls.append(import_vals)
       
        if err_log:
            self.write(cr, uid, ids[0], {'note': err_log})
            self.write(cr, uid, ids[0], {'state': 'error'})
        else:
            for aml in amls:
                sale_channel_ids = township_ids = temp_id = customize_id = sale_channel_id = branch_ids = city_id = sale_channel_idcity_id = shop_id = state_ids = shop_ids = state_id = partner_id = demarcation_ids = class_ids = township_id = partner_ids = None
                value = []
                region = str(aml['region'])
                postal_code = str(aml['postal code'])
                class_name = str(aml['class'])
                customer_code = str(aml['outlet id code'])  # #in this case i check the customer id with the customer_code not to be duplicated.i make that there's not contained customer_code ,I fill this blank with customer name + count++
                shop_name = str(aml['outlet name'])
                shop_type = str(aml['outlet type'])
                address = str(aml['address'])
                street = str(aml['ward'])
                territory = str(aml['district'])
                township = str(aml['township'])
                village = str(aml['village/ village group'])
                phone = str(aml['telephone'])
                brand = str(aml['selling brand'])
                contact = str(aml['contact person'])
                city = str(aml['city/town'])
                sale_channel = str(aml['sale channel'])
                branch_code = str(aml['branch code'])
                demarcation = str(aml['demarcation code'])
                ka_tha = str(aml['ka_tha'])
                display = str(aml['display'])
                class_val = str(aml['class'])
                
                if display:
                    display = display.strip()
                if ka_tha:
                    ka_tha = ka_tha.strip()
                if branch_code:
                    branch_code = branch_code.strip()
                    branch_code = branch_code.replace('.0', '')
                if city:
                    city = city.strip()
                    cr.execute("""select id from res_city where lower(name) like %s """, (city.lower(),))
                    data = cr.fetchall()
                    if data:
                        city_id = data[0][0]
                    else:
                        city_id = None
                print 'city_id >>>', city_id
                if contact:
                    contact = contact.strip()
                if brand:
                    brand = brand.strip()
                if phone:
                    phone = phone.strip()
                    phone = phone.replace('.0', '')
                if village:
                    village = village.strip()
                if township:
                    township = township.strip()
                    cr.execute("""select id from res_township where lower(name) like %s""", (township.lower(),))
                    data = cr.fetchall()
                    township_val = {'name':township, 'code':township, 'city':city_id}
                    if data:
                        township_id = data[0][0]
                        township_obj.write(cr, uid, township_id, township_val, context=context)
                    else:
                        township_ids = township_obj.create(cr, uid, township_val, context=context)
                        township_id = township_ids
                print 'township_id >>>>', township_id
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
                if class_val:
                    class_val = class_val.strip()
                    cr.execute("""select id from sale_class where lower(name) like %s""", (class_val.lower(),))
                    data = cr.fetchall()
                    if data:
                        class_id = data[0][0]
                    class_res = {'name':class_val, 'class_code':class_val}
                    if not class_id:
                        class_ids = class_obj.create(cr, uid, class_res, context)
                    else:
                        class_obj.write(cr, uid, class_id, class_res)
                        class_ids = class_id
                        
                if demarcation:
                    demarcation = demarcation.strip()
                    cr.execute("""select id from sale_demarcation where lower(name) like %s""", (demarcation.lower(),))
                    data = cr.fetchall()
                    if data:
                        demarcation_id = data[0][0]
                    demarcation_res = {'name':demarcation, 'demarcation_desc':demarcation}
                    if not demarcation_id:
                        demarcation_ids = demarcation_obj.create(cr, uid, demarcation_res, context)
                    else:
                        demarcation_obj.write(cr, uid, demarcation_id, demarcation_res)
                        demarcation_ids = demarcation_id
                        
                if len(sale_channel) > 0:
                    sale_channel = sale_channel.strip()
                    cr.execute("""select id from sale_channel where lower(name) like %s""", (sale_channel.lower(),))
                    data = cr.fetchall()
                    if data:
                        sale_channel_id = data[0][0]
                    sale_channel = {
                                      'name':sale_channel, 'code':sale_channel}
                    if not sale_channel_id :
                        
                        sale_channel_ids = sale_channel_obj.create(cr, uid, sale_channel, context)
                    else:
                        sale_channel_obj.write(cr, uid, sale_channel_id, sale_channel)
                        sale_channel_ids = sale_channel_id
                if region:
                    region = region.strip()
                    print 'region', region   
                    state_id = state_obj.search(cr, uid, [('name', '=', region)])
                    state_res = {
                               'name':region,
                               'code':region,
                               'country_id':country_id}
                    if not state_id:
                        state_ids = state_obj.create(cr, uid, state_res, context)
                    else:
                        state_ids = state_id[0]
                print 'state_ids', state_ids   
                if branch_code:
                    branch_code = branch_code.strip()
                    print 'branch_code', branch_code   
                    branch_id = branch_obj.search(cr, uid, [('name', '=', branch_code)])
                    branch_res = {'name':branch_code, 'branch_code':branch_code}
                    if not branch_id:
                        branch_ids = branch_obj.create(cr, uid, branch_res, context)
                    else:
                        branch_obj.write(cr, uid, branch_id[0], branch_res)
                        branch_ids = branch_id[0]
                if len(shop_type) > 0:
                    shop_type = shop_type.strip()
                    shop_id = outlet_obj.search(cr, uid, [('name', '=', shop_type)])
                    shop_res = {
                                  'name':shop_type}
                    if not shop_id:

                        shop_ids = outlet_obj.create(cr, uid, shop_res, context)
                    else:
                        shop_ids = outlet_obj.write(cr, uid, shop_id[0], shop_res)
                        shop_ids = shop_id[0]
                value = {
                       'customer_code':customer_code,
                       'shop_name':shop_name,
                       'address':address,
                       'street':street,
                       'outlet_type':shop_ids,
                       'territory':territory,
                        'township':township_id,
                       'village':village,
                       'phone':phone,
                       'brand':brand,
                       'name':shop_name,
#                        'display_name':shop_name,
                       'state_id':state_ids,
                       'zip':postal_code,
                       'temp_customer':contact,
                       'branch_id':branch_ids,
                       'demarcation_id':demarcation_ids,
                       'sales_channel':sale_channel_ids,
                       'class_id':class_ids,
                       'ref':ka_tha,
                        'city':city_id,
                       'display':display }
                # ##below code is purpose for contained customer_code
            # #   print 'NOT CONTAIN CUSTOMER_CODE'
#                 if shop_name or customer_code and shop_ids and sale_channel_ids:
                if customer_code and shop_name:
                    cr.execute("""select id from res_partner where lower(customer_code) like %s""", (customer_code.lower(),))
                    data = cr.fetchall()
                    if data:
                        partner_id = data[0][0]
                    if not partner_id:
                        value['customer_code'] = customer_code
                        partner_ids = partner_obj.create(cr, uid, value, context)
                    else:
                        print 'partner_ids>>>>', partner_ids
                        partner_ids = partner_obj.write(cr, uid, partner_id, value)
#                 elif len(shop_name) == 0 or len(customer_code) == 0 or shop_id == '' or sale_channel_ids == '':   
#                     print 'this is temp_customer'
#                     temp_id = temp_customer_obj.search(cr, uid, [('customer_code', '=', customer_code)])
#                     temp_value = {'customer_code':aml['customer_code'],
#                                'shop_name':aml['shop_name'],
#                                'address':aml['address'],
#                                'street':aml['street'],
#                                'shop_type':aml['shop_type'],
#                                'territory':aml['territory'],
#                                'township':aml['township'],
#                                'village':aml['village'],
#                                'phone':aml['phone'],
#                                'brand':aml['brand'],
#                                'name':aml['name'],
#                                'sales_channel':aml['sale_channel'],
#                                'display_name':aml['name'],
#                                'temp_customer':aml['name'],
#                                'branch_code':aml['branch_code'],
#                                'rb_code':aml['rb_code'],
#                                'region':region,
#                                'postal_code':postal_code,
#                                'zip':aml['zip'],
#                                'class':class_name,
#                                'ka_tha':ka_tha,
#                                'display':display
#                            }
#                     if not temp_id:
#                     
#                         temp_customer_obj.create(cr, uid, temp_value, context)
#                     else:
#                         temp_customer_obj.write(cr, uid, temp_id[0], temp_value)
#                     print 'this is not create in res partner'
                       
            self.write(cr, uid, ids[0], {'state': 'completed'})
        print amls
