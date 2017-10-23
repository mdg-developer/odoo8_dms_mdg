from openerp.osv import fields, osv
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare, float_is_zero
from openerp.tools.translate import _  
class sale_order(osv.osv):
    _inherit = 'sale.order'
    _columns = {                    
                    'supermarket_sale': fields.boolean("SuperMarket Sale" , readonly=True),                    
                    }
        
    def action_button_confirm(self, cr, uid, ids, context=None):
        product_uom_obj = self.pool.get('product.uom')
        product_obj = self.pool.get('product.product')        
        stock_obj = self.pool.get('stock.location')        
        
        if not context:
            context = {}
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'
        self.signal_workflow(cr, uid, ids, 'order_confirm')        
        if context.get('send_email'):
            self.force_quotation_send(cr, uid, ids, context=context)
        data = self.browse(cr, uid, ids,context=context)
        if data:
            location_id =761
            location_ids = stock_obj.search(cr, uid, ['|',('location_id', '=', location_id),('id','=',location_id)], context=context)            
            print 'location_ids',location_ids
            for line  in data.order_line:
                uom =line.product_uom.id
                cr.execute("select COALESCE(sum(qty),0) from stock_quant where location_id  = %s and product_id =%s",(location_ids,line.product_id.id,))      
                qty =cr.fetchone()[0]   
                if uom:
                    uom_record = product_uom_obj.browse(cr, uid, uom, context=context)
                    product_obj = product_obj.browse(cr, uid, line.product_id.id, context=context)
                    if product_obj.uom_id.category_id.id != uom_record.category_id.id:
                        uom_record = False
                if not uom_record:
                    uom_record = product_obj.uom_id
                compare_qty = float_compare(qty, line.product_uom_qty, precision_rounding=uom_record.rounding)                                       
                if compare_qty == -1:
                    raise osv.except_osv(_("Not enough stock ! : ") , _(" Your Product Name '%s' is not enough stock !") % (line.product_id.name_template,))
            cr.execute("update stock_picking set branch_id=%s where origin=%s",(data.branch_id.id,data.name,))
            cr.execute("update stock_move set branch_id=%s where picking_id in(select id from stock_picking where origin=%s)",(data.branch_id.id,data.name,))    
        return True
sale_order()

