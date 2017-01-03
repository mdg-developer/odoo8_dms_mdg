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
from mako.runtime import _inherit_from
import math
from openerp.tools import amount_to_text_en, float_round

class account_invoice(osv.osv):
    _inherit = 'account.invoice'
    def _get_corresponding_sale_order(self, cr, uid, ids, field_name, arg, context=None):
        result = {}
        order_id = None
        for rec in self.browse(cr, uid, ids, context=context):
            print'rec >>> ', rec
            cr.execute("""select order_id from sale_order_invoice_rel where invoice_id=%s""", (rec.id,))
            data = cr.fetchall()
            if data:
                order_id = data[0]
            print 'order_id >>> ', order_id
            result[rec.id] = order_id
        return result
    
    def convert(self, amount, currency=False):
        check_amount_in_words = amount_to_text_en.amount_to_text(math.floor(amount), lang='en', currency='')
        return check_amount_in_words
    
    _columns = {
              'sale_order_id':fields.function(_get_corresponding_sale_order, type='many2one', relation='sale.order', string='Sale Order'),
              }
