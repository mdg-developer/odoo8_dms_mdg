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

import xlwt
import time
from datetime import datetime
from openerp.osv import orm
from openerp.report import report_sxw
from common_report_header import common_report_header
from openerp.addons.report_xls.report_xls import report_xls
from openerp.addons.report_xls.utils import rowcol_to_cell, _render
from openerp.tools.translate import translate, _
import logging
_logger = logging.getLogger(__name__)

_ir_translation_name = 'account.financial.report.xls'

class account_financial_report_xls_parser(report_sxw.rml_parse,common_report_header):

    def __init__(self, cr, uid, name, context):
        if context is None:
            context = {}
        super(account_financial_report_xls_parser, self).__init__(cr, uid, name, context=context)
        self.context = context
        self.localcontext.update({
            '_': self._,
            'get_lines': self.get_lines,
            'time': time,
            'get_fiscalyear': self._get_fiscalyear,
            'get_account': self._get_account,
            'get_start_period': self.get_start_period,
            'get_end_period': self.get_end_period,
            'get_filter': self._get_filter,
            'get_start_date':self._get_start_date,
            'get_end_date':self._get_end_date,
            'get_target_move': self._get_target_move,
            'get_analytic_code':self._get_analytic_code,

        })
        self.context = context

    def _(self, src):
        lang = self.context.get('lang', 'en_US')
        return translate(self.cr, _ir_translation_name, 'report', lang, src) or src

    def _get_analytic_code(self, data):
        if data['form']['account_analytic_id']:
            return data['form']['account_analytic_id'][1]
        return ''
    
    def _get_selection_label(self, object, field, val, context=None):
        """ return label of selection list in language of the user """
        field_dict = self.pool.get(object._name).fields_get(self.cr, self.uid, allfields=[field], context=context)
        result_list = field_dict[field]['selection']
        result = filter(lambda x: x[0] == val, result_list)[0][1]
        return result
    
    def set_context(self, objects, data, ids, report_type=None):
        new_ids = ids
        
        new_ids = 'chart_account_id' in data['form'] and [data['form']['chart_account_id']] or []
        objects = self.pool.get('account.account').browse(self.cr, self.uid, new_ids)
        super(account_financial_report_xls_parser, self).set_context(objects, data, new_ids, report_type=report_type)

        cr = self.cr
        uid = self.uid
        context = self.context
        _ = self._

        report_name = 'financial_report'
        
        self.localcontext.update( {
            'report_name': report_name,
        })
        
      
    def get_lines(self, data):
        lines = []
        account_obj = self.pool.get('account.account')

        currency_obj = self.pool.get('res.currency')
        context=data['form']['used_context']
        comparison_context = data['form']['comparison_context']
        account_analytic_id = data['form']['account_analytic_id']
        if account_analytic_id != False:
            if "comparison_context" in data['form']:
                 comparison_context.update({
                                    "account_analytic_id":account_analytic_id[0],
                                    })
            context.update({
                                "account_analytic_id":account_analytic_id[0],
                                })
        ids2 = self.pool.get('account.financial.report')._get_children_by_order(self.cr, self.uid, [data['form']['account_report_id'][0]], context=context)
        for report in self.pool.get('account.financial.report').browse(self.cr, self.uid, ids2, context=context):
            vals = {
                'name': report.name,
                'balance': report.balance * report.sign or 0.0,
                'type': 'report',
                'level': bool(report.style_overwrite) and report.style_overwrite or report.level,
                'account_type': report.type =='sum' and 'view' or False, #used to underline the financial report balances
            }
            if report.account_analytic_id:
                vals['account_analytic_code'] = report.account_analytic_id.code
            else:
                vals['account_analytic_code'] = ""
            if account_analytic_id and report.account_analytic_id:
                analytic_id = int(account_analytic_id[0])
                if analytic_id != int(report.account_analytic_id.id):
                    continue
            if data['form']['debit_credit']:
                vals['debit'] = report.debit
                vals['credit'] = report.credit
            if data['form']['enable_filter']:
                vals['balance_cmp'] = self.pool.get('account.financial.report').browse(self.cr, self.uid, report.id, context=comparison_context).balance * report.sign or 0.0
            lines.append(vals)
            account_ids = []

            if report.display_detail == 'no_detail':
                #the rest of the loop is used to display the details of the financial report, so it's not needed here.
                continue
            if report.type == 'accounts' and report.account_ids:
                account_ids = account_obj._get_children_and_consol(self.cr, self.uid, [x.id for x in report.account_ids])
            elif report.type == 'account_type' and report.account_type_ids:
                account_ids = account_obj.search(self.cr, self.uid, [('user_type','in', [x.id for x in report.account_type_ids])])
            if account_ids:
                for account in account_obj.browse(self.cr, self.uid, account_ids, context=context):
                    #if there are accounts to display, we add them to the lines with a level equals to their level in
                    #the COA + 1 (to avoid having them with a too low level that would conflicts with the level of data
                    #financial reports for Assets, liabilities...)
                    if report.display_detail == 'detail_flat' and account.type == 'view':
                        continue
                    flag = False
                    vals = {
                        'name': account.code + ' ' + account.name,
                        'balance':  account.balance != 0 and account.balance * report.sign or account.balance,
                        'type': 'account',
                        'level': report.display_detail == 'detail_with_hierarchy' and min(account.level + 1,6) or 6, #account.level + 1
                        'account_type': account.type,
                    }

                    if data['form']['debit_credit']:
                        vals['debit'] = account.debit
                        vals['credit'] = account.credit
                    if not currency_obj.is_zero(self.cr, self.uid, account.company_id.currency_id, vals['balance']):
                        flag = True
                    if data['form']['enable_filter']:
                        vals['balance_cmp'] = account_obj.browse(self.cr, self.uid, account.id, context=comparison_context).balance * report.sign or 0.0
                        if not currency_obj.is_zero(self.cr, self.uid, account.company_id.currency_id, vals['balance_cmp']):
                            flag = True
                    if flag:
                        lines.append(vals)
        return lines
    
        

class account_financial_report_xls(report_xls):

    _column_size_acc_code = 12
    _column_size_acc_name = 60
    _column_size_values = 17
    _column_size_type = 12
    _column_size_level = 10

    def __init__(self, name, table, rml=False, parser=False, header=True, store=False):
        super(account_financial_report_xls, self).__init__(name, table, rml, parser, header, store)

        # Cell Styles
        _xs = self.xls_styles
        _xs.update({
            'fill_grey': 'pattern: pattern solid, fore_color 22;',
            'fill_blue': 'pattern: pattern solid, fore_color 27;',
            'borders_all_black': 'borders: left thin, right thin, top thin, bottom thin;',
            'borders_left_black': 'borders: left thin, right thin, top thin, bottom thin, '
                'left_colour %s, right_colour %s, top_colour %s, bottom_colour %s;' %(0, self._bc, self._bc, self._bc),
            'borders_right_black': 'borders: left thin, right thin, top thin, bottom thin, '
                'left_colour %s, right_colour %s, top_colour %s, bottom_colour %s;' %(self._bc, 0, self._bc, self._bc),
            'borders_left_right_black': 'borders: left thin, right thin, top thin, bottom thin, '
                'left_colour %s, right_colour %s, top_colour %s, bottom_colour %s;' %(0, 0, self._bc, self._bc),                
            'borders_top_black': 'borders: left thin, right thin, top thin, bottom thin, '
                'left_colour %s, right_colour %s, top_colour %s, bottom_colour %s;' %(self._bc, self._bc, 0, self._bc),
            'borders_bottom_black': 'borders: left thin, right thin, top thin, bottom thin, '
                'left_colour %s, right_colour %s, top_colour %s, bottom_colour %s;' %(self._bc, self._bc, self._bc, 0),
            'borders_left_top_black': 'borders: left thin, right thin, top thin, bottom thin, '
                'left_colour %s, right_colour %s, top_colour %s, bottom_colour %s;' %(0, self._bc, 0, self._bc),
            'borders_right_top_black': 'borders: left thin, right thin, top thin, bottom thin, '
                'left_colour %s, right_colour %s, top_colour %s, bottom_colour %s;' %(self._bc, 0, 0, self._bc),
            'borders_left_right_top_black': 'borders: left thin, right thin, top thin, bottom thin, '
                'left_colour %s, right_colour %s, top_colour %s, bottom_colour %s;' %(0, 0, 0, self._bc),
            'borders_left_bottom_black': 'borders: left thin, right thin, top thin, bottom thin, '
                'left_colour %s, right_colour %s, top_colour %s, bottom_colour %s;' %(0, self._bc, self._bc, 0),
            'borders_right_bottom_black': 'borders: left thin, right thin, top thin, bottom thin, '
                'left_colour %s, right_colour %s, top_colour %s, bottom_colour %s;' %(self._bc, 0, self._bc, 0),
            'borders_left_right_bottom_black': 'borders: left thin, right thin, top thin, bottom thin, '
                'left_colour %s, right_colour %s, top_colour %s, bottom_colour %s;' %(0, 0, self._bc, 0),
        })

        # Period Header format
        ph_cell_format = _xs['bold'] + _xs['fill_grey'] + _xs['borders_all_black']
        self.ph_empty2_cell_style = xlwt.easyxf('borders: right thin, right_colour 0;')
        self.ph_cell_style = xlwt.easyxf(ph_cell_format)
        self.ph_cell_style_center = xlwt.easyxf(ph_cell_format + _xs['center'])

        # Values Header format
        vh_cell_format = _xs['bold'] + _xs['fill_blue']
        self.vh_code_cell_style = xlwt.easyxf(vh_cell_format + _xs['borders_left_top_black'])
        self.vh_account_cell_style = xlwt.easyxf(vh_cell_format + _xs['borders_right_top_black'])
        self.vh_debit_cell_style = xlwt.easyxf(vh_cell_format + _xs['borders_left_top_black'] + _xs['right'])
        self.vh_credit_cell_style = xlwt.easyxf(vh_cell_format + _xs['borders_top_black'] + _xs['right'])
        self.vh_balance_cell_style = xlwt.easyxf(vh_cell_format + _xs['borders_right_top_black'] + _xs['right'])
        self.vh_type_cell_style = xlwt.easyxf(vh_cell_format + _xs['borders_left_right_top_black'] + _xs['center'])
        self.vh_level_cell_style = xlwt.easyxf(vh_cell_format + _xs['borders_left_right_top_black'] + _xs['center'])

        # Column Data format for accounts of type View
        av_cell_format = _xs['bold'] + _xs['fill']
        self.av_code_cell_style = xlwt.easyxf(av_cell_format + _xs['borders_left_black'])
        self.av_account_cell_style = xlwt.easyxf(av_cell_format + _xs['borders_right_black'])
        self.av_debit_cell_style = xlwt.easyxf(av_cell_format + _xs['borders_left_black'] + _xs['right'], num_format_str = report_xls.decimal_format)
        self.av_credit_cell_style = xlwt.easyxf(av_cell_format + _xs['borders_all'] + _xs['right'], num_format_str = report_xls.decimal_format)
        self.av_balance_cell_style = xlwt.easyxf(av_cell_format + _xs['borders_right_black'] + _xs['right'], num_format_str = report_xls.decimal_format)
        self.av_type_cell_style = xlwt.easyxf(av_cell_format + _xs['borders_left_right_black'] + _xs['center'])
        self.av_level_cell_style = xlwt.easyxf(av_cell_format + _xs['borders_left_right_black'] + _xs['center'])
        self.av_type_cell_style_last = xlwt.easyxf(av_cell_format + _xs['borders_left_right_bottom_black'] + _xs['center'])
        self.av_level_cell_style_last = xlwt.easyxf(av_cell_format + _xs['borders_left_right_bottom_black'] + _xs['center'])

        # Column Data format for regular accounts
        self.ar_code_cell_style = xlwt.easyxf(_xs['borders_left_black'])
        self.ar_account_cell_style = xlwt.easyxf(_xs['borders_right_black'])
        self.ar_debit_cell_style = xlwt.easyxf(_xs['borders_left_black'] + _xs['right'], num_format_str = report_xls.decimal_format)
        self.ar_credit_cell_style = xlwt.easyxf(_xs['borders_all'] + _xs['right'], num_format_str = report_xls.decimal_format)
        self.ar_balance_cell_style = xlwt.easyxf(_xs['borders_right_black'] + _xs['right'], num_format_str = report_xls.decimal_format)
        self.ar_type_cell_style = xlwt.easyxf(_xs['borders_left_right_black'] + _xs['center'])
        self.ar_level_cell_style = xlwt.easyxf(_xs['borders_left_right_black'] + _xs['center'])
        self.ar_type_cell_style_last = xlwt.easyxf(_xs['borders_left_right_bottom_black'] + _xs['center'])
        self.ar_level_cell_style_last = xlwt.easyxf(_xs['borders_left_right_bottom_black'] + _xs['center'])

        # totals
        tot_cell_format = _xs['bold'] + _xs['fill_blue']
        self.tot_code_cell_style = xlwt.easyxf(tot_cell_format + _xs['borders_left_bottom_black'])
        self.tot_account_cell_style = xlwt.easyxf(tot_cell_format + _xs['borders_right_bottom_black'])
        self.tot_debit_cell_style = xlwt.easyxf(tot_cell_format + _xs['borders_left_bottom_black'] + _xs['right'], num_format_str = report_xls.decimal_format)
        self.tot_credit_cell_style = xlwt.easyxf(tot_cell_format + _xs['borders_bottom_black'] + _xs['right'], num_format_str = report_xls.decimal_format)
        self.tot_balance_cell_style = xlwt.easyxf(tot_cell_format + _xs['borders_right_bottom_black'] + _xs['right'], num_format_str = report_xls.decimal_format)

    def _tb_report_title(self, ws, _p, row_pos, xlwt, _xs):

        cell_style = xlwt.easyxf(_xs['xls_title'])  
        report_name = _p.report_name
        c_specs = [
            ('report_name', 1, 0, 'text', report_name),
        ]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(ws, row_pos, row_data, row_style=cell_style)
        
        # write empty row to define column sizes
        #c_sizes = [self._column_size_acc_code, self._column_size_acc_name] + 3 * (len(_p.periods) + 1) * [self._column_size_values] + [self._column_size_type, self._column_size_level]
        #c_specs = [('empty%s'%i, 1, c_sizes[i], 'text', None) for i in range(0,len(c_sizes))]
        #row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        #row_pos = self.xls_write_row(ws, row_pos, row_data, set_column_size=True)

        return row_pos + 1

    def generate_xls_report(self, _p, _xs, data, objects, wb):

        sheet_name = 'financial_report'
        ws = wb.add_sheet(sheet_name)
        ws.panes_frozen = True
        ws.remove_splits = True
        ws.portrait = 0  # Landscape
        ws.fit_width_to_pages = 1
        row_pos = 0

        # set print header/footer
        ws.header_str = self.xls_headers['standard']
        ws.footer_str = self.xls_footers['standard']

        # Header
        row_pos = self._tb_report_title(ws, _p, row_pos, xlwt, _xs)
      

account_financial_report_xls('report.account.financial.report.xls', 'account.journal',
    parser=account_financial_report_xls_parser)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
