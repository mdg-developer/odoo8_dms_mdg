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
header_fields = [ 'sale channel','postal code','region','class','outlet id code','outlet name',
                 'outlet type','address','ward','district','township','city/town','village/ village group',
                 'telephone','contact person','rb code','selling brand','branch code','demarcation code','display','ka_tha']


class temp_customer(osv.osv):
    _name = 'temp.customer'
    _columns={
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
                'temp_customer':fields.many2one('temp.customer','Error Log')
              
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
    
    _constraints = [(_check_file_ext,"Please import Excel file!",['import_fname'])]
    
    def import_data(self, cr, uid, ids, context=None):
        partner_obj = self.pool.get('res.partner')
        res_country_state_obj=self.pool.get('res.country.state')
        shoptype_obj=self.pool.get('shoptype.shoptype')
        temp_customer_obj=self.pool.get('temp.customer')
        branch_obj= self.pool.get('sale.branch')
        sale_channel_obj = self.pool.get('sale.channel')
        state_obj =self.pool.get('res.country.state')
        demarcation_obj =self.pool.get('sale.demarcation')
        class_obj = self.pool.get('sale.class')
        cr.execute('DELETE from temp_customer')
        cr.execute('select id from res_country where name like %s',('Myanmar',))
        country_id = cr.fetchall()[0]
        data = self.browse(cr,uid,ids)[0]
        company_id = data.company_id.id
        import_file = data.import_file
        import_filename = data.name

        err_log = ''
        header_line = False

        lines = base64.decodestring(import_file)
        wb = open_workbook(file_contents = lines)
        excel_rows=[]
        for s in wb.sheets():
            #header
            headers=[]
            header_row=0
            for hcol in range(0,s.ncols):
                headers.append(s.cell(header_row,hcol).value)
            #add header
            excel_rows.append(headers)
            for row in range(header_row+1,s.nrows):
                values = []
                for col in range(0,s.ncols):
                    values.append(s.cell(row,col).value)
                excel_rows.append(values)
        amls = []

        for ln in excel_rows:

            if not ln or ln and ln[0] and ln[0][0] in ['', '#']:
                continue
            
            # process header line
                        
            if not header_line:
                if ln[0].strip().lower() not in header_fields:
                    raise orm.except_orm(_('Error :'), _("Error while processing the header line %s. \n\nPlease check your Excel separator as well as the column header fields") %ln)
                else:
                    header_line = True
                    display_i = city_i = rb_code_i = postal_code_i = region_i = sale_channel_i = class_i = demarcation_i = customer_code_i = shop_name_i = shop_type_i = address_i = street_i =  state_id_i =territory_i = township_i = village_i = phone_i = name_i = brand_i  = branch_code_i = ka_tha_i =None
                    column_cnt = 0
                    for cnt in range(len(ln)):
                        if ln[cnt] == '':
                            column_cnt = cnt
                            break
                        elif cnt == len(ln)-1:
                            column_cnt = cnt + 1
                            break
                    for i in range(column_cnt):
                        # header fields
                        header_field = ln[i].strip().lower()
                        if header_field not in header_fields:
                            err_log += '\n' + _("Invalid EXCEL File, Header Field '%s' is not supported !") %ln[i]
                        # required header fields : account, debit, credit
                        elif header_field == 'class':
                            class_i =i
                        elif header_field == 'postal code':
                            postal_code_i =i
                        elif header_field == 'region':
                            region_i =i
                        elif header_field == 'sale channel':
                            sale_channel_i =i
                        elif header_field == 'outlet id code':
                            customer_code_i =i
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
                            rb_code_i =i
                        elif header_field == 'city/town':
                            city_i =i
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
                    for f in [(display_i,'display'),(postal_code_i,'postal_code'),(city_i,'city'),(rb_code_i,'rb_code'),(region_i,'region'),(sale_channel_i,'sale_channel'),(class_i,'class'),(demarcation_i,'demarcation'),(customer_code_i,'customer_code'),(shop_name_i,'shop_name'),(shop_type_i,'shop_type'),(address_i,'address'),(street_i,'street'),(territory_i,'territory'),(township_i,'township'),(village_i,'village'),(phone_i,'phone'),(name_i,'name'),(brand_i,'brand'),(branch_code_i,'branch_code'),(ka_tha_i,'ka_tha')]:
                        
                        if not isinstance(f[0],int):
                            err_log += '\n'+ _("Invalid EXCEL file, Header '%s' is missing !") % f[1]
                    #process data lines   
            else:
                if ln and ln[0] and ln[0][0] not in ['#','']:
                    
                    import_vals = {}

                    import_vals['sale channel'] =  ln[sale_channel_i]
                    import_vals['class'] =  ln[class_i].strip()
                    import_vals['outlet id code'] =  ln[customer_code_i].strip()
                    import_vals['outlet name'] =  ln[shop_name_i]
                    import_vals['outlet type'] =  ln[shop_type_i].strip()
                    import_vals['address'] =  ln[address_i].strip()
                    import_vals['ward'] =  ln[street_i].strip()
                    import_vals['district'] =  ln[territory_i].strip()
                    import_vals['township'] =  ln[township_i].strip()
                    import_vals['village/ village group'] =  ln[village_i].strip()
                    import_vals['telephone'] =  ln[phone_i]
                    import_vals['selling brand'] =  ln[brand_i].strip()
                    import_vals['contact person'] =  ln[name_i].strip()
                    import_vals['rb code'] =  ln[rb_code_i].strip()
                    import_vals['city/town'] =  ln[city_i].strip()
                    import_vals['branch code'] = ln[branch_code_i].strip()
                    import_vals['demarcation code'] = ln[demarcation_i].strip()
                    import_vals['postal code'] = ln[postal_code_i].strip()
                    import_vals['region'] = ln[region_i].strip()
                    import_vals['ka_tha'] = ln[ka_tha_i].strip()
                    import_vals['display'] = ln[display_i].strip()
                    
                    amls.append(import_vals)
       
        if err_log:
            self.write(cr, uid, ids[0], {'note': err_log})
            self.write(cr, uid, ids[0], {'state': 'failed'})
        else:
            for aml in amls:
                temp_id = customize_id = shop_id =state_ids = shop_ids = state_id = partner_id = None
                value=[]
                region = aml['region']
                postal_code = aml['postal code']
                class_name = aml['class']
                customer_code = aml['outlet id code']##in this case i check the customer id with the customer_code not to be duplicated.i make that there's not contained customer_code ,I fill this blank with customer name + count++
                shop_name = aml['outlet name']
                shop_type = aml['outlet type']
                address = aml['address']
                street  = aml['ward']
                territory = aml['district']
                township = aml['township']
                village = aml['village/ village group']
                phone = str(aml['telephone'])
                brand = aml['selling brand']
                contact  = aml['contact person']
                rb_code  = aml['rb code']
                city  = aml['city/town']
                sale_channel= aml['sale channel']
                branch_code = aml['branch code']
                demarcation = aml['demarcation code']
                ka_tha = aml['ka_tha']
                display=aml['display']
                class_val=aml['class']
                if class_val:
                    class_id=class_obj.search(cr,uid,[('name','=',class_val)])
                    class_res= {'name':class_val,'class_code':class_val}
                    if not class_id:
                        class_ids=class_obj.create(cr,uid,class_res,context)
                    
                    else:
                        class_obj.write(cr,uid,class_id[0],class_res)
                        class_ids=class_id[0]
                if demarcation:
                    demarcation_id= demarcation_obj.search(cr,uid,[('name','=',demarcation)])
                    demarcation_res={'name':demarcation,'demarcation_desc':demarcation}
                    if not demarcation_id:
                        demarcation_ids=demarcation_obj.create(cr,uid,demarcation_res,context)
                    else:
                        demarcation_obj.write(cr,uid,demarcation_id[0],demarcation_res)
                        demarcation_ids=demarcation_id[0]
                    
                if len(sale_channel)>0:
                    sale_channel_id = sale_channel_obj.search(cr,uid,[('name','=',sale_channel)])
                    sale_channel={
                                      'name':sale_channel}
                    if not sale_channel_id :
                        
                        sale_channel_ids= sale_channel_obj.create(cr,uid,sale_channel,context)
                    else:
                        sale_channel_obj.write(cr,uid,sale_channel_id[0],sale_channel)
                        sale_channel_ids= sale_channel_id[0]
                if region:
                    state_id = state_obj.search(cr,uid,[('name','=',region)])
                    state_res={
                               'name':region,
                               'code':region,
                               'country_id':country_id}
                    if not state_id:
                        state_ids = state_obj.create(cr,uid,state_res,context)
                    else:
                        state_ids = state_id[0]
                if branch_code:
                    branch_id=branch_obj.search(cr,uid,[('name','=',branch_code)])
                    branch_res={'name':branch_code,'branch_code':branch_code}
                    if not branch_id:
                        branch_ids=branch_obj.create(cr,uid,branch_res,context)
                    else:
                        branch_obj.write(cr,uid,branch_id[0],branch_res)
                        branch_ids=branch_id[0]
                if len(shop_type)>0:
                    shop_id = shoptype_obj.search(cr,uid,[('name','=',shop_type)])
                    shop_res={
                                  'name':shop_type}
                    if not shop_id:

                        shop_ids=shoptype_obj.create(cr,uid,shop_res,context)
                    else:
                        shop_ids=shoptype_obj.write(cr,uid,shop_id[0],shop_res)
                        shop_ids=shop_id[0]
                value={
                       'customer_code':customer_code,
                       'shop_name':shop_name,
                       'address':address,
                       'street':street,
                       'shop_type':shop_ids,
                       'territory':territory,
                       'township':township,
                       'village':village,
                       'phone':phone,
                       'brand':brand,
                       'name':shop_name,
                       'rb_code':rb_code,
                       'display_name':shop_name,
                       'state_id':state_ids,
                       'zip':postal_code,
                       'temp_customer':contact,
                       'branch_id':branch_ids,
                       'demarcation_id':demarcation_ids,
                       'sales_channel':sale_channel_ids,
                       'class_id':class_ids,
                       'ref':ka_tha,
                       'city':city,
                       'display':display }
                ###below code is purpose for contained customer_code
            ##   print 'NOT CONTAIN CUSTOMER_CODE'
                if len(shop_name)>0 and len(customer_code)>0 and shop_id!='' and sale_channel_ids!='':
                    partner_id = partner_obj.search(cr,uid,[('customer_code','=',customer_code)])
                    if not partner_id:
                        value['customer_code']=customer_code
                        partner_ids=partner_obj.create(cr,uid,value,context)
                    else:
                        partner_ids=partner_obj.write(cr,uid,partner_id[0],value)
                        print 'CONTAIN CUSTOMER_CODE & PARTNER_ID is ',partner_ids
                elif len(shop_name)==0 or len(customer_code)==0 or shop_id=='' or sale_channel_ids=='':   
                    print 'this is temp_customer'
                    temp_id=temp_customer_obj.search(cr,uid,[('customer_code','=',customer_code)])
                    temp_value={'customer_code':aml['customer_code'],
                               'shop_name':aml['shop_name'],
                               'address':aml['address'],
                               'street':aml['street'],
                               'shop_type':aml['shop_type'],
                               'territory':aml['territory'],
                               'township':aml['township'],
                               'village':aml['village'],
                               'phone':aml['phone'],
                               'brand':aml['brand'],
                               'name':aml['name'],
                               'sales_channel':aml['sale_channel'],
                               'display_name':aml['name'],
                               'temp_customer':aml['name'],
                               'branch_code':aml['branch_code'],
                               'rb_code':aml['rb_code'],
                               'region':region,
                               'postal_code':postal_code,
                               'zip':aml['zip'],
                               'class':class_name,
                               'ka_tha':ka_tha,
                               'display':display
                           }
                    if not temp_id:
                    
                        temp_customer_obj.create(cr,uid,temp_value,context)
                    else:
                        temp_customer_obj.write(cr,uid,temp_id[0],temp_value)
                    print 'this is not create in res partner'
                       
            self.write(cr, uid, ids[0], {'state': 'completed'})
        
        
                
        print amls
#         cr.execute('select count(*) from temp_customer')      
#         result=cr.fetchAll()                  
#         if result>0:
            

                        
                    
                        
                            


        