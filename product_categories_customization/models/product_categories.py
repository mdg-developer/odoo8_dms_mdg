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

class product_category(osv.osv):
    _inherit = "product.category"
    _columns = {
        'property_account_income_categ': fields.property(
            type='many2one',
            relation='account.account',
            string="Sale",
            help="This account will be used for invoices to value sales."),
        'property_account_expense_categ': fields.property(
            type='many2one',
            relation='account.account',
            string="GIT Account",
            help="This account will be used for invoices to value expenses."),
                
        'property_stock_account_input_categ': fields.property(
            type='many2one',
            relation='account.account',
            string='GIT',
            help="When doing real-time inventory valuation, counterpart journal items for all incoming stock moves will be posted in this account, unless "
                 "there is a specific valuation account set on the source location. This is the default value for all products in this category. It "
                 "can also directly be set on each product"),
        'property_stock_account_output_categ': fields.property(
            type='many2one',
            relation='account.account',
            string='COGS',
            help="When doing real-time inventory valuation, counterpart journal items for all outgoing stock moves will be posted in this account, unless "
                 "there is a specific valuation account set on the destination location. This is the default value for all products in this category. It "
                 "can also directly be set on each product"),
                
        'property_stock_valuation_account_id': fields.property(
            type='many2one',
            relation='account.account',
            string="Inventory Account",
            help="When real-time inventory valuation is enabled on a product, this account will hold the current value of the products.",),
                
        'property_sale_credit_account_id': fields.property(
            type='many2one',
            relation='account.account',
            string="Sale Credit Account",
            help="When real-time inventory valuation is enabled on a product, this account will hold the current value of the products.",),
                
                                
                
    }
    
    
class product_template(osv.osv):
    _inherit = "product.template"
    _columns = {
                
            'property_account_credit_income': fields.property(
            type='many2one',
            relation='account.account',
            string="Income Credit Account",
            help="This account will be used for invoices instead of the default one to value sales for the current product."),
                }