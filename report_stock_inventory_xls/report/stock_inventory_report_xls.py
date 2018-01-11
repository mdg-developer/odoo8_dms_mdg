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

import xlwt
from datetime import datetime
from openerp.addons.report_xls.report_xls import report_xls
from openerp.addons.report_xls.utils import rowcol_to_cell
from openerp.tools.translate import _
from .inventory_report import inventory_report

class stock_inventory_report_xls(report_xls):
    column_sizes = [17, 17, 17, 17, 17, 17, 17, 17, 17, 17]

    def generate_xls_report(self, _p, _xs, data, objects, wb):

        ws = wb.add_sheet(_p.report_name[:31])
        ws.panes_frozen = True
        ws.remove_splits = True
        ws.portrait = 0  # Landscape
        ws.fit_width_to_pages = 1
        row_pos = 0

        # set print header/footer
        ws.header_str = self.xls_headers['standard']
        ws.footer_str = self.xls_footers['standard']
        
        company_obj = self.pool.get('res.company')
        company_name = '' 
        main_form= data.get('form')
        cid=main_form.get('company_id')
        if cid:            
            for company in company_obj.browse(self.cr,self.uid,cid,context=None):
                company_name += str(company.name) + ','
            company_name = company_name[:-1]    
        else:
            company_name = 'All' 
        # Title
        cell_style = xlwt.easyxf(_xs['xls_title'])
        report_name = ' - '.join([_p.report_name.upper()])
        c_specs = [
            ('report_name', 1, 0, 'text', 'INVENTORY REPORT'),
        ]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(
            ws, row_pos, row_data, row_style=cell_style)

        # write empty row to define column sizes
        c_sizes = self.column_sizes
        c_specs = [('empty%s' % i, 1, c_sizes[i], 'text', None)
                   for i in range(0, len(c_sizes))]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(
            ws, row_pos, row_data, set_column_size=True)

        # Header Table
        cell_format = _xs['bold'] + _xs['fill_blue'] + _xs['borders_all']
        cell_style = xlwt.easyxf(cell_format)
        cell_style_center = xlwt.easyxf(cell_format + _xs['center'])
        c_specs = [
            ('company', 2, 0, 'text', _('Company')),
            ('warehouse', 2, 0, 'text', _('Warehouse')),
            ('date', 2, 0, 'text', _('Date')),
            ('sortby', 1, 0, 'text', _('Sort By')),
        ]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(
            ws, row_pos, row_data, row_style=cell_style_center)

        cell_format = _xs['borders_all']
        cell_style = xlwt.easyxf(cell_format)
        cell_style_center = xlwt.easyxf(cell_format + _xs['center'])
        c_specs = [
            ('company', 2, 0, 'text', company_name),            
            ('warehouse', 2, 0, 'text', data['form']['warehouse_ids'] and _p.get_warehouse_name(data['form']['warehouse_ids']) or 'ALL'),
            ('date', 2, 0, 'text', data['form']['start_date'] + ' To ' + data['form']['end_date']),
            ('sortby', 1, 0, 'text', data['form']['sort_order'] if data['form']['sort_order'] else '-'),
        ]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(
            ws, row_pos, row_data, row_style=cell_style_center)
        ws.set_horz_split_pos(row_pos)
        row_pos += 1

        # Column Title Row
        cell_format = _xs['bold']
        c_title_cell_style = xlwt.easyxf(cell_format)

        # Column Header Row
        cell_format = _xs['bold'] + _xs['fill'] + _xs['borders_all']
        c_hdr_cell_style = xlwt.easyxf(cell_format)
        c_hdr_cell_style_right = xlwt.easyxf(cell_format + _xs['right'])
        c_hdr_cell_style_center = xlwt.easyxf(cell_format + _xs['center'])
        c_hdr_cell_style_decimal = xlwt.easyxf(
            cell_format + _xs['right'],
            num_format_str=report_xls.decimal_format)

        cell_format = _xs['italic'] + _xs['borders_all']
        c_init_cell_style = xlwt.easyxf(cell_format)
        c_init_cell_style_decimal = xlwt.easyxf(
            cell_format + _xs['right'],
            num_format_str=report_xls.decimal_format)
        c_init_cell_style_decimal_bold = xlwt.easyxf(
            cell_format + _xs['right'] + _xs['bold'],
            num_format_str=report_xls.decimal_format)
        
        c_specs = [
            ('product', 2, 0, 'text', _('Product'), None, c_hdr_cell_style),
            ('beginning', 1, 0, 'text', _('Beginning'), None, c_hdr_cell_style),
            ('purchase', 1, 0, 'text', _('Purchase'), None, c_hdr_cell_style),
            ('sales_return', 1, 0, 'text', _('Sales Return'), None, c_hdr_cell_style),
            ('sales', 1, 0, 'text', _('Sales'), None, c_hdr_cell_style),
            ('internal', 1, 0, 'text', _('Internal'), None, c_hdr_cell_style),
            ('adjustments', 1, 0, 'text', _('Adjustments'), None, c_hdr_cell_style),
            ('ending', 1, 0, 'text', _('Ending'), None, c_hdr_cell_style),
        ]    
        c_hdr_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])        
        row_pos = self.xls_write_row(ws, row_pos, c_hdr_data)
        for line_wh in data['form']['warehouse_ids']:
            for line in _p['get_lines'][line_wh]:
                product_name=_p.get_product_name(line.get('product_id'))
                begin_qty=_p.get_beginning_inventory(data,line.get('product_id'),line_wh,_p['get_lines'][line_wh])
                c_specs = [    
                        ('product', 2, 0, 'text', product_name or ''),                    
                        ('beginning', 1, 0, 'number', begin_qty,None, c_init_cell_style_decimal),
                        ('purchase', 1, 0, 'number', line.get('product_qty_purchase', 0.0),None, c_init_cell_style_decimal),
                        ('sales_return', 1, 0, 'number', line.get('product_qty_sales_return', 0.0),None, c_init_cell_style_decimal),
                        ('sales', 1, 0, 'number', line.get('product_qty_out', 0.0),None, c_init_cell_style_decimal),
                        ('internal', 1, 0, 'number', line.get('product_qty_internal', 0.0),None, c_init_cell_style_decimal),
                        ('adjustments', 1, 0, 'number', line.get('product_qty_adjustment', 0.0),None, c_init_cell_style_decimal),
                        ('ending', 1, 0, 'number', (begin_qty + line.get('product_qty_purchase', 0.0) + line.get('product_qty_sales_return', 0.0)
                         + line.get('product_qty_out', 0.0) + line.get('product_qty_internal', 0.0) + line.get('product_qty_adjustment', 0.0)),None, c_init_cell_style_decimal),
                    ]
                row_data = self.xls_row_template(
                    c_specs, [x[0] for x in c_specs])
                row_pos = self.xls_write_row(
                    ws, row_pos, row_data, c_title_cell_style)
            _p.get_value_exist(line_wh,cid[0])
            toal_val=_p.total_vals(cid[0])
            c_specs = [    
                        ('product', 2, 0, 'text', _p.get_warehouse_name(data['form']['warehouse_ids']) or ''),
                        ('beginning', 1, 0, 'number', toal_val[0],None, c_init_cell_style_decimal),
                        ('purchase', 1, 0, 'number',  toal_val[1],None, c_init_cell_style_decimal),
                        ('sales_return', 1, 0, 'number',  toal_val[2],None, c_init_cell_style_decimal),
                        ('sales', 1, 0, 'number',  toal_val[3],None, c_init_cell_style_decimal),
                        ('internal', 1, 0, 'number',  toal_val[4],None, c_init_cell_style_decimal),
                        ('adjustments', 1, 0, 'number',  toal_val[5],None, c_init_cell_style_decimal),
                        ('ending', 1, 0, 'number',  toal_val[6],None, c_init_cell_style_decimal),                    
                        
                    ]
            row_data = self.xls_row_template(
                c_specs, [x[0] for x in c_specs])
            row_pos = self.xls_write_row(
                ws, row_pos, row_data, c_title_cell_style)
            row_pos += 1
        total_toal_val=_p.total_vals(cid[0])
        c_specs = [    
                        ('product', 2, 0, 'text', 'Total Inventory'),
                        ('beginning', 1, 0, 'number', total_toal_val[0],None, c_init_cell_style_decimal),
                        ('purchase', 1, 0, 'number',  total_toal_val[1],None, c_init_cell_style_decimal),
                        ('sales_return', 1, 0, 'number',  total_toal_val[2],None, c_init_cell_style_decimal),
                        ('sales', 1, 0, 'number',  total_toal_val[3],None, c_init_cell_style_decimal),
                        ('internal', 1, 0, 'number',  total_toal_val[4],None, c_init_cell_style_decimal),
                        ('adjustments', 1, 0, 'number',  total_toal_val[5],None, c_init_cell_style_decimal),
                        ('ending', 1, 0, 'number',  total_toal_val[6],None, c_init_cell_style_decimal),                    
                        
                    ]
        row_data = self.xls_row_template(
                c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(
                ws, row_pos, row_data, c_title_cell_style)
        row_pos += 1

stock_inventory_report_xls('report.stock_inventory_report.inventory_report_by_warehouse_xls',
                   'stock.inventory.reports',
                   parser=inventory_report)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: