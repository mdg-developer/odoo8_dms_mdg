from openerp.osv import fields, osv
from openerp.tools.translate import _

class res_city(osv.osv):
    _inherit = "res.city"
    
    _columns = {
               'delivery_team_id':fields.many2one('crm.case.section', 'Delivery Team',required=False),
               }
    
    def get_stock_status_label(self, cr, uid, ids, city_name=None, township_name=None, context=None):
         
        city_obj = self.pool.get('res.city')       
        if city_name:
            city_data = city_obj.search(cr, uid, [('name', '=', city_name)], context=context)            
            if city_data:
                city = city_obj.browse(cr, uid, city_data, context=context)
                if city.delivery_team_id:
                    issue_location = city.delivery_team_id.issue_location_id.id                             
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
                                    and location_id=%s
                                    group by default_code
                                )B on (A.default_code=B.default_code)
                                where qty is null''',(issue_location,))
                    product_record = cr.dictfetchall()                    
                    if product_record:
                        return product_record                  
                                    