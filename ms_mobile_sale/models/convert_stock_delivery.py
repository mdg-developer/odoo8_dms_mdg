from openerp.osv import fields, osv

class mobile_stock_delivery(osv.osv):
    _name = "stock.delivery"
    _description = "Mobile Stock Delivery"
    _rec_name = 'so_ref_no'
    _columns = {
       'customer_id':fields.many2one('res.partner', 'Customer'),
        'date':fields.date('Date'),
        'status':fields.char('Status'),
        'delivery_line': fields.one2many('stock.delivery.line', 'stock_delivery_id', 'Delivery Order Lines'),
        'note':fields.text('Note'),
        'so_ref_no':fields.char('Sale Order No'),
        'm_status' : fields.char('Status'),
        'picking_ref_id':fields.many2one('stock.picking', 'Picking Ref'),

#             'tranc_type':fields.selection([
#                                              ('exchange', 'Exchange'),
#                                              ('color_change', 'Color Change'),
#                                              ('delivery', 'Delivery'),
#                                              ('sale_return', 'Sale Return')], 'Transaction Type'),

    }
    
    _defaults = {
                 'm_status' : 'draft'
    }
    
    def product_qty_in_stock(self, cr, uid, warehouse_id , context=None, **kwargs):
            cr.execute("""
                select product_id,qty_on_hand + qty as qty_on_hand,main_group,name_template from (
                select sm.product_id  ,sum(sm.product_uos_qty) as qty_on_hand ,0 as qty, pt.main_group, pp.name_template
                                      from stock_move sm , stock_picking sp , stock_picking_type spt,product_template pt, product_product pp
                                      where sm.picking_id = sp.id
                          and sm.state = 'done'                     
                          and spt.id = sm.picking_type_id
                          and sp.picking_type_id = sm.picking_type_id
                          and spt.code = 'internal'
                          and sm.location_dest_id = %s
                          and sm.create_date::date = now()::date
                          and sm.product_id = pp.id
                          and pp.product_tmpl_id = pt.id
                          group by product_id, pt.main_group, pp.name_template)A
                """, (warehouse_id,))
    #         cr.execute("""
    #                   select product_id,qty_on_hand + qty as qty_on_hand from (
    #             select sm.product_id  ,sum(sm.product_uos_qty) as qty_on_hand ,0 as qty
    #                                   from stock_move sm , stock_picking sp , stock_picking_type spt
    #                                   where sm.picking_id = sp.id
    #                       and sm.state = 'done'
    #                       and sm.origin is null
    #                       and sp.origin is null
    #                       and spt.id = sm.picking_type_id
    #                       and sp.picking_type_id = sm.picking_type_id
    #                       and spt.code = 'internal'
    #                       and sm.location_dest_id = %s
    #                       and sm.create_date::date = now()::date
    #                       group by product_id
    # 
    #             union All
    #               select sm.product_id,0 as qty,-sum(sm.product_uos_qty) as qty_on_hand 
    #                         from stock_move sm , stock_picking sp , stock_picking_type spt
    #                         where sm.picking_id = sp.id
    #                         and sm.state = 'done'
    #                         and sm.origin is null
    #                         and sp.origin is null
    #                         and spt.id = sm.picking_type_id
    #                         and sp.picking_type_id = sm.picking_type_id
    #                         and spt.code = 'internal'
    #                         and sm.location_id = %s
    #                         and sm.create_date::date = now()::date
    #                         group by product_id
    #                        )
    #                 A
    #             """, (warehouse_id, warehouse_id,))
            datas = cr.fetchall()
            print 'datas',datas
            return datas
	
    def stock_delivery_line(self, cr, uid, pick_id , context=None, **kwargs):
        cr.execute(""" select sm.product_id,sum(sm.product_uos_qty) as product_uos_qty
                        from stock_move sm , stock_picking sp
                        where sm.picking_id = sp.id
                        and sm.state ='assigned'
                        and sp.id = %s
                        group by sp.name ,sm.partner_id ,sm.date::date ,sm.product_id
                    """, (pick_id,))
        datas = cr.fetchall()
        return datas

    def stock_delivery(self, cr, uid, user_id, context=None, **kwargs):
        cr.execute("""select sm.origin as so_name, sm.partner_id ,sm.date::date,
                        sm.tb_ref_no,sp.id as pick_id ,
                        sp.name as pick_name,sp.tranc_type
                        from stock_move sm , stock_picking sp
                        where sm.picking_id = sp.id
                        and sm.state ='assigned'
                        and sp.create_uid = %s
                        group by sp.id,sm.origin ,sm.partner_id ,sm.date::date,
                        sm.tb_ref_no ,sp.tranc_type ,sp.name
                        """, (user_id,))

        datas = cr.fetchall()
        return datas

    def action_convert_sd(self, cr, uid, ids, context=None):
        for stockdeli in self.browse(cr, uid, ids, context=context):            
            cr.execute('SELECT import_mobile_sd_to_server(%s,%s,%s)', (stockdeli['so_ref_no'], stockdeli.picking_ref_id.id, stockdeli['id']))
            cr.execute("update stock_delivery set m_status='done' where so_ref_no = %s and picking_ref_id = %s and id = %s", (stockdeli['so_ref_no'], stockdeli.picking_ref_id.id, stockdeli['id'],))
mobile_stock_delivery()


class mobile_stock_delivery_line(osv.osv):
    _name = "stock.delivery.line"
    _description = "Mobile Stock Delivery"

    _columns = {
       'product_id':fields.many2one('product.product', 'Product'),
        'product_uos_qty':fields.float('Quantity'),
         'product_delivered_qty':fields.float('Delivered Quantity'),
        'stock_delivery_id':fields.many2one('stock.delivery', 'Delivey Id'),
        'tablet_id':fields.many2one('tablets.information', 'Tablet Id'),
         # 'delivery_id': fields.many2one('mobile.sale.order', 'Sale Order'),

    }
    _defaults = {
                 'product_uos_qty':1.0,
                 'product_delivered_qty':1.0,
    }
mobile_stock_delivery_line()