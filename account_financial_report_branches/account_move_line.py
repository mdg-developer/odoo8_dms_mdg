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

import logging
from datetime import datetime
from dateutil.relativedelta import relativedelta
from operator import itemgetter
import time
from openerp import tools
from openerp.osv import fields, osv, expression
from openerp.tools.translate import _
from openerp.tools.float_utils import float_round as round

import openerp.addons.decimal_precision as dp
#Finder.Type_Definitions import columns
_logger = logging.getLogger(__name__)


# class account_financial_report(osv.osv):
#     _name = "account.financial.report"
#     _inherit = "account.report.general.ledger"
#     def _get_balance(self, cr, uid, ids, field_names, args, context=None):
#         '''returns a dictionary with key=the ID of a record and value=the balance amount 
#            computed for this record. If the record is of type :
#                'accounts' : it's the sum of the linked accounts
#                'account_type' : it's the sum of leaf accoutns with such an account_type
#                'account_report' : it's the amount of the related report
#                'sum' : it's the sum of the children of this record (aka a 'view' record)'''
#         account_obj = self.pool.get('account.account')
#         res = {}
#         for report in self.browse(cr, uid, ids, context=context):
#             new_context={}
#             new_context.update(context);
#             if "account_analytic_code" not in context and report.account_analytic_id:
#                 new_context.update({
#                                 'account_analytic_id':report.account_analytic_id.id,
#                                 })
#             if report.id in res:
#                 continue
#             res[report.id] = dict((fn, 0.0) for fn in field_names)
#             if report.type == 'accounts':
#                 # it's the sum of the linked accounts
#                 for a in report.account_ids:
#                     for field in field_names:
#                         res[report.id][field] += getattr(a, field)
#             elif report.type == 'account_type':
#                 # it's the sum the leaf accounts with such an account type
#                 report_types = [x.id for x in report.account_type_ids]
#                 account_ids = account_obj.search(cr, uid, [('user_type','in', report_types), ('type','!=','view')], context=new_context)
#                 for a in account_obj.browse(cr, uid, account_ids, context=context):
#                     for field in field_names:
#                         res[report.id][field] += getattr(a, field)
#             elif report.type == 'account_report' and report.account_report_id:
#                 # it's the amount of the linked report
#                 res2 = self._get_balance(cr, uid, [report.account_report_id.id], field_names, False, context=new_context)
#                 for key, value in res2.items():
#                     for field in field_names:
#                         res[report.id][field] += value[field]
#             elif report.type == 'sum':
#                 # it's the sum of the children of this account.report
#                 res2 = self._get_balance(cr, uid, [rec.id for rec in report.children_ids], field_names, False, context=new_context)
#                 for key, value in res2.items():
#                     for field in field_names:
#                         res[report.id][field] += value[field]
#         return res
#     
#     _columns = {
#         'account_analytic_id':  fields.many2one('account.analytic.account', 'Analytic Account'),
#                 }
class account_move_line(osv.osv):
    _inherit = "account.move.line"
    
    
    def _query_get(self, cr, uid, obj='l', context=None):
        fiscalyear_obj = self.pool.get('account.fiscalyear')
        fiscalperiod_obj = self.pool.get('account.period')
        account_obj = self.pool.get('account.account')
        analtyic_obj = self.pool.get('account.analytic.account')
        fiscalyear_ids = []
        context = dict(context or {})
        initial_bal = context.get('initial_bal', False)
        company_clause = " "
        if context.get('company_id', False):
            company_clause = " AND " +obj+".company_id = %s" % context.get('company_id', False)
        if not context.get('fiscalyear', False):
            if context.get('all_fiscalyear', False):
                #this option is needed by the aged balance report because otherwise, if we search only the draft ones, an open invoice of a closed fiscalyear won't be displayed
                fiscalyear_ids = fiscalyear_obj.search(cr, uid, [])
            else:
                fiscalyear_ids = fiscalyear_obj.search(cr, uid, [('state', '=', 'draft')])
        else:
            #for initial balance as well as for normal query, we check only the selected FY because the best practice is to generate the FY opening entries
            fiscalyear_ids = [context['fiscalyear']]

        fiscalyear_clause = (','.join([str(x) for x in fiscalyear_ids])) or '0'
        state = context.get('state', False)
        where_move_state = ''
        where_move_lines_by_date = ''

        if context.get('date_from', False) and context.get('date_to', False):
            if initial_bal:
                where_move_lines_by_date = " AND " +obj+".move_id IN (SELECT id FROM account_move WHERE date < '" +context['date_from']+"')"
            else:
                where_move_lines_by_date = " AND " +obj+".move_id IN (SELECT id FROM account_move WHERE date >= '" +context['date_from']+"' AND date <= '"+context['date_to']+"')"

       
            
        if state:
            if state.lower() not in ['all']:
                where_move_state= " AND "+obj+".move_id IN (SELECT id FROM account_move WHERE account_move.state = '"+state+"')"
        if context.get('period_from', False) and context.get('period_to', False) and not context.get('periods', False):
            if initial_bal:
                period_company_id = fiscalperiod_obj.browse(cr, uid, context['period_from'], context=context).company_id.id
                first_period = fiscalperiod_obj.search(cr, uid, [('company_id', '=', period_company_id)], order='date_start', limit=1)[0]
                context['periods'] = fiscalperiod_obj.build_ctx_periods(cr, uid, first_period, context['period_from'])
            else:
                context['periods'] = fiscalperiod_obj.build_ctx_periods(cr, uid, context['period_from'], context['period_to'])
        if context.get('periods', False):
            if initial_bal:
                query = obj+".state <> 'draft' AND "+obj+".period_id IN (SELECT id FROM account_period WHERE fiscalyear_id IN (%s)) %s %s" % (fiscalyear_clause, where_move_state, where_move_lines_by_date)
                period_ids = fiscalperiod_obj.search(cr, uid, [('id', 'in', context['periods'])], order='date_start', limit=1)
                if period_ids and period_ids[0]:
                    first_period = fiscalperiod_obj.browse(cr, uid, period_ids[0], context=context)
                    ids = ','.join([str(x) for x in context['periods']])
                    query = obj+".state <> 'draft' AND "+obj+".period_id IN (SELECT id FROM account_period WHERE fiscalyear_id IN (%s) AND date_start <= '%s' AND id NOT IN (%s)) %s %s" % (fiscalyear_clause, first_period.date_start, ids, where_move_state, where_move_lines_by_date)
            else:
                ids = ','.join([str(x) for x in context['periods']])
                query = obj+".state <> 'draft' AND "+obj+".period_id IN (SELECT id FROM account_period WHERE fiscalyear_id IN (%s) AND id IN (%s)) %s %s" % (fiscalyear_clause, ids, where_move_state, where_move_lines_by_date)
        else:
            query = obj+".state <> 'draft' AND "+obj+".period_id IN (SELECT id FROM account_period WHERE fiscalyear_id IN (%s)) %s %s" % (fiscalyear_clause, where_move_state, where_move_lines_by_date)
        
        if initial_bal and not context.get('periods', False) and not where_move_lines_by_date:
            #we didn't pass any filter in the context, and the initial balance can't be computed using only the fiscalyear otherwise entries will be summed twice
            #so we have to invalidate this query
            raise osv.except_osv(_('Warning!'),_("You have not supplied enough arguments to compute the initial balance, please select a period and a journal in the context."))


        if context.get('journal_ids', False):
            query += ' AND '+obj+'.journal_id IN (%s)' % ','.join(map(str, context['journal_ids']))

        if context.get('chart_account_id', False):
            child_ids = account_obj._get_children_and_consol(cr, uid, [context['chart_account_id']], context=context)
            query += ' AND '+obj+'.account_id IN (%s)' % ','.join(map(str, child_ids))
        if context.get('branch_ids',False):
            branch_id = context['branch_ids']
            query += ' AND '+obj+'.branch_id IN (%s)' % ','.join(map(str, context['branch_ids']))
            
            
        query += company_clause
        return query

