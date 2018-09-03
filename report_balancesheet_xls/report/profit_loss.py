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

from datetime import datetime
from openerp import pooler
from openerp.report import report_sxw
from openerp.tools.translate import _
from openerp.addons.account_financial_report_webkit.report.common_balance_reports import CommonBalanceReportHeaderWebkit
from openerp.addons.account_financial_report_webkit.report.webkit_parser_header_fix import HeaderFooterTextWebKitParser

def sign(number):
    return cmp(number, 0)


class ProfitLossWebkit(report_sxw.rml_parse,
                         CommonBalanceReportHeaderWebkit):

    def __init__(self, cursor, uid, name, context):
        super(ProfitLossWebkit, self).__init__(cursor, uid, name,
                                                 context=context)
        self.pool = pooler.get_pool(self.cr.dbname)
        self.cursor = self.cr

        company = self.pool.get('res.users').browse(self.cr, uid, uid,
                                                    context=context).company_id
        report_id = context.get('default_account_report_id') or context.get('account_report_id') or context['data']['form'].get('account_report_id') or False
        if report_id:
            report_name = self.pool.get('account.financial.report').browse(cursor, uid, int(report_id))
            header_report_name = ' - '.join((_(report_name and report_name.name or ''), company.name,
                                             company.currency_id.name))

            footer_date_time = self.formatLang(str(datetime.today()),
                                               date_time=True)
            get_data = self.pool.get('account.account')
            self.localcontext.update({
                'cr': cursor,
                'uid': uid,
                'report_name': _(report_name and report_name.name or ''),
                'display_account': self._get_display_account,
                'display_account_raw': self._get_display_account_raw,
                'display_target_move': self._get_display_target_move,
                'accounts': self._get_accounts_br,
                'additional_args': [
                    ('--header-font-name', 'Helvetica'),
                    ('--footer-font-name', 'Helvetica'),
                    ('--header-font-size', '10'),
                    ('--footer-font-size', '6'),
                    ('--header-left', header_report_name),
                    ('--header-spacing', '2'),
                    ('--footer-left', footer_date_time),
                    ('--footer-right', ' '.join((_('Page'), '[page]', _('of'),
                                                 '[topage]'))),
                    ('--footer-line',),
                ],
            })
            data = context.get('data')
            objects, new_ids, context_report_values = self.\
                compute_balance_data(data)
            self.localcontext.update(context_report_values)
            lines_data = self.get_lines(data, context)
            filter_form = self._get_filter(data)
            self.localcontext.update({'lines_data': lines_data})
            self.localcontext.update({'target_move': data['form']['target_move'].title()})
            self.localcontext.update({'filter_form': filter_form})
            self.localcontext.update({'enable_filter': data['form']['enable_filter']})
            self.localcontext.update({'label_filter': data['form']['label_filter']})
            self.localcontext.update({'debit_credit': data['form']['debit_credit']})
            self.localcontext.update({'branch_ids': data['form']['branch_ids']})
            self.set_context(
                objects, data, new_ids, report_type='webkit')

    def set_context(self, objects, data, ids, report_type=None, context=None):
        return super(ProfitLossWebkit, self).set_context(
            objects, data, ids, report_type=report_type)

    def get_lines(self, data, context):
        lines = []
        account_obj = self.pool.get('account.account')
        currency_obj = self.pool.get('res.currency')
        ids2 = self.pool.get('account.financial.report')._get_children_by_order(self.cr, self.uid, [data['form']['account_report_id']], context=data['form']['used_context'])
        for report in self.pool.get('account.financial.report').browse(self.cr, self.uid, ids2, context=data['form']['used_context']):
            balance = 0.0
            if report.balance:
                balance = report.balance
            vals = {
                'current': report,
                #'balance': report.balance * report.sign or 0.0,
                'balance': balance * report.sign or 0.0,
                'type': 'report',
                'level': bool(report.style_overwrite) and report.style_overwrite or report.level,
                'account_type': report.type =='sum' and 'view' or False, #used to underline the financial report balances
            }
            if data['form']['debit_credit']:
                vals['debit'] = report.debit
                vals['credit'] = report.credit
            if data['form']['enable_filter']:
                vals['balance_cmp'] = self.pool.get('account.financial.report').browse(self.cr, self.uid, report.id, context=data['form']['comparison_context']).balance * report.sign or 0.0
            lines.append(vals)
            account_ids = []
            if report.display_detail == 'no_detail':
                continue
            if report.type == 'accounts' and report.account_ids:
                account_ids = account_obj._get_children_and_consol(self.cr, self.uid, [x.id for x in report.account_ids])
            elif report.type == 'account_type' and report.account_type_ids:
                account_ids = account_obj.search(self.cr, self.uid, [('user_type','in', [x.id for x in report.account_type_ids])])
            if account_ids:
                for account in account_obj.browse(self.cr, self.uid, account_ids, context=data['form']['used_context']):
                    if report.display_detail == 'detail_flat' and account.type == 'view':
                        continue
                    flag = False
                    vals = {
                        'current': account,
                        'code': account.code,
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
                        vals['balance_cmp'] = account_obj.browse(self.cr, self.uid, account.id, context=data['form']['comparison_context']).balance * report.sign or 0.0
                        if not currency_obj.is_zero(self.cr, self.uid, account.company_id.currency_id, vals['balance_cmp']):
                            flag = True
                    if flag:
                        lines.append(vals)
        return lines

HeaderFooterTextWebKitParser(
    'report.account.account_report_profit_loss_webkit',
    'account.account',
    'addons/report_balancesheet_xls/report/templates/\
        account_report_profit_loss.mako',
    parser=ProfitLossWebkit)
