#-*- encoding: utf-8 -*-
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
from xlrd import open_workbook
from openerp.tools.translate import _
from datetime import datetime
import base64
import logging
_logger = logging.getLogger(__name__)
#header_fields = ['default_code', 'product_name', 'public_price', 'uom', 'balance_qty', 'cost_price']
header_fields = ['product',  'uom', 'real quantity', 'serial number','theoretical quantity','location','pack','serial']

class customer_target(osv.osv):
    _name = 'customer.target'
    _description = 'Customer Target'
    _columns = {
        'partner_id': fields.many2one('res.partner', string='Customer'),
        'outlet_type': fields.many2one('outlettype.outlettype',string="Outlet type"), 
        'address': fields.char(string='Address'), 
        'date': fields.date(string="Target Date",required=True), 
        'township': fields.many2one('res.township',string="Township"),          
        'branch_id': fields.many2one('res.branch',string="Branch"),
        'section_ids': fields.many2many('crm.case.section','customer_target_team_rel','target_id','section_id',string="Sale Team"),
        'delivery_team_id': fields.many2one('crm.case.section',string="Delivery Team"),
        'delivery': fields.char(string='Delivery'),   
        'updated_by': fields.many2one('res.user',string="Updated By"),
        'updated_time': fields.datetime(string='Updated Date Time'),
        #'target_id':fields.many2one('res.partner', 'Target Items'),                      
        'target_line_ids':fields.one2many('customer.target.line', 'line_id', 'Target Items'),
    }
    _defaults = {
       
    }
  
    def _check_file_ext(self, cursor, user, ids):
        for import_file in self.browse(cursor, user, ids):
            if '.xls' in import_file.import_fname:return True
            else: return False
        return True
    
    #_constraints = [(_check_file_ext, "Please import Excel file!", ['import_fname'])]
    
    def default_get(self, cr, uid, fields, context=None):
        if context is None: context = {}
        res = super(customer_target, self).default_get(cr, uid, fields, context=context)
        partner_ids = context.get('partner_id', False)
        if partner_ids and 'partner_id' in fields:
            for partner_id in self.pool.get('res.partner').browse(cr,uid,partner_ids,context=context):
                partner = {'partner_id': partner_id.id,'outlet_type':partner_id.outlet_type.id,'township':partner_id.township.id,'address':partner_id.street,'delivery_team_id':partner_id.delivery_team_id.id,'branch_id':partner_id.branch_id.id}
                res.update(partner)
        return res
    def get_product_from_inventory(self, cr, uid, from_location, context=None):
        location_obj = self.pool.get('stock.location')
        product_obj = self.pool.get('product.product')
        location_ids = location_obj.search(cr, uid, [('id', 'child_of', [from_location])], context=context)
        domain = ' location_id in %s'
        args = (tuple(location_ids),)
        cr.execute('''
           SELECT product_id, sum(qty) as product_qty, location_id, lot_id as prod_lot_id, package_id, owner_id as partner_id
           FROM stock_quant WHERE''' + domain + '''
           GROUP BY product_id, location_id, lot_id, package_id, partner_id
        ''', args)
        vals = []
        for product_line in cr.dictfetchall():
            # replace the None the dictionary by False, because falsy values are tested later on
            for key, value in product_line.items():
                if not value:
                    product_line[key] = False
            # product_line['inventory_id'] = inventory.id
            product_line['theoretical_qty'] = product_line['product_qty']
            if product_line['product_id']:
                product = product_obj.browse(cr, uid, product_line['product_id'], context=context)
                product_line['product_uom_id'] = product.uom_id.id
            vals.append(product_line)
        return vals   
    
    def get_so_qty(self,cr,uid,ids,t_date,context=None):
        month_count = 6
        start_date = end_date = None
        month_qty = []
        if t_date:
            year,month,date = t_date.split('-')
            cr.execute("select (%s::timestamp - '6 month'::interval)::date",(t_date,))
            start_date = cr.fetchone()[0]
            start_year,start_month,start_day = start_date.split('-')
            if start_month not in ('10','11','12'):
               start_month = start_month.replace('0','')
            customer_target_line_obj = self.pool.get('customer.target.line')
            line_ids = customer_target_line_obj.search(cr,uid,[('line_id','=',ids)],context=context)    
            for target in customer_target_line_obj.browse(cr, uid, line_ids, context):
                cr.execute("""select --case when report_uom_id is not null and report_uom_id <> t.uom_id then
                --sum(d.product_uom_qty) * floor(round(1/u.factor,2))
                sum(d.product_uom_qty) * floor(round(1/u.factor,2)) from sale_order h,sale_order_line d,product_product p,product_template t,product_uom u
                where h.id=d.order_id and d.product_id=p.id and p.product_tmpl_id=t.id and d.product_uom=u.id
                and extract(year from h.date_order::date) = %s and extract(month from h.date_order::date)=%s and d.product_id=%s
                group by d.product_id,u.factor""",(start_year,start_month,target.product_id,id))
            print 'end_date',end_date
            print 'year>>',year
            print 'month>>',month
        #if not month and year:
            #for range(0,5):
    def update(self, cr, uid, ids, context=None):
        
        
        data = self.browse(cr, uid, ids)[0]
        if data:
            self.get_so_qty(cr, uid, ids, data.date,context=None)
            self.write(cr, uid, ids, {'target_id':data.partner_id.id}, context=context)
        #import_file = data.sl_data
        # print 'file',data.sl_data
                   
customer_target()
  
class customer_target_line(osv.osv):
    _name = 'customer.target.line'
    
    def _amount_6ams(self, cr, uid, ids, name, args, context=None):
        res = dict.fromkeys(ids, 0)

#         res=dict(cr.fetchall())
        for target in self.browse(cr, uid, ids, context):
#             company_currency =  self.pool.get('res.users').browse(cr, uid, uid).company_id.currency_id.id
#             current_currency = self.pool.get('res.users').browse(cr, uid, uid).company_id.currency_id.id
#             amount = self.pool['res.currency'].compute(cr, uid, company_currency, current_currency, res.get(target.id, 0.0), context=context)
            cr.execute("""SELECT
                SUM(abs(l.month1+l.month2+l.month3+l.month4+l.month5+l.month6))/6 AS amount
            FROM
                customer_target_line l
            WHERE
                l.id IN %s GROUP BY l.line_id,l.product_id """, (tuple(ids),))
            data = cr.fetchall() 
            if data:
                amount = data[0][0]
            res[target.id] =  amount 
#         for id in ids:
#             res.setdefault(id, 0.0)
        return res
    
    _columns = {
                
                'line_id':fields.many2one('customer.target', 'Target Items'),
               
                'product_id':fields.many2one('product.product', 'Product Name'),
                'product_uom':fields.many2one('product.uom', 'UOM'),            
                
                'price':fields.float('Unit Price'),
                'month1':fields.float('Month1'),
                'month2':fields.float('Month2'),
                'month3':fields.float('Month3'),
                'month4':fields.float('Month4'),
                'month5':fields.float('Month5'),
                'month6':fields.float('Month6'),                
                '6ams': fields.function(_amount_6ams, type='float', method=True, store=True,                                            
                                             string='6 A.M.S'),
                'target_qty':fields.float('Target Qty'),
                'ach_qty':fields.float('Achieve Qty'),   
                }