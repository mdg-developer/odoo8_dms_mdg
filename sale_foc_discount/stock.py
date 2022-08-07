from openerp.osv import fields, osv
from datetime import datetime
from openerp.tools.translate import _
from openerp.fields import Many2one
from openerp import tools

class stock_move(osv.osv):
    _inherit = 'stock.move'
    _columns = {
        'foc': fields.boolean('FOC',readonly=True),
        
               }

#     def _picking_assign(self, cr, uid, move_ids, procurement_group, location_from, location_to, context=None):
#         """Assign a picking on the given move_ids, which is a list of move supposed to share the same procurement_group, location_from and location_to
#         (and company). Those attributes are also given as parameters.
#         """
#         pick_obj = self.pool.get("stock.picking")
#         # Use a SQL query as doing with the ORM will split it in different queries with id IN (,,)
#         # In the next version, the locations on the picking should be stored again.
#         query = """
#             SELECT stock_picking.id FROM stock_picking, stock_move
#             WHERE
#                 stock_picking.state in ('draft', 'confirmed', 'waiting') AND
#                 stock_move.picking_id = stock_picking.id AND
#                 stock_move.location_id = %s AND
#                 stock_move.location_dest_id = %s AND
#         """
#         params = (location_from, location_to)
#         if not procurement_group:
#             query += "stock_picking.group_id IS NULL LIMIT 1"
#         else:
#             query += "stock_picking.group_id = %s LIMIT 1"
#             params += (procurement_group,)
#         cr.execute(query, params)
#         [pick] = cr.fetchone() or [None]
#         if not pick:
#             move = self.browse(cr, uid, move_ids, context=context)[0]
#             date_value = datetime.strptime(move.date, '%Y-%m-%d %H:%M:%S')            
#             
#             values = {
#                 'origin': move.origin,
#                 'company_id': move.company_id and move.company_id.id or False,
#                 'move_type': move.group_id and move.group_id.move_type or 'direct',
#                 'partner_id': move.partner_id.id or False,
#                 'picking_type_id': move.picking_type_id and move.picking_type_id.id or False,
#                 'date':date_value
#             }
#             pick = pick_obj.create(cr, uid, values, context=context)
#         return self.write(cr, uid, move_ids, {'picking_id': pick}, context=context)

class stock_picking(osv.osv):
    _inherit = 'stock.picking'
   

  
#     def do_enter_transfer_details(self, cr, uid, picking, context=None):
#         invoice_obj = self.pool.get("account.invoice")
#         result = super(stock_picking,self).do_enter_transfer_details(cr,uid,picking,context)
#         picking_data = self.browse(cr, uid, picking, context=context)
#         if picking_data and picking_data.origin:
#             sale_order_number = picking_data.origin
#             invoice_ids = invoice_obj.search(cr,uid,[('origin','=',sale_order_number),])
#             if invoice_ids and len(invoice_ids)>0:
#                 invoice_obj.signal_workflow(cr,uid,invoice_ids,'invoice_open')
#                 return result
#             #else:
#                 #raise osv.except_osv(('Invalid Action!'), ('Please create invoice for Sale Order %s !!' % (sale_order_number)))
#               #  return False
#         return result