# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Business Applications
#    Copyright (C) 2004-2012 OpenERP S.A. (<http://openerp.com>).
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

from openerp.osv import fields, osv
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)
class res_company(osv.osv):
    _inherit = "res.company"
    _columns = {
        'foc_account_id': fields.many2one(
            'account.account',
            string="FOC Account",
            domain="[('type', '=', 'other')]",),
        'discount_account_id': fields.many2one(
            'account.account',
            string="Discount Account",
            domain="[('type', '=', 'other')]",),
        'discount_cash_account_id': fields.many2one(
            'account.account',
            string="Deduction Account",
            domain="[('type', '=', 'other')]",),
    }



class account_config_settings(osv.osv_memory):
    _name = 'account.config.settings'
    _inherit = 'account.config.settings'

    def onchange_discount_foc(self, cr, uid, ids, module_sale_foc_discount, context=None):
        res = {}
        if not module_sale_foc_discount:
            res['value'] = {'foc_account_id': False, 'discount_account_id': False,'discount_cash_account_id':False}
        return res
    _columns = {
        
        'module_sale_foc_discount': fields.boolean("Allow Sale FOC And Discount",
            implied_group='sale.module_sale_foc_discount',
            help="Allows you to apply some discount per sales order line."),
      'foc_account_id': fields.related(
            'company_id', 'foc_account_id',
            type='many2one',
            relation='account.account',
            string="FOC Account", 
            domain="[('type', '=', 'other')]"),
      'discount_account_id': fields.related(
            'company_id', 'discount_account_id',
            type="many2one",
            relation='account.account',
            string="Discount Account",
            domain="[('type', '=', 'other')]"),
        'discount_cash_account_id': fields.related(
            'company_id', 'discount_cash_account_id',
            type='many2one',
            relation='account.account',
            string="Deduction Account", 
            domain="[('type', '=', 'other')]"),
        
    }
    
    def onchange_company_id(self, cr, uid, ids, company_id, context=None):
        res = super(account_config_settings, self).onchange_company_id(cr, uid, ids, company_id, context=context)
        if company_id:
            company = self.pool.get('res.company').browse(cr, uid, company_id, context=context)
            res['value'].update({'foc_account_id': company.foc_account_id and company.foc_account_id.id or False, 
                                 'discount_account_id': company.discount_account_id and company.discount_account_id.id or False,
                                 'discount_cash_account_id': company.discount_cash_account_id and company.discount_cash_account_id.id or False})
        else: 
            res['value'].update({'foc_account_id': False, 
                                 'discount_account_id': False,
                                 'discount_cash_account_id': False})
        return res

    