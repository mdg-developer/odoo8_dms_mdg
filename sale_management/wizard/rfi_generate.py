from openerp.osv import fields, osv
from openerp.tools.translate import _

class rfi_generate(osv.osv_memory):
    _name = "rfi.generate"     
    
    _columns = {
                'is_generate':fields.selection([('true', 'True'), ('false', 'False')], 'RFI Generated'),
    }
    
    def generate_rfi(self, cr, uid, ids, context=None):
        data = self.read(cr, uid, ids, context=context)[0]        
        is_generate = data['is_generate']        
        order_obj = self.pool.get('sale.order')        
        datas = {
             'ids': context.get('active_ids', []),
             'model': 'sale.order',
             'form': data
            }
        
        order_id=datas['ids']
        for order in order_id: 
            sale_data=order_obj.browse(cr,uid,order,context=context)
            cr.execute("update sale_order set is_generate=%s where id=%s",(is_generate,sale_data.id,))                  
        return True
