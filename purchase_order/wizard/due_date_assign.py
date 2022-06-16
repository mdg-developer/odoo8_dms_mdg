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

class set_due_date_assign(osv.osv_memory):
    _name = "due.date.assign"
    _description = "Reassign Due Date"
    _columns = {
        
                'due_date':fields.date('Due Date'),
                'invoice_id':fields.many2one('account.invoice','Invoice',store=True),

    }

    
    def make_set_due_date(self, cr, uid, ids, context=None):
        if ids:
            data_obj=self.pool.get('due.date.assign').browse(cr, uid, ids[0], context=context)
            due_date=data_obj.due_date
            invoice_id=data_obj.invoice_id.id
            cr.execute("update account_invoice set date_due=%s where id =%s",(due_date,invoice_id,))
        return True        
        


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

