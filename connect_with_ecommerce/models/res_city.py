from openerp.osv import fields, osv
from openerp.tools.translate import _
import logging

class res_city(osv.osv):
    _inherit = "res.city"
    
    _columns = {
               'delivery_team_id':fields.many2one('crm.case.section', 'Delivery Team',required=False),
               }
    
    def get_stock_status_label(self, cr, uid, ids, city_name=None, township_name=None, context=None):
         
        city_obj = self.pool.get('res.city')   
        location_ids = []     
        if city_name:
            city_data = city_obj.search(cr, uid, [('name', '=', city_name)], context=context)            
            if city_data:
                cr.execute('''select lot_stock_id
                            from res_branch rb,stock_warehouse sw,res_branch_city_rel rel
                            where rb.id=sw.branch_id
                            and sw.branch_id=rel.branch_id
                            and rel.city_id=%s
                            and main_location=true''',(city_data[0],))
                location_record = cr.fetchall()                    
                if location_record:
                    for loc in location_record:
                        location_ids.append(loc[0])
                    logging.warning("Check location for out of stock: %s", location_ids)
                    if location_ids:                                
                        cr.execute('''select A.default_code product_code,case when B.qty is null then 'Out of Stock' end as label
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
                                    where qty is null''',(tuple(location_ids),))
                        product_record = cr.dictfetchall()                    
                        if product_record:
                            return product_record                  
                                    