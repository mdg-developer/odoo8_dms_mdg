##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
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

import time

from openerp.report import report_sxw
from common_report_header import common_report_header
from openerp.tools.translate import _
from openerp.osv import osv


class report_account_common(report_sxw.rml_parse, common_report_header):

    def __init__(self, cr, uid, name, context=None):
        super(report_account_common, self).__init__(cr, uid, name, context=context)
        self.localcontext.update( {
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
        
    def _get_analytic_code(self, data):
        if data['form']['account_analytic_id']:
            return data['form']['account_analytic_id'][1]
        return ''

    def set_context(self, objects, data, ids, report_type=None):
        new_ids = ids
        if (data['model'] == 'ir.ui.menu'):
            new_ids = 'chart_account_id' in data['form'] and [data['form']['chart_account_id']] or []
            objects = self.pool.get('account.account').browse(self.cr, self.uid, new_ids)
        return super(report_account_common, self).set_context(objects, data, new_ids, report_type=report_type)

    def get_lines(self, data):
        lines = []
        account_obj = self.pool.get('account.account')
     
        currency_obj = self.pool.get('res.currency')
        context=data['form']['used_context']
        comparison_context = data['form']['comparison_context']
        account_analytic_id = None
        if data['form']['account_analytic_id']:
           account_analytic_id =  data['form']['account_analytic_id']
        if account_analytic_id :
            if "comparison_context" in data['form']:
                 comparison_context.update({    
                                    "account_analytic_id":account_analytic_id[0],
                                    })
            context.update({    
                                "account_analytic_id":account_analytic_id[0],
                                })
        ids2 = self.pool.get('account.financial.report')._get_children_by_order(self.cr, self.uid, [data['form']['account_report_id'][0]], context=context)
        for report in self.pool.get('account.financial.report').browse(self.cr, self.uid, ids2, context=context):
            flag = True
            #update the from period to period.
            #add to context 
            #back_period=report.back_period
            #if back_period:
                #x find out what is currently year period 1
                # find out what is current period
                #from_period = x 
                #to_period = current_period - back_period
                 #context.update({'period_from":from_period,
                 #"period_to": to_period,
                 #})
            #else  context.del('period_from'), context.del('period_to')
            if "account_analytic_code" not in context and report.account_analytic_id:
                context.update({
                                'account_analytic_id':report.account_analytic_id.id,
                                })
                report = self.pool.get('account.financial.report').browse(self.cr, self.uid, report.id, context=context)
                if int(report.balance)==0:
                    flag = False
                    continue;
            #print "before",report.name,report.balance
           # print "after",report.name,report.balance
            vals = {
                'name': report.name,
                'balance': report.balance * report.sign or 0.0,
                'type': 'report',
                'level': bool(report.style_overwrite) and report.style_overwrite or report.level,
                'account_type': report.type =='sum' and 'view' or False, #used to underline the financial report balances
            }
            
            if data['form']['debit_credit']:
                vals['debit'] = report.debit
                vals['credit'] = report.credit
            if data['form']['enable_filter']:
                vals['balance_cmp'] = self.pool.get('account.financial.report').browse(self.cr, self.uid, report.id, context=comparison_context).balance * report.sign or 0.0
            if account_analytic_id:
                        if report.account_analytic_id ==False  or account_analytic_id[0] != int(report.account_analytic_id.id):
                            flag=False 
            if flag:
                lines.append(vals)
            account_ids = []
              
            if "account_analytic_code" not in context and report.account_analytic_id:
                context.update({
                                "account_analytic_id":report.account_analytic_id.id,
                                })
                
            if report.account_analytic_id:
                vals['account_analytic_code'] = report.account_analytic_id.code
            else:
                vals['account_analytic_code'] = ""
              
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
                            
                    if account_analytic_id:
                        if report.account_analytic_id ==False  or int(account_analytic_id[0]) != int(report.account_analytic_id.id):
                            flag=False
                    if flag:
                        lines.append(vals)
        return lines


class report_financial(osv.AbstractModel):
    _name = 'report.account_financial_report_xls.report_financial_cust'
    _inherit = 'report.abstract_report'
    _template = 'account_financial_report_xls.report_financial_cust'
    _wrapped_report_class = report_account_common

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: