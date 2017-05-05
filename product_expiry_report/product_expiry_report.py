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

from openerp import models, fields
from openerp import tools


class product_expiry_report(models.Model):
  
    _name = "product.expiry.report"
    _auto = False
    product_id=fields.Many2one('product.product', 'Product Name', readonly=True)
    use_date = fields.Datetime('Best Before Date', readonly=True)
    life_date = fields.Datetime('End of Life Date', readonly=True)
    removal_date = fields.Datetime('Removal Date', readonly=True)
    alert_date = fields.Datetime('Alert Date', readonly=True)
    lot_id = fields.Many2one('stock.production.lot', 'Lot', readonly=True)
    location_id= fields.Many2one('stock.location', 'Location', readonly=True)
    qty=fields.Float('Qty')

    


    def init(self, cr):
        """Initialize the sql view for the event registration"""
        tools.drop_view_if_exists(cr, 'product_expiry_report')

        # TOFIX this request won't select events that have no registration
        cr.execute(""" CREATE VIEW product_expiry_report AS (

            SELECT  sq.id as id,
                sq.product_id as product_id,
                sq.lot_id as lot_id,
                sq.location_id as location_id,
            
                sq.qty,
                sp.use_date,
                sp.life_date,
                sp.removal_date,
                sp.alert_date
                FROM stock_production_lot sp,
                stock_quant sq
                WHERE sp.id=sq.lot_id AND sq.location_id != 9
                
 
        )
        """)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
