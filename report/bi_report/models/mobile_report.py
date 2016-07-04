'''
Created on Nov 14, 2014

@author: Thazin Khiang at seventhcomputing
'''

from openerp import tools
from openerp.osv import fields, osv

class sale_report(osv.osv):
    _name = "mobile.sale.report"
    _description = "Mobile Sales Orders Statistics"
    _auto = False
    _rec_name = 'date'

    _columns = {
         'name': fields.char('Order Reference', size=64),
        'partner_id':fields.many2one('res.partner', 'Customer'),
          'product_id':fields.many2one('product.product', '# of Product'),
        'user_id':fields.many2one('res.users', 'Saleman Name'),
        'sub_total':fields.float('Total Amount'),
        'categ_id':fields.many2one('product.category', 'Saleman Name'),
        'type':fields.selection([
                ('credit', 'Credit'),
                ('cash', 'Cash'),
                ('consiment', 'Consiment'),
                ('advanced', 'Advanced')
            ], 'Payment Type'),
        'delivery_remark':fields.selection([
                ('partial', 'Partial'),
                ('delivered', 'Delivered'),
                ('none', 'None')
            ], 'Deliver Remark'),
        'date':fields.date('Date'),
        'tablet_id':fields.many2one('tablets.information', 'Tablet Id'),
        'sale_plan_day_id':fields.many2one('sale.plan.day', 'Sale Plan Day'),
        'sale_plan_trip_id':fields.many2one('sale.plan.trip', 'Sale Plan Trip'),
        'warehouse_id' : fields.many2one('stock.warehouse', 'Warehouse'),
        'location_id'  : fields.many2one('stock.location', 'Location'),
        'm_status':fields.char('Status'),
     'product_uos_qty': fields.float('Qty', readonly=True),
     'unit_price': fields.float('Unit_price', readonly=True),
     'discount': fields.float('Discount', readonly=True),
     'additional_discount': fields.float('Additional_discount', readonly=True),
     'deduction_amount': fields.float('Deduction_amount', readonly=True),
     'sale_channel': fields.many2one('sale.channel','Channel'),
     'main_group':fields.many2one('product.maingroup','Main Group',readonly=True),
     'customer_code':fields.char('Customer Code')
    }
    _order = 'date desc'

    def _select(self):
        select_str = """
              SELECT min(l.id) as id,sum(l.product_uos_qty) as product_uos_qty,sc.id as sale_channel,
                    sum(l.discount) as discount,
                    sum(s.additional_discount) as additional_discount,
                    l.product_id as product_id,
                    count(*) as nbr,
                    s.date::date as date,
                    s.partner_id as partner_id,
                    s.user_id as user_id,
                    extract(epoch from avg(date_trunc('day',s.date)-date_trunc('day',s.create_date)))/(24*60*60)::decimal(16,2) as delay,
                    s.m_status,
                    t.categ_id as categ_id,
                    s.tablet_id as tablet_id,
                    s.delivery_remark,
                    s.warehouse_id,
                    s.name,
                    l.sub_total,
                    t.list_price as unit_price,
                   
                    s.deduction_amount,
                    s.type,
                    s.location_id,
                     s.sale_plan_day_id,
                     s.sale_plan_trip_id,
                     t.main_group,
                    r.customer_code
        """
        return select_str

    def _from(self):
        from_str = """
                   mobile_sale_order_line l
                      join mobile_sale_order s on (l.order_id=s.id) 
                        left join product_product p on (l.product_id=p.id)
                            left join product_template t on (p.product_tmpl_id=t.id)
                            left join res_partner r on (s.partner_id = r.id)
                            left join sale_channel sc on (r.sales_channel = sc.id)
                             
        """
        return from_str

    def _group_by(self):
        group_by_str = """
              GROUP BY l.product_id,
                    l.order_id,
                    t.uom_id,
                    t.categ_id,
                    s.date,
                    s.partner_id,
                    s.user_id,
                    s.m_status,
                    s.tablet_id ,
                     s.delivery_remark,
                    s.warehouse_id,
                    s.name,
                    l.sub_total,
                    s.type,
                    s.location_id,
                    s.sale_plan_day_id,
                    s.sale_plan_trip_id,
                    unit_price,
                    l.discount,
                    s.additional_discount,
                    s.deduction_amount,
                    sc.id,
                    t.main_group,
                    r.customer_code,
                    s.void_flag
                    having  s.void_flag='none'
                    
        """
        return group_by_str

    def init(self, cr):
        # self._table = sale_report
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (
            %s
            FROM ( %s )
            %s
            )""" % (self._table, self._select(), self._from(), self._group_by()))

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
