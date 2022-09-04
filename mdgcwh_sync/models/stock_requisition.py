'''
Sales Team RFI & GIN ( From CWHA/B )
 1 . If RFI Approved state in odoo 8 , create GIN in MDGCWH ( odoo15)
 2 . If GIN is issued in MDGCWH(odoo 15) , Auto GIN issued with this Qty in odoo8.
@author: Su Nandar
'''

from openerp.osv import fields, osv
import xmlrpclib

class stock_requisition(osv.osv):
    _inherit = "stock.requisition"

    def approve(self, cr, uid, ids, context=None):
        try:
            result = super(stock_requisition, self).approve(cr, uid, ids, context=context)
            requisition_obj = self.pool.get('stock.requisition')
            if ids:
                req_value = requisition_obj.browse(cr, uid, ids[0], context=context)
                if not req_value.to_location_id.is_cwh_location:
                    return result
                sd_uid, url, db, password = self.pool['cwh.connection'].get_connection_data(cr, uid, context=None)
                models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(url))
                location_ids_stock_a = models.execute_kw(db, sd_uid, password, 'stock.location', 'search',
                                                        [[('complete_name', '=', 'CWHA/Stock')]], {'limit': 1})
                location_ids_stock_b = models.execute_kw(db, sd_uid, password, 'stock.location', 'search',
                                                         [[('complete_name', '=', 'CWHB/Stock')]], {'limit': 1})
                gin_line_array = []
                gin_line = False
                gin_obj = req_value.good_issue_id
                gin_vals = {
                    'name': req_value.good_issue_id.name,
                    'gin_ref': req_value.good_issue_id.name,
                    'delivery_team': req_value.good_issue_id.sale_team_id.name,
                    'requested_by': req_value.good_issue_id.request_by.name,
                    'rfi_ref': req_value.name,
                    'request_warehouse': req_value.good_issue_id.from_location_id.name,
                    'branch': req_value.good_issue_id.branch_id.name,
                    'vehicle_no':req_value.good_issue_id.vehicle_id.name,
                    # 'state':'approve',
                }
                if req_value.to_location_id.name in ('MDGCWH1-Sellable','MDGCWHA-Sellable'):
                    gin_vals['requesting_loc'] = location_ids_stock_a[0]
                if req_value.to_location_id.name in ('MDGCWH2-Sellable','MDGCWHB-Sellable'):
                    gin_vals['requesting_loc'] = location_ids_stock_b[0]

                gin_id = models.execute_kw(db, sd_uid, password, 'good.issue.note', 'create', [gin_vals])

                for line in gin_obj.p_line:
                    product_ids = models.execute_kw(db, sd_uid, password, 'product.product', 'search',
                                                    [[('default_code', '=', line.product_id.default_code)]],
                                                    {'limit': 1})
                    uom_id = models.execute_kw(db, sd_uid, password, 'uom.uom', 'search',
                                               [[('name', '=', line.product_uom.name)]], {'limit': 1})
                    if product_ids:
                        gin_line = True
                        gin_line_value = {
                            'product_id': product_ids[0],
                            'order_qty': line.order_qty,
                            'total_req_qty': line.total_request_qty,
                            'qty': line.issue_quantity,
                            'product_uom_id': uom_id[0],
                            'batch_no': line.batch_no.name,
                            'expiry_date': line.expiry_date,
                            'qty_on_hand': line.qty_on_hand,
                            'remark': line.remark,
                            'gin_id': gin_id,
                        }
                        gin_line_array.append(gin_line_value)
                if gin_line == True:
                    models.execute_kw(db, sd_uid, password, 'good.issue.note.line', 'create', [gin_line_array])
                else:
                    models.execute_kw(db, sd_uid, password, 'good.issue.note', 'unlink', [[gin_id]])
                # models.execute_kw(db, sd_uid, password, 'good.issue.note', 'action_approve', [gin_id])

        except Exception, e:
            raise e