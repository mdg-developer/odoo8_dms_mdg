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

class stock_picking(osv.osv):
    _inherit = 'stock.picking'
    
    def _get_corresponding_team(self, cr, uid, ids, field_name, arg, context=None):
        result = {}
        order_id = None
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.origin:
                cr.execute("""select section_id from sale_order where name=%s""", (rec.origin,))
                data = cr.fetchall()
                if data:
                    order_id = data[0]
                print 'order_id >>> ', order_id
                result[rec.id] = order_id
            else:
                result[rec.id] = None
        return result    
    
    def _get_corresponding_user(self, cr, uid, ids, field_name, arg, context=None):
        result = {}
        order_id = None
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.origin:
                cr.execute("""select user_id from sale_order where name=%s""", (rec.origin,))
                data = cr.fetchall()
                if data:
                    order_id = data[0]
                print 'order_id >>> ', order_id
                result[rec.id] = order_id
            else:
                result[rec.id] = None
        return result      
    
    _columns = {

              'section_id':fields.function(_get_corresponding_team, type='many2one', relation='crm.case.section', string='Sales Team', states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}, copy=False,store=True),
              'user_id':fields.function(_get_corresponding_user, type='many2one', relation='res.users', string='Salesperson', states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}, copy=False,store=True),

              }
