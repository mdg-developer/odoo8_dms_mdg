from openerp.osv import fields, osv
from datetime import datetime
import openerp.addons.decimal_precision as dp
from openerp import api

class branch_stock_requisition(osv.osv):
    _inherit = "branch.stock.requisition"

    def _max_viss_amount_one(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        max_viss = 0
        if context is None:
            context = {}
        for order in self.browse(cr, uid, ids, context=context):
            val1 = 0.0

            if order.truck_one_type_id:
                truck_data = self.pool.get('truck.type').browse(cr, uid, order.truck_one_type_id.id, context=context)
                max_viss = truck_data.est_viss
            if order.vehicle_id:
                vehicle_data = self.pool.get('fleet.vehicle').browse(cr, uid, order.vehicle_id.id, context=context)
                max_viss = vehicle_data.alert_weight_viss

            val1 = max_viss
            res[order.id] = val1
        return res

    def _max_cbm_amount_one(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        max_viss=0
        if context is None:
            context = {}
        for order in self.browse(cr, uid, ids, context=context):
            val1 = 0.0
            if order.truck_one_type_id:
                truck_data = self.pool.get('truck.type').browse(cr, uid, order.truck_one_type_id.id, context=context)
                max_viss = truck_data.est_cbm
            if order.vehicle_id:
                vehicle_data = self.pool.get('fleet.vehicle').browse(cr, uid, order.vehicle_id.id, context=context)
                max_viss = vehicle_data.alert_vol_cbm
            val1 = max_viss
            res[order.id] = val1
        return res

    def _max_viss_amount_two(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        max_viss = 0
        if context is None:
            context = {}
        for order in self.browse(cr, uid, ids, context=context):
            val1 = 0.0

            if order.truck_two_type_id:
                truck_data = self.pool.get('truck.type').browse(cr, uid, order.truck_two_type_id.id, context=context)
                max_viss = truck_data.est_viss
            if order.vehicle_id:
                vehicle_data = self.pool.get('fleet.vehicle').browse(cr, uid, order.vehicle_id.id, context=context)
                max_viss = vehicle_data.alert_weight_viss

            val1 = max_viss
            res[order.id] = val1
        return res

    def _max_cbm_amount_two(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        max_viss=0
        if context is None:
            context = {}
        for order in self.browse(cr, uid, ids, context=context):
            val1 = 0.0
            if order.truck_two_type_id:
                truck_data = self.pool.get('truck.type').browse(cr, uid, order.truck_two_type_id.id, context=context)
                max_viss = truck_data.est_cbm
            if order.vehicle_id:
                vehicle_data = self.pool.get('fleet.vehicle').browse(cr, uid, order.vehicle_id.id, context=context)
                max_viss = vehicle_data.alert_vol_cbm
            val1 = max_viss
            res[order.id] = val1
        return res

    def _max_viss_amount_three(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        max_viss = 0
        if context is None:
            context = {}
        for order in self.browse(cr, uid, ids, context=context):
            val1 = 0.0

            if order.truck_three_type_id:
                truck_data = self.pool.get('truck.type').browse(cr, uid, order.truck_three_type_id.id, context=context)
                max_viss = truck_data.est_viss
            if order.vehicle_id:
                vehicle_data = self.pool.get('fleet.vehicle').browse(cr, uid, order.vehicle_id.id, context=context)
                max_viss = vehicle_data.alert_weight_viss

            val1 = max_viss
            res[order.id] = val1
        return res

    def _max_cbm_amount_three(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        max_viss=0
        if context is None:
            context = {}
        for order in self.browse(cr, uid, ids, context=context):
            val1 = 0.0
            if order.truck_three_type_id:
                truck_data = self.pool.get('truck.type').browse(cr, uid, order.truck_three_type_id.id, context=context)
                max_viss = truck_data.est_cbm
            if order.vehicle_id:
                vehicle_data = self.pool.get('fleet.vehicle').browse(cr, uid, order.vehicle_id.id, context=context)
                max_viss = vehicle_data.alert_vol_cbm
            val1 = max_viss
            res[order.id] = val1
        return res

    def _max_viss_amount_four(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        max_viss = 0
        if context is None:
            context = {}
        for order in self.browse(cr, uid, ids, context=context):
            val1 = 0.0

            if order.truck_four_type_id:
                truck_data = self.pool.get('truck.type').browse(cr, uid, order.truck_four_type_id.id, context=context)
                max_viss = truck_data.est_viss
            if order.vehicle_id:
                vehicle_data = self.pool.get('fleet.vehicle').browse(cr, uid, order.vehicle_id.id, context=context)
                max_viss = vehicle_data.alert_weight_viss

            val1 = max_viss
            res[order.id] = val1
        return res

    def _max_cbm_amount_four(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        max_viss=0
        if context is None:
            context = {}
        for order in self.browse(cr, uid, ids, context=context):
            val1 = 0.0
            if order.truck_four_type_id:
                truck_data = self.pool.get('truck.type').browse(cr, uid, order.truck_four_type_id.id, context=context)
                max_viss = truck_data.est_cbm
            if order.vehicle_id:
                vehicle_data = self.pool.get('fleet.vehicle').browse(cr, uid, order.vehicle_id.id, context=context)
                max_viss = vehicle_data.alert_vol_cbm
            val1 = max_viss
            res[order.id] = val1
        return res

    def _max_viss_amount_five(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        max_viss = 0
        if context is None:
            context = {}
        for order in self.browse(cr, uid, ids, context=context):
            val1 = 0.0

            if order.truck_five_type_id:
                truck_data = self.pool.get('truck.type').browse(cr, uid, order.truck_five_type_id.id, context=context)
                max_viss = truck_data.est_viss
            if order.vehicle_id:
                vehicle_data = self.pool.get('fleet.vehicle').browse(cr, uid, order.vehicle_id.id, context=context)
                max_viss = vehicle_data.alert_weight_viss

            val1 = max_viss
            res[order.id] = val1
        return res

    def _max_cbm_amount_five(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        max_viss=0
        if context is None:
            context = {}
        for order in self.browse(cr, uid, ids, context=context):
            val1 = 0.0
            if order.truck_five_type_id:
                truck_data = self.pool.get('truck.type').browse(cr, uid, order.truck_five_type_id.id, context=context)
                max_viss = truck_data.est_cbm
            if order.vehicle_id:
                vehicle_data = self.pool.get('fleet.vehicle').browse(cr, uid, order.vehicle_id.id, context=context)
                max_viss = vehicle_data.alert_vol_cbm
            val1 = max_viss
            res[order.id] = val1
        return res

    _columns = {

        'truck_one_type_id': fields.many2one('truck.type', 'Truck Type 1'),
        'truck_two_type_id': fields.many2one('truck.type', 'Truck Type 2'),
        'truck_three_type_id': fields.many2one('truck.type', 'Truck Type 3'),
        'truck_four_type_id': fields.many2one('truck.type', 'Truck Type 4'),
        'truck_five_type_id': fields.many2one('truck.type', 'Truck Type 5'),
        'original_rfi': fields.char("Original RFI"),
        'max_viss_one': fields.function(_max_viss_amount_one, string='Truck1 Viss',
                                    digits_compute=dp.get_precision('Product Price'), type='float'),
        'max_cbm_one': fields.function(_max_cbm_amount_one, string='Truck1 CBM', digits_compute=dp.get_precision('Product Price'),
                                   type='float'),
        'max_viss_two': fields.function(_max_viss_amount_two, string='Truck2 Viss',
                                        digits_compute=dp.get_precision('Product Price'), type='float'),
        'max_cbm_two': fields.function(_max_cbm_amount_two, string='Truck2 CBM',
                                       digits_compute=dp.get_precision('Product Price'),
                                       type='float'),
        'max_viss_three': fields.function(_max_viss_amount_three, string='Truck3 Viss',
                                        digits_compute=dp.get_precision('Product Price'), type='float'),
        'max_cbm_three': fields.function(_max_cbm_amount_three, string='Truck3 CBM',
                                       digits_compute=dp.get_precision('Product Price'),
                                       type='float'),
        'max_viss_four': fields.function(_max_viss_amount_four, string='Truck4 Viss',
                                          digits_compute=dp.get_precision('Product Price'), type='float'),
        'max_cbm_four': fields.function(_max_cbm_amount_four, string='Truck4 CBM',
                                         digits_compute=dp.get_precision('Product Price'),
                                         type='float'),

        'max_viss_five': fields.function(_max_viss_amount_five, string='Truck5 Viss',
                                         digits_compute=dp.get_precision('Product Price'), type='float'),
        'max_cbm_five': fields.function(_max_cbm_amount_five, string='Truck5 CBM',
                                        digits_compute=dp.get_precision('Product Price'),
                                        type='float'),

        'state': fields.selection([
            ('draft', 'Draft'),
            ('confirm', 'Confirm'),
            ('loading_plan', 'Loading Plan Confirmed'),
            ('loaded', 'Loaded'),
            ('approve', 'Approved'),
            ('partial', 'Partial Complete'),
            ('full_complete', 'Full Complete'),
            #             ('done', 'Done'),
            #             ('complete_partial', 'Complete Partial'),
            ('cancel', 'Cancel'),
        ], 'Status', readonly=True, copy=False, help="Gives the status of the quotation or sales order.\
                  \nThe exception status is automatically set when a cancel operation occurs \
                  in the invoice validation (Invoice Exception) or in the picking list process (Shipping Exception).\nThe 'Waiting Schedule' status is set when the invoice is confirmed\
                   but waiting for the scheduler to run on the order date.", select=True),


    }

    def loaded(self,cr,uid,ids,context=None):
        requisition_obj = self.pool.get('branch.stock.requisition')
        requisition_line_obj = self.pool.get('branch.stock.requisition.line')
        for order in self.browse(cr, uid, ids, context=context):
            is_brfi_one = False
            is_brfi_two = False
            is_brfi_three = False
            is_brfi_four = False
            is_brfi_five = False

            for line in order.p_line:
                if line.truck_one_quantity and line.truck_one_quantity != 0:
                    is_brfi_one = True
                if line.truck_two_quantity and line.truck_two_quantity !=0:
                    is_brfi_two = True
                if line.truck_three_quantity and line.truck_three_quantity !=0:
                    is_brfi_three = True
                if line.truck_four_quantity and line.truck_four_quantity !=0:
                    is_brfi_four = True
                if line.truck_five_quantity and line.truck_five_quantity != 0:
                    is_brfi_five = True
            branch_id = order.branch_id.id
            from_location_id = order.from_location_id.id
            issue_to = order.issue_to
            to_location_id = order.to_location_id.id
            vehicle_id = order.vehicle_id.id
            internal_reference = order.internal_reference
            branch_target_id = order.branch_target_id.id
            original_rfi = order.name
            pricelist_id =order.pricelist_id.id

            values = {
                        'branch_id':branch_id,
                        'from_location_id': from_location_id,
                        'issue_to': issue_to,
                        'to_location_id': to_location_id,
                        'vehicle_id': vehicle_id,
                        'internal_reference': internal_reference,
                        'branch_target_id': branch_target_id,
                        'original_rfi': original_rfi,
                        'pricelist_id': pricelist_id,

                    }

            if is_brfi_one == True:
                values['truck_type_id'] = order.truck_one_type_id.id
                brfi_one_id = requisition_obj.create(cr, uid, values, context=context)
                for line in order.p_line:
                    product_id = line.product_id.id
                    req_quantity = line.truck_one_quantity
                    line_id = brfi_one_id
                    product_uom = line.product_uom.id
                    line_val = {
                        'product_id' : product_id,
                        'req_quantity' : req_quantity,
                        'line_id' : line_id,
                        'product_uom' : product_uom,
                    }
                    requisition_line_obj.create(cr, uid, line_val, context=context)

            if is_brfi_two == True:
                values['truck_type_id'] = order.truck_two_type_id.id
                brfi_two_id = requisition_obj.create(cr, uid, values, context=context)
                for line in order.p_line:
                    product_id = line.product_id.id
                    req_quantity = line.truck_two_quantity
                    line_id = brfi_two_id
                    product_uom = line.product_uom.id
                    line_val = {
                        'product_id': product_id,
                        'req_quantity': req_quantity,
                        'line_id': line_id,
                        'product_uom': product_uom,
                    }
                    requisition_line_obj.create(cr, uid, line_val, context=context)

            if is_brfi_three == True:
                values['truck_type_id'] = order.truck_three_type_id.id
                brfi_three_id = requisition_obj.create(cr, uid, values, context=context)
                for line in order.p_line:
                    product_id = line.product_id.id
                    req_quantity = line.truck_three_quantity
                    line_id = brfi_three_id
                    product_uom = line.product_uom.id
                    line_val = {
                        'product_id': product_id,
                        'req_quantity': req_quantity,
                        'line_id': line_id,
                        'product_uom': product_uom,
                    }
                    requisition_line_obj.create(cr, uid, line_val, context=context)

            if is_brfi_four == True:
                values['truck_type_id'] = order.truck_four_type_id.id
                brfi_four_id = requisition_obj.create(cr, uid, values, context=context)
                for line in order.p_line:
                    product_id = line.product_id.id
                    req_quantity = line.truck_four_quantity
                    line_id = brfi_four_id
                    product_uom = line.product_uom.id
                    line_val = {
                        'product_id': product_id,
                        'req_quantity': req_quantity,
                        'line_id': line_id,
                        'product_uom': product_uom,
                    }
                    requisition_line_obj.create(cr, uid, line_val, context=context)

            if is_brfi_five == True:
                values['truck_type_id'] = order.truck_five_type_id.id
                brfi_five_id = requisition_obj.create(cr, uid, values, context=context)
                for line in order.p_line:
                    product_id = line.product_id.id
                    req_quantity = line.truck_five_quantity
                    line_id = brfi_five_id
                    product_uom = line.product_uom.id
                    line_val = {
                        'product_id': product_id,
                        'req_quantity': req_quantity,
                        'line_id': line_id,
                        'product_uom': product_uom,
                    }
                    requisition_line_obj.create(cr, uid, line_val, context=context)







        return self.write(cr, uid, ids, {'state':'loaded'})

class stock_requisition_line(osv.osv):
    _inherit = 'branch.stock.requisition.line'

    _columns = {

        'truck_one_quantity': fields.float(string='Truck 1', digits=(16, 0)),
        'truck_two_quantity': fields.float(string='Truck 2', digits=(16, 0)),
        'truck_three_quantity': fields.float(string='Truck 3', digits=(16, 0)),
        'truck_four_quantity': fields.float(string='Truck 4', digits=(16, 0)),
        'truck_five_quantity': fields.float(string='Truck 5', digits=(16, 0)),
        'req_quantity_diff_truck': fields.float(compute='_compute_req_qty_diff_truck',string='Req Diff(Qty)', digits=(16, 0)),


    }

    @api.one
    @api.depends('truck_one_quantity','truck_two_quantity','truck_three_quantity','truck_four_quantity', 'truck_five_quantity','req_quantity')
    def _compute_req_qty_diff_truck(self):
        total_truck = req_qty = 0
        req_qty = self.req_quantity
        if self.truck_one_quantity:
            total_truck += self.truck_one_quantity
        if self.truck_two_quantity:
            total_truck += self.truck_two_quantity
        if self.truck_three_quantity:
            total_truck += self.truck_three_quantity
        if self.truck_four_quantity:
            total_truck += self.truck_four_quantity
        if self.truck_five_quantity:
            total_truck += self.truck_five_quantity

        val = req_qty - total_truck
        self.req_quantity_diff_truck = val




