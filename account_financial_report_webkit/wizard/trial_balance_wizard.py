# -*- encoding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier
#    Copyright Camptocamp SA 2011
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

from openerp.osv import orm,fields


class AccountTrialBalanceWizard(orm.TransientModel):
    """Will launch trial balance report and pass required args"""

    _inherit = "account.common.balance.report"
    _name = "trial.balance.webkit"
    _description = "Trial Balance Report"
    
    _columns = {
                'amount_currency': fields.boolean("With Currency",
                                          help="It adds the currency column"),
                'analytic_account_ids': fields.many2many(
                    'account.analytic.account', string='Filter on analytic accounts',
                    help="""Only selected analytic accounts will be printed. Leave empty to
                            print all analytic accounts."""),
                'branch_ids': fields.many2many('res.branch', string='Filter on branches'),
                }

    def pre_print_report(self, cr, uid, ids, data, context=None):
        data = super(AccountTrialBalanceWizard, self).pre_print_report(
            cr, uid, ids, data, context)
        if context is None:
            context = {}
        # will be used to attach the report on the main account
        data['ids'] = [data['form']['chart_account_id']]
        vals = self.read(cr, uid, ids,
                         ['amount_currency',
                          'display_account',
                          'account_ids',
                          'analytic_account_ids','branch_ids'],
                         context=context)[0]     
        data['form'].update(vals)
        return data


    def _print_report(self, cursor, uid, ids, data, context=None):
        context = context or {}
        # we update form with display account value
        data = self.pre_print_report(cursor, uid, ids, data, context=context)

        return {'type': 'ir.actions.report.xml',
                'report_name': 'account.account_report_trial_balance_webkit',
                'datas': data}
