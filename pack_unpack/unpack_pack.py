# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import time
import openerp.addons.decimal_precision as dp
from openerp.osv import fields, osv, orm
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.tools import float_compare
from openerp.tools.translate import _
from openerp import tools, SUPERUSER_ID
from openerp.addons.product import _common

#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
class product_unpacking(osv.osv):
    """
    Production Orders / Manufacturing Orders
    """
    _name = 'product.unpacking'
    _description = 'Manufacturing Order'
    _date_name = 'date_planned'
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    def _production_calc(self, cr, uid, ids, prop, unknow_none, context=None):
        """ Calculates total hours and total no. of cycles for a production order.
        @param prop: Name of field.
        @param unknow_none:
        @return: Dictionary of values.
        """
        result = {}
        for prod in self.browse(cr, uid, ids, context=context):
            result[prod.id] = {
                'hour_total': 0.0,
                'cycle_total': 0.0,
            }
        return result

    def _src_id_default(self, cr, uid, ids, context=None):
        try:
            location_model, location_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'stock', 'stock_location_stock')
            self.pool.get('stock.location').check_access_rule(cr, uid, [location_id], 'read', context=context)
        except (orm.except_orm, ValueError):
            location_id = False
        return location_id

    def _dest_id_default(self, cr, uid, ids, context=None):
        try:
            location_model, location_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'stock', 'stock_location_stock')
            self.pool.get('stock.location').check_access_rule(cr, uid, [location_id], 'read', context=context)
        except (orm.except_orm, ValueError):
            location_id = False
        return location_id

    def _get_progress(self, cr, uid, ids, name, arg, context=None):
        """ Return product quantity percentage """
        result = dict.fromkeys(ids, 100)
        for pack_unpack_production in self.browse(cr, uid, ids, context=context):
            if pack_unpack_production.product_qty:
                done = 0.0
                for move in pack_unpack_production.move_created_ids2:
                    if not move.scrapped and move.product_id == pack_unpack_production.product_id:
                        done += move.product_qty
                result[pack_unpack_production.id] = done / pack_unpack_production.product_qty * 100
        return result

    def _moves_assigned(self, cr, uid, ids, name, arg, context=None):
        """ Test whether all the consume lines are assigned """
        res = {}
        for production in self.browse(cr, uid, ids, context=context):
            res[production.id] = True
            states = [x.state != 'assigned' for x in production.move_lines if x]
            if any(states) or len(states) == 0: #When no moves, ready_production will be False, but test_ready will pass
                res[production.id] = False
        return res

    def _from_move(self, cr, uid, ids, context=None):
        """ Return mrp"""
        res = []
        for move in self.browse(cr, uid, ids, context=context):
            res += self.pool.get("product.unpacking").search(cr, uid, [('move_lines', 'in', move.id)], context=context)
        return res

    _columns = {
        'name': fields.char('Reference', required=True, readonly=True, states={'draft': [('readonly', False)]}, copy=False),
        'origin': fields.char('Source Document', readonly=True, states={'draft': [('readonly', False)]},
            help="Reference of the document that generated this production order request.", copy=False),
        'priority': fields.selection([('0', 'Not urgent'), ('1', 'Normal'), ('2', 'Urgent'), ('3', 'Very Urgent')], 'Priority',
            select=True, readonly=True, states=dict.fromkeys(['draft', 'confirmed'], [('readonly', False)])),

        'product_id': fields.many2one('product.product', 'Product', required=True, readonly=True, states={'draft': [('readonly', False)]}, 
                                      domain=[('type','!=','service')]),
        'product_qty': fields.float('Product Quantity', digits_compute=dp.get_precision('Product Unit of Measure'), required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'product_uom': fields.many2one('product.uom', 'Product Unit of Measure', required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'product_uos_qty': fields.float('Product UoS Quantity', readonly=True, states={'draft': [('readonly', False)]}),
        'product_uos': fields.many2one('product.uom', 'Product UoS', readonly=True, states={'draft': [('readonly', False)]}),
        'progress': fields.function(_get_progress, type='float',
            string='Production progress'),

        'location_src_id': fields.many2one('stock.location', 'Raw Materials Location', required=True,
            readonly=True, states={'draft': [('readonly', False)]},
            help="Location where the system will look for components."),
        'location_dest_id': fields.many2one('stock.location', 'Finished Products Location', required=True,
            readonly=True, states={'draft': [('readonly', False)]},
            help="Location where the system will stock the finished products."),
        'date_planned': fields.datetime('Scheduled Date', required=True, select=1, readonly=True, states={'draft': [('readonly', False)]}, copy=False),
        'date_start': fields.datetime('Start Date', select=True, readonly=True, copy=False),
        'date_finished': fields.datetime('End Date', select=True, readonly=True, copy=False),
        'bom_id': fields.many2one('bom.product', 'Bill of Materials', readonly=True, states={'draft': [('readonly', False)]},
            help="Ingredients allow you to define the list of required raw materials to make a finished product."),
        'move_prod_id': fields.many2one('stock.move', 'Product Move', readonly=True, copy=False),
        'move_lines': fields.one2many('stock.move', 'unpack_unpack_id', 'Products to Consume',
            domain=[('state', 'not in', ('done', 'cancel'))], readonly=True, states={'draft': [('readonly', False)]}),
        'move_lines2': fields.one2many('stock.move', 'unpack_unpack_id', 'Consumed Products',
            domain=[('state', 'in', ('done', 'cancel'))], readonly=True),
        'move_created_ids': fields.one2many('stock.move', 'unpacking_id', 'Products to Produce',
            domain=[('state', 'not in', ('done', 'cancel'))], readonly=True),
        'move_created_ids2': fields.one2many('stock.move', 'unpacking_id', 'Produced Products',
            domain=[('state', 'in', ('done', 'cancel'))], readonly=True),
        'product_lines': fields.one2many('product.unpacking.line', 'production_id', 'Scheduled goods',
            readonly=True),
        'state': fields.selection(
            [('draft', 'New'), ('cancel', 'Cancelled'), ('confirmed', 'Awaiting Raw Materials'),
                ('ready', 'Ready to Produce'), ('in_production', 'Production Started'), ('done', 'Done')],
            string='Status', readonly=True,
            track_visibility='onchange', copy=False,
            help="When the production order is created the status is set to 'Draft'.\n\
                If the order is confirmed the status is set to 'Waiting Goods'.\n\
                If any exceptions are there, the status is set to 'Picking Exception'.\n\
                If the stock is available then the status is set to 'Ready to Produce'.\n\
                When the production gets started then the status is set to 'In Production'.\n\
                When the production is over, the status is set to 'Done'."),
        'hour_total': fields.function(_production_calc, type='float', string='Total Hours', multi='workorder', store=True),
        'cycle_total': fields.function(_production_calc, type='float', string='Total Cycles', multi='workorder', store=True),
        'user_id': fields.many2one('res.users', 'Responsible'),
        'company_id': fields.many2one('res.company', 'Company', required=True),
        'ready_production': fields.function(_moves_assigned, type='boolean', store={'stock.move': (_from_move, ['state'], 10)})
    }

    _defaults = {
        'priority': lambda *a: '1',
        'state': lambda *a: 'draft',
        'date_planned': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        'product_qty': lambda *a: 1.0,
        'user_id': lambda self, cr, uid, c: uid,
        'name': lambda x, y, z, c: x.pool.get('ir.sequence').get(y, z, 'product.unpacking') or '/',
        'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'product.unpacking', context=c),
        'location_src_id': _src_id_default,
        'location_dest_id': _dest_id_default
    }

    _sql_constraints = [
        ('name_uniq', 'unique(name, company_id)', 'Reference must be unique per Company!'),
    ]

    _order = 'priority desc, date_planned asc'

    def _check_qty(self, cr, uid, ids, context=None):
        for order in self.browse(cr, uid, ids, context=context):
            if order.product_qty <= 0:
                return False
        return True

    _constraints = [
        (_check_qty, 'Order quantity cannot be negative or zero!', ['product_qty']),
    ]

    def unlink(self, cr, uid, ids, context=None):
        for production in self.browse(cr, uid, ids, context=context):
            if production.state not in ('draft', 'cancel'):
                raise osv.except_osv(_('Invalid Action!'), _('Cannot delete a manufacturing order in state \'%s\'.') % production.state)
        return super(product_unpacking, self).unlink(cr, uid, ids, context=context)

    def location_id_change(self, cr, uid, ids, src, dest, context=None):
        """ Changes destination location if source location is changed.
        @param src: Source location id.
        @param dest: Destination location id.
        @return: Dictionary of values.
        """
        if dest:
            return {}
        if src:
            return {'value': {'location_dest_id': src}}
        return {}

    def product_id_change(self, cr, uid, ids, product_id, product_qty=0, context=None):
        """ Finds UoM of changed product.
        @param product_id: Id of changed product.
        @return: Dictionary of values.
        """
        result = {}
        if not product_id:
            return {'value': {
                'product_uom': False,
                'bom_id': False,
                'routing_id': False,
                'product_uos_qty': 0,
                'product_uos': False
            }}
        bom_obj = self.pool.get('bom.product')
        product = self.pool.get('product.product').browse(cr, uid, product_id, context=context)
        bom_id = bom_obj._bom_find(cr, uid, product_id=product.id, properties=[], context=context)
        routing_id = False
        if bom_id:
            bom_point = bom_obj.browse(cr, uid, bom_id, context=context)
#             routing_id = bom_point.routing_id.id or False
        product_uom_id = product.uom_id and product.uom_id.id or False
        result['value'] = {'product_uos_qty': 0, 'product_uos': False, 'product_uom': product_uom_id, 'bom_id': bom_id
#                            , 'routing_id': routing_id
                           }
        if product.uos_id.id:
            result['value']['product_uos_qty'] = product_qty * product.uos_coeff
            result['value']['product_uos'] = product.uos_id.id
        return result

    def bom_id_change(self, cr, uid, ids, bom_id, context=None):
        """ Finds routing for changed BoM.
        @param product: Id of product.
        @return: Dictionary of values.
        """
        if not bom_id:
            return {'value': {
#                 'routing_id': False
            }}
        bom_point = self.pool.get('bom.product').browse(cr, uid, bom_id, context=context)
        result = {}
        return {'value': result}

#------------------------------UNPACK------------------------------

    def _bom_explode_unpack(self, cr, uid, bom, product, factor, properties=None, level=0, routing_id=False, previous_products=None, master_bom=None, context=None):
        """ Finds Products and Work Centers for related BoM for manufacturing order.
        @param bom: BoM of particular product template.
        @param product: Select a particular variant of the BoM. If False use BoM without variants.
        @param factor: Factor represents the quantity, but in UoM of the BoM, taking into account the numbers produced by the BoM
        @param properties: A List of properties Ids.
        @param level: Depth level to find BoM lines starts from 10.
        @param previous_products: List of product previously use by bom explore to avoid recursion
        @param master_bom: When recursion, used to display the name of the master bom
        @return: result: List of dictionaries containing product details.
                 result2: List of dictionaries containing Work Center details.
        """
        
        uom_obj = self.pool.get("product.uom")
        #routing_obj = self.pool.get('mrp.routing')
        result=[]
        result2=[]
        if bom:
            result.append({
                    'name': product.product_id.name,
                    'product_id': product.product_id.id,
                    'product_qty': product.product_qty,
                    'product_uom': product.product_uom.id,
                    'product_uos_qty': product.product_uos_qty  or False,
                    'product_uos': product.product_uos or False,
                })
        
        return result, result2

#--------------------unpacking ----------------

    def _action_compute_lines_unpack(self, cr, uid, ids, properties=None, context=None):
        """ Compute product_lines and workcenter_lines from BoM structure
        @return: product_lines
        """
        if properties is None:
            properties = []
        results = []
        bom_obj = self.pool.get('bom.product')
        uom_obj = self.pool.get('product.uom')
        prod_line_obj = self.pool.get('product.unpacking.line')
        
        ###needt to add typr of packing and unpacking here
       # workcenter_line_obj = self.pool.get('mrp.production.workcenter.line')
        for production in self.browse(cr, uid, ids, context=context):
            #unlink product_lines
            prod_line_obj.unlink(cr, SUPERUSER_ID, [line.id for line in production.product_lines], context=context)
            #unlink workcenter_lines
            #workcenter_line_obj.unlink(cr, SUPERUSER_ID, [line.id for line in production.workcenter_lines], context=context)
            # search BoM structure and route
            bom_point = production.bom_id
            bom_id = production.bom_id.id
            if not bom_point:
                bom_id = bom_obj._bom_find(cr, uid, product_id=production.product_id.id, properties=properties, context=context)
                if bom_id:
                    bom_point = bom_obj.browse(cr, uid, bom_id)
                   # routing_id = bom_point.routing_id.id or False
                    self.write(cr, uid, [production.id], {'bom_id': bom_id
                                                         # 'routing_id': routing_id
                                                          })
    
            if not bom_id:
                raise osv.except_osv(_('Error!'), _("Cannot find a ingredients for this product."))

            # get components and workcenter_lines from BoM structure
            factor = uom_obj._compute_qty(cr, uid, production.product_uom.id, production.product_qty, bom_point.product_uom.id)
            # product_lines, workcenter_lines
            print 'bom_points bom_id',bom_point
            results, results2 = self._bom_explode_unpack(cr, uid, bom_point, production, factor / bom_point.product_qty, properties
                                                     , routing_id=False,
                                                      context=context)

            # reset product_lines in production order
            for line in results:
                line['production_id'] = production.id
                prod_line_obj.create(cr, uid, line)

            #reset workcenter_lines in production order
#             for line in results2:
#                 line['production_id'] = production.id
#                 workcenter_line_obj.create(cr, uid, line)
        print 'result',results
        return results

#--------------------packing ----------
    def _action_compute_lines_pack(self, cr, uid, ids, properties=None, context=None):
        """ Compute product_lines and workcenter_lines from BoM structure
        @return: product_lines
        """
        if properties is None:
            properties = []
        results = []
        bom_obj = self.pool.get('bom.product')
        uom_obj = self.pool.get('product.uom')
        prod_line_obj = self.pool.get('product.unpacking.line')
        
        ###needt to add typr of packing and unpacking here
       # workcenter_line_obj = self.pool.get('mrp.production.workcenter.line')
        for production in self.browse(cr, uid, ids, context=context):
            #unlink product_lines
            prod_line_obj.unlink(cr, SUPERUSER_ID, [line.id for line in production.product_lines], context=context)
            #unlink workcenter_lines
            #workcenter_line_obj.unlink(cr, SUPERUSER_ID, [line.id for line in production.workcenter_lines], context=context)
            # search BoM structure and route
            bom_point = production.bom_id
            bom_id = production.bom_id.id
            if not bom_point:
                bom_id = bom_obj._bom_find(cr, uid, product_id=production.product_id.id, properties=properties, context=context)
                if bom_id:
                    bom_point = bom_obj.browse(cr, uid, bom_id)
                   # routing_id = bom_point.routing_id.id or False
                    self.write(cr, uid, [production.id], {'bom_id': bom_id
                                                         # 'routing_id': routing_id
                                                          })
    
            if not bom_id:
                raise osv.except_osv(_('Error!'), _("Cannot find a ingredients for this product."))

            # get components and workcenter_lines from BoM structure
            factor = uom_obj._compute_qty(cr, uid, production.product_uom.id, production.product_qty, bom_point.product_uom.id)
            # product_lines, workcenter_lines
            results, results2 = bom_obj._bom_explode(cr, uid, bom_point, production.product_id, factor / bom_point.product_qty, properties
                                                     , routing_id=False,
                                                      context=context)

            # reset product_lines in production order
            for line in results:
                line['production_id'] = production.id
                prod_line_obj.create(cr, uid, line)

            #reset workcenter_lines in production order
#             for line in results2:
#                 line['production_id'] = production.id
#                 workcenter_line_obj.create(cr, uid, line)
        return results
## that show the require product for packing or unpacking

    def action_compute(self, cr, uid, ids, properties=None, context=None):
        """ Computes ingredients of a product.
        @param properties: List containing dictionaries of properties.
        @return: No. of products.
        """
        return len(self._action_compute_lines_unpack(cr, uid, ids, properties=properties, context=context))
    def action_cancel(self, cr, uid, ids, context=None):
        """ Cancels the production order and related stock moves.
        @return: True
        """
        if context is None:
            context = {}
        move_obj = self.pool.get('stock.move')
        proc_obj = self.pool.get('procurement.order')
        for production in self.browse(cr, uid, ids, context=context):
            if production.move_created_ids:
                move_obj.action_cancel(cr, uid, [x.id for x in production.move_created_ids])
            procs = proc_obj.search(cr, uid, [('move_dest_id', 'in', [x.id for x in production.move_lines])], context=context)
            if procs:
                proc_obj.cancel(cr, uid, procs, context=context)
            move_obj.action_cancel(cr, uid, [x.id for x in production.move_lines])
        self.write(cr, uid, ids, {'state': 'cancel'})
        # Put related procurements in exception
        proc_obj = self.pool.get("procurement.order")
        procs = proc_obj.search(cr, uid, [('unpacking_id', 'in', ids)], context=context)
        if procs:
            proc_obj.write(cr, uid, procs, {'state': 'exception'}, context=context)
        return True
#------------------------------------Finished Product ---------------------------------
    def action_ready(self, cr, uid, ids, context=None):
        """ Changes the production state to Ready and location id of stock move.
        @return: True
        """
        move_obj = self.pool.get('stock.move')
        self.write(cr, uid, ids, {'state': 'ready'})

        for production in self.browse(cr, uid, ids, context=context):
            if not production.move_created_ids:
                self._make_production_produce_line(cr, uid, production, context=context)

            if production.move_prod_id and production.move_prod_id.location_id.id != production.location_dest_id.id:
                move_obj.write(cr, uid, [production.move_prod_id.id],
                        {'location_id': production.location_dest_id.id})
        return True

    def action_production_end(self, cr, uid, ids, context=None):
        """ Changes production state to Finish and writes finished date.
        @return: True
        """
        #for production in self.browse(cr, uid, ids):
            #self._costs_generate(cr, uid, production)
        write_res = self.write(cr, uid, ids, {'state': 'done', 'date_finished': time.strftime('%Y-%m-%d %H:%M:%S')})
        # Check related procurements
        proc_obj = self.pool.get("procurement.order")
        procs = proc_obj.search(cr, uid, [('unpacking_id', 'in', ids)], context=context)
        proc_obj.check(cr, uid, procs, context=context)
        return write_res

    def test_production_done(self, cr, uid, ids):
        """ Tests whether production is done or not.
        @return: True or False
        """
        res = True
        for production in self.browse(cr, uid, ids):
            if production.move_lines:
                res = False

            if production.move_created_ids:
                res = False
        return res

    def _get_subproduct_factor(self, cr, uid, production_id, move_id=None, context=None):
        """ Compute the factor to compute the qty of procucts to produce for the given production_id. By default,
            it's always equal to the quantity encoded in the production order or the production wizard, but if the
            module mrp_subproduct is installed, then we must use the move_id to identify the product to produce
            and its quantity.
        :param production_id: ID of the mrp.order
        :param move_id: ID of the stock move that needs to be produced. Will be used in mrp_subproduct.
        :return: The factor to apply to the quantity that we should produce for the given production order.
        """
        return 1

    def _get_produced_qty(self, cr, uid, production, context=None):
        ''' returns the produced quantity of product 'production.product_id' for the given production, in the product UoM
        '''
        produced_qty = 0
        for produced_product in production.move_created_ids2:
            if (produced_product.scrapped) or (produced_product.product_id.id != production.product_id.id):
                continue
            produced_qty += produced_product.product_qty
        return produced_qty

    def _get_consumed_data(self, cr, uid, production, context=None):
        ''' returns a dictionary containing for each raw material of the given production, its quantity already consumed (in the raw material UoM)
        '''
        consumed_data = {}
        # Calculate already consumed qtys
        for consumed in production.move_lines2:
            if consumed.scrapped:
                continue
            if not consumed_data.get(consumed.product_id.id, False):
                consumed_data[consumed.product_id.id] = 0
            consumed_data[consumed.product_id.id] += consumed.product_qty
        return consumed_data

    def _calculate_qty(self, cr, uid, production, product_qty=0.0, context=None):
        """
            Calculates the quantity still needed to produce an extra number of products
            product_qty is in the uom of the product
        """
        quant_obj = self.pool.get("stock.quant")
        uom_obj = self.pool.get("product.uom")
        produced_qty = self._get_produced_qty(cr, uid, production, context=context)
        consumed_data = self._get_consumed_data(cr, uid, production, context=context)

        #In case no product_qty is given, take the remaining qty to produce for the given production
        if not product_qty:
            product_qty = uom_obj._compute_qty(cr, uid, production.product_uom.id, production.product_qty, production.product_id.uom_id.id) - produced_qty
        production_qty = uom_obj._compute_qty(cr, uid, production.product_uom.id, production.product_qty, production.product_id.uom_id.id)

        scheduled_qty = {}
        for scheduled in production.product_lines:
            if scheduled.product_id.type == 'service':
                continue
            qty = uom_obj._compute_qty(cr, uid, scheduled.product_uom.id, scheduled.product_qty, scheduled.product_id.uom_id.id)
            if scheduled_qty.get(scheduled.product_id.id):
                scheduled_qty[scheduled.product_id.id] += qty
            else:
                scheduled_qty[scheduled.product_id.id] = qty
        dicts = {}
        # Find product qty to be consumed and consume it
        for product_id in scheduled_qty.keys():

            consumed_qty = consumed_data.get(product_id, 0.0)
            
            # qty available for consume and produce
            sched_product_qty = scheduled_qty[product_id]
            qty_avail = sched_product_qty - consumed_qty
            if qty_avail <= 0.0:
                # there will be nothing to consume for this raw material
                continue

            if not dicts.get(product_id):
                dicts[product_id] = {}

            # total qty of consumed product we need after this consumption
            if product_qty + produced_qty <= production_qty:
                total_consume = ((product_qty + produced_qty) * sched_product_qty / production_qty)
            else:
                total_consume = sched_product_qty
            qty = total_consume - consumed_qty

            # Search for quants related to this related move
            for move in production.move_lines:
                if qty <= 0.0:
                    break
                if move.product_id.id != product_id:
                    continue

                q = min(move.product_qty, qty)
                quants = quant_obj.quants_get_prefered_domain(cr, uid, move.location_id, move.product_id, q, domain=[('qty', '>', 0.0)],
                                                     prefered_domain_list=[[('reservation_id', '=', move.id)]], context=context)
                for quant, quant_qty in quants:
                    if quant:
                        lot_id = quant.lot_id.id
                        if not product_id in dicts.keys():
                            dicts[product_id] = {lot_id: quant_qty}
                        elif lot_id in dicts[product_id].keys():
                            dicts[product_id][lot_id] += quant_qty
                        else:
                            dicts[product_id][lot_id] = quant_qty
                        qty -= quant_qty
            if qty > 0:
                if dicts[product_id].get(False):
                    dicts[product_id][False] += qty
                else:
                    dicts[product_id][False] = qty

        consume_lines = []
        for prod in dicts.keys():
            for lot, qty in dicts[prod].items():
                consume_lines.append({'product_id': prod, 'product_qty': qty, 'lot_id': lot})
        return consume_lines


##-----------------making the stock move ------------------
    def action_produce(self, cr, uid, production_id, production_qty, production_mode, wiz=False, context=None):
        """ To produce final product based on production mode (consume/consume&produce).
        If Production mode is consume, all stock move lines of raw materials will be done/consumed.
        If Production mode is consume & produce, all stock move lines of raw materials will be done/consumed
        and stock move lines of final product will be also done/produced.
        @param production_id: the ID of mrp.production object
        @param production_qty: specify qty to produce in the uom of the production order
        @param production_mode: specify production mode (consume/consume&produce).
        @param wiz: the mrp produce product wizard, which will tell the amount of consumed products needed
        @return: True
        """
        type = None
        stock_mov_obj = self.pool.get('stock.move')
        uom_obj = self.pool.get("product.uom")
        production = self.browse(cr, uid, production_id, context=context)
        production_qty_uom = uom_obj._compute_qty(cr, uid, production.product_uom.id, production_qty, production.product_id.uom_id.id)
        print 'I am in the action_produce'
        
        main_production_move = False
        if production_mode == 'con_produce':
            print 'I am consume Produce'
            # To produce remaining qty of final product
            produced_products = {}
            print 'production.move_created_ids2',production.move_created_ids2
            print 'production',production
            for produced_product in production.move_created_ids2:
                print 'produced_product',produced_product
                if produced_product.scrapped:
                    continue
                if not produced_products.get(produced_product.product_id.id, False):
                    produced_products[produced_product.product_id.id] = 0
                produced_products[produced_product.product_id.id] += produced_product.product_qty
    #finished
            for produce_product in production.move_created_ids:
                location_id = False
                print 'produce_product',produce_product
                print 'produce_product.product_qty',produce_product.product_qty
                vals = {'restrict_lot_id': False,
                        'restrict_partner_id': False,
                        'unpack_used_for': False}
                if location_id:
                    vals.update({'location_id': location_id})
                self.pool.get('stock.move').write(cr, uid, [produce_product.id], vals, context=context)
            # Original moves will be the quantities consumed, so they need to be done
                self.pool.get('stock.move').action_done(cr, uid, produce_product.id, context=context)
    
        if production_mode in ['con_only', 'con_produce']:
            print 'I am only produce'
            if wiz:
                consume_lines = []
                for cons in wiz.consume_lines:
                    consume_lines.append({'product_id': cons.product_id.id, 'lot_id': cons.lot_id.id, 'product_qty': cons.product_qty})
            else:
                consume_lines = self._calculate_qty(cr, uid, production, production_qty_uom, context=context)
            for consume in consume_lines:
                remaining_qty = consume['product_qty']
                for raw_material_line in production.move_lines:
                    prod_orders=set()
                    location_id = False
                    if raw_material_line.product_qty==production.product_qty:
                        prod_orders.add(raw_material_line.unpack_unpack_id.id or raw_material_line.unpacking_id.id)
                        
                        vals = {'restrict_lot_id': False,
                                'restrict_partner_id': False,
                                'unpack_used_for': False}
                        if location_id:
                            vals.update({'location_id': location_id})
                        self.pool.get('stock.move').write(cr, uid, [raw_material_line.id], vals, context=context)
                    # Original moves will be the quantities consumed, so they need to be done
                        self.pool.get('stock.move').action_done(cr, uid, raw_material_line.id, context=context)
                        self.signal_workflow(cr, uid, list(prod_orders), 'button_produce')
        self.message_post(cr, uid, production_id, body=_("%s produced") % self._description, context=context)
        self.signal_workflow(cr, uid, [production_id], 'button_produce_done')
        return True



    def action_in_production(self, cr, uid, ids, context=None):
        """ Changes state to In Production and writes starting date.
        @return: True
        """
        return self.write(cr, uid, ids, {'state': 'in_production', 'date_start': time.strftime('%Y-%m-%d %H:%M:%S')})

    def consume_lines_get(self, cr, uid, ids, *args):
        res = []
        for order in self.browse(cr, uid, ids, context={}):
            res += [x.id for x in order.move_lines]
        return res

    def test_ready(self, cr, uid, ids):
        res = True
        for production in self.browse(cr, uid, ids):
            if production.move_lines and not production.ready_production:
                res = False
        return res

    
    #----product.packing form's product creating  
#     def _make_production_produce_line(self, cr, uid, production, context=None):
#         stock_move = self.pool.get('stock.move')
#         proc_obj = self.pool.get('procurement.order')
#         source_location_id = production.product_id.property_stock_production.id
#         destination_location_id = production.location_dest_id.id
#         procs = proc_obj.search(cr, uid, [('unpacking_id', '=', production.id)], context=context)
#         procurement = procs and\
#             proc_obj.browse(cr, uid, procs[0], context=context) or False
#         data = {
#             'name': production.name,
#             'date': production.date_planned,
#             'product_id': production.product_id.id,
#             'product_uom': production.product_uom.id,
#             'product_uom_qty': production.product_qty,
#             'product_uos_qty': production.product_uos and production.product_uos_qty or False,
#             'product_uos': production.product_uos and production.product_uos.id or False,
#             'location_id': source_location_id,
#             'location_dest_id': destination_location_id,
#             'move_dest_id': production.move_prod_id.id,
#             'procurement_id': procurement and procurement.id,
#             'company_id': production.company_id.id,
#             'unpacking_id': production.id,
#             'origin': production.name,
#             'group_id': procurement and procurement.group_id.id,
#         }
#         move_id = stock_move.create(cr, uid, data, context=context)
#         #a phantom bom cannot be used in mrp order so it's ok to assume the list returned by action_confirm
#         #is 1 element long, so we can take the first.
#         return stock_move.action_confirm(cr, uid, [move_id], context=context)[0]
##finished product form create by product_unpack
    def _make_production_produce_line_unpack(self, cr, uid, production, context=None):
        stock_move = self.pool.get('stock.move')
        proc_obj = self.pool.get('procurement.order')
        bom_obj = self.pool.get('bom.product')
        bom__line_obj = self.pool.get('bom.product.line')
        bom_line_obj =self.pool.get('bom.product.line')
        if production:
            print 'production',production
        #    bom_ids = bom_obj.search(cr,uid,[('id','=',production.bom_id.id)],context=context)
            bom_id = production.bom_id.id
            print 'bom_ids',bom_id
            if bom_id:
                bom_val =bom_line_obj.search(cr,uid,[('bom_id','=',bom_id)],context=context)
                print 'bom_val',bom_val
                if bom_val :
                    for val in bom_val:
                        obj =bom_line_obj.browse(cr,uid,val,context=context)
                        source_location_id = obj.product_id.property_stock_production.id
                        destination_location_id = production.location_dest_id.id
                        procs = proc_obj.search(cr, uid, [('packing_id', '=', production.id)], context=context)
                        procurement = procs and\
                            proc_obj.browse(cr, uid, procs[0], context=context) or False
                        data = {
                            'name': obj.product_id.name,
                            'date': production.date_planned,
                            'product_id': obj.product_id.id,
                            'product_uom': obj.product_uom.id,
                            'product_uom_qty': obj.product_qty *production.product_qty ,
                            'product_uos_qty': obj.product_uos and obj.product_uos_qty or False,
                            'product_uos': obj.product_uos and obj.product_uos.id or False,
                            'location_id': source_location_id,
                            'location_dest_id': destination_location_id,
                            'move_dest_id': production.move_prod_id.id,
                            'procurement_id': procurement and procurement.id,
                            'company_id': production.company_id.id,
                            'unpacking_id': production.id,
                            'origin': production.name,
                            'group_id': procurement and procurement.group_id.id,
                        }
                        move_id = stock_move.create(cr, uid, data, context=context)
                            #a phantom bom cannot be used in mrp order so it's ok to assume the list returned by action_confirm
                            #is 1 element long, so we can take the first.
        return stock_move.action_confirm(cr, uid, [move_id], context=context)[0]
    def _get_raw_material_procure_method(self, cr, uid, product, context=None):
        '''This method returns the procure_method to use when creating the stock move for the production raw materials'''
        warehouse_obj = self.pool['stock.warehouse']
        try:
            mto_route = warehouse_obj._get_mto_route(cr, uid, context=context)
        except:
            return "make_to_stock"
        routes = product.route_ids + product.categ_id.total_route_ids
        if mto_route in [x.id for x in routes]:
            return "make_to_order"
        return "make_to_stock"

    def _create_previous_move(self, cr, uid, move_id, product, source_location_id, dest_location_id, context=None):
        '''
        When the routing gives a different location than the raw material location of the production order, 
        we should create an extra move from the raw material location to the location of the routing, which 
        precedes the consumption line (chained).  The picking type depends on the warehouse in which this happens
        and the type of locations. 
        '''
        loc_obj = self.pool.get("stock.location")
        stock_move = self.pool.get('stock.move')
        type_obj = self.pool.get('stock.picking.type')
        # Need to search for a picking type
        move = stock_move.browse(cr, uid, move_id, context=context)
        src_loc = loc_obj.browse(cr, uid, source_location_id, context=context)
        dest_loc = loc_obj.browse(cr, uid, dest_location_id, context=context)
        code = stock_move.get_code_from_locs(cr, uid, move, src_loc, dest_loc, context=context)
        if code == 'outgoing':
            check_loc = src_loc
        else:
            check_loc = dest_loc
        wh = loc_obj.get_warehouse(cr, uid, check_loc, context=context)
        domain = [('code', '=', code)]
        if wh: 
            domain += [('warehouse_id', '=', wh)]
        types = type_obj.search(cr, uid, domain, context=context)
        move = stock_move.copy(cr, uid, move_id, default = {
            'location_id': source_location_id,
            'location_dest_id': dest_location_id,
            'procure_method': self._get_raw_material_procure_method(cr, uid, product, context=context),
            'unpack_unpack_id': False, 
            'move_dest_id': move_id,
            'picking_type_id': types and types[0] or False,
        }, context=context)
        return move
###-------------------------------------------Consumed Product lines --------------------------------------------
    def _make_consume_line_from_data(self, cr, uid, production, product, uom_id, qty, uos_id, uos_qty, context=None):
        stock_move = self.pool.get('stock.move')
        loc_obj = self.pool.get('stock.location')
        # Internal shipment is created for Stockable and Consumer Products
        if product.type not in ('product', 'consu'):
            return False
        # Take routing location as a Source Location.
        source_location_id = production.location_src_id.id
        prod_location_id = source_location_id
        prev_move= False

        destination_location_id = production.product_id.property_stock_production.id
        move_id = stock_move.create(cr, uid, {
            'name': production.name,
            'date': production.date_planned,
            'product_id': product.id,
            'product_uom_qty': qty,
            'product_uom': uom_id,
            'product_uos_qty': uos_id and uos_qty or False,
            'product_uos': uos_id or False,
            'location_id': source_location_id,
            'location_dest_id': destination_location_id,
            'company_id': production.company_id.id,
            'procure_method': prev_move and 'make_to_stock' or self._get_raw_material_procure_method(cr, uid, product, context=context), #Make_to_stock avoids creating procurement
            'unpack_unpack_id': production.id,
            #this saves us a browse in create()
            'price_unit': product.standard_price,
            'origin': production.name,
            'warehouse_id': loc_obj.get_warehouse(cr, uid, production.location_src_id, context=context),
            'group_id': production.move_prod_id.group_id.id,
        }, context=context)
        
        if prev_move:
            prev_move = self._create_previous_move(cr, uid, move_id, product, prod_location_id, source_location_id, context=context)
            stock_move.action_confirm(cr, uid, [prev_move], context=context)
        return move_id

    def _make_production_consume_line(self, cr, uid, line, context=None):
        return self._make_consume_line_from_data(cr, uid, line.production_id, line.product_id, line.product_uom.id, line.product_qty, line.product_uos.id, line.product_uos_qty, context=context)


    def _make_service_procurement(self, cr, uid, line, context=None):
        prod_obj = self.pool.get('product.product')
        if prod_obj.need_procurement(cr, uid, [line.product_id.id], context=context):
            vals = {
                'name': line.production_id.name,
                'origin': line.production_id.name,
                'company_id': line.production_id.company_id.id,
                'date_planned': line.production_id.date_planned,
                'product_id': line.product_id.id,
                'product_qty': line.product_qty,
                'product_uom': line.product_uom.id,
                'product_uos_qty': line.product_uos_qty,
                'product_uos': line.product_uos.id,
                }
            proc_obj = self.pool.get("procurement.order")
            proc = proc_obj.create(cr, uid, vals, context=context)
            proc_obj.run(cr, uid, [proc], context=context)


    def action_confirm(self, cr, uid, ids, context=None):
        """ Confirms production order.
        @return: Newly generated Shipment Id.
        """
        uncompute_ids = filter(lambda x: x, [not x.product_lines and x.id or False for x in self.browse(cr, uid, ids, context=context)])
        print 'uncompute_ids',uncompute_ids
        self.action_compute(cr, uid, uncompute_ids, context=context)

        for production in self.browse(cr, uid, ids, context=context):
            self._make_production_produce_line_unpack(cr, uid, production, context=context)

            stock_moves = []
            for line in production.product_lines:
                if line.product_id.type != 'service':
                    stock_move_id = self._make_production_consume_line(cr, uid, line, context=context)
                    stock_moves.append(stock_move_id)
                else:
                    self._make_service_procurement(cr, uid, line, context=context)
            if stock_moves:
                self.pool.get('stock.move').action_confirm(cr, uid, stock_moves, context=context)
            production.write({'state': 'confirmed'})
        return 0

    def action_assign(self, cr, uid, ids, context=None):
        """
        Checks the availability on the consume lines of the production order
        """
        from openerp import workflow
        move_obj = self.pool.get("stock.move")
        for production in self.browse(cr, uid, ids, context=context):
            move_obj.action_assign(cr, uid, [x.id for x in production.move_lines], context=context)
            if self.pool.get('product.unpacking').test_ready(cr, uid, [production.id]):
                workflow.trg_validate(uid, 'product.unpacking', production.id, 'moves_ready', cr)


    def force_production(self, cr, uid, ids, *args):
        """ Assigns products.
        @param *args: Arguments
        @return: True
        """
        from openerp import workflow
        move_obj = self.pool.get('stock.move')
        for order in self.browse(cr, uid, ids):
            move_obj.force_assign(cr, uid, [x.id for x in order.move_lines])
            if self.pool.get('product.unpacking').test_ready(cr, uid, [order.id]):
                workflow.trg_validate(uid, 'product.unpacking', order.id, 'moves_ready', cr)
        return True

     
product_unpacking()

class product_unpacking_line(osv.osv):
    _name = 'product.unpacking.line'
    _description = 'Production Scheduled Product'
    _columns = {
        'name': fields.char('Name', required=True),
        'product_id': fields.many2one('product.product', 'Product', required=True),
        'product_qty': fields.float('Product Quantity', digits_compute=dp.get_precision('Product Unit of Measure'), required=True),
        'product_uom': fields.many2one('product.uom', 'Product Unit of Measure', required=True),
        'product_uos_qty': fields.float('Product UOS Quantity'),
        'product_uos': fields.many2one('product.uom', 'Product UOS'),
        'production_id': fields.many2one('product.unpacking', 'Production Order', select=True),
    }

product_unpacking_line()