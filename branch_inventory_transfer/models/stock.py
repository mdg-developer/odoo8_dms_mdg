from openerp.osv import fields, osv

class stock_warehouse(osv.osv):
    _inherit = "stock.warehouse"
    
    _columns = {
                'target_ratio': fields.float('Target Ratio'),
                'warehouse_spacing': fields.float('Warehouse Spacing(CBM)'),
                'resupply_line': fields.one2many('warehouse.resupply.rule.line', 'warehouse_id', 'Resupply Lines'),
            }
    
    def retrieve_resupply_rule(self, cr, uid, ids, context=None): 
        
        warehouse_resupply_obj = self.pool.get('warehouse.resupply.rule.line')
        if ids:
            warehouse = self.browse(cr, uid, ids[0], context=context)
            warehouse.resupply_line.unlink()
            cr.execute("""select pp.id,uom.id uom,cbm_value,ctn_pallet
                        from product_product pp,product_template pt,product_uom uom
                        where pp.product_tmpl_id=pt.id 
                        and pt.report_uom_id=uom.id
                        and pt.type!='service' 
                        and is_foc!='True'
                        and pt.active='True'
                        and pp.active='True' 
                        order by pp.sequence asc""")
            product_data = cr.fetchall()
            if product_data:
                for p_line in product_data:      
                    product_id = p_line[0]
                    uom_id = p_line[1]
                    cbm_value = p_line[2]
                    ctn_pallet = p_line[3]
                    warehouse_resupply_obj.create(cr, uid, {'warehouse_id': ids[0],                                                            
                                                            'product_id': product_id, 
                                                            'uom_id': uom_id, 
                                                            'cbm_value': cbm_value, 
                                                            'ctn_pallet': ctn_pallet, 
                                                        }, context=context)
        return True
    
class warehouse_resupply_rule_line(osv.osv):
    
    _name = "warehouse.resupply.rule.line"
    _description = "Resupply Lines"

    _columns = {
                'warehouse_id': fields.many2one('stock.warehouse', 'Warehouse'),
                'product_id':fields.many2one('product.product', 'Product'),
                'sequence' : fields.related('product_id', 'sequence',
                                          type='char',
                                          readonly=True,
                                          string='Sequence'),       
                'uom_id' : fields.related('product_id', 'product_tmpl_id', 'report_uom_id',
                                          type='many2one',
                                          readonly=True,
                                          relation='product.uom',
                                          string='UOM'),                         
                'moq_value':fields.float('MOQ'),
                'factor':fields.float('Factor'),                
                'qty':fields.float('Standard(Qty)'),
                'cbm_value' : fields.related('product_id', 'product_tmpl_id', 'cbm_value',
                                          type='float',
                                          readonly=True,                                         
                                          string='CBM'),
                'pallet_value' : fields.related('product_id', 'product_tmpl_id', 'ctn_pallet',
                                          type='float',
                                          readonly=True,                                         
                                          string='Pallet'),               
            } 
    