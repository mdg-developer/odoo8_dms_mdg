import pytz
from openerp import SUPERUSER_ID, workflow
from datetime import datetime
from dateutil.relativedelta import relativedelta
from operator import attrgetter
from openerp.tools.safe_eval import safe_eval as eval
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from openerp.osv.orm import browse_record_list, browse_record, browse_null
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP
from openerp.tools.float_utils import float_compare
  
class stock_picking(osv.osv): 
    _inherit = 'stock.picking'
    
    #def change_location(self,cr,uid,ids,picking_type_id,context=None):
    def change_location(self,cr,uid,ids,context=None):
        picking_type_obj = self.pool.get('stock.picking.type')
        stock_move_obj = self.pool.get('stock.move')
        sequence_obj = self.pool.get('ir.sequence')
        result = {}
        move_lines = []
        for picking in self.browse(cr, uid, ids, context=context):
            picking_type = picking_type_obj.browse(cr,uid,picking.picking_type_id.id,context=context)
            if picking_type:
                move_id = stock_move_obj.search(cr,uid,[('picking_id', '=', ids)], context=context)
                #stock_move = stock_move_obj.browse(cr,uid,move_id,context=context)
                
                for stock_move_id in stock_move_obj.browse(cr,uid,move_id,context=context):
                    stock_move_obj.write(cr,uid,stock_move_id.id,{'location_dest_id':picking_type.default_location_dest_id.id,'picking_type_id':picking_type.id},context=context)
                    move_lines.append(stock_move_id.id)
                sequence = sequence_obj.browse(cr,uid,picking_type.sequence_id.id,context=context)
                self.write(cr, uid, ids, {'picking_type_id':picking_type.id}, context=context)
                if sequence:
                    #txnCode = self.pool.get('ir.sequence').get(cr, uid,sequence.name) or '/'
                    txnCode = sequence_obj.next_by_id(cr, uid, sequence.id, context=context)
                    if txnCode:
                        self.write(cr, uid, ids, {'name':txnCode}, context=context)
                model_obj = self.pool.get('ir.model.data')
                data_id = model_obj._get_id(cr,uid,'stock', 'action_picking_tree_done')

#                 result['value'] = {'name':txnCode,'move_lines': [(6, 0, move_lines)]}
#                 return result
                if data_id:
                    view_id = model_obj.browse(cr,uid,data_id).res_id
#                     return {
#                             'name': _('Import File result'),
#                             'res_id': ids[0],
#                             'view_type': 'form',
#                             'view_mode': 'form',
#                             'res_model': 'stock.picking',
#                             'view_id': [view_id[1]],
#                             'target': 'new',
#                             'type': 'ir.actions.act_window',
#                         }
#                     return {
#     
#                          'type': 'ir.actions.act_window',
#                 
#                          'tag': 'reload',               
#                 
#                          'name': _('View Name'),               
#                 
#                          'res_model': 'stock.picking',               
#                 
#                          'view_type': 'form',               
#                 
#                          'view_mode': 'form',               
#                 
#                          'view_id': view_id,               
#                 
#                          'target': 'new',               
#                 
#                          #'nodestroy': True,
#                 
#                      }        
#                 return {'type': 'ir.actions.act_window',
#                 'res_model': 'stock.picking',
#                 'view_mode': 'form',
#                 'res_id': picking.id,
#                 'target': 'current',
#                 'target': 'new',
#                 #'flags': {'form': {'action_buttons': True}}
#                 }        