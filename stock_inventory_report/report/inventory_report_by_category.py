# -*- coding: utf-8 -*-
#################################################################################
#
#Copyright (c) 2015-Present TidyWay Software Solution. (<https://tidyway.in/>)
#
#################################################################################
import pytz

from openerp.osv import osv
from openerp.report import report_sxw
from operator import itemgetter
from itertools import groupby
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime


class inventory_report_category(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(inventory_report_category, self).__init__(cr, uid, name, context=context)
        self.begining_qty = 0.0
        self.total_in = 0.0
        self.total_out = 0.0
        self.total_int = 0.0
        self.total_adj = 0.0
        self.total_begin = 0.0
        self.total_end = 0.0
        self.total_inventory = []
        self.value_exist = {}
        self.localcontext.update({
            'get_warehouse_name': self.get_warehouse_name,
            'get_company': self._get_company,
            'get_product_name': self._product_name,
            'get_categ':self._get_categ,
            'get_lines': self._get_lines,
            'get_beginning_inventory' : self._get_beginning_inventory,
            'get_ending_inventory' : self._get_ending_inventory,
            'get_value_exist': self._get_value_exist,
            'total_in': self._total_in,
            'total_out': self._total_out,
            'total_int': self._total_int,
            'total_adj': self._total_adj,
            'total_begin': self._total_begin,
            'total_vals': self._total_vals,
            'total_end': self._total_end
        })

    def _total_in(self):
        """
        category wise inward Qty
        """
        return self.total_in

    def _total_out(self):
        """
        category wise out Qty
        """
        return self.total_out

    def _total_int(self):
        """
        category wise internal Qty
        """
        return self.total_int

    def _total_adj(self):
        """
        category wise adjustment Qty
        """
        return self.total_adj

    def _total_begin(self):
        """
        category wise begining Qty
        """
        return self.total_begin

    def _total_end(self):
        """
        category wise ending Qty
        """
        return self.total_end

    def _total_vals(self, company_id):
        """
        Grand Total Inventory
        """
        ftotal_in = ftotal_out = ftotal_int = ftotal_adj = ftotal_begin = ftotal_end = 0.0
        for data in self.total_inventory:
            for key,value in data.items():
                if key[1] == company_id:
                    ftotal_in += value['total_in']
                    ftotal_out += value['total_out']
                    ftotal_int += value['total_int']
                    ftotal_adj += value['total_adj']
                    ftotal_begin += value['total_begin']
                    ftotal_end += value['total_end']

        return ftotal_begin, ftotal_in,ftotal_out,ftotal_int,ftotal_adj,ftotal_end 

    def _get_value_exist(self,categ_id, company_id):
        """
        Compute Total Values
        """
        total_in = total_out = total_int = total_adj = total_begin = 0.0
        for warehouse in self.value_exist[categ_id]:
            total_in  += warehouse.get('product_qty_in',0.0)
            total_out  += warehouse.get('product_qty_out',0.0)
            total_int  += warehouse.get('product_qty_internal',0.0)
            total_adj  += warehouse.get('product_qty_adjustment',0.0)
            total_begin += warehouse.get('begining_qty',0.0)

        self.total_in = total_in
        self.total_out = total_out
        self.total_int = total_int
        self.total_adj = total_adj
        self.total_begin = total_begin
        self.total_end = total_begin + total_in + total_out + total_int + total_adj
        self.total_inventory.append({
                                     (categ_id,company_id):{
                                                            'total_in': total_in, 
                                                            'total_out': total_out,
                                                            'total_int':total_int,
                                                            'total_adj':total_adj,
                                                            'total_begin':total_begin,
                                                            'total_end':total_begin + total_in + total_out + total_int + total_adj
                                                            }})
        return ''

    def _get_company(self, company_ids):
        res_company_pool = self.pool.get('res.company')
        if not company_ids:
            company_ids  = res_company_pool.search(self.cr, self.uid, []) 

        #filter to only have warehouses.
        selected_companies = []
        for company_id in company_ids:
            if self.pool.get('stock.warehouse').search(self.cr, self.uid, [('company_id','=',company_id)]):
                selected_companies.append(company_id)

        return res_company_pool.read(self.cr, self.uid, selected_companies, ['name'])

    def get_warehouse_name(self, warehouse_ids):
        """
        Return warehouse names
            - WH A, WH B...
        """
        warehouse_obj = self.pool.get('stock.warehouse')
        if not warehouse_ids:
            warehouse_ids = warehouse_obj.search(self.cr, self.uid, [])
        war_detail = warehouse_obj.read(self.cr, self.uid, warehouse_ids,['name'])
        return ', '.join([lt['name'] or '' for lt in war_detail])

    def _get_beginning_inventory(self, data, company_id,product_id,current_record):
        """
        Process:
            -Pass locations , start date and product_id
        Return:
            - Beginning inventory of product for exact date
        """

        #find all warehouses and get data for that product
        warehouse_ids = data['form'] and data['form'].get('warehouse_ids',[]) or []
        if not warehouse_ids:
            warehouse_ids = self.find_warehouses(company_id)
        #find all locations from all warehouse for that company

        location_id = data['form'] and data['form'].get('location_id') or False
        if location_id:
            locations = [location_id]
        else:
            locations = self._find_locations(warehouse_ids)

        from_date = self.convert_withtimezone(data['form']['start_date']+' 00:00:00')
        self.cr.execute(''' 
                        SELECT id,coalesce(sum(qty), 0.0) as qty
                        FROM
                            ((
                            SELECT pp.id,pp.name_template, pp.default_code,m.date,
                                CASE when pt.uom_id = m.product_uom 
                                THEN u.name 
                                ELSE (select name from product_uom where id = pt.uom_id) 
                                END AS name,
                        
                                CASE when pt.uom_id = m.product_uom  
                                THEN coalesce(sum(-m.product_qty)::decimal, 0.0)
                                ELSE coalesce(sum(-m.product_qty * pu.factor / u.factor )::decimal, 0.0) 
                                END AS qty
                        
                            FROM product_product pp 
                            LEFT JOIN stock_move m ON (m.product_id=pp.id)
                            LEFT JOIN product_template pt ON (pp.product_tmpl_id=pt.id)
                            LEFT JOIN stock_location l ON (m.location_id=l.id)    
                            LEFT JOIN stock_picking p ON (m.picking_id=p.id)
                            LEFT JOIN product_uom pu ON (pt.uom_id=pu.id)
                            LEFT JOIN product_uom u ON (m.product_uom=u.id)
                            WHERE m.date <  %s AND (m.location_id in %s) AND m.state='done' AND pp.active=True AND pp.id = %s
                            GROUP BY  pp.id,pp.name_template,pt.uom_id , m.product_uom ,pp.default_code,u.name,m.date
                            ) 
                            UNION ALL
                            (
                            SELECT pp.id,pp.name_template, pp.default_code,m.date,
                                CASE when pt.uom_id = m.product_uom 
                                THEN u.name 
                                ELSE (select name from product_uom where id = pt.uom_id) 
                                END AS name,
                        
                                CASE when pt.uom_id = m.product_uom 
                                THEN coalesce(sum(m.product_qty)::decimal, 0.0)
                                ELSE coalesce(sum(m.product_qty * pu.factor / u.factor )::decimal, 0.0) 
                                END  AS qty
                            FROM product_product pp 
                            LEFT JOIN stock_move m ON (m.product_id=pp.id)
                            LEFT JOIN product_template pt ON (pp.product_tmpl_id=pt.id)
                            LEFT JOIN stock_location l ON (m.location_dest_id=l.id)    
                            LEFT JOIN stock_picking p ON (m.picking_id=p.id)
                            LEFT JOIN product_uom pu ON (pt.uom_id=pu.id)
                            LEFT JOIN product_uom u ON (m.product_uom=u.id)
                            WHERE m.date <  %s AND (m.location_dest_id in %s) AND m.state='done' AND pp.active=True AND pp.id = %s
                            GROUP BY  pp.id,pp.name_template,pt.uom_id , m.product_uom ,pp.default_code,u.name,m.date
                            ))
                        AS foo
                        GROUP BY id
                    ''',(from_date, tuple(locations),product_id, from_date, tuple(locations),product_id))

        res = self.cr.dictfetchall()
        self.begining_qty = res and res[0].get('qty',0.0) or 0.0

        current_record.update({'begining_qty': res and res[0].get('qty',0.0) or 0.0})
        return self.begining_qty

    def _get_ending_inventory(self, in_qty, out_qty,internal_qty,adjust_qty):
        """
        Process:
            -Inward, outward, internal, adjustment
        Return:
            - total of those qty
        """
        return self.begining_qty + in_qty + out_qty + internal_qty + adjust_qty

    #Report totally depends on picking type, need to check in deeply when directly move created from anywhere.
    def category_wise_value(self, start_date, end_date, locations, include_zero=False, filter_product_categ_ids=[]):
        """
        Complete data with category wise
            - In Qty (Inward Quantity to given location)
            - Out Qty(Outward Quantity to given location)
            - Internal Qty(Internal Movements(or null movements) to given location: out/in both : out must be - ,In must be + )
            - Adjustment Qty(Inventory Loss movements to given location: out/in both: out must be - ,In must be + )
        Return:
            [{},{},{}...]
        """

        self.cr.execute('''
                        SELECT pp.id AS product_id,pt.categ_id,
                            sum((
                            CASE WHEN spt.code in ('outgoing') AND sm.location_id in %s AND sourcel.usage !='inventory' AND destl.usage !='inventory' 
                            THEN -(sm.product_qty * pu.factor / pu2.factor) 
                            ELSE 0.0 
                            END
                            )) AS product_qty_out,
                        
                            sum((
                            CASE WHEN spt.code in ('incoming') AND sm.location_dest_id in %s AND sourcel.usage !='inventory' AND destl.usage !='inventory' 
                            THEN (sm.product_qty * pu.factor / pu2.factor) 
                            ELSE 0.0 
                            END
                            )) AS product_qty_in,
                        
                            sum((
                            CASE WHEN (spt.code ='internal' OR spt.code is null) AND sm.location_dest_id in %s AND sourcel.usage !='inventory' AND destl.usage !='inventory' 
                            THEN (sm.product_qty * pu.factor / pu2.factor)  
                            WHEN (spt.code ='internal' OR spt.code is null) AND sm.location_id in %s AND sourcel.usage !='inventory' AND destl.usage !='inventory' 
                            THEN -(sm.product_qty * pu.factor / pu2.factor) 
                            ELSE 0.0 
                            END
                            )) AS product_qty_internal,
                        
                            sum((
                            CASE WHEN sourcel.usage = 'inventory' AND sm.location_dest_id in %s  
                            THEN  (sm.product_qty * pu.factor / pu2.factor)
                            WHEN destl.usage ='inventory' AND sm.location_id in %s 
                            THEN -(sm.product_qty * pu.factor / pu2.factor)
                            ELSE 0.0 
                            END
                            )) AS product_qty_adjustment
                        
                        FROM product_product pp 
                        LEFT JOIN  stock_move sm ON (sm.product_id = pp.id and sm.date >= %s and sm.date <= %s and sm.state = 'done' and sm.location_id != sm.location_dest_id)
                        LEFT JOIN stock_picking sp ON (sm.picking_id=sp.id)
                        LEFT JOIN stock_picking_type spt ON (spt.id=sp.picking_type_id)
                        LEFT JOIN stock_location sourcel ON (sm.location_id=sourcel.id)
                        LEFT JOIN stock_location destl ON (sm.location_dest_id=destl.id)
                        LEFT JOIN product_uom pu ON (sm.product_uom=pu.id)
                        LEFT JOIN product_uom pu2 ON (sm.product_uom=pu2.id)
                        LEFT JOIN product_template pt ON (pp.product_tmpl_id=pt.id)
                        GROUP BY pt.categ_id, pp.id order by pt.categ_id

                        ''',(tuple(locations),tuple(locations),tuple(locations),tuple(locations),tuple(locations),tuple(locations),start_date, end_date))

        values = self.cr.dictfetchall()

        for none_to_update in values:
            if not none_to_update.get('product_qty_out'):
                none_to_update.update({'product_qty_out':0.0})
            if not none_to_update.get('product_qty_in'):
                none_to_update.update({'product_qty_in':0.0})

        #Removed zero values dictionaries
        if not include_zero:
            values = self._remove_zero_inventory(values)
        #filter by categories
        if filter_product_categ_ids:
            values = self._remove_product_cate_ids(values, filter_product_categ_ids)
        return values

    def _remove_zero_inventory(self, values):
        final_values = []
        for rm_zero in values:
            if rm_zero['product_qty_in'] == 0.0 and rm_zero['product_qty_internal'] == 0.0 and rm_zero['product_qty_out'] == 0.0 and rm_zero['product_qty_adjustment'] == 0.0:
                pass
            else: final_values.append(rm_zero)
        return final_values

    def _remove_product_cate_ids(self, values, filter_product_categ_ids):
        final_values = []
        for rm_products in values:
            if rm_products['categ_id'] not in filter_product_categ_ids:
                pass
            else: final_values.append(rm_products)
        return final_values

    def _get_categ(self, categ):
        """
        Find category name with id
        """
        return self.pool.get('product.category').read(self.cr, self.uid, categ,['name'])['name']

    def _product_name(self, product_id):
        """
        Find product name and assign to it
        """
        product = self.pool.get('product.product').name_get(self.cr, self.uid, [product_id])
        return product and product[0] and product[0][1] or ''

    def find_warehouses(self,company_id):
        """
        Find all warehouses
        """
        return self.pool.get('stock.warehouse').search(self.cr, self.uid, [('company_id','=',company_id)])

    def _find_locations(self, warehouses):
        """
            Find all warehouses stock locations and its childs.
        """
        warehouse_obj = self.pool.get('stock.warehouse')
        location_obj = self.pool.get('stock.location')

        stock_ids = [x['view_location_id'] and x['view_location_id'][0] for x in warehouse_obj.read(self.cr, 1, warehouses, ['view_location_id'])]
        return location_obj.search(self.cr, self.uid, [('location_id', 'child_of', stock_ids)])

    def convert_withtimezone(self, userdate, context=None):
        """ 
        Convert to Time-Zone with compare to UTC
        """
        user_date = datetime.strptime(userdate, DEFAULT_SERVER_DATETIME_FORMAT)
        if context and context.get('tz'):
            tz_name = context['tz']
        else:
            tz_name = self.pool.get('res.users').read(self.cr, 1, self.uid, ['tz'])['tz']
        if tz_name:
            utc = pytz.timezone('UTC')
            context_tz = pytz.timezone(tz_name)
            # not need if you give default datetime into entry ;)
            user_datetime = user_date  # + relativedelta(hours=24.0)
            local_timestamp = context_tz.localize(user_datetime, is_dst=False)
            user_datetime = local_timestamp.astimezone(utc)
            return user_datetime.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        return user_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT)

    def _get_lines(self, data, company):
        """
        Process:
            Pass start date, end date, locations to get data from moves,
            Merge those data with locations,
        Return:
            {category : [{},{},{}...], category : [{},{},{}...],...}
        """

        start_date = self.convert_withtimezone(data['form']['start_date']+' 00:00:00')
        end_date =  self.convert_withtimezone(data['form']['end_date']+' 23:59:59')

        warehouse_ids = data['form'] and data['form'].get('warehouse_ids',[]) or []
        include_zero = data['form'] and data['form'].get('include_zero') or False
        filter_product_categ_ids = data['form'] and data['form'].get('filter_product_categ_ids') or []
        if not warehouse_ids:
            warehouse_ids = self.find_warehouses(company)

        #find all locations from all warehouse for that company
        location_id = data['form'] and data['form'].get('location_id') or False
        if location_id:
            locations = [location_id]
        else:
            locations = self._find_locations(warehouse_ids)

        #get data from all warehouses.
        records = self.category_wise_value(start_date, end_date, locations, include_zero,filter_product_categ_ids)

        #records by categories
        sort_by_categories = sorted(records, key=itemgetter('categ_id'))
        records_by_categories = dict((k, [v for v in itr]) for k, itr in groupby(sort_by_categories, itemgetter('categ_id')))

        self.value_exist = records_by_categories
        return records_by_categories

class inventory_report_by_category(osv.AbstractModel):
    _name = 'report.stock_inventory_report.inventory_report_by_category'
    _inherit = 'report.abstract_report'
    _template = 'stock_inventory_report.inventory_report_by_category'
    _wrapped_report_class = inventory_report_category

#report_sxw.report_sxw('report.stock.inventory.reports.by.category','stock.inventory','addons/inventory_reports/report/inventory_report_by_category.rml',parser=inventory_report_by_category, header='internal')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
