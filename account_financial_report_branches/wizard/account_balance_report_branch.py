from openerp.osv import fields, osv
#from openerp.tools.translate import _


class account_balance_report_branch(osv.osv_memory):
    _name = 'account.balance.report'
    _inherit = "account.balance.report"    
    _description = 'Trial Balance Report'

    _columns = {
        'branch_ids': fields.many2many('res.branch', 'account_balance_report_branch_rel', 'account_id', 'branch_id', 'Branches'),
    }
       
    
    def _build_contexts(self, cr, uid, ids, data, context=None):
        print 'T'
        if context is None:
            context = {}
        result = {}
        result['fiscalyear'] = 'fiscalyear_id' in data['form'] and data['form']['fiscalyear_id'] or False
        result['journal_ids'] = 'journal_ids' in data['form'] and data['form']['journal_ids'] or False
        result['branch_ids'] = 'branch_ids' in data['form'] and data['form']['branch_ids'] or False
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
        print 'T result>>>',   result 
        return result

#     def _print_report(self, cr, uid, ids, data, context=None):
#         raise (_('Error!'), _('Not implemented.'))
    
    def check_report(self, cr, uid, ids, context=None):
        print 'T our check_report'
        if context is None:
            context = {}
        data = {}
        data['ids'] = context.get('active_ids', [])
        data['model'] = context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(cr, uid, ids, ['date_from',  'date_to',  'fiscalyear_id', 'journal_ids', 'branch_ids', 'period_from', 'period_to',  'filter',  'chart_account_id', 'target_move'], context=context)[0]
        for field in ['fiscalyear_id', 'chart_account_id', 'period_from', 'period_to']:
            if isinstance(data['form'][field], tuple):
                data['form'][field] = data['form'][field][0]
        used_context = self._build_contexts(cr, uid, ids, data, context=context)
        print 'used_context1>>>',used_context
        data['form']['periods'] = used_context.get('periods', False) and used_context['periods'] or []
        
        data['form']['used_context'] = dict(used_context, lang=context.get('lang', 'en_US'))
        print 'fi context>>',context
        return self._print_report(cr, uid, ids, data, context=context)
#     def _build_contexts(self, cr, uid, ids, data, context=None):
#         print 'new balance context'
#         if context is None:
#             context = {}
#         result = {}
#         result['fiscalyear'] = 'fiscalyear_id' in data['form'] and data['form']['fiscalyear_id'] or False
#         result['journal_ids'] = 'journal_ids' in data['form'] and data['form']['journal_ids'] or False
#         result['branch_ids'] = 'branch_ids' in data['form'] and data['form']['branch_ids'] or False
#         result['chart_account_id'] = 'chart_account_id' in data['form'] and data['form']['chart_account_id'] or False
#         result['state'] = 'target_move' in data['form'] and data['form']['target_move'] or ''
#         if data['form']['filter'] == 'filter_date':
#             result['date_from'] = data['form']['date_from']
#             result['date_to'] = data['form']['date_to']
#         elif data['form']['filter'] == 'filter_period':
#             if not data['form']['period_from'] or not data['form']['period_to']:
#                 raise osv.except_osv(_('Error!'),_('Select a starting and an ending period.'))
#             result['period_from'] = data['form']['period_from']
#             result['period_to'] = data['form']['period_to']
#         print 'result>>>',result    
#         return result
#  
#      
#  
#     def check_report(self, cr, uid, ids, context=None):
#         print 'new balance check_report'
#         if context is None:
#             context = {}
#         data = {}
#         data['ids'] = context.get('active_ids', [])
#         data['model'] = context.get('active_model', 'ir.ui.menu')
#         data['form'] = self.read(cr, uid, ids, ['date_from',  'date_to',  'fiscalyear_id', 'journal_ids', 'branch_ids' ,'period_from', 'period_to',  'filter',  'chart_account_id', 'target_move'], context=context)[0]
#         for field in ['fiscalyear_id', 'chart_account_id', 'period_from', 'period_to']:
#             if isinstance(data['form'][field], tuple):
#                 data['form'][field] = data['form'][field][0]
#         used_context = self._build_contexts(cr, uid, ids, data, context=context)
#         data['form']['periods'] = used_context.get('periods', False) and used_context['periods'] or []
#         data['form']['used_context'] = dict(used_context, lang=context.get('lang', 'en_US'))
#          
#         return self._print_report(cr, uid, ids, data, context=context)