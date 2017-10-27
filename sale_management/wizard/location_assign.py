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
    _name = "sale.make.location"
    _description = "Sales Make location"
    
    def on_change_sale_team_id(self, cr, uid, ids, section_id, context=None):
        values = {}
        sale_team_obj = self.pool.get('crm.case.section')        
        team_data=sale_team_obj.browse(cr, uid, section_id, context=context)
        warehouse_id=team_data.warehouse_id.id
        location_id=team_data.location_id.id
        values = {
                  'warehouse_id':warehouse_id,
                  'location_id':location_id,
        }
        return {'value': values}        
    
    _columns = {
                'section_id':fields.many2one('crm.case.section','Delivery Team',required=True),
                'user_id':fields.many2one('res.users','Salesperson',required=True),
                'warehouse_id':fields.many2one('stock.warehouse','Warehouse',store=True),
                'location_id':fields.many2one('stock.location','Location',store=True),

    }

    
    def make_location(self, cr, uid, ids, context=None):
        data = self.read(cr, uid, ids, context=context)[0]
        order_obj = self.pool.get('sale.order')
        section_obj = self.pool.get('crm.case.section')
        section_id=data['section_id'][0]
        user_id=data['user_id'][0]
        section_data=section_obj.browse(cr,uid,section_id,context=context)
        warehouse_id=section_data.warehouse_id.id
        lcoation_id =section_data.location_id.id
        datas = {
             'ids': context.get('active_ids', []),
             'model': 'sale.order',
             'form': data
            }
        
        order_id=datas['ids']
        for order in order_id: 
            sale_data=order_obj.browse(cr,uid,order,context=context)
            so_no=sale_data.name
            cr.execute("update sale_order set delivery_id =%s ,user_id=%s,warehouse_id =%s where name =%s and state!='done'",(section_id,user_id,warehouse_id,so_no,))
            #picking_ids = self.pool.get('stock.picking').search(cr, uid, [('origin', '=',so_no),('state','!=','done')], context=context)
            picking_ids = self.pool.get('stock.picking').search(cr, uid, [('group_id', '=',so_no),('state','!=','done')], context=context)
            if picking_ids:
                for picking_id in picking_ids: 
                    self.pool.get('stock.picking').unlink(cr,uid,picking_id,context=context)
            procurement_order_obj = self.pool.get('procurement.order')        
            procurement_ids = self.pool.get('procurement.order').search(cr,uid,[('group_id', '=',so_no)], context=context)
            if procurement_ids:
                for procurement_id in procurement_ids:
                    osv.osv.unlink(procurement_order_obj, cr, uid, procurement_id, context=context)
                    cr.execute("delete from procurement_order where id=%s",(procurement_id,))
                    #self.pool.get('procurement.order').unlink(cr,uid,procurement_id,context=context)
#             cr.execute("update stock_move set location_id =%s where picking_id in %s ",(lcoation_id,tuple(picking_ids),))
#             cr.execute('''select id from stock_picking_type where lower(name) like 'delivery orders' and default_location_src_id= %s''',(lcoation_id,))
#             picking_type_id=cr.fetchone()[0]
#             if picking_type_id:
#                 cr.execute("update stock_picking set picking_type_id =%s where id in %s ",(picking_type_id,tuple(picking_ids),))
#             cr.execute("update account_invoice set user_id =%s ,section_id=%s,collection_user_id =%s ,collection_team_id=%s where origin =%s and state ='draft' ",(user_id,section_id,user_id,section_id,so_no,))
        #self.signal_workflow(cr,uid,ids,'ship_recreate')
        self.pool.get('sale.order').action_ship_create(cr,uid,order,context=context)
        return True


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

