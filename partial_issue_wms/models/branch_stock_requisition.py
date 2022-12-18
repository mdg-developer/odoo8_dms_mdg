from openerp.osv import fields, osv
from datetime import datetime

class branch_stock_requisition(osv.osv):
    _inherit = "branch.stock.requisition"

    _columns = {

        'truck_one_type_id': fields.many2one('truck.type', 'Truck Type 1'),
        'truck_two_type_id': fields.many2one('truck.type', 'Truck Type 2'),
        'truck_three_type_id': fields.many2one('truck.type', 'Truck Type 3'),
        'truck_four_type_id': fields.many2one('truck.type', 'Truck Type 4'),
        'truck_five_type_id': fields.many2one('truck.type', 'Truck Type 5'),
        'original_rfi': fields.char("Original RFI"),

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
            branch_id = order.branch_id
            from_location_id = order.from_location_id
            issue_to = order.issue_to
            to_location_id = order.to_location_id
            vehicle_id = order.vehicle_id
            internal_reference = order.internal_reference
            # branch_target_id = order.branch_target_id
            truck_type_id = order.truck_type_id
            original_rfi = order.name

            values = {
                        'branch_id':branch_id,
                        'from_location_id': from_location_id,
                        'issue_to': issue_to,
                        'to_location_id': to_location_id,
                        'vehicle_id': vehicle_id,
                        'internal_reference': internal_reference,
                        # 'branch_target_id': branch_target_id,
                        'truck_type_id': truck_type_id,
                        'original_rfi': original_rfi,

                    }

            if is_brfi_one == True:
                brfi_one_id = requisition_obj.create(cr, uid, values, context=context)
                for line in order.p_line:
                    product_id = line.product_id.id
                    req_quantity = line.truck_one_quantity
                    line_id = brfi_one_id
                    line_val = {
                        product_id : product_id,
                        req_quantity : req_quantity,
                        line_id : line_id,
                    }
                    requisition_line_obj.create(cr, uid, line_val, context=context)

            if is_brfi_two == True:
                brfi_two_id = requisition_obj.create(cr, uid, values, context=context)
                for line in order.p_line:
                    product_id = line.product_id.id
                    req_quantity = line.truck_two_quantity
                    line_id = brfi_two_id
                    line_val = {
                        product_id: product_id,
                        req_quantity: req_quantity,
                        line_id: line_id,
                    }
                    requisition_line_obj.create(cr, uid, line_val, context=context)

            if is_brfi_three == True:
                brfi_three_id = requisition_obj.create(cr, uid, values, context=context)
                for line in order.p_line:
                    product_id = line.product_id.id
                    req_quantity = line.truck_three_quantity
                    line_id = brfi_three_id
                    line_val = {
                        product_id: product_id,
                        req_quantity: req_quantity,
                        line_id: line_id,
                    }
                    requisition_line_obj.create(cr, uid, line_val, context=context)

            if is_brfi_four == True:
                brfi_four_id = requisition_obj.create(cr, uid, values, context=context)
                for line in order.p_line:
                    product_id = line.product_id.id
                    req_quantity = line.truck_four_quantity
                    line_id = brfi_four_id
                    line_val = {
                        product_id: product_id,
                        req_quantity: req_quantity,
                        line_id: line_id,
                    }
                    requisition_line_obj.create(cr, uid, line_val, context=context)

            if is_brfi_five == True:
                brfi_five_id = requisition_obj.create(cr, uid, values, context=context)
                for line in order.p_line:
                    product_id = line.product_id.id
                    req_quantity = line.truck_five_quantity
                    line_id = brfi_five_id
                    line_val = {
                        product_id: product_id,
                        req_quantity: req_quantity,
                        line_id: line_id,
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

    }
