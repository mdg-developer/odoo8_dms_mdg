# -*- coding: utf-8 -*-
###############################################################################
#
#   report_aged_partner_xls for Odoo
#   Copyright (C) 2004-today OpenERP SA (<http://www.openerp.com>)
#   Copyright (C) 2016-today Geminate Consultancy Services (<http://geminatecs.com>).
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

from openerp.osv import orm
from openerp.osv import fields, osv

class inventory_reports_wizard(orm.TransientModel):
    _name = 'stock.inventory.reports'
    _inherit = 'stock.inventory.reports'

    def _build_contexts(self, cr, uid, ids, data, context=None):
        print 'inherit pl build context'
        if context is None:
            context = {}
        result = {}
        result['company_id'] = 'company_id' in data['form'] and data['form']['company_id'] or False
        result['warehouse_ids'] = 'warehouse_ids' in data['form'] and data['form']['warehouse_ids'] or False
        result['location_id'] = 'location_id' in data['form'] and data['form']['location_id'] or False
        result['start_date'] = 'start_date' in data['form'] and data['form']['start_date'] or False
        result['end_date'] = 'end_date' in data['form'] and data['form']['end_date'] or False
        return result

    def check_report(self, cr, uid, ids, context=None):
        print 'inherit pl check_report'
        if context is None:
            context = {}
        data = {}
        data['ids'] = context.get('active_ids', [])
        data['model'] = context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(cr, uid, ids, ['company_id',  'warehouse_ids',  'location_id', 'start_date', 'end_date',  'include_zero', 'display_all_products',  'sort_order',  'id', 'filter_product_ids','filter_product_categ_ids'], context=context)[0]
        for field in ['company_id', 'warehouse_ids', 'location_id', 'start_date','end_date']:
            if isinstance(data['form'][field], tuple):
                data['form'][field] = data['form'][field][0] 
                            
        used_context = self._build_contexts(cr, uid, ids, data, context=context)
        data['form']['used_context'] = dict(used_context, lang=context.get('lang', 'en_US'))
        return self._print_report(cr, uid, ids, data, context=context)
    
    def pre_print_report(self, cr, uid, ids, data, context=None):
        #data = super(inventory_reports_wizard, self).pre_print_report(cr, uid, ids, data, context)
        wizard_data = self.browse(cr, uid, ids)
        vals = {
                    'company_id': wizard_data.company_id and [wizard_data.company_id.id] or [],
                    'warehouse_ids': [y.id for y in wizard_data.warehouse_ids],
                    'location_id': wizard_data.location_id and wizard_data.location_id.id or False,
                    'start_date': wizard_data.start_date,
                    'end_date': wizard_data.end_date,
                    'include_zero': wizard_data.include_zero,
                    'sort_order': wizard_data.sort_order,
                    'display_all_products': wizard_data.display_all_products,
                    'id': wizard_data.id,
                    'filter_product_ids': [p.id for p in wizard_data.filter_product_ids],
                    'filter_product_categ_ids': [p.id for p in wizard_data.filter_product_categ_ids] 
        }
        data['form'].update(vals)
        return data

    def xls_export(self, cr, uid, ids, context=None):
        return self.check_report(cr, uid, ids, context=context)

    def _print_report(self, cr, uid, ids, data, context=None):
        context = context or {}
        if context.get('xls_export'):
            data = self.pre_print_report(cr, uid, ids, data, context=context)
            sort_by = data['form']['sort_order'] or 'warehouse'
            if sort_by == 'product_category':
                return {'type': 'ir.actions.report.xml',
                        'report_name': 'stock_inventory_report.inventory_report_by_category_xls',
                        'datas': data}
            else:
                return {'type': 'ir.actions.report.xml',
                        'report_name': 'stock_inventory_report.inventory_report_by_warehouse_xls',
                        'datas': data}
        else:
            return super(inventory_reports_wizard, self)._print_report(
                cr, uid, ids, data, context=context)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: