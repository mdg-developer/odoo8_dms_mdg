from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from openerp.exceptions import except_orm, Warning, RedirectWarning
    
class account_invoice(osv.osv):
    _inherit = 'account.invoice'    
    
    def _get_corresponding_supermarket(self, cr, uid, ids, field_name, arg, context=None):
        result = {}
        order_id = None
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.origin:
                cr.execute("""select supermarket_sale from sale_order where name=%s""", (rec.origin,))
                data = cr.fetchall()
                if data:
                    order_id = data[0]
                print 'order_id >>> ', order_id
                result[rec.id] = order_id
            else:
                result[rec.id] = None
        return result      
    
    _columns = {
                'supermarket_sale': fields.function(_get_corresponding_supermarket,type='boolean',string="SuperMarket Sale" ,readonly=True,store=True),                                 
}
        
account_invoice()   

