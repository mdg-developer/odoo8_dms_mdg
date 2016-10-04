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
import time
from openerp.osv import fields, osv

class unassign_sale_team(osv.osv_memory):
    _name = 'partner.unassign.sale.team'
    _description = 'Unassign Sale Team'
    _columns = {
        'confirm':fields.boolean('Unassign Sale Team' ,readonly=True),
    }

    _defaults = {
         'confirm': True,         
    }

    def print_report(self, cr, uid, ids, context=None):
        data = self.read(cr, uid, ids, context=context)[0]
        partner_obj = self.pool.get('res.partner')
        datas = {
             'ids': context.get('active_ids', []),
             'model': 'res.partner',
             'form': data
            }
        partner_id=datas['ids']
        print 'mobile_id',partner_id
        for partner in partner_id: 
            cr.execute('update res_partner set section_id=null where id=%s',(partner,))      
            cr.execute('delete from sale_team_customer_rel where sale_team_id=%s',(partner,))      
        return True
                                                                                         
            
               


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
