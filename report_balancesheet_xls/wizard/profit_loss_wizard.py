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

from openerp.osv import orm
from openerp.osv import fields, osv

class AccountProfitLossWizard(orm.TransientModel):
    _name = "profit.loss.webkit"    
    _inherit = ['account.common.balance.report','accounting.report']
    _description = "Profit loss Report"
    
    _columns = {
          
        'branch_ids': fields.many2many('res.branch', 'account_profit_and_loss_report_branch_rel', 'account_id', 'branch_id', 'Branches'),
        'analytic_account_ids':  fields.many2many('account.analytic.account','account_profit_and_loss_report_analytic_rel', 'account_id', 'analytic_id', 'Analytic Account'),
        #'account_analytic_id':  fields.many2one('account.analytic.account', 'Analytic Account'),
    }
    
    def _build_comparison_context(self, cr, uid, ids, data, context=None):
        if context is None:
            context = {}
        result = {}
        result['fiscalyear'] = 'fiscalyear_id_cmp' in data['form'] and data['form']['fiscalyear_id_cmp'] or False
        result['journal_ids'] = 'journal_ids' in data['form'] and data['form']['journal_ids'] or False
        result['branch_ids'] = 'branch_ids' in data['form'] and data['form']['branch_ids'] or False
        result['account_analytic_id'] = 'account_analytic_ids' in data['form'] and data['form']['account_analytic_ids'] or False
        result['chart_account_id'] = 'chart_account_id' in data['form'] and data['form']['chart_account_id'] or False
        result['state'] = 'target_move' in data['form'] and data['form']['target_move'] or ''
        if data['form']['filter_cmp'] == 'filter_date':
            result['date_from'] = data['form']['date_from_cmp']
            result['date_to'] = data['form']['date_to_cmp']
        elif data['form']['filter_cmp'] == 'filter_period':
            if not data['form']['period_from_cmp'] or not data['form']['period_to_cmp']:
                raise osv.except_osv(_('Error!'),_('Select a starting and an ending period'))
            result['period_from'] = data['form']['period_from_cmp']
            result['period_to'] = data['form']['period_to_cmp']
        return result
    
    def _build_contexts(self, cr, uid, ids, data, context=None):
        if context is None:
            context = {}
        result = {}
        result['fiscalyear'] = 'fiscalyear_id' in data['form'] and data['form']['fiscalyear_id'] or False
        result['journal_ids'] = 'journal_ids' in data['form'] and data['form']['journal_ids'] or False
        result['branch_ids'] = 'branch_ids' in data['form'] and data['form']['branch_ids'] or False
        result['account_analytic_id'] = 'analytic_account_ids' in data['form'] and data['form']['analytic_account_ids'] or False
        result['chart_account_id'] = 'chart_account_id' in data['form'] and data['form']['chart_account_id'] or False
        result['state'] = 'target_move' in data['form'] and data['form']['target_move'] or ''
        if data['form']['filter'] == 'filter_date':
            result['date_from'] = data['form']['date_from']
            result['date_to'] = data['form']['date_to']
        elif data['form']['filter'] == 'filter_period':
            if not data['form']['period_from'] or not data['form']['period_to']:
                raise osv.except_osv(_('Error!'),_('Select a starting and an ending period.'))
            result['period_from'] = data['form']['period_from']
            result['period_to'] = data['form']['period_to']
        return result
    
    def check_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        data = {}
        data['ids'] = context.get('active_ids', [])
        data['model'] = context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(cr, uid, ids, ['date_from',  'date_to',  'fiscalyear_id', 'journal_ids', 'branch_ids',  'period_from', 'period_to',  'filter',  'chart_account_id', 'target_move','analytic_account_ids'], context=context)[0]
        for field in ['fiscalyear_id', 'chart_account_id', 'period_from', 'period_to']:
            if isinstance(data['form'][field], tuple):
                data['form'][field] = data['form'][field][0]
        
#         if 'analytic_account_ids' in data['form']:
#             if data['form']['analytic_account_ids']:
#                 account_analytic= data['form']['analytic_account_ids']
#                 data['form'].update(
#                                     {
#                                      "account_analytic_code":account_analytic[1],
#                                      }
#                                     )
#                 if account_analytic != False:
#                     context.update({    
#                                     "account_analytic_id":account_analytic[0],
#                                     })   
                            
        used_context = self._build_contexts(cr, uid, ids, data, context=context)
        data['form']['periods'] = used_context.get('periods', False) and used_context['periods'] or []
        data['form']['used_context'] = dict(used_context, lang=context.get('lang', 'en_US'))
        return self._print_report(cr, uid, ids, data, context=context)
    
    def pre_print_report(self, cr, uid, ids, data, context=None):
        data = super(AccountProfitLossWizard, self).pre_print_report(
            cr, uid, ids, data, context)
        data['ids'] = [data['form']['chart_account_id']]
        wizard_data = self.browse(cr, uid, ids)
        vals = {
            'fiscalyear_id': wizard_data.fiscalyear_id and wizard_data.fiscalyear_id.id or False,
            'chart_account_id': wizard_data.chart_account_id and wizard_data.chart_account_id.id or False,
            'target_move': wizard_data.target_move,
            'label_filter': wizard_data.label_filter and wizard_data.label_filter or False,
            'fiscalyear_id_cmp': wizard_data.fiscalyear_id_cmp and wizard_data.fiscalyear_id_cmp.id or False,
            'date_from_cmp': wizard_data.date_from_cmp or False,
            'date_to_cmp': wizard_data.date_to_cmp or False,
            'account_report_id': wizard_data.account_report_id and wizard_data.account_report_id.id or False
        }
        data['form'].update(vals)
        return data
        
    def xls_export(self, cr, uid, ids, context=None):
        return self.check_report(cr, uid, ids, context=context)

    def _print_report(self, cr, uid, ids, data, context=None):
        context = context or {}
        data = self.pre_print_report(cr, uid, ids, data, context=context)
        data['form'].update(self.read(cr, uid, ids, ['date_from_cmp',  'debit_credit', 'period_from_cmp', 'period_to_cmp',  'filter_cmp', 'enable_filter'], context=context)[0])
        context.update({'data': data})
        if context.get('xls_export'):
            return {'type': 'ir.actions.report.xml',
                    'report_name': 'account.account_report_profit_loss_webkit_xls',
                    'context': context,
                    'data': data}
        else:
            return {'type': 'ir.actions.report.xml',
                'report_name': 'account.account_report_profit_loss_webkit',
                'data': data,
                'context': context
                }
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

