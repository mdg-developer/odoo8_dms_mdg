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

class sale_make_location(osv.osv_memory):
    _name = "rfi.reassign.location"
    _description = "Reassign Location"
        
    
    _columns = {
        
                'section_id':fields.many2one('crm.case.section','Delivery Team',readonly=True),
                'location_id':fields.many2one('section.warehouse','Location',store=True),
                'request_id':fields.many2one('stock.requisition','Stock Request',store=True),

    }

    
    def make_location(self, cr, uid, ids, context=None):
        
        if ids:
            data_obj=self.pool.get('rfi.reassign.location').browse(cr, uid, ids[0], context=context)
            location_id=data_obj.location_id.id
            request_id=data_obj.request_id.id
            assign_obj=self.pool.get('section.warehouse').browse(cr, uid, location_id, context=context)
            cr.execute("update stock_requisition set to_location_id=%s where id =%s",(assign_obj.location_id.id,request_id,))
            cr.execute("update stock_requisition_line set qty_on_hand=0 where line_id =%s",(request_id,))
        return True        
        


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

