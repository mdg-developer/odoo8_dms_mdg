# -*- coding: utf-8 -*-
###############################################################################
#
#   report_balancesheet_xls for Odoo
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
from .profit_loss import ProfitLossWebkit
from openerp.tools.translate import _

class profit_loss_xls(report_xls):
    column_sizes = [17, 17, 17, 17, 17, 17, 17, 17, 17, 17]

    def generate_xls_report(self, _p, _xs, data, objects, wb):
        ws = wb.add_sheet(_p.report_name[:31])
        ws.panes_frozen = True
        ws.remove_splits = True
        ws.portrait = 0  # Landscape
        ws.fit_width_to_pages = 1
        row_pos = 0
        
        branch_obj = self.pool.get('res.branch')
        branch_name = '' 
        print '_p>>>',_p  
        try:
            if _p.branch_id:
            
                for branch in branch_obj.browse(self.cr,self.uid,_p.branch_id,context=None):
                    branch_name += str(branch.branch_code) + ','
                branch_name = branch_name[:-1]    
            else:
                branch_name = 'All' 
                
        except Exception, e:     
            if _p.branch_ids:
            
                for branch in branch_obj.browse(self.cr,self.uid,_p.branch_ids,context=None):
                    branch_name += str(branch.branch_code) + ','
                branch_name = branch_name[:-1]    
            else:
                branch_name = 'All' 
        # set print header/footer
        ws.header_str = self.xls_headers['standard']
        ws.footer_str = self.xls_footers['standard']

        # Title
        cell_style = xlwt.easyxf(_xs['xls_title'])
        report_name = ' - '.join([_p.report_name.upper(),
                                 _p.company.partner_id.name,
                                 _p.company.currency_id.name])
        c_specs = [
            ('report_name', 1, 0, 'text', report_name),
        ]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(
            ws, row_pos, row_data, row_style=cell_style)

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
            ('coa', 2, 0, 'text', _('Chart of Account')),
            ('fy', 1, 0, 'text', _('Fiscal Year')),
            ('df', 2, 0, 'text', _p.filter_form ==
             'filter_date' and _('Dates Filter') or _('Periods Filter')),
            ('tm', 2, 0, 'text', _('Target Moves')),
            ('br', 2, 0, 'text', _('Branch')),

        ]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(
            ws, row_pos, row_data, row_style=cell_style_center)

        cell_format = _xs['borders_all']
        cell_style = xlwt.easyxf(cell_format)
        cell_style_center = xlwt.easyxf(cell_format + _xs['center'])
        c_specs = [
            ('coa', 2, 0, 'text', _p.chart_account.name),
            ('fy', 1, 0, 'text', _p.fiscalyear.name if _p.fiscalyear else '-'),
        ]
        df = _('From') + ': '
        if _p.filter_form == 'filter_date':
            df += _p.start_date if _p.start_date else u''
        else:
            df += _p.start_period.name if _p.start_period else u''
        df += ' ' + _('To') + ': '
        if _p.filter_form == 'filter_date':
            df += _p.stop_date if _p.stop_date else u''
        else:
            df += _p.stop_period.name if _p.stop_period else u''
        c_specs += [
            ('df', 2, 0, 'text', df),
            ('tm', 2, 0, 'text', _p.target_move),
            ('br', 2, 0, 'text', branch_name), 
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

        cell_format = _xs['borders_all']
        c_init_cell_style = xlwt.easyxf(cell_format)
        c_init_cell_style_decimal = xlwt.easyxf(
            cell_format + _xs['right'],
            num_format_str=report_xls.decimal_format)
        c_init_cell_style_decimal_bold = xlwt.easyxf(
            cell_format + _xs['right'] + _xs['bold'],
            num_format_str=report_xls.decimal_format)

        c_specs = [
            ('account', 5, 0, 'text', _('Account'), None, c_hdr_cell_style),
        ]
        if _p.debit_credit:
            c_specs = [
                ('account', 4, 0, 'text', _('Account'), None, c_hdr_cell_style),
            ]
            c_specs.append(('debit', 1, 0, 'text', _('Debit'), None, c_hdr_cell_style))
            c_specs.append(('credit', 1, 0, 'text', _('Credit'), None, c_hdr_cell_style))

        c_specs.append(('balance', 1, 0, 'text', _('Balance'), None, c_hdr_cell_style))

        if _p.enable_filter:
            c_specs.append(('balance_lbl', 1, 0, 'text', _(_p.label_filter), None, c_hdr_cell_style))

        cnt = 0
    
        c_hdr_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])

        # cell styles for aged lines
        ll_cell_format = _xs['borders_all']
        ll_cell_style = xlwt.easyxf(ll_cell_format)
        ll_cell_style_center = xlwt.easyxf(ll_cell_format + _xs['center'])
        ll_cell_style_date = xlwt.easyxf(
            ll_cell_format + _xs['left'],
            num_format_str=report_xls.date_format)
        ll_cell_style_decimal = xlwt.easyxf(
            ll_cell_format + _xs['right'],
            num_format_str=report_xls.decimal_format)

        row_pos = self.xls_write_row(ws, row_pos, c_hdr_data)
        row_start = row_pos

        cnt = 0
        for acc in _p.lines_data:
            current_account = acc['current']
            level = acc['level']
            if level:
                left_padding = ''
                left_padding += '  ' * level
                if level < 4:
                    c_specs = [('acc_title', 5, 0, 'text', left_padding + _(current_account['name']), None, c_hdr_cell_style)]
                else:
                    c_specs = [('acc_title', 5, 0, 'text', left_padding + _(current_account['name']), None, c_init_cell_style)]
                if _p.debit_credit:
                    if level < 4:
                        c_specs = [('acc_title', 4, 0, 'text', left_padding + current_account['name'], None, c_hdr_cell_style)]
                        c_specs.append(('debit', 1, 0, 'number', current_account['debit'], None, c_init_cell_style_decimal_bold))
                        c_specs.append(('credit', 1, 0, 'number', current_account['credit'] * -1, None, c_init_cell_style_decimal_bold))
                    else:
                        c_specs = [('acc_title', 4, 0, 'text', left_padding + current_account['name'], None, c_init_cell_style)]
                        c_specs.append(('debit', 1, 0, 'number', current_account['debit'], None, c_init_cell_style_decimal))
                        c_specs.append(('credit', 1, 0, 'number', current_account['credit'] * -1, None, c_init_cell_style_decimal))
                if level < 4:
                    c_specs.append(('balance', 1, 0, 'number', acc['balance'], None, c_init_cell_style_decimal_bold))
                else:
                    c_specs.append(('balance', 1, 0, 'number', acc['balance'], None, c_init_cell_style_decimal))
                if _p.enable_filter:
                    if level < 4:
                        c_specs.append(('balance_lbl', 1, 0, 'number', acc['balance_cmp'], None, c_init_cell_style_decimal_bold))
                    else:
                        c_specs.append(('balance_lbl', 1, 0, 'number', acc['balance_cmp'], None, c_init_cell_style_decimal))
                row_data = self.xls_row_template(
                    c_specs, [x[0] for x in c_specs])
                row_pos = self.xls_write_row(
                    ws, row_pos, row_data, c_title_cell_style)

profit_loss_xls('report.account.account_report_profit_loss_webkit_xls',
                   'account.account',
                   parser=ProfitLossWebkit)
