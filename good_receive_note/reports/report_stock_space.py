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

class report_stock_space(osv.osv):
    _name = "report.stock.space"
    _description = "Space Availability Report"
    _auto = False
    _columns = {
        'name':fields.char('Location Name', readonly=True),
        'maingroup_id': fields.many2one('product.maingroup', 'Principle', readonly=True, select=True),
        'product_move_type_id': fields.many2one('product.move.type', 'Product Nature', readonly=True, select=True),
        'row':fields.char('Location Row', readonly=True),
        'layer':fields.char('Location Layer', readonly=True),
        'room':fields.char('Location Room', readonly=True),
        'cell':fields.char('Location Cell', readonly=True),
    }

    def init(self, cr):
        drop_view_if_exists(cr, 'report_stock_space')
        cr.execute("""
            create or replace view report_stock_space as (
                select id,name,maingroup_id,product_move_type_id,row,layer,room,cell 
                from stock_location 
                where  id not in (select location_id from stock_quant group by location_id)
                group by id
            )""")


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
