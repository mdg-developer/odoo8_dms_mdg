from openerp.osv import fields, osv
# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import fields, osv
class accounting_report(osv.osv_memory):
    _name = "account.report.general.ledger"
    _inherit = "account.report.general.ledger"
    _description = "Accounting Report"

    _columns = {
        # 'enable_filter': fields.boolean('Enable Comparison'),
        # 'account_report_id': fields.many2one('account.financial.report', 'Account Reports', required=True),
        # 'label_filter': fields.char('Column Label', help="This label will be displayed on report to show the balance computed for the given comparison filter."),
        # 'fiscalyear_id_cmp': fields.many2one('account.fiscalyear', 'Fiscal Year', help='Keep empty for all open fiscal year'),
        # 'filter_cmp': fields.selection([('filter_no', 'No Filters'), ('filter_date', 'Date'), ('filter_period', 'Periods')], "Filter by", required=True),
        # 'period_from_cmp': fields.many2one('account.period', 'Start Period'),
        # 'period_to_cmp': fields.many2one('account.period', 'End Period'),
        # 'date_from_cmp': fields.date("Start Date"),
        # 'date_to_cmp': fields.date("End Date"),
        # 'debit_credit': fields.boolean('Display Debit/Credit Columns', help="This option allows you to get more details about the way your balances are computed. Because it is space consuming, we do not allow to use it while doing a comparison."),
        'branch_ids': fields.many2many('res.branch', 'account_report_general_ledger_branch_rel', 'account_id', 'branch_id', 'Branches'),
        'account_analytic_id':  fields.many2one('account.analytic.account', 'Analytic Account'),
    }
    
    def _build_contexts(self, cr, uid, ids, data, context=None):
        print 'new build context'
        if context is None:
            context = {}
        result = {}
        result['fiscalyear'] = 'fiscalyear_id' in data['form'] and data['form']['fiscalyear_id'] or False
        result['journal_ids'] = 'journal_ids' in data['form'] and data['form']['journal_ids'] or False
        result['branch_ids'] = 'branch_ids' in data['form'] and data['form']['branch_ids'] or False
        result['account_analytic_id'] = 'account_analytic_id' in data['form'] and data['form']['account_analytic_id'] or False
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
        print 'new check_report'
        if context is None:
            context = {}
        data = {}
        data['ids'] = context.get('active_ids', [])
        data['model'] = context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(cr, uid, ids, ['date_from',  'date_to',  'fiscalyear_id', 'journal_ids', 'branch_ids' ,'period_from', 'period_to',  'filter',  'chart_account_id', 'target_move','account_analytic_id'], context=context)[0]
        
        for field in ['fiscalyear_id', 'chart_account_id', 'period_from', 'period_to']:
            if isinstance(data['form'][field], tuple):
                data['form'][field] = data['form'][field][0]
                
        if 'account_analytic_id' in data['form']:
            if data['form']['account_analytic_id']:
                account_analytic= data['form']['account_analytic_id']
                data['form'].update(
                                    {
                                     "account_analytic_code":account_analytic[1],
                                     }
                                    )
                if account_analytic != False:
                    context.update({    
                                    "account_analytic_id":account_analytic[0],
                                    })       
                    
        used_context = self._build_contexts(cr, uid, ids, data, context=context)
        print 'used_context!!!!',used_context
        data['form']['periods'] = used_context.get('periods', False) and used_context['periods'] or []
        data['form']['used_context'] = dict(used_context, lang=context.get('lang', 'en_US'))
        return self._print_report(cr, uid, ids, data, context=context)
    
    
    def _print_report(self, cr, uid, ids, data, context=None):
        if context is None:
            context = {}
        data = self.pre_print_report(cr, uid, ids, data, context=context)
        data['form'].update(self.read(cr, uid, ids, ['landscape',  'initial_balance', 'amount_currency', 'sortby', 'account_analytic_id'])[0])
        if not data['form']['fiscalyear_id']:# GTK client problem onchange does not consider in save record
            data['form'].update({'initial_balance': False})
 
        if data['form']['landscape'] is False:
            data['form'].pop('landscape')
        else:
            context['landscape'] = data['form']['landscape']
             
             
        if 'account_analytic_id' in data['form']:
            account_analytic= data['form']['account_analytic_id']
            if account_analytic != False:
                context.update({    
                                "account_analytic_id":account_analytic[0],
                                })    
 
        return self.pool['report'].get_action(cr, uid, [], 'account.report_generalledger', data=data, context=context)
    
     