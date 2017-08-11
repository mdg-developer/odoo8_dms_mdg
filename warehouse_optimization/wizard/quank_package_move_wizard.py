# -*- coding: utf-8 -*-
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, fields, api


class StockQuantPackageMove(models.TransientModel):
    _inherit = 'stock.quant.package.move'

    pack_move_items = fields.One2many(
        comodel_name='stock.quant.package.move_items', inverse_name='move_id',
        string='Packs')

    @api.model
    def default_get(self, fields):
        res = super(StockQuantPackageMove, self).default_get(fields)
        packages_ids = self.env.context.get('active_ids', [])
        if not packages_ids:
            return res
        packages_obj = self.env['stock.quant.package']
        packages = packages_obj.browse(packages_ids)
        items = []
        for package in packages:
            res = {}
            value = {}
#             if package.strickering_state != 'retransfer':
#                  #res['domain'] = {'dest_loc': [('location_id', '=', self.source_loc),('stickering_location','=',True)]}
#                  to_loc_id = []
#                  ids = self.env['stock.location'].search([('location_id', '=', package.location_id.location_id.id),('stickering_location','=',True)])
#                  
#                  for loc_ids in ids:
#                      to_loc_id.append(loc_ids.id)
#                  res['domain'] = {'dest_loc': [('id', 'in', to_loc_id)]}
#                  #value = {'domain':{'dest_loc':[('id','in',ids)]}
#             else:
#                  ids = self.env['stock.location'].search([('usage', '=', 'internal')])
#                 
#                  for loc_ids in ids:
#                      to_loc_id.append(loc_ids)
#                  res['domain'] = {'dest_loc': [('id', 'in', to_loc_id)]}        
            if not package.parent_id and package.location_id:
                item = {
                    'package': package.id,
                    'source_loc': package.location_id.id,
                    #'dest_loc': res,
                }
                items.append(item)
        res.update(pack_move_items=items)
        return res

    @api.one
    def do_detailed_transfer(self):
        for item in self.pack_move_items:
            package_id = location_id = original_location_id = None
            if item.dest_loc is not item.source_loc:
                for quant in item.package.quant_ids:
                    package_id = quant.package_id.id
                    original_location_id = quant.location_id.id
                    location_id = item.dest_loc
                    quant.move_to(item.dest_loc)
                    quant.write({'package_id':package_id})
                for package in item.package.children_ids:
                    for quant in package.quant_ids:
                        package_id = quant.package_id.id
                        quant.move_to(item.dest_loc)
                        location_id = item.dest_loc
                        quant.write({'package_id':package_id})
                for packageid in item.package:
                    if packageid.strickering_state == 'draft':
                        packageid.write({'origin_location_id':original_location_id,'strickering_state':'transfer','location_id':location_id.id})
                    else:    
                        packageid.write({'location_id':location_id.id})        
        return True
    
#     @api.one
#     def do_detailed_transfer(self):
#         for item in self.pack_move_items:
#             if item.dest_loc is not item.source_loc:
#                 for quant in item.package.quant_ids:
#                     quant.move_to(item.dest_loc)
#                 for package in item.package.children_ids:
#                     for quant in package.quant_ids:
#                         quant.move_to(item.dest_loc)
#         return True

class StockQuantPackageMoveItems(models.TransientModel):
    _inherit = 'stock.quant.package.move_items'
    

#     @api.one
#     @api.onchange('package')
#     def onchange_quant(self):
#         self.source_loc = self.package.location_id
        
    @api.one    
    @api.onchange('source_loc')
    def onchange_source_loc(self):
        res = {}
        if self.source_loc:
            if self.package.stickering_state != 'retransfer':
                res['domain'] = {'dest_loc': [('location_id', '=', self.source_loc),('stickering_location','=',True)]}
        return res
    
    @api.one
    @api.onchange('package')
    def onchange_quant(self):
        self.source_loc = self.package.location_id
        res = {}
        if self.source_loc:
            if self.package.stickering_state != 'retransfer':
                res['domain'] = {'dest_loc': [('location_id', '=', self.source_loc),('stickering_location','=',True)]}
        return res
       
