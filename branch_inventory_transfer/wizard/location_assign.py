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

class change_location(osv.osv_memory):
    _name = "change.diff.location"
    _description = "Change Difference Location"
        
    
    _columns = {
                'from_location_id':fields.many2one('stock.location','From Location',store=True),
                'note_id':fields.many2one('branch.good.issue.note','Good Issue Note',store=True),
                'to_location_id':fields.many2one('stock.location','To Location',required=True),
                'transfer_date':fields.date('Transfer Date',required=True),
                'remark': fields.text("Remark")
    }

    
    def make_location(self, cr, uid, ids, context=None):
        default =  {}
        if ids:
            data_obj=self.pool.get('change.diff.location').browse(cr, uid, ids[0], context=context)
            from_location_id=data_obj.from_location_id.id
            to_location_id=data_obj.to_location_id.id
            date=data_obj.transfer_date
            note_id=data_obj.note_id.id
            note_data=self.pool.get('branch.good.issue.note').browse(cr, uid, note_id, context=context)
            default.update({
            'state':'pending',
            'from_location_id':from_location_id,
            'issue_date':date,
            'remark':data_obj.remark,            
            })
            gin = self.pool.get('branch.good.issue.note').transfer_other_location_gin(cr,uid,note_id,default,context=context)
            #self.pool.get('branch.good.issue.note').transfer_other_location(cr, uid,note_id,from_location_id,to_location_id,date, context=context)

            

        return True        
        


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

