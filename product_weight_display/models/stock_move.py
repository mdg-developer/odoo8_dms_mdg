from openerp.osv import fields, osv
from math import floor

class stock_move(osv.osv):
    _inherit = 'stock.move'   
    
    def _get_gross_weight(self, cr, uid, ids, field_name, arg, context=None):
        res = dict(map(lambda x: (x, 0), ids))        
        product_tmpl_obj = self.pool.get('product.template')
        for data in self.browse(cr, uid, ids, context=context):
            total = 0
            cr.execute("select floor(round(1/factor,2)) as ratio from product_uom where active = true and id=%s", (data.product_uom.id,))
            uom_qty = cr.fetchone()[0]
            if  uom_qty > 1 :
                total_qty = data.product_uom_qty * uom_qty
                template_data = product_tmpl_obj.browse(cr, uid, data.product_id.product_tmpl_id.id, context=context)
                gross_weight = template_data.weight
                total = total_qty * gross_weight
                 
            res[data.id] = total
        return res
    
    def _get_net_weight(self, cr, uid, ids, field_name, arg, context=None):
        res = dict(map(lambda x: (x, 0), ids))        
        product_tmpl_obj = self.pool.get('product.template')
        for data in self.browse(cr, uid, ids, context=context):
            total = 0
            cr.execute("select floor(round(1/factor,2)) as ratio from product_uom where active = true and id=%s", (data.product_uom.id,))
            uom_qty = cr.fetchone()[0]
            if  uom_qty > 1 :
                total_qty = data.product_uom_qty * uom_qty
                template_data = product_tmpl_obj.browse(cr, uid, data.product_id.product_tmpl_id.id, context=context)
                net_weight = template_data.weight_net
                total = total_qty * net_weight                 
            res[data.id] = total
        return res
    
    
    def _get_smaller_qty(self, cr, uid, ids, field_name, arg, context=None):
        res = dict(map(lambda x: (x, 0), ids))        
        product_tmpl_obj = self.pool.get('product.template')
        for data in self.browse(cr, uid, ids, context=context):
            total_qty = 0
            cr.execute("select floor(round(1/factor,2)) as ratio from product_uom where active = true and id=%s", (data.product_uom.id,))
            uom_qty = cr.fetchone()[0]
            if  uom_qty > 1 :
                total_qty = data.product_uom_qty * uom_qty
            res[data.id] = total_qty
        return res

    def _get_bigger_qty(self, cr, uid, ids, field_name, arg, context=None):
        res = dict(map(lambda x: (x, 0), ids))        
        product_tmpl_obj = self.pool.get('product.template')
        for data in self.browse(cr, uid, ids, context=context):
            total_pieces = 0
            cr.execute("select floor(round(1/factor,2)) as ratio from product_uom where active = true and id=%s", (data.product_uom.id,))
            uom_qty = cr.fetchone()[0]
            if  uom_qty > 1 :
                total_qty = data.product_uom_qty * uom_qty
                cr.execute('''select max(d.ratio) ratio
                from
                (
                    select rel.product_template_id pid, rel.product_uom_id uom, floor(1/u.factor) ratio
                    from
                    product_template_product_uom_rel rel,
                    product_uom u
                    where rel.product_uom_id=u.id
                    and rel.product_template_id =%s
                    order by rel.product_template_id
                )d group by d.pid''', (data.product_id.product_tmpl_id.id,))
                bigger_uom_ratio = cr.fetchone()[0]
                print ' bigger_uom_ratio', bigger_uom_ratio
                total_pieces = floor(total_qty / bigger_uom_ratio)
            res[data.id] = total_pieces
        return res
         
    _columns = {
                'gross_weight': fields.function(_get_gross_weight, type='float', string='Gross Weight'),
                'net_weight': fields.function(_get_net_weight, type='float', string='Net Weight'),
                'smaller_qty': fields.function(_get_smaller_qty, type='float', string='Smaller Pieces'),
                'bigger_qty': fields.function(_get_bigger_qty, type='integer', string='CTN'),
              }

stock_move()
class stock_transfer_details(osv.osv):
    
    _inherit = 'stock.transfer_details'
    
    def default_get(self, cr, uid, fields, context=None):
        if context is None: context = {}
        res = super(stock_transfer_details, self).default_get(cr, uid, fields, context=context)
        picking_ids = context.get('active_ids', [])
        active_model = context.get('active_model')

        if not picking_ids or len(picking_ids) != 1:
            # Partial Picking Processing may only be done for one picking at a time
            return res
        assert active_model in ('stock.picking'), 'Bad context propagation'
        picking_id, = picking_ids
        picking = self.pool.get('stock.picking').browse(cr, uid, picking_id, context=context)
        items = []
        packs = []
        if not picking.pack_operation_ids:
            picking.do_prepare_partial()
        for op in picking.pack_operation_ids:
            total_qty = op.product_qty 
            cr.execute('''select max(d.ratio) ratio
            from
            (
                select rel.product_template_id pid, rel.product_uom_id uom, floor(1/u.factor) ratio
                from
                product_template_product_uom_rel rel,
                product_uom u
                where rel.product_uom_id=u.id
                and rel.product_template_id =%s
                order by rel.product_template_id
            )d group by d.pid''', (op.product_id.product_tmpl_id.id,))
            bigger_uom_ratio = cr.fetchone()[0]
            total_pieces = floor(total_qty / bigger_uom_ratio)            
                        
            item = {
                'packop_id': op.id,
                'product_id': op.product_id.id,
                'product_uom_id': op.product_uom_id.id,
                'quantity': op.product_qty,
                'bigger_qty':total_pieces,
                'package_id': op.package_id.id,
                'lot_id': op.lot_id.id,
                'sourceloc_id': op.location_id.id,
                'destinationloc_id': op.location_dest_id.id,
                'result_package_id': op.result_package_id.id,
                'date': op.date,
                'owner_id': op.owner_id.id,
            }
            if op.product_id:
                items.append(item)
            elif op.package_id:
                packs.append(item)
        res.update(item_ids=items)
        res.update(packop_ids=packs)
        return res
    
class stock_transfer_details_items(osv.osv):
    
    _inherit = 'stock.transfer_details_items'
    _columns = {
        'bigger_qty': fields.integer('CTN', default=0)
    }
  
  
