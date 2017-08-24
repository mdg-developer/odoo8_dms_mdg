from openerp.osv import fields, osv
from openerp.tools.translate import _


class account_invoice_line(osv.osv):
    
    _inherit = "account.invoice.line"    

    
    def _get_bigger_qty(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        uom_obj = self.pool.get('product.uom')
        #total_qty = remainder_amt = modulus_amt = smaller_qty = bigger_qty = factor = 0
        for data in self.browse(cr, uid, ids, context=context):
            adr_id = False
            total_qty = remainder_amt = modulus_amt = smaller_qty = bigger_qty = factor = 0
            if data.uos_id.id == data.product_id.big_uom_id.id:
                
                
                total_qty = data.quantity * data.product_id.big_uom_id.factor
                total_qty = self.uom_convert(cr, uid, data.product_id.big_uom_id.id, data.quantity, context)
                factor = self.uom_factor_convert(cr, uid, data.product_id.big_uom_id.id, context)
                #total_qty = uom_obj._compute_qty_obj(cr, uid, data.product_uom, data.product_uom_qty, data.product_id.uom_id, context=context)
                
                remainder_amt = total_qty % factor
                modulus_amt = int(total_qty / factor)
                
                if modulus_amt >= 1:
                   bigger_qty = modulus_amt 
                   
#                 if remainder_amt > 0:
#                     smaller_qty =  remainder_amt * factor
            else:
                smaller_qty = data.quantity       
            res[data.id] = bigger_qty
        return res
    
    def _get_smaller_qty(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        uom_obj = self.pool.get('product.uom')
        #total_qty = remainder_amt = modulus_amt = smaller_qty = bigger_qty = factor = 0
        for data in self.browse(cr, uid, ids, context=context):
            adr_id = False
            total_qty = remainder_amt = modulus_amt = smaller_qty = bigger_qty = factor = 0
            if data.uos_id.id == data.product_id.big_uom_id.id:
                
                
                total_qty = data.quantity * data.product_id.big_uom_id.factor
                total_qty = self.uom_convert(cr, uid, data.product_id.big_uom_id.id, data.quantity, context)
                factor = self.uom_factor_convert(cr, uid, data.product_id.big_uom_id.id, context)
                #total_qty = uom_obj._compute_qty_obj(cr, uid, data.product_uom, data.product_uom_qty, data.product_id.uom_id, context=context)
                
                remainder_amt = total_qty % factor
                modulus_amt = int(total_qty / factor)                
                
                   
                if remainder_amt > 0:
                    #smaller_qty =  remainder_amt
                    smaller_qty = int(round(remainder_amt)) 
                
                if modulus_amt < 1 :
                   smaller_qty += modulus_amt * factor    
            else:
                smaller_qty = data.quantity       
            res[data.id] = smaller_qty
        return res
    
    def _get_bigger_uom(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        
        for data in self.browse(cr, uid, ids, context=context):
            adr_id = False
            res[data.id] = data.product_id.big_uom_id.id
#             if data.uos_id.id == data.product_id.big_uom_id.id:
#                 adr_id = data.uos_id.id
#             else:
#                 adr_id = data.uos_id.id
#                 
#             res[data.id] = adr_id
        return res

    def _get_smaller_uom(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        
        for data in self.browse(cr, uid, ids, context=context):
            adr_id = False
            res[data.id] = data.product_id.uom_id.id
#             if data.uos_id.id == data.product_id.big_uom_id.id:
#                 adr_id = data.uos_id.id
#             else:
#             adr_id = data.product_id.uom_id.id    
#             res[data.id] = adr_id
        return res   
    
    def _get_state(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        
        for data in self.browse(cr, uid, ids, context=context):
            adr_id = False
            res[data.id] = data.invoice_id.state

        return res   
    _columns ={
                #'state' : fields.function(_get_state, string="state", type="char"),     
                'big_uom_id': fields.function(_get_bigger_uom, type="many2one", relation="product.uom"),
                'bigger_qty' : fields.function(_get_bigger_qty, string="Bigger Qty",  type="float"),
                'smaller_uom_id': fields.function(_get_smaller_uom, type="many2one", relation="product.uom"),
                'smaller_qty' : fields.function(_get_smaller_qty, string="Smaller Qty",  type="float"),
              }
    
    def uom_factor_convert(self,cr,uid,uom_id,context = None):
        bigger_qty = 0
        if uom_id:
            cr.execute("select floor(round(1/factor,2)) as ratio from product_uom where active = true and id=%s", (uom_id,))
            bigger_qty = cr.fetchone()[0]
            bigger_qty =int(bigger_qty) 
        return bigger_qty
    
    def uom_convert(self,cr,uid,uom_id,qty,context = None):
        bigger_qty = 0
        if uom_id:
            cr.execute("select floor(round(1/factor,2)) as ratio from product_uom where active = true and id=%s", (uom_id,))
            bigger_qty = cr.fetchone()[0]
            bigger_qty = bigger_qty * qty#int(bigger_qty) 
        return bigger_qty 
    
account_invoice_line()  