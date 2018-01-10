# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#
#    Copyright (c) 2014 Noviat nv/sa (www.noviat.com). All rights reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp.osv import orm
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
import logging
_logger = logging.getLogger(__name__)

class purchase_order(osv.osv):

    _name = 'purchase.order'
    _inherit = 'purchase.order' 

    def import_lines(self, cr, uid, ids, context=None):
        mod_obj = self.pool.get('ir.model.data')
        wiz_view = mod_obj.get_object_reference(cr, uid, 'purchase_order_import', 'pol_import_view')
        for po in self.browse(cr, uid, ids, context=context):
            if po.order_line:
                raise orm.except_orm(_('Unsupported Function :'),
                    _("Import not allowed when there are already purchase order lines. \nPlease remove these first."))
            ctx = {
                'company_id': po.company_id.id,
                'order_id': po.id,
            }
            act_import = {
                'name': _('Import File'),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'pol.import',
                'view_id': [wiz_view[1]],
                'nodestroy': True,
                'target': 'new',
                'type': 'ir.actions.act_window',
                'context': ctx,
            }
            return act_import
purchase_order()
