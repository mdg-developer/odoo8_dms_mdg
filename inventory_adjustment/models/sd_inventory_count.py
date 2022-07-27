from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.exceptions import Warning

class sd_inventory_count(osv.osv):

    _name = "sd.inventory.count"
    _description = "SD Inventory Count"
    _columns = {
        'name': fields.char('Adjustment Reference', readonly=True),
        'subject': fields.char('Subjectt', required=True),
        'team': fields.many2one('crm.case.section', 'Sale Team'),
        'date': fields.date('Date'),
        'inventory_line': fields.one2many('sd.inventory.count.line', 'sd_inventory_id', 'Inventory Lines',states={'draft': [('readonly', False)], 'validate': [('readonly', True)], 'cancel': [('readonly', True)]}),

        'state': fields.selection([('draft', 'Draft'), ('validate', 'Validate'), ('cancel', 'Cancel')], 'Status'),
    }

    _defaults = {
        'state': 'draft',

    }

    def create(self, cursor, user, vals, context=None):
        id_code = self.pool.get('ir.sequence').get(cursor, user,
                                                'sd.inventory.count.code') or '/'
        vals['name'] = id_code
        return super(sd_inventory_count, self).create(cursor, user, vals, context=context)

    def validate(self, cr, uid, vals, context):
        inventory_count = self.browse(cr, uid, vals, context=context)
        stock_move_obj = self.pool.get('stock.move')
        team_obj = self.pool.get('crm.case.section')
        product_obj = self.pool.get('product.product')
        team = team_obj.browse(cr, uid, inventory_count.team.id, context=context)
        inv_loss_location = self.pool.get('stock.location').search(cr, uid, [('name', '=', 'Inventory loss')], context=context)[0]
        # sellable_location = 12
        sellable_location = team.location_id.id
        # inv_loss_location = 5


        # diff <0 : adjustment to sellable
        # diff>0 : sellable to adjustment

        for line in inventory_count.inventory_line:
            dom = [('product_id', '=', line.product_id.id), ('sd_inventory_id.state', '=', 'draft'),
                   ('sd_inventory_id.team', '=', inventory_count.team.id), ('sd_inventory_id.id', '!=', inventory_count.id)]
            res = self.pool.get('sd.inventory.count.line').search(cr, uid, dom, context=context)
            if res:
                team = self.pool['crm.case.section'].browse(cr, uid, inventory_count.team.id, context=context)
                product = product_obj.browse(cr, uid, line.product_id.id, context=context)
                raise Warning(
                    _("You cannot have two inventory adjustements in state 'Draft' with the same product(%s) and same team(%s). Please first validate the first inventory adjustement with this product before creating another one.") % (
                    product.name, team.name))
                return


        for line in inventory_count.inventory_line:

            if line.diff_pcs < 0:
                stock_move_value = {
                    'name': line.product_id.name,
                    # 'picking_id':inventory_count.name,
                    'product_id': line.product_id.id,
                    'location_dest_id': inv_loss_location,
                    'location_id': sellable_location,
                    'product_uom_qty': abs(line.diff_pcs),
                    # 'product_uom': line.smaller_product_uom.id,
                    'product_uom':1,
                    'origin': inventory_count.name,
                }

            else:
                stock_move_value = {
                    'name': line.product_id.name,
                    # 'picking_id':inventory_count.name,
                    'product_id': line.product_id.id,
                    'location_dest_id': sellable_location,
                    'location_id': inv_loss_location,
                    'product_uom_qty': abs(line.diff_pcs),
                    # 'product_uom': line.smaller_product_uom.id,
                    'product_uom':1,
                    'origin': inventory_count.name,
                }

            move_id = stock_move_obj.create(cr, uid, stock_move_value, context=context)
            stock_move_obj.action_done(cr, uid, move_id, context=context)

        return self.write(cr, uid, vals, {'state': 'validate'})


    def cancel(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state':'cancel' })

sd_inventory_count()

class sd_inventory_count_line(osv.osv):

    _name = "sd.inventory.count.line"
    _description = "SD Inventory Count Line"
    _columns = {
        'sd_inventory_id': fields.many2one('sd.inventory.count', 'SD Inventory', required=True, ondelete='cascade'),
        'principle_id':fields.many2one('product.maingroup', 'Principle'),
        'category_id': fields.many2one('product.category', 'Category'),
        'bigger_product_uom': fields.many2one('product.uom', 'B.UOM'),
        'smaller_product_uom': fields.many2one('product.uom', 'S.UOM'),
        'product_id': fields.many2one('product.product', 'SKU Name'),

        'ctns': fields.float('Ctns'),
        'pcs': fields.float('Pcs'),
        'total_pcs': fields.float('Total Pcs'),
        'actual_ctns': fields.float('Actual Ctns Qty'),
        'actual_pcs': fields.float('Actual Pcs Qty'),
        'diff_pcs': fields.float('Different Pcs Qty'),

    }

    # def create(self, cr, uid, values, context=None):
    #     product_obj = self.pool.get('product.product')
    #     dom = [('product_id', '=', values.get('product_id')), ('sd_inventory_id.state', '=', 'draft'),
    #            ('sd_inventory_id.team', '=', values.get('team'))]
    #     res = self.search(cr, uid, dom, context=context)
    #     if res:
    #         team = self.pool['crm.case.section'].browse(cr, uid, values.get('team'), context=context)
    #         product = product_obj.browse(cr, uid, values.get('product_id'), context=context)
    #         raise Warning(_("You cannot have two inventory adjustements in state 'Draft' with the same product(%s) and same location(%s). Please first validate the first inventory adjustement with this product before creating another one.") % (product.name, team.name))
    #     return super(sd_inventory_count_line, self).create(cr, uid, values, context=context)

sd_inventory_count_line()


