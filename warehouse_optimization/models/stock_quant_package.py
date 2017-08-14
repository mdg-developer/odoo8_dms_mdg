from openerp.osv import fields, osv
from openerp.tools.translate import _

class stock_quant_package(osv.osv):

    _inherit = "stock.quant.package"
    
    def _get_packages(self, cr, uid, ids, context=None):
        """Returns packages from quants for store"""
        res = set()
        for quant in self.browse(cr, uid, ids, context=context):
            pack = quant.package_id
            while pack:
                res.add(pack.id)
                pack = pack.parent_id
        return list(res)
    
    def _get_package_info_new(self, cr, uid, ids, name, args, context=None):
        quant_obj = self.pool.get("stock.quant")
        move_items_obj = self.pool.get("stock.quant.package.stickering.move_items")
        move_items_pack_obj = self.pool.get("stock.quant.package.move_items")
        default_company_id = self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.id
        res = dict((res_id, {'location_id': False, 'company_id': default_company_id, 'owner_id': False}) for res_id in ids)
        for pack in self.browse(cr, uid, ids, context=context):
            quants = quant_obj.search(cr, uid, [('package_id', 'child_of', pack.id)], context=context)
            print 'context>>>',context
            if quants:
                
                quant = quant_obj.browse(cr, uid, quants[0], context=context)
                res[pack.id]['location_id'] = quant.location_id.id
                res[pack.id]['owner_id'] = quant.owner_id.id
                res[pack.id]['company_id'] = quant.company_id.id
            else:
                
                if len(quants) == 0:
                    orderby = 'id DESC'
                    offset = 0
                    move = move_items_pack_obj.search(cr, uid, [('package', '=', ids)],order=orderby, limit=1, offset=offset, context=context)
                    move_loc = move_items_pack_obj.browse(cr,uid,move,context=context)
                    if move_loc:                        
                        res[pack.id]['location_id'] = move_loc.dest_loc.id or False 
#                     if pack.strickering_state != 'retransfer':                        
#                         move = move_items_obj.search(cr, uid, [('package', '=', ids)],order=orderby, limit=1, offset=offset, context=context)
#                         move_loc = move_items_obj.browse(cr,uid,move,context=context)
#                         if move_loc:                        
#                             res[pack.id]['location_id'] = move_loc.dest_loc.id or False
#                     else:
#                         move = move_items_pack_obj.search(cr, uid, [('package', '=', ids)],order=orderby, limit=1, offset=offset, context=context)
#                         move_loc = move_items_pack_obj.browse(cr,uid,move,context=context)
#                         if move_loc:                        
#                             res[pack.id]['location_id'] = move_loc.dest_loc.id or False 
                                   
                res[pack.id]['owner_id'] = False
                res[pack.id]['company_id'] = False
        return res
    
    def _get_packages_to_relocate(self, cr, uid, ids, context=None):
        res = set()
        for pack in self.browse(cr, uid, ids, context=context):
            res.add(pack.id)
            if pack.parent_id:
                res.add(pack.parent_id.id)
        return list(res)
    
    _columns = {
        'stickering_start_date': fields.datetime('Additional Process Start'),        
        'stickering_end_date': fields.datetime('Additional Process End'),
        'repacking_start_date': fields.datetime('Repacking Start'),
        'repacking_end_date': fields.datetime('Repacking End'),
        'saleable': fields.boolean('Saleable'),       
        'stickering_chk': fields.boolean("Additional Process Require"),
        'repacking_chk': fields.boolean("Repacking Process"),
        'stickering_process_chk': fields.boolean("Additional Process Complete"),
        'repacking_process_chk': fields.boolean("Repacking Process Complete"),
        'strickering_state':fields.selection([('draft', 'Draft'), ('transfer', 'Transfer'), ('complete', 'Additional Process Complete'), ('retransfer', 'Retransfer')], 'Status'),
        'repacking_state':fields.selection([('draft', 'Draft'), ('transfer', 'Transfer'), ('complete', 'Repacking Complete'), ('retransfer', 'Retransfer')], 'Status'),
        'origin_location_id': fields.many2one('stock.location', 'Original Location'),
        'location_id': fields.function(_get_package_info_new, type='many2one', relation='stock.location', string='Location', multi="package",
                                    store={
                                       'stock.quant': (_get_packages, ['location_id'], 10),
                                       'stock.quant.package': (_get_packages_to_relocate, ['quant_ids', 'children_ids', 'parent_id'], 10),
                                    }, readonly=True, select=True),
    }
    
    _defaults = {
                 'strickering_state':'draft',
                 'repacking_state':'draft',
                 } 
    
    
    def stickering_complete(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'strickering_state':'complete'}, context=context)
        return True
    
    def repacking_complete(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'repacking_state':'complete'}, context=context)
        return True
    
    def repacking_retransfer(self, cr, uid, ids, context=None):
        move_obj = self.pool.get("stock.quant.package.repacking.move")
        move_items_obj = self.pool.get("stock.quant.package.repacking.move_items")         
        for data in self.browse(cr, uid, ids, context=context):
            from_loc = data.location_id.id
            to_loc = data.origin_location_id.id
            move_id = move_obj.create(cr,uid,{},context=context)
            values= {'move_id':move_id,
                    'package': ids[0],
                    'source_loc':from_loc,
                    'dest_loc':to_loc                    
                     }
            move_items = move_items_obj.create(cr,uid,values,context=context)
            wizard_obj = move_obj.browse(cr, uid, move_id, context=context)
            if wizard_obj:
                wizard_obj.do_detailed_transfer()
                self.write(cr, uid, ids, {'repacking_state':'retransfer'}, context=context)
        return True
    
    def retransfer(self, cr, uid, ids, context=None):
        move_obj = self.pool.get("stock.quant.package.move")
        move_items_obj = self.pool.get("stock.quant.package.move_items")         
        for data in self.browse(cr, uid, ids, context=context):
            from_loc = data.location_id.id
            to_loc = data.origin_location_id.id
            move_id = move_obj.create(cr,uid,{},context=context)
            values= {'move_id':move_id,
                    'package': ids[0],
                    'source_loc':from_loc,
                    'dest_loc':to_loc                    
                     }
            move_items = move_items_obj.create(cr,uid,values,context=context)
            wizard_obj = move_obj.browse(cr, uid, move_id, context=context)
            if wizard_obj:
                wizard_obj.do_detailed_transfer()
                self.write(cr, uid, ids, {'strickering_state':'retransfer','saleable':True}, context=context)
        return True