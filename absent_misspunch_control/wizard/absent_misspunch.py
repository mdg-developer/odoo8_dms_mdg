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
from openerp.tools.translate import _

class control_absent_misspunch(osv.osv_memory):
    _name = "absent.misspunch.control"
    
    def control_absent_misspunch(self, cr, uid, ids, context=None):
        data = self.read(cr, uid, ids, context=context)
        ot_obj = self.pool.get('attendance.data.import')
        datas = {
             'ids': context.get('active_ids', []),
              'model': 'attendance.data.import',
              'form': data
            }
        ot_id=datas['ids']
        for id in ot_id: 
            ot_obj.is_not_absent(cr, uid, id,context=context)   
        return True 
control_absent_misspunch()