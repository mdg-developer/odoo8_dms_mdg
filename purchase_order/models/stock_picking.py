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
import datetime
JOURNAL_TYPE_MAP = {
    ('outgoing', 'customer'): ['sale'],
    ('outgoing', 'supplier'): ['purchase_refund'],
    ('outgoing', 'transit'): ['sale', 'purchase_refund'],
    ('incoming', 'supplier'): ['purchase'],
    ('incoming', 'customer'): ['sale_refund'],
    ('incoming', 'transit'): ['purchase', 'sale_refund'],
}  
class stock_picking(osv.osv): 
    _inherit = 'stock.picking'
    _columns = {
                'customer' :fields.related('partner_id', 'customer', type='boolean', string='Customer'),
                'supplier' :fields.related('partner_id', 'supplier', type='boolean', string='Supplier'),
                'bl_date':fields.date('BOL Received Date'),
                'staffing_date':fields.date('Staffing Date'),
                'etd_date':fields.date('ETD Date'),
                'eta_date':fields.date('ETA Date'),
                'order_date':fields.date('Order Confirmed Date'),
                'invoice_date':fields.date('Invoice Date'),
               }    
    #def change_location(self,cr,uid,ids,picking_type_id,context=None):
    def change_location(self,cr,uid,ids,context=None):
        picking_type_obj = self.pool.get('stock.picking.type')
        stock_move_obj = self.pool.get('stock.move')
        sequence_obj = self.pool.get('ir.sequence')
        stock_pack_obj=self.pool.get('stock.pack.operation')
        move_lines = []
        for picking in self.browse(cr, uid, ids, context=context):
            picking_type = picking_type_obj.browse(cr,uid,picking.picking_type_id.id,context=context)
            if picking_type:
                move_id = stock_move_obj.search(cr,uid,[('picking_id', 'in', ids)], context=context)                
                for stock_move_id in stock_move_obj.browse(cr,uid,move_id,context=context):
                    stock_move_obj.write(cr,uid,stock_move_id.id,{'location_dest_id':picking_type.default_location_dest_id.id,'picking_type_id':picking_type.id},context=context)
                    move_lines.append(stock_move_id.id)
                pack_ids=stock_pack_obj.search(cr,uid,[('picking_id', 'in', ids)], context=context)   
                for pack_id in stock_pack_obj.browse(cr,uid,pack_ids,context=context):
                    stock_pack_obj.write(cr,uid,pack_id.id,{'location_dest_id':picking_type.default_location_dest_id.id},context=context)
                sequence = sequence_obj.browse(cr,uid,picking_type.sequence_id.id,context=context)
                self.write(cr, uid, ids, {'picking_type_id':picking_type.id}, context=context)
                if sequence:
                    txnCode = sequence_obj.next_by_id(cr, uid, sequence.id, context=context)
                    if txnCode:
                        self.write(cr, uid, ids, {'name':txnCode}, context=context)
                model_obj = self.pool.get('ir.model.data')
                model_obj._get_id(cr,uid,'stock', 'action_picking_tree_done')
                
    def _get_invoice_vals(self, cr, uid, key, inv_type, journal_id, move, context=None):
        
        invoice_vals = super(stock_picking,self)._get_invoice_vals(cr, uid, key, inv_type, journal_id, move, context=context)        
        if invoice_vals:                 
            if invoice_vals.get('type') == 'in_invoice':      
                invoice_vals['origin'] = 'PO-' + invoice_vals.get('origin')
            else:
                invoice_vals['origin'] = invoice_vals['origin']
        return invoice_vals
                
class stock_shipping(osv.osv):                 
    _inherit = "stock.invoice.onshipping"
    
    
    def onchange_journal_id(self, cr, uid, ids, journal_id, context=None):
        if context is None:
            context = {}
        domain = {}
        value = {}
        invoice_date=None
        active_id = context.get('active_id')
        if active_id:
            picking = self.pool['stock.picking'].browse(cr, uid, active_id, context=context)
            type = picking.picking_type_id.code
        invoice_date =datetime.datetime.now().date()

        if picking.partner_id:
            if picking.partner_id.base_on_payment is not None:
                base_on_payment =picking.partner_id.base_on_payment 
                if base_on_payment =='bol_date':
                    invoice_date = picking.bl_date
                if base_on_payment =='etd_date':
                    invoice_date = picking.etd_date
                if base_on_payment =='eta_date':
                    invoice_date = picking.eta_date                                    
                if base_on_payment =='received_date':
                    date_done = datetime.datetime.strptime(picking.date_done,'%Y-%m-%d %H:%M:%S')
                    invoice_date = date_done.date()
                if base_on_payment =='order_date':
                    invoice_date = picking.order_date    
                if base_on_payment=='invoice_date':
                    invoice_date =picking.invoice_date                                
            if invoice_date:
                value['invoice_date']=invoice_date                         
            usage = picking.move_lines[0].location_id.usage if type == 'incoming' else picking.move_lines[0].location_dest_id.usage
            journal_types = JOURNAL_TYPE_MAP.get((type, usage), ['sale', 'purchase', 'sale_refund', 'purchase_refund'])
            domain['journal_id'] = [('type', 'in', journal_types)]
        if journal_id:
            journal = self.pool['account.journal'].browse(cr, uid, journal_id, context=context)
            value['journal_type'] = journal.type
        return {'value': value, 'domain': domain}                
#     def create_invoice(self, cr, uid, ids, context=None):
#         context = dict(context or {})
#         picking_pool = self.pool.get('stock.picking')
#         data = self.browse(cr, uid, ids[0], context=context)
#         invoice_date=data.invoice_date
#         if data.partner_id:
#             if data.base_on_payment is not None:
#                 base_on_payment =data.base_on_payment 
#                 if base_on_payment =='bol_date':
#                     invoice_date = data.bl_date
#                 if base_on_payment =='etd_date':
#                     invoice_date = data.etd_date
#                 if base_on_payment =='eta_date':
#                     invoice_date = data.eta_date                                    
#                 if base_on_payment =='received_date':
#                     invoice_date = data.date_done.date()
#                 if base_on_payment =='order_date':
#                     invoice_date = data.date.date()                
#                                         
#         journal2type = {'sale':'out_invoice', 'purchase':'in_invoice', 'sale_refund':'out_refund', 'purchase_refund':'in_refund'}
#         context['date_inv'] = invoice_date
#         acc_journal = self.pool.get("account.journal")
#         inv_type = journal2type.get(data.journal_type) or 'out_invoice'
#         context['inv_type'] = inv_type
# 
#         active_ids = context.get('active_ids', [])
#         
#         res = picking_pool.action_invoice_create(cr, uid, active_ids,
#               journal_id = data.journal_id.id,
#               group = data.group,
#               type = inv_type,
#               context=context)
#         return res
                