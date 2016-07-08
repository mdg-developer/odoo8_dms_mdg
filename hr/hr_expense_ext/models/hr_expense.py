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

import time

from openerp.osv import fields, osv
from openerp.tools.translate import _

import openerp.addons.decimal_precision as dp

class hr_expense_expense(osv.osv):

    _inherit = "hr.expense.expense"
    _rec_name="employee_id"
    _columns = {
        'notify_manager': fields.many2one('hr.employee', "Notify Manager", required=True),
        'note': fields.text('Notes'),
        'branch_id': fields.many2one('branch', 'Branch'),
        'type':fields.selection([('expenses', 'Expenses'), ('advance', 'Advance'), ('claim', 'Claim')], 'Type'),
        'state': fields.selection([
            ('draft', 'New'),
            ('cancelled', 'Refused'),
            ('manager_approve', 'Manager Waiting Approval'),
            ('gm_approve', 'GM Waiting Approval'),
            ('finance_approve', 'Finance Waiting Approval'),
            ('cashier_approve', 'Cashier Waiting Approval'),
            ('paid', 'Paid'),
            ],
              'Status', readonly=True, track_visibility='onchange', copy=False,
            help='When the expense request is created the status is \'Draft\'.\n It is confirmed by the user and request is sent to admin, the status is \'Waiting Confirmation\'.\
            \nIf the admin accepts it, the status is \'Accepted\'.\n If the accounting entries are made for the expense request, the status is \'Waiting Payment\'.'),                    
    }

    def expense_manager_accept(self, cr, uid, ids, context=None):
        for expense in self.browse(cr, uid, ids):
            if expense.employee_id and expense.employee_id.parent_id.user_id:
                self.message_subscribe_users(cr, uid, [expense.id], user_ids=[expense.employee_id.parent_id.user_id.id])
        return self.write(cr, uid, ids, {'state': 'manager_approve'}, context=context)
    
    def expense_gm_accept(self, cr, uid, ids, context=None):
        for expense in self.browse(cr, uid, ids):
            if expense.employee_id and expense.employee_id.parent_id.user_id:
                self.message_subscribe_users(cr, uid, [expense.id], user_ids=[expense.employee_id.parent_id.user_id.id])
        return self.write(cr, uid, ids, {'state': 'gm_approve'}, context=context)
    
    def expense_finance_accept(self, cr, uid, ids, context=None):
        for expense in self.browse(cr, uid, ids):
            if expense.employee_id and expense.employee_id.parent_id.user_id:
                self.message_subscribe_users(cr, uid, [expense.id], user_ids=[expense.employee_id.parent_id.user_id.id])
        return self.write(cr, uid, ids, {'state': 'finance_approve'}, context=context)
    
    def expense_cashier_accept(self, cr, uid, ids, context=None):
        for expense in self.browse(cr, uid, ids):
            if expense.employee_id and expense.employee_id.parent_id.user_id:
                self.message_subscribe_users(cr, uid, [expense.id], user_ids=[expense.employee_id.parent_id.user_id.id])
        return self.write(cr, uid, ids, {'state': 'cashier_approve'}, context=context)
    
    def expense_paid(self, cr, uid, ids, context=None):
        for expense in self.browse(cr, uid, ids):
            if expense.employee_id and expense.employee_id.parent_id.user_id:
                self.message_subscribe_users(cr, uid, [expense.id], user_ids=[expense.employee_id.parent_id.user_id.id])
        return self.write(cr, uid, ids, {'state': 'paid'}, context=context)

    def expense_canceled(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'cancelled'}, context=context)

class hr_expense_line(osv.osv):
    _inherit = "hr.expense.line"
    _columns = {
        'product_id': fields.many2one('product.product', 'Expense Type', domain=[('hr_expense_ok','=',True)]),
        'date_value': fields.date('Date', required=True),
        'ref': fields.char('Reference'),
        'uom_id': fields.many2one('product.uom', 'Unit of Measure', required=True),
        }
    