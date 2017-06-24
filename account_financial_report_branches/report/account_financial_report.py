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
    
    _name = "accounting.report.gl.branch"
    _inherit = "account.common.report"
    
    def set_context(self, objects, data, ids, report_type=None):
        new_ids = ids
        obj_move = self.pool.get('account.move.line')
        self.sortby = data['form'].get('sortby', 'sort_date')
        self.query = obj_move._query_get(self.cr, self.uid, obj='l', context=data['form'].get('used_context',{}))
        ctx2 = data['form'].get('used_context',{}).copy()
        self.init_balance = data['form'].get('initial_balance', True)
        if self.init_balance:
            ctx2.update({'initial_bal': True})
        self.init_query = obj_move._query_get(self.cr, self.uid, obj='l', context=ctx2)
        self.display_account = data['form']['display_account']
        self.target_move = data['form'].get('target_move', 'all')
        ctx = self.context.copy()
        ctx['fiscalyear'] = data['form']['fiscalyear_id']
        if data['form']['filter'] == 'filter_period':
            ctx['periods'] = data['form']['periods']
        elif data['form']['filter'] == 'filter_date':
            ctx['date_from'] = data['form']['date_from']
            ctx['date_to'] =  data['form']['date_to']
        ctx['state'] = data['form']['target_move']
        self.context.update(ctx)
        if (data['model'] == 'ir.ui.menu'):
            new_ids = [data['form']['chart_account_id']]
            objects = self.pool.get('account.account').browse(self.cr, self.uid, new_ids)
        return super(report_account_common, self).set_context(objects, data, new_ids, report_type=report_type)
    
    

    
    def __init__(self, cr, uid, name, context=None): 
        if context is None:
            context = {}
        super(report_account_common, self).__init__(cr, uid, name, context=context)
        self.query = ""
        self.tot_currency = 0.0
        self.period_sql = ""
        self.sold_accounts = {}
        self.sortby = 'sort_date' 
        
        self.localcontext.update( {
            'time': time,
            'lines': self.lines,
            'sum_debit_account': self._sum_debit_account,
            'sum_credit_account': self._sum_credit_account,
            'sum_balance_account': self._sum_balance_account,
            'sum_currency_amount_account': self._sum_currency_amount_account,
            'get_children_accounts': self.get_children_accounts,
            'get_fiscalyear': self._get_fiscalyear,
            'get_journal': self._get_journal,
            'get_account': self._get_account,
            'get_start_period': self.get_start_period,
            'get_end_period': self.get_end_period,
            'get_filter': self._get_filter,
            'get_sortby': self._get_sortby,
            'get_start_date':self._get_start_date,
            'get_end_date':self._get_end_date,
            'get_target_move': self._get_target_move,
            'get_branch_code':self._get_branch,
        })
        self.context = context

    def _sum_currency_amount_account(self, account):
        self.cr.execute('SELECT sum(l.amount_currency) AS tot_currency \
                FROM account_move_line l \
                WHERE l.account_id = %s AND %s' %(account.id, self.query))
        sum_currency = self.cr.fetchone()[0] or 0.0
        if self.init_balance:
            self.cr.execute('SELECT sum(l.amount_currency) AS tot_currency \
                            FROM account_move_line l \
                            WHERE l.account_id = %s AND %s '%(account.id, self.init_query))
            sum_currency += self.cr.fetchone()[0] or 0.0
        return sum_currency
    
    def _get_branch(self, data):
        if data['form']['branch_ids']:
            return data['form']['branch_ids'][1]
        return ''
    
    def get_children_accounts(self, account):
        res = []
        currency_obj = self.pool.get('res.currency')
        ids_acc = self.pool.get('account.account')._get_children_and_consol(self.cr, self.uid, account.id)
        currency = account.currency_id and account.currency_id or account.company_id.currency_id
        for child_account in self.pool.get('account.account').browse(self.cr, self.uid, ids_acc, context=self.context):
            sql = """
                SELECT count(id)
                FROM account_move_line AS l
                WHERE %s AND l.account_id = %%s
            """ % (self.query)
            self.cr.execute(sql, (child_account.id,))
            num_entry = self.cr.fetchone()[0] or 0
            sold_account = self._sum_balance_account(child_account)
            self.sold_accounts[child_account.id] = sold_account
            if self.display_account == 'movement':
                if child_account.type != 'view' and num_entry <> 0:
                    res.append(child_account)
            elif self.display_account == 'not_zero':
                if child_account.type != 'view' and num_entry <> 0:
                    if not currency_obj.is_zero(self.cr, self.uid, currency, sold_account):
                        res.append(child_account)
            else:
                res.append(child_account)
        if not res:
            return [account]
        return res

    def lines(self, account):
        """ Return all the account_move_line of account with their account code counterparts """
        move_state = ['draft','posted']
        if self.target_move == 'posted':
            move_state = ['posted', '']
        # First compute all counterpart strings for every move_id where this account appear.
        # Currently, the counterpart info is used only in landscape mode
        sql = """
            SELECT m1.move_id,
                array_to_string(ARRAY(SELECT DISTINCT a.code
                                          FROM account_move_line m2
                                          LEFT JOIN account_account a ON (m2.account_id=a.id)
                                          WHERE m2.move_id = m1.move_id
                                          AND m2.account_id<>%%s), ', ') AS counterpart
                FROM (SELECT move_id
                        FROM account_move_line l
                        LEFT JOIN account_move am ON (am.id = l.move_id)
                        WHERE am.state IN %s and %s AND l.account_id = %%s GROUP BY move_id) m1
        """% (tuple(move_state), self.query)
        self.cr.execute(sql, (account.id, account.id))
        counterpart_res = self.cr.dictfetchall()
        counterpart_accounts = {}
        for i in counterpart_res:
            counterpart_accounts[i['move_id']] = i['counterpart']
        del counterpart_res

        # Then select all account_move_line of this account
        if self.sortby == 'sort_journal_partner':
            sql_sort='j.code, p.name, l.move_id'
        else:
            sql_sort='l.date, l.move_id'
        print 'self.query>>>',self.query    
        sql = """
            SELECT l.id AS lid, l.date AS ldate, j.code AS lcode, l.currency_id,l.amount_currency,l.ref AS lref, l.name AS lname, COALESCE(l.debit,0) AS debit, COALESCE(l.credit,0) AS credit, l.period_id AS lperiod_id, l.partner_id AS lpartner_id,
            m.name AS move_name, m.id AS mmove_id,per.code as period_code,
            c.symbol AS currency_code,
            i.id AS invoice_id, i.type AS invoice_type, i.number AS invoice_number,
            p.name AS partner_name
            FROM account_move_line l
            JOIN account_move m on (l.move_id=m.id)
            LEFT JOIN res_currency c on (l.currency_id=c.id)
            LEFT JOIN res_partner p on (l.partner_id=p.id)
            LEFT JOIN account_invoice i on (m.id =i.move_id)
            LEFT JOIN account_period per on (per.id=l.period_id)
            JOIN account_journal j on (l.journal_id=j.id)
            WHERE %s AND m.state IN %s AND l.account_id = %%s ORDER by %s
        """ %(self.query, tuple(move_state), sql_sort)
        self.cr.execute(sql, (account.id,))
        res_lines = self.cr.dictfetchall()
        res_init = []
        if res_lines and self.init_balance:
            #FIXME: replace the label of lname with a string translatable
            sql = """
                SELECT 0 AS lid, '' AS ldate, '' AS lcode, COALESCE(SUM(l.amount_currency),0.0) AS amount_currency, '' AS lref, 'Initial Balance' AS lname, COALESCE(SUM(l.debit),0.0) AS debit, COALESCE(SUM(l.credit),0.0) AS credit, '' AS lperiod_id, '' AS lpartner_id,
                '' AS move_name, '' AS mmove_id, '' AS period_code,
                '' AS currency_code,
                NULL AS currency_id,
                '' AS invoice_id, '' AS invoice_type, '' AS invoice_number,
                '' AS partner_name
                FROM account_move_line l
                LEFT JOIN account_move m on (l.move_id=m.id)
                LEFT JOIN res_currency c on (l.currency_id=c.id)
                LEFT JOIN res_partner p on (l.partner_id=p.id)
                LEFT JOIN account_invoice i on (m.id =i.move_id)
                JOIN account_journal j on (l.journal_id=j.id)
                WHERE %s AND m.state IN %s AND l.account_id = %%s
            """ %(self.init_query, tuple(move_state))
            self.cr.execute(sql, (account.id,))
            res_init = self.cr.dictfetchall()
        res = res_init + res_lines
        account_sum = 0.0
        for l in res:
            l['move'] = l['move_name'] != '/' and l['move_name'] or ('*'+str(l['mmove_id']))
            l['partner'] = l['partner_name'] or ''
            account_sum += l['debit'] - l['credit']
            l['progress'] = account_sum
            l['line_corresp'] = l['mmove_id'] == '' and ' ' or counterpart_accounts[l['mmove_id']].replace(', ',',')
            # Modification of amount Currency
            if l['credit'] > 0:
                if l['amount_currency'] != None:
                    l['amount_currency'] = abs(l['amount_currency']) * -1
            if l['amount_currency'] != None:
                self.tot_currency = self.tot_currency + l['amount_currency']
        return res

    def _sum_debit_account(self, account):
        if account.type == 'view':
            return account.debit
        move_state = ['draft','posted']
        if self.target_move == 'posted':
            move_state = ['posted','']
        self.cr.execute('SELECT sum(debit) \
                FROM account_move_line l \
                JOIN account_move am ON (am.id = l.move_id) \
                WHERE (l.account_id = %s) \
                AND (am.state IN %s) \
                AND '+ self.query +' '
                ,(account.id, tuple(move_state)))
        sum_debit = self.cr.fetchone()[0] or 0.0
        if self.init_balance:
            self.cr.execute('SELECT sum(debit) \
                    FROM account_move_line l \
                    JOIN account_move am ON (am.id = l.move_id) \
                    WHERE (l.account_id = %s) \
                    AND (am.state IN %s) \
                    AND '+ self.init_query +' '
                    ,(account.id, tuple(move_state)))
            # Add initial balance to the result
            sum_debit += self.cr.fetchone()[0] or 0.0
        return sum_debit

    def _sum_credit_account(self, account):
        if account.type == 'view':
            return account.credit
        move_state = ['draft','posted']
        if self.target_move == 'posted':
            move_state = ['posted','']
        self.cr.execute('SELECT sum(credit) \
                FROM account_move_line l \
                JOIN account_move am ON (am.id = l.move_id) \
                WHERE (l.account_id = %s) \
                AND (am.state IN %s) \
                AND '+ self.query +' '
                ,(account.id, tuple(move_state)))
        sum_credit = self.cr.fetchone()[0] or 0.0
        if self.init_balance:
            self.cr.execute('SELECT sum(credit) \
                    FROM account_move_line l \
                    JOIN account_move am ON (am.id = l.move_id) \
                    WHERE (l.account_id = %s) \
                    AND (am.state IN %s) \
                    AND '+ self.init_query +' '
                    ,(account.id, tuple(move_state)))
            # Add initial balance to the result
            sum_credit += self.cr.fetchone()[0] or 0.0
        return sum_credit

    def _sum_balance_account(self, account):
        if account.type == 'view':
            return account.balance
        move_state = ['draft','posted']
        if self.target_move == 'posted':
            move_state = ['posted','']
        self.cr.execute('SELECT (sum(debit) - sum(credit)) as tot_balance \
                FROM account_move_line l \
                JOIN account_move am ON (am.id = l.move_id) \
                WHERE (l.account_id = %s) \
                AND (am.state IN %s) \
                AND '+ self.query +' '
                ,(account.id, tuple(move_state)))
        sum_balance = self.cr.fetchone()[0] or 0.0
        if self.init_balance:
            self.cr.execute('SELECT (sum(debit) - sum(credit)) as tot_balance \
                    FROM account_move_line l \
                    JOIN account_move am ON (am.id = l.move_id) \
                    WHERE (l.account_id = %s) \
                    AND (am.state IN %s) \
                    AND '+ self.init_query +' '
                    ,(account.id, tuple(move_state)))
            # Add initial balance to the result
            sum_balance += self.cr.fetchone()[0] or 0.0
        return sum_balance

    def _get_sortby(self, data):
        if self.sortby == 'sort_date':
            return self._translate('Date')
        elif self.sortby == 'sort_journal_partner':
            return self._translate('Journal & Partner')
        return self._translate('Date')
    
    

class report_generalledger(osv.AbstractModel):
    _name = 'report.account.report_generalledger'
    _inherit = 'report.abstract_report'
    _template = 'account.report_generalledger'
    _wrapped_report_class = report_account_common
    # def __init__(self, cr, uid, name, context=None):
        # super(report_account_common, self).__init__(cr, uid, name, context=context)
        # self.localcontext.update( {
            # 'get_lines': self.get_lines,
            # 'time': time,
            # 'get_fiscalyear': self._get_fiscalyear,
            # 'get_account': self._get_account,
            # 'get_start_period': self.get_start_period,
            # 'get_end_period': self.get_end_period,
            # 'get_filter': self._get_filter,
            # 'get_start_date':self._get_start_date,
            # 'get_end_date':self._get_end_date,
            # 'get_target_move': self._get_target_move,
            # 'get_analytic_code':self._get_analytic_code,
        # })
        # self.context = context
        
    # def _get_analytic_code(self, data):
        # if data['form']['account_analytic_id']:
            # return data['form']['account_analytic_id'][1]
        # return ''

    # def set_context(self, objects, data, ids, report_type=None):
        # new_ids = ids
        # if (data['model'] == 'ir.ui.menu'):
            # new_ids = 'chart_account_id' in data['form'] and [data['form']['chart_account_id']] or []
            # objects = self.pool.get('account.account').browse(self.cr, self.uid, new_ids)
        # return super(report_account_common, self).set_context(objects, data, new_ids, report_type=report_type)

    # def get_lines(self, data):
        # lines = []
        # account_obj = self.pool.get('account.account')
     
        # currency_obj = self.pool.get('res.currency')
        # context=data['form']['used_context']
        # comparison_context = data['form']['comparison_context']
        # account_analytic_id = None
        # if data['form']['account_analytic_id']:
           # account_analytic_id =  data['form']['account_analytic_id']
        # if account_analytic_id :
            # if "comparison_context" in data['form']:
                 # comparison_context.update({    
                                    # "account_analytic_id":account_analytic_id[0],
                                    # })
            # context.update({    
                                # "account_analytic_id":account_analytic_id[0],
                                # })
        # ids2 = self.pool.get('account.financial.report')._get_children_by_order(self.cr, self.uid, [data['form']['account_report_id'][0]], context=context)
        # for report in self.pool.get('account.financial.report').browse(self.cr, self.uid, ids2, context=context):
            # flag = True
            # if "account_analytic_code" not in context and report.account_analytic_id:
                # context.update({
                                # 'account_analytic_id':report.account_analytic_id.id,
                                # })
                # report = self.pool.get('account.financial.report').browse(self.cr, self.uid, report.id, context=context)
                # if int(report.balance)==0:
                    # flag = False
                    # continue;
            # #print "before",report.name,report.balance
           # # print "after",report.name,report.balance
            # vals = {
                # 'name': report.name,
                # 'balance': report.balance * report.sign or 0.0,
                # 'type': 'report',
                # 'level': bool(report.style_overwrite) and report.style_overwrite or report.level,
                # 'account_type': report.type =='sum' and 'view' or False, #used to underline the financial report balances
            # }
            
            # if data['form']['debit_credit']:
                # vals['debit'] = report.debit
                # vals['credit'] = report.credit
            # if data['form']['enable_filter']:
                # vals['balance_cmp'] = self.pool.get('account.financial.report').browse(self.cr, self.uid, report.id, context=comparison_context).balance * report.sign or 0.0
            # if account_analytic_id:
                        # if report.account_analytic_id ==False  or account_analytic_id[0] != int(report.account_analytic_id.id):
                            # flag=False 
            # if flag:
                # lines.append(vals)
            # account_ids = []
              
            # if "account_analytic_code" not in context and report.account_analytic_id:
                # context.update({
                                # "account_analytic_id":report.account_analytic_id.id,
                                # })
                
            # if report.account_analytic_id:
                # vals['account_analytic_code'] = report.account_analytic_id.code
            # else:
                # vals['account_analytic_code'] = ""
              
            # if report.display_detail == 'no_detail':
                # #the rest of the loop is used to display the details of the financial report, so it's not needed here.
                # continue
            # if report.type == 'accounts' and report.account_ids:
                # account_ids = account_obj._get_children_and_consol(self.cr, self.uid, [x.id for x in report.account_ids])
            # elif report.type == 'account_type' and report.account_type_ids:
                # account_ids = account_obj.search(self.cr, self.uid, [('user_type','in', [x.id for x in report.account_type_ids])])
            
            # if account_ids:
                # for account in account_obj.browse(self.cr, self.uid, account_ids, context=context):
                    # #if there are accounts to display, we add them to the lines with a level equals to their level in
                    # #the COA + 1 (to avoid having them with a too low level that would conflicts with the level of data
                    # #financial reports for Assets, liabilities...)
                    # if report.display_detail == 'detail_flat' and account.type == 'view':
                        # continue
                    # flag = False
                    # vals = {
                        # 'name': account.code + ' ' + account.name,
                        # 'balance':  account.balance != 0 and account.balance * report.sign or account.balance,
                        # 'type': 'account',
                        # 'level': report.display_detail == 'detail_with_hierarchy' and min(account.level + 1,6) or 6, #account.level + 1
                        # 'account_type': account.type,
                    # }

                    # if data['form']['debit_credit']:
                        # vals['debit'] = account.debit
                        # vals['credit'] = account.credit
                    
                    # if not currency_obj.is_zero(self.cr, self.uid, account.company_id.currency_id, vals['balance']):
                        # flag = True
                    # if data['form']['enable_filter']:
                        # vals['balance_cmp'] = account_obj.browse(self.cr, self.uid, account.id, context=comparison_context).balance * report.sign or 0.0
                        # if not currency_obj.is_zero(self.cr, self.uid, account.company_id.currency_id, vals['balance_cmp']):
                            # flag = True
                            
                    # if account_analytic_id:
                        # if report.account_analytic_id ==False  or int(account_analytic_id[0]) != int(report.account_analytic_id.id):
                            # flag=False
                    # if flag:
                        # lines.append(vals)
        # return lines


# class report_financial(osv.AbstractModel):
    # _name = 'report.account_financial_report_xls.report_financial_cust'
    # _inherit = 'report.abstract_report'
    # _template = 'account_financial_report_xls.report_financial_cust'
    # _wrapped_report_class = report_account_common

