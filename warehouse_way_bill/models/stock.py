# -*- coding: utf-8 -*-
#
#
#    Author: Nicolas Bessi, Guewen Baconnier, Yannick Vaucher
#    Copyright 2013-2015 Camptocamp SA
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
#
"""Adds a split button on stock picking out to enable partial picking without
   passing backorder state to done"""
from openerp import models, api, _


class stock_picking(models.Model):
    """Adds picking split without done state."""

    _inherit = "stock.picking"

    @api.multi
    def split_process(self):
        """Use to trigger the wizard from button with
           correct context"""
        ctx = {
            'active_model': self._name,
            'active_ids': self.ids,
            'active_id': len(self.ids) and self.ids[0] or False,
            'do_only_split': True,
            'default_picking_id': len(self.ids) and self.ids[0] or False,
        }
        self.env.cr.execute("select waybill_no from stock_picking where id= %s", (self.ids[0],))
        waybill_no =self.env.cr.fetchone()[0]
        if waybill_no is None:
                id_code = self.pool.get('ir.sequence').get(self.env.cr, self.env.user.id,
                                                'way.bill.code') or '/'
                self.env.cr.execute("update stock_picking set waybill_no=%s where id =%s and  waybill_no is null", (id_code,self.ids[0],))
        view = self.env.ref('stock.view_stock_enter_transfer_details')
        return {
            'name': _('Enter quantities to split'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'stock.transfer_details',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'context': ctx,
        }

