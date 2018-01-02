# -*- coding: utf-8 -*-
#################################################################################
#
#Copyright (c) 2015-Present TidyWay Software Solution. (<https://tidyway.in/>)
#
#################################################################################

import time
from openerp.osv import osv
from openerp import api, fields, _
from openerp.exceptions import Warning
from dateutil import parser
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta

class inventory_reports(osv.osv_memory):
    _name = 'stock.inventory.reports'

    company_id = fields.Many2one('res.company', string='Company')
    warehouse_ids = fields.Many2many('stock.warehouse', string='warehouse')
    location_id = fields.Many2one('stock.location', string='Location')
    start_date = fields.Date('Beginning Date', required=True, default= lambda *a:(parser.parse(datetime.now().strftime('%Y-%m-%d')) + relativedelta(days=-1)).strftime('%Y-%m-%d'))
    end_date = fields.Date('End Date', required=True, default= lambda *a :  time.strftime('%Y-%m-%d'))
    sort_order = fields.Selection([('warehouse', 'Warehouse'), ('product_category', 'Product Category')], 'Group By', required=True, default='warehouse')
    include_zero = fields.Boolean('Include Zero Movement?', help="True, if you want to see zero movements of products.\nNote: It will consider only movements done in-between dates.", default=True)
    filter_product_ids = fields.Many2many('product.product', string='Products')
    filter_product_categ_ids = fields.Many2many('product.category', string='Categories')
    display_all_products = fields.Boolean('Display Products?', help="True, if you want to display only warehouse/categories total.", default=True)

    def onchange_sortorder(self, cr, uid, ids, sort_order, context=None):
        """
        Set blank values
        """
        res = {'value':{}}
        if sort_order == 'warehouse': res['value']['filter_product_categ_ids'] = []
        if sort_order == 'product_category': res['value']['filter_product_ids'] = []
        return res

    @api.v7
    def onchange_company_id(self, cr, uid, ids, company_id, context=None):
        """
        Make warehouse compatible with company
        """
        warehouse_ids = self.pool.get('stock.warehouse').search(cr, 1, [])
        if company_id:
            warehouse_ids = self.pool.get('stock.warehouse').search(cr, 1, [('company_id', '=', company_id)])
        return {
                'domain':
                        {
                         'warehouse_ids': [('id', 'in', warehouse_ids)]
                         },
                'value':
                        {
                        'warehouse_ids': False
                        }
                }

    @api.v7
    def onchange_warehouse(self, cr, uid, ids, warehouse_ids, context=None):
        """
        Make warehouse compatible with company
        """
        warehouse_obj = self.pool.get('stock.warehouse')
        location_obj = self.pool.get('stock.location')

        location_ids = location_obj.search(cr, uid, [('usage', '=', 'internal')])
        total_warehouses = warehouse_ids[0][2]
        if total_warehouses:
            addtional_ids = []
            for warehouse in total_warehouses:
                store_location_id = warehouse_obj.browse(cr, uid, warehouse).view_location_id.id
                addtional_ids.extend(location_obj.search(cr, uid, [('location_id', 'child_of', store_location_id), ('usage', '=', 'internal')]))
            location_ids = addtional_ids
        return {
                  'domain':
                            {
                             'location_id': [('id', 'in', location_ids)]
                             },
                'value':
                        {
                        'location_id': False
                        }
                }

    @api.multi
    def print_report(self):
        """
            Print report either by warehouse or product-category
        """
        assert len(self) == 1, 'This option should only be used for a single id at a time.'
        datas = {
                 'form': 
                        {
                            'company_id': self.company_id and [self.company_id.id] or [],
                            'warehouse_ids': [y.id for y in self.warehouse_ids],
                            'location_id': self.location_id and self.location_id.id or False,
                            'start_date': self.start_date,
                            'end_date': self.end_date,
                            'include_zero': self.include_zero,
                            'sort_order': self.sort_order,
                            'display_all_products': self.display_all_products,
                            'id': self.id,
                            'filter_product_ids': [p.id for p in self.filter_product_ids],
                            'filter_product_categ_ids': [p.id for p in self.filter_product_categ_ids] 
                        }
                }

        if [y.id for y in self.warehouse_ids] and (not self.company_id):
            self.warehouse_ids = []
            raise Warning(_('Please select company of those warehouses to get correct view.\nYou should remove all warehouses first from selection field.'))
        sort_by = self.sort_order or 'warehouse'
        if sort_by == 'product_category':
            return self.pool['report'].get_action(self._cr, self._uid, [], 'stock_inventory_report.inventory_report_by_category', data=datas)
        return self.pool['report'].get_action(self._cr, self._uid, [], 'stock_inventory_report.inventory_report_by_warehouse', data=datas)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
