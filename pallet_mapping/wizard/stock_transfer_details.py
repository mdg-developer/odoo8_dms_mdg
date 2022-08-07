# from openerp import models, fields, api
# from openerp.exceptions import Warning
# from openerp.tools.translate import _
# import openerp.addons.decimal_precision as dp
# from datetime import datetime
from openerp.osv import orm
from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import datetime
import openerp.addons.decimal_precision as dp

#class stock_transfer_details(models.TransientModel):
class stock_transfer_details(osv.osv):
    
    _inherit = 'stock.transfer_details'
    
    def on_change_template_id(self, cr, uid, ids, template_id):
        res = {}
        if template_id:
            res['value'] = {'line_ids': []}
            template_pool = self.pool.get('account.move.template')
            template = template_pool.browse(cr, uid, template_id)
            for line in template.template_line_ids:
                if line.type == 'input':
                    res['value']['line_ids'].append({
                        'sequence': line.sequence,
                        'name': line.name,
                        'account_id': line.account_id.id,
                        'move_line_type': line.move_line_type,
                        })
        return res
    
    def create_pack_operation(self,cr,uid,product_id,product_uom_id,product_qty,package_id,lot_id,location_id,location_dest_id,result_package_id,date,owner_id):
       
        pack_datas = {
            'product_id': product_id,
            'product_uom_id': product_uom_id,
            'product_qty': product_qty,
            'package_id': package_id,
            'lot_id': lot_id,
            'location_id': location_id,
            'location_dest_id': location_dest_id,
            'result_package_id': result_package_id,
            'date': date if date else datetime.now(),
            'owner_id': owner_id,
        }
        
        packop_id = self.pool.get['stock.pack.operation'].create(pack_datas)
           
       
        return True
    
    def get_uom_id(self, cr, uid, po_no, product_id, context=None):
        uom_id = None
        if po_no:
            cr.execute("""select product_uom from purchase_order_line 
            where order_id in(select id from purchase_order where name=%s)
            and product_id=%s""",(po_no,product_id,))
            data = cr.fetchall()
            if data:
                for uom in data:
                    uom_id = uom[0]
        return uom_id            
    def allocate_pallet(self, cr, uid, ids, context=None):
        res1 = {}       
        
        res1['value'] = {'item_ids': []}
        pallet_mapping_obj = self.pool.get('pallet.mapping')
        transfer_details_items_obj = self.pool.get('stock.transfer_details_items')
        uom_obj = self.pool.get('product.uom')
        stock_quant_package_obj = self.pool.get('stock.quant.package')
        transfer_details_ids = transfer_details_items_obj.search(cr,uid,[('transfer_id', '=', ids)], context=context)
        for transfer in transfer_details_items_obj.browse(cr,uid,transfer_details_ids, context=context):
            uom_id = self.get_uom_id(cr, uid, transfer.transfer_id.picking_id.origin, transfer.product_id.id, context=context)
            uom = uom_obj.browse(cr,uid,uom_id,context=context)
            pallet_id = pallet_mapping_obj.search(cr,uid,[('product_id', '=', transfer.product_id.id), ('big_uom_id', '=', uom_id)], context=context)
            if len(pallet_id) == 0:
                raise orm.except_orm(_('Alert!:'), _("Product %s and Bigger UOM %s doesn\'t exit in Pallet Mapping!"%(transfer.product_id.name,uom.name,)))
                 
            if pallet_id:
                for pallet in pallet_mapping_obj.browse(cr,uid,pallet_id,context=context):
                    pallet_qty = pallet.smaller_qty
                    if transfer.quantity > pallet_qty:
                        total_lines = remainder_amt = modulus_amt = remainder_qty=0
                        remainder_qty = transfer.quantity
                        remainder_amt = transfer.quantity % pallet_qty
                        modulus_amt = int(transfer.quantity / pallet_qty)
                        
                        
                        if remainder_amt > 0:
                            total_lines = modulus_amt + 1
                        else:
                            total_lines = modulus_amt
                            
                        for x in range(0, int(total_lines)):
                            if x == total_lines - 1:     
                                item = {
                                            'transfer_id': ids[0],
                                            'packop_id': transfer.packop_id.id,
                                            'product_id': transfer.product_id.id,
                                            'product_uom_id': transfer.product_uom_id.id,
                                            'quantity': remainder_qty,#remainder_amt,
                                            'package_id': transfer.package_id.id,
                                            'lot_id':transfer.lot_id.id,
                                            'sourceloc_id': transfer.sourceloc_id.id,
                                            'destinationloc_id': transfer.destinationloc_id.id,
                                            'result_package_id': transfer.result_package_id.id,
                                            'date': transfer.date, 
                                            'owner_id': transfer.owner_id.id,
                                        }
                                res1['value']['item_ids'].append({
                                            'transfer_id': ids[0],
                                            'packop_id': transfer.packop_id.id,
                                            'product_id': transfer.product_id.id,
                                            'product_uom_id': transfer.product_uom_id.id,
                                            'quantity': remainder_qty,#remainder_amt,
                                            'package_id': transfer.package_id.id,
                                            'lot_id':transfer.lot_id.id,
                                            'sourceloc_id': transfer.sourceloc_id.id,
                                            'destinationloc_id': transfer.destinationloc_id.id,
                                            'result_package_id': transfer.result_package_id.id,
                                            'date': transfer.date, 
                                            'owner_id': transfer.owner_id.id,
                                                        })
                            else:
                                remainder_qty -= pallet_qty
                                item = {
                                            'transfer_id': ids[0],
                                            'packop_id': False,
                                            'product_id': transfer.product_id.id,
                                            'product_uom_id': transfer.product_uom_id.id,
                                            'quantity': pallet_qty,
                                            'package_id': transfer.package_id.id,
                                            'lot_id':transfer.lot_id.id,
                                            'sourceloc_id': transfer.sourceloc_id.id,
                                            'destinationloc_id': transfer.destinationloc_id.id,
                                            'result_package_id': transfer.result_package_id.id,
                                            'date': transfer.date, 
                                            'owner_id': transfer.owner_id.id,
                                        }
                                res1['value']['item_ids'].append({
                                            'transfer_id': ids[0],
                                            'packop_id': False,#transfer.packop_id.id,
                                            'product_id': transfer.product_id.id,
                                            'product_uom_id': transfer.product_uom_id.id,
                                            'quantity': pallet_qty,
                                            'package_id': transfer.package_id.id,
                                            'lot_id':transfer.lot_id.id,
                                            'sourceloc_id': transfer.sourceloc_id.id,
                                            'destinationloc_id': transfer.destinationloc_id.id,
                                            'result_package_id': transfer.result_package_id.id,
                                            'date': transfer.date, 
                                            'owner_id': transfer.owner_id.id,
                                                        })
                              
                            new_id =transfer_details_items_obj.create(cr,uid,item,context=context)
                            pack_id =transfer_details_items_obj.put_in_pack(cr,uid,new_id,context=context)
                            if new_id:
                                details = transfer_details_items_obj.browse(cr, uid, new_id, context=context)
                                if details:
                                    stock_quant_package_obj.write(cr,uid,details.result_package_id.id,{'stickering_chk':details.product_id.product_tmpl_id.stickering_chk,
                                                                                                       'repacking_chk':details.product_id.product_tmpl_id.repacking_chk},context=context)
                                    #if details.product_id.product_tmpl_id.stickering_chk == False and details.product_id.product_tmpl_id.repacking_chk == False:
                                    if details.product_id.product_tmpl_id.stickering_chk != True:
                                        stock_quant_package_obj.write(cr,uid,details.result_package_id.id,{'saleable':True,'strickering_state':'retransfer'},context=context)
                        cr.execute("delete from stock_transfer_details_items where id =%s",(transfer.id,))
                    else:#no need to allocat pallet
                        item = {
                                            'transfer_id': ids[0],
                                            'packop_id': transfer.packop_id.id,
                                            'product_id': transfer.product_id.id,
                                            'product_uom_id': transfer.product_uom_id.id,
                                            'quantity': transfer.quantity,
                                            'package_id': transfer.package_id.id,
                                            'lot_id':transfer.lot_id.id,
                                            'sourceloc_id': transfer.sourceloc_id.id,
                                            'destinationloc_id': transfer.destinationloc_id.id,
                                            'result_package_id': transfer.result_package_id.id,
                                            'date': transfer.date, 
                                            'owner_id': transfer.owner_id.id,
                                        }
                        res1['value']['item_ids'].append({
                                            'transfer_id': ids[0],
                                            'packop_id': transfer.packop_id.id,
                                            'product_id': transfer.product_id.id,
                                            'product_uom_id': transfer.product_uom_id.id,
                                            'quantity': transfer.quantity,
                                            'package_id': transfer.package_id.id,
                                            'lot_id':transfer.lot_id.id,
                                            'sourceloc_id': transfer.sourceloc_id.id,
                                            'destinationloc_id': transfer.destinationloc_id.id,
                                            'result_package_id': transfer.result_package_id.id,
                                            'date': transfer.date, 
                                            'owner_id': transfer.owner_id.id,
                                                        }) 
                        new_id =transfer_details_items_obj.create(cr,uid,item,context=context)
                        pack_id =transfer_details_items_obj.put_in_pack(cr,uid,new_id,context=context)
                        cr.execute("delete from stock_transfer_details_items where id =%s",(transfer.id,))
                        if new_id:
                                details = transfer_details_items_obj.browse(cr, uid, new_id, context=context)
                                if details:
                                    stock_quant_package_obj.write(cr,uid,details.result_package_id.id,{'stickering_chk':details.product_id.product_tmpl_id.stickering_chk,
                                                                                                       'repacking_chk':details.product_id.product_tmpl_id.repacking_chk},context=context)
                                    #if details.product_id.product_tmpl_id.stickering_chk == False and details.product_id.product_tmpl_id.repacking_chk == False:
                                    if details.product_id.product_tmpl_id.stickering_chk != True :
                                        stock_quant_package_obj.write(cr,uid,details.result_package_id.id,{'saleable':True,'strickering_state':'retransfer'},context=context)
                                           
        return self.pool['stock.transfer_details'].wizard_view(cr, uid, ids[0], context)
    
    
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
            item = {
                'packop_id': op.id,
                'product_id': op.product_id.id,
                'product_uom_id': op.product_uom_id.id,
                'quantity': op.product_qty,
                'temp_qty':op.product_qty,
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
        'temp_qty': fields.float('Temp Qty', digits=dp.get_precision('temp_qty'), default = 0.0)
    }

    def on_change_qty_change(self, cr, uid, ids, quantity, temp_qty, context=None):
        if quantity:
            if quantity > temp_qty:
                raise osv.except_osv(('Warning'), ('Quantity should not be larger than available quantity!'))                          
        