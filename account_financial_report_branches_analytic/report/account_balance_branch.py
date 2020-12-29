import time

from openerp.osv import osv
from openerp.report import report_sxw
from common_report_header import common_report_header


class account_balance_branch(report_sxw.rml_parse, common_report_header):
    
    _name = 'report.account.account.balance.branch'
    _inherit = 'report.account.account.balance'
    
        
    def __init__(self, cr, uid, name, context=None):
        super(account_balance_branch, self).__init__(cr, uid, name, context=context)
        self.sum_debit = 0.00
        self.sum_credit = 0.00
        self.date_lst = []
        self.date_lst_string = ''
        self.result_acc = []
        self.localcontext.update({
            'time': time,
            'lines': self.lines,
            'sum_debit': self._sum_debit,
            'sum_credit': self._sum_credit,
            'get_fiscalyear':self._get_fiscalyear,
            'get_filter': self._get_filter,
            'get_start_period': self.get_start_period,
            'get_end_period': self.get_end_period ,
            'get_account': self._get_account,
            'get_journal': self._get_journal,
            'get_start_date':self._get_start_date,
            'get_end_date':self._get_end_date,
            'get_target_move': self._get_target_move,
            'get_branch_code':self._get_branch,
            'get_analytic_code':self._get_analytic_code,
        })
        print 'context>>>',context
        self.context = context
    
    def _get_analytic_code(self, data):
        if data['form']['account_analytic_id']:
            return data['form']['account_analytic_id'][1]
        return ''
        
    def _get_branch(self, data):
        print '_get_branch'
        if data['form']['branch_ids']:
            print '_get_branch_code>>>',data['form']['branch_ids']
            return data['form']['branch_ids'][1]
        return ''
    
#     def set_context(self, objects, data, ids, report_type=None):
#         print 'data new>>>',data
#         new_ids = ids
#         obj_move = self.pool.get('account.move.line')
#         self.sortby = data['form'].get('sortby', 'sort_date')
#         self.query = obj_move._query_get(self.cr, self.uid, obj='l', context=data['form'].get('used_context',{}))
#         ctx2 = data['form'].get('used_context',{}).copy()
#         self.init_balance = data['form'].get('initial_balance', True)
#         if self.init_balance:
#             ctx2.update({'initial_bal': True})
#         print 'update ctx2>>>',ctx2 
#         self.query = obj_move._query_get(self.cr, self.uid, obj='l', context=ctx2)   
#         #self.query = obj_move._query_get(self.cr, self.uid, obj='l', context=ctx2)
#         self.display_account = data['form']['display_account']
#         self.target_move = data['form'].get('target_move', 'all')
#         ctx = self.context.copy()
#         ctx['fiscalyear'] = data['form']['fiscalyear_id']
#         if data['form']['filter'] == 'filter_period':
#             ctx['periods'] = data['form']['periods']
#         elif data['form']['filter'] == 'filter_date':
#             ctx['date_from'] = data['form']['date_from']
#             ctx['date_to'] =  data['form']['date_to']
#         ctx['state'] = data['form']['target_move']
#         self.context.update(ctx)
#         if (data['model'] == 'ir.ui.menu'):
#             new_ids = [data['form']['chart_account_id']]
#             objects = self.pool.get('account.account').browse(self.cr, self.uid, new_ids)
#         return super(account_balance_branch, self).set_context(objects, data, new_ids, report_type=report_type)
    def set_context(self, objects, data, ids, report_type=None):
        print 'data balance>>>',data
        new_ids = ids
        obj_move = self.pool.get('account.move.line')
        self.query = obj_move._query_get(self.cr, self.uid, obj='l', context=data['form'].get('used_context',{}))
        #self.init_balance = data['form'].get('branch_ids', True)
#         self.branch_ids = data['form']['branch_ids']
#         ctx = self.context.copy()
#         self.context.update(ctx)
        print 'balance self.query>>>',self.query
        if (data['model'] == 'ir.ui.menu'):
            new_ids = 'chart_account_id' in data['form'] and [data['form']['chart_account_id']] or []
            objects = self.pool.get('account.account').browse(self.cr, self.uid, new_ids)
        return super(account_balance_branch, self).set_context(objects, data, new_ids, report_type=report_type)
    
    def lines(self, form, ids=None, done=None):
        def _process_child(accounts, disp_acc, parent):
                
                account_rec = [acct for acct in accounts if acct['id']==parent][0]
                currency_obj = self.pool.get('res.currency')
                acc_id = self.pool.get('account.account').browse(self.cr, self.uid, account_rec['id'])
                currency = acc_id.currency_id and acc_id.currency_id or acc_id.company_id.currency_id
                res = {
                    'id': account_rec['id'],
                    'type': account_rec['type'],
                    'code': account_rec['code'],
                    'name': account_rec['name'],
                    'level': account_rec['level'],
                    'debit': account_rec['debit'],
                    'credit': account_rec['credit'],
                    'balance': account_rec['balance'],
                    'parent_id': account_rec['parent_id'],
                    'bal_type': '',
                }
                self.sum_debit += account_rec['debit']
                self.sum_credit += account_rec['credit']
                if disp_acc == 'movement':
                    if not currency_obj.is_zero(self.cr, self.uid, currency, res['credit']) or not currency_obj.is_zero(self.cr, self.uid, currency, res['debit']) or not currency_obj.is_zero(self.cr, self.uid, currency, res['balance']):
                        self.result_acc.append(res)
                elif disp_acc == 'not_zero':
                    if not currency_obj.is_zero(self.cr, self.uid, currency, res['balance']):
                        self.result_acc.append(res)
                else:
                    self.result_acc.append(res)
                if account_rec['child_id']:
                    for child in account_rec['child_id']:
                        _process_child(accounts,disp_acc,child)

        obj_account = self.pool.get('account.account')
        if not ids:
            ids = self.ids
        if not ids:
            return []
        if not done:
            done={}

        ctx = self.context.copy()
        
        self.branch_ids = form['branch_ids']
        ctx = self.context.copy()
        self.context.update(ctx)
        print 'form[branch_ids]>>>',form['branch_ids']
        print 'ctx>>>>',ctx
        ctx['fiscalyear'] = form['fiscalyear_id']
        if form['filter'] == 'filter_period':
            ctx['period_from'] = form['period_from']
            ctx['period_to'] = form['period_to']
        elif form['filter'] == 'filter_date':
            ctx['date_from'] = form['date_from']
            ctx['date_to'] =  form['date_to']
            
        if form['branch_ids']:
            ctx['branch_ids'] = form['branch_ids']
              
        ctx['state'] = form['target_move']
        parents = ids
        child_ids = obj_account._get_children_and_consol(self.cr, self.uid, ids, ctx)
        if child_ids:
            ids = child_ids
        accounts = obj_account.read(self.cr, self.uid, ids, ['type','code','name','debit','credit','balance','parent_id','level','child_id'], ctx)

        for parent in parents:
                if parent in done:
                    continue
                done[parent] = 1
                _process_child(accounts,form['display_account'],parent)
        return self.result_acc
        
    
    
class report_trialbalance(osv.AbstractModel):
    _name = 'report.account.report_trialbalance'
    _inherit = 'report.abstract_report'
    _template = 'account.report_trialbalance'
    _wrapped_report_class = account_balance_branch    