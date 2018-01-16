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
from openerp.tools.sql import drop_view_if_exists

class report_pallet_stock(osv.osv):
    _name = "report.pallet.stock"
    _description = "Pallet Stock Report"
    _auto = False
    _columns = {
        'name':fields.char('Location Name', readonly=True),
        'maingroup_id': fields.many2one('product.maingroup', 'Principle', readonly=True, select=True),
        'product_move_type_id': fields.many2one('product.move.type', 'Product Nature', readonly=True, select=True),
        'row':fields.char('Location Row', readonly=True),
        'layer':fields.char('Location Layer', readonly=True),
        'room':fields.char('Location Room', readonly=True),
        'cell':fields.char('Location Cell', readonly=True),
        'qty':fields.integer('Quantity', readonly=True),
        'product_id': fields.many2one('product.product', 'Product', readonly=True, select=True),
        'package_id': fields.many2one('stock.quant.package', 'Pallet', readonly=True, select=True),
        'location_id':fields.many2one('stock.location', 'Location', readonly=True, select=True),
    }

    def init(self, cr):
        drop_view_if_exists(cr, 'report_pallet_stock')
        cr.execute("""
            create or replace view report_pallet_stock as (
                 select min(sq.id)as id,sq.location_id ,sl.name,sl.maingroup_id,sl.product_move_type_id,sl.row,sl.layer,sl.room,sl.cell,sum(sq.qty) as qty ,sq.product_id,sq.package_id
                 from stock_location sl ,stock_quant sq ,stock_quant_package sqp
                 where sl.id= sq.location_id
                 and sq.package_id=sqp.id
                 and sqp.location_id= sq.location_id
                 group by sq.product_id,sl.id,sl.name,sl.maingroup_id,sq.location_id,sl.product_move_type_id,sl.row,sl.layer,sl.room,sl.cell,sq.package_id
                 order by sl.row ,sl.layer,sl.room,sl.cell
            )""")


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
