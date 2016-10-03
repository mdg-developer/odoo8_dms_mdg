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
from openerp.tools.translate import _

class insert_sale_team(osv.osv_memory):
    _name = 'partner.sale.team'
    _description = 'Sale Team Insert'
    _columns = {
        'section_id':fields.many2one('crm.case.section','Sales Team' ),
                'outlet_type': fields.many2one('outlettype.outlettype', 'Outlet Type'),
                'sales_channel':fields.many2one('sale.channel', 'Sale Channel'),
                'frequency_id':fields.many2one('plan.frequency','Frequency'),
                'class_id':fields.many2one('sale.class', 'Class'),
                'branch_id':fields.many2one('res.branch', 'Branch'),
                'chiller':fields.boolean('Chiller'),
                'state_id':fields.many2one('res.country.state','State'),                
                'city':fields.many2one('res.city','City'),
                'township':fields.many2one('res.township','Township'),        
    }

    def print_report(self, cr, uid, ids, context=None):
        data = self.read(cr, uid, ids, context=context)[0]
        partner_obj = self.pool.get('res.partner')
        team_obj=self.pool.get('crm.case.section')
        
        datas = {
             'ids': context.get('active_ids', []),
             'model': 'res.partner',
             'form': data
            }
        partner_id=datas['ids']
        section_id=data['section_id']
        outlet_type=data['outlet_type']
        sales_channel=data['sales_channel']        
        frequency_id=data['frequency_id']
        class_id=data['class_id']
        branch_id=data['branch_id']
        chiller=data['chiller']
        state_id=data['state_id']        
        city=data['city']
        township=data['township']
        
        print 'partner_id',partner_id
        for partner in partner_id: 
            partner_data=partner_obj.browse(cr,uid,partner,context=context)
            if section_id:
                team=team_obj.browse(cr,uid,section_id[0],context=context)
                team_name=team.name
                cr.execute('select sale_team_id,partner_id from sale_team_customer_rel where partner_id=%s and sale_team_id=%s',(section_id[0],partner,))
                team_id=cr.fetchone()
                if team_id:
                    raise osv.except_osv(_('Warning!'),_('You inserted this sales team (%s) in (%s ,%s).')%(team_name,partner_data.name,partner_data.customer_code,))                    
                else:
                    cr.execute('INSERT INTO sale_team_customer_rel (sale_team_id,partner_id) VALUES (%s,%s)', ( partner,section_id[0],))
            if  outlet_type:
                cr.execute('update res_partner set outlet_type=%s where id=%s',(outlet_type[0],partner,))
            if  sales_channel:
                cr.execute('update res_partner set sales_channel=%s where id=%s',(sales_channel[0],partner,))
            if  frequency_id:
                cr.execute('update res_partner set frequency_id=%s where id=%s',(frequency_id[0],partner,))
            if  class_id:
                cr.execute('update res_partner set class_id=%s where id=%s',(class_id[0],partner,))
            if  branch_id:
                cr.execute('update res_partner set branch_id=%s where id=%s',(branch_id[0],partner,))
            if chiller is True:
                cr.execute('update res_partner set chiller=%s where id=%s',(True,partner,))
            if  state_id:
                cr.execute('update res_partner set state_id=%s where id=%s',(state_id[0],partner,))
            if  city:
                cr.execute('update res_partner set city=%s where id=%s',(city[0],partner,))
            if  township:
                cr.execute('update res_partner set township=%s where id=%s',(township[0],partner,))                                                
        return True              
