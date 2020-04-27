from openerp import models,fields,api
from .. import woocommerce
import requests
   
class account_invoice(models.Model):
    _inherit="account.invoice"
    
    woo_instance_id=fields.Many2one("woo.instance.ept","Instances")
    is_refund_in_woo=fields.Boolean("Refund In Woo Commerce",default=False)
    @api.multi
    def refund_in_woo(self):
        transaction_log_obj=self.env['woo.transaction.log']
        for refund in self:
            if not refund.woo_instance_id:
                continue
            wcapi = refund.woo_instance_id.connect_in_woo()
            for order in refund.sale_ids:
                data = {'amount':str(refund.amount_total),'reason':str(refund.name or '')}
                if refund.woo_instance_id.woo_version == 'old':
                    response = wcapi.post('orders/%s/refunds'%(order.woo_order_id),{'order_refund':data})
                elif refund.woo_instance_id.woo_version == 'new':
                    response = wcapi.post('orders/%s/refunds'%(order.woo_order_id),data)
                if not isinstance(response,requests.models.Response):
                    transaction_log_obj.create({'message':"Refund \n Response is not in proper format :: %s"%(response),
                                                 'mismatch_details':True,
                                                 'type':'sales',
                                                 'woo_instance_id':refund.woo_instance_id.id
                                                })
                    continue
                if response.status_code not in [200,201]:
                    transaction_log_obj.create(
                                        {'message':"Refund \n%s"%(response.content),
                                         'mismatch_details':True,
                                         'type':'sales',
                                         'woo_instance_id':refund.woo_instance_id.id
                                        })
                    continue
                response = response.json()
            refund.write({'is_refund_in_woo':True})
        return True

    @api.model
    def _prepare_refund(self, invoice, date=None, period_id=None, description=None, journal_id=None):
        values = super(account_invoice,self)._prepare_refund(invoice, date=date, period_id=period_id, description=description, journal_id=journal_id)
        if invoice.woo_instance_id:
            values.update({'woo_instance_id':invoice.woo_instance_id.id,'sale_ids':[(6,0,invoice.sale_ids.ids)]})        
        return values    

class sale_order(models.Model):
    _inherit="sale.order"
 
    def _make_invoice(self, cr, uid, order, lines, context=None):    
        inv_id=super(sale_order,self)._make_invoice(cr,uid,order,lines,context)        
        if inv_id and order.woo_instance_id:            
            inv=self.pool.get('account.invoice').write(cr,uid,inv_id,{'woo_instance_id':order.woo_instance_id.id})
        return inv_id
    
class stock_picking(models.Model):
    _inherit="stock.picking"
    
    def _create_invoice_from_picking(self, cr, uid, picking, vals, context=None):                  
        if picking.sale_id and picking.sale_id.woo_instance_id:                                         
            vals.update({'woo_instance_id':picking.sale_id.woo_instance_id.id})
        return super(stock_picking,self)._create_invoice_from_picking(cr,uid,picking,vals,context)