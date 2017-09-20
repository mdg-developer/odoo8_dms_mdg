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
        'code':fields.char('Code'),
		'is_oldproduct':fields.boolean('Is Old Product'),
        'property_whole_account_income_categ': fields.property(
                    type='many2one',
                    relation='account.account',
                    string="Whole Sale Income Account",
                    help="This   will be used for invoices instead of the default one to value sales for the current product."), }
    _defaults = {
        'is_oldproduct': False,
    }
					
    def create(self, cr, uid, vals, context=None):
        category_code = None
        if vals:
            category_code = self.pool.get('ir.sequence').get(cr, uid, 'product.category.code')
            vals['code'] = category_code
            new_id = super(product_category, self).create(cr, uid, vals, context=context)
            return new_id
        
