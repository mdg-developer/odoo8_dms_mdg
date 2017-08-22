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

class collection_team_assign(osv.osv_memory):
    _name = "collection.assign"
    _description = "Collection Team Assign"
    
    _columns = {
                'section_id':fields.many2one('crm.case.section','Collection Team',required=True),
                'user_id':fields.many2one('res.users','Salesperson',required=True),

    }

    
    def make_assign(self, cr, uid, ids, context=None):
        data = self.read(cr, uid, ids, context=context)[0]
        section_id=data['section_id'][0]
        user_id=data['user_id'][0]
        datas = {
             'ids': context.get('active_ids', []),
             'model': 'account.invoice',
             'form': data
            }
        
        invoice_id=datas['ids']
        for invoice in invoice_id: 
            cr.execute("update account_invoice set collection_user_id =%s ,collection_team_id=%s where id=%s and state !='paid'  ",(user_id,section_id,invoice,))
        return True


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

