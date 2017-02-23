# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 NovaPoint Group LLC (<http://www.novapointgroup.com>)
#    Copyright (C) 2004-2010 OpenERP SA (<http://www.openerp.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################

from openerp.osv import fields
from openerp.osv import osv
class SaleOrder(osv.osv):
    '''
    Sale Order
    '''
    _inherit = 'sale.order'
    
    _columns = {
        'coupon_code':fields.char('Promo Coupon Code', size=20),
    }
    
    def apply_promotions(self, cursor, user, ids, context=None):
        """
        Applies the promotions to the given records
        @param cursor: Database Cursor
        @param user: ID of User
        @param ids: ID of current record.
        @param context: Context(no direct use).
        """
        data=True
        promotions_obj = self.pool.get('promos.rules')
        sale_obj = self.pool.get('sale.order')

        for order_id in ids:
            data=promotions_obj.apply_promotions(cursor, user,
                                            order_id, context=None)

        if data!=True:
            return data
        sale_obj.button_dummy(cursor, user, [order_id], context=context)
        sale_obj.action_button_confirm(cursor, user, [order_id], context=context)
        return True
            
SaleOrder()

