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

from openerp.osv import orm
from openerp.osv import fields, osv

class sale_report_url(osv.osv):
    _name = 'sale.report.url'
    _description = 'Report_URL'
    _rec_name="url_name"
    
    _columns = {
                    'url_link':fields.char('URL', size=150, required=True),
                    'url_name':fields.char('Report Name', size=150, required=True),
					'local_cloud':fields.selection([('local', 'Local Server'),
                ('cloud', 'Cloud Server'),
                ('null', ''),
            ], 'Local_Cloud'),
                   
                }
    
    def go_report(self, cr, uid, ids, context=None):
        result =  {
                  'name'     : 'Go to Report',
                  'res_model': 'ir.actions.act_url',
                  'type'     : 'ir.actions.act_url',
                  'target'   : 'new',
               }
        for record in self.browse(cr,uid,ids,context=context):
            user_id = uid
            print user_id
            print record.url_link+'&user_id='+ str(user_id)
            result['url'] = record.url_link+'&user_id='+ str(user_id)
            
        return result


sale_report_url()