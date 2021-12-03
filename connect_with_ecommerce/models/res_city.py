from openerp.osv import fields, osv
from openerp.tools.translate import _
import logging

class res_city(osv.osv):
    _inherit = "res.city"
    
    _columns = {
               'delivery_team_id':fields.many2one('crm.case.section', 'Delivery Team',required=False),
               }
    
    def get_stock_status_label(self, cr, uid, ids, city_name=None, township_name=None, woo_customer_id=None, context=None):
         
        partner_obj = self.pool.get('res.partner')
        location_ids = []     
        if woo_customer_id:
            woo_customer = '1_' + woo_customer_id
            partner_data = partner_obj.search(cr, uid, [('woo_customer_id', '=', woo_customer)], context=context)
            if partner_data:
                partner_value = partner_obj.browse(cr, uid, partner_data, context=context)
                branch_id = partner_value.township.delivery_team_id.branch_id.id if partner_value.township.delivery_team_id.branch_id else None       
                if branch_id:
                    cr.execute('''select lot_stock_id
                                from res_branch rb,stock_warehouse sw
                                where rb.id=sw.branch_id
                                and rb.active=true
                                and rb.id=%s
                                and main_location=true''',(branch_id,))
                    location_record = cr.fetchall()                    
                    if location_record:
                        for loc in location_record:
                            location_ids.append(loc[0])
                        logging.warning("Check location for out of stock: %s", location_ids)
                        if location_ids:                                
                            cr.execute('''select A.default_code product_code,case when B.qty is null or B.qty = 0 then 'Out of Stock' end as label
                                        from
                                        (   select default_code
                                            from product_product pp,product_template pt
                                            where pp.product_tmpl_id=pt.id
                                            and pp.active=true
                                            and pt.active=true
                                            and type!='service'
                                            and default_code is not null     
                                        )A
                                        left join
                                        (
                                            select COALESCE(sum(qty),0) qty,default_code
                                            from stock_quant sq,product_product pp,product_template pt
                                            where sq.product_id=pp.id
                                            and pp.product_tmpl_id=pt.id
                                            and location_id in %s
                                            group by default_code
                                        )B on (A.default_code=B.default_code)
                                        where qty is null or qty=0''',(tuple(location_ids),))
                            product_record = cr.dictfetchall()                    
                            if product_record:
                                return product_record                  
                                    