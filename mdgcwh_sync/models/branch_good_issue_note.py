from openerp.osv import fields, osv
import xmlrpclib
from openerp.tools.translate import _

class branch_good_issue_note(osv.osv):
    _inherit = "branch.good.issue.note"

    def set_issue_qty_zero(self, cr, uid, ids, context=None):
        note_obj = self.pool.get('branch.good.issue.note')
        if ids:
            note_value = note_obj.browse(cr, uid, ids[0], context=context)
            for note_id in note_value.p_line:
                note_id.write({'issue_quantity': 0})
        return True

    def approve(self, cr, uid, ids, context=None):
        try:
            result = super(branch_good_issue_note, self).approve(cr, uid, ids, context=context)
            order_id = False
            product_line_obj = self.pool.get('branch.stock.requisition.line')
            requisition_obj = self.pool.get('branch.stock.requisition')
            good_obj = self.pool.get('branch.good.issue.note')
            branch_obj = self.pool.get('res.branch')
            product_obj = self.pool.get('product.product')

            good_line_obj = self.pool.get('branch.good.issue.note.line')

            sd_uid, url, db, password = self.pool['cwh.connection'].get_connection_data(cr, uid, context=None)
            models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(url))
            so_vals = {}
            so_vals['partner_id'] = 7
            so_vals['order_line'] = []
            gin_id = self.browse(cr, uid, ids, context=context)
            to_location = gin_id.to_location_id.name
            if gin_id.request_id:
                # req_value = requisition_obj.browse(cr, uid, ids[0], context=context)
                req_value = gin_id.request_id
                if not req_value.to_location_id.is_cwh_location:
                    return result
                # check_brfi = models.execute_kw(db, sd_uid, password, 'sale.order', 'search',[[('origin', '=', req_value.name)]], {'limit': 1})
                # if check_brfi:
                #     return result

                so_vals['client_order_ref'] = req_value.from_location_id.name or ''
                so_vals['origin'] = req_value.name or ''
                so_create = False
                data_line = []
                cr.execute('''select sum(req_quantity_2) as req_quantity,l.product_id,l.product_loss,pt.ctn_pallet,pp.name_template,l.product_uom,uom.name
                             from branch_good_issue_note s,branch_good_issue_note_line l ,product_uom uom ,product_product pp ,product_template pt
                             where  s.id = l.line_id and l.product_id= pp.id and pp.product_tmpl_id = pt.id and l.product_uom =uom.id and s.id =%s
                             group by product_id ,product_loss,pt.ctn_pallet,pp.name_template,l.product_uom,uom.name''',(ids[0],))
                req_record = cr.fetchall()
                if req_record:
                    for req_data in req_record:
                        product_id = int(req_data[1])
                        loose = req_data[2]
                        pallet_size = int(req_data[3])
                        if not pallet_size:
                            raise osv.except_osv(
                                _('Warning!'),
                                _('Please Check Ctn/Pallet Value for the product '+ product_obj.browse(cr, uid, product_id).name)
                            )
                        req_qty = float(req_data[0])
                        p_name = req_data[4]
                        uom_id = req_data[5]
                        uom_name = req_data[6]
                        if loose != True:
                            if req_qty >= pallet_size:
                                req_quantity = int(req_qty / pallet_size)
                                pallet_req_qty = req_quantity * pallet_size
                                ctn_qty = req_qty % pallet_size
                                data_line.append(
                                    {'req_quantity': pallet_req_qty, 'product_uom': uom_id, 'product_id': product_id,
                                     'uom_name': uom_name, 'product_name': p_name, 'loose': loose, 'ctn_line': False})
                                if ctn_qty > 0:
                                    data_line.append(
                                        {'req_quantity': ctn_qty, 'product_uom': uom_id, 'product_id': product_id,
                                         'uom_name': uom_name, 'product_name': p_name, 'loose': loose, 'ctn_line': True})
                            else:
                                data_line.append({'req_quantity': req_qty, 'product_uom': uom_id, 'product_id': product_id,
                                                  'uom_name': uom_name, 'product_name': p_name, 'loose': loose,
                                                  'ctn_line': True})
                        else:
                            data_line.append({'req_quantity': req_qty, 'product_uom': uom_id, 'product_id': product_id,
                                              'uom_name': uom_name, 'product_name': p_name, 'loose': loose,
                                              'ctn_line': False})

                for req_line_value in data_line:
                    # for req_line_id in req_value.p_line:
                    product_data = product_obj.browse(cr, uid, req_line_value['product_id'], context=context)
                    if req_line_value['req_quantity'] > 0:

                        product_ids = models.execute_kw(db, sd_uid, password,'product.product', 'search',[[('default_code', '=', product_data.default_code)]],{'limit': 1})
                        if product_ids:
                            loose = False
                            route = False
                            if req_line_value['loose'] == True and to_location not in ('MDGCWH1-Sellable','MDGCWHA-Sellable'):
                                route_id = models.execute_kw(db, sd_uid, password,'stock.location.route', 'search',[[('pickface_pcs_route', '=', True), ('active', '=', True)]],{'limit': 1})
                                if route_id:
                                    route = route_id[0]
                            if req_line_value['ctn_line'] == True and to_location not in ('MDGCWH1-Sellable','MDGCWHA-Sellable'):
                                route_id = models.execute_kw(db, sd_uid, password,'stock.location.route', 'search',[[('pickface_ctn_route', '=', True), ('active', '=', True)]],{'limit': 1})
                                if route_id:
                                    route = route_id[0]
                            so_create = True
                            uom_id = False
                            # product_id=models.execute_kw(db, sd_uid, password, 'product.product', 'read', [product_ids])[0]
                            product_id = models.execute_kw(db, sd_uid, password, 'product.product', 'read', [product_ids])[0]
                            uom_id = models.execute_kw(db, sd_uid, password, 'uom.uom', 'search',
                                                       [[('name', '=', req_line_value['uom_name'])]],
                                                       {'limit': 1})
                            so_vals['order_line'].append(
                                [0, False, {'name': req_line_value['product_name'], 'product_id': product_id['id'],
                                            'product_uom_qty': req_line_value['req_quantity'], 'product_uom': uom_id[0],
                                            'price_unit': product_id['lst_price'],
                                            'loose': req_line_value['loose'], 'route_id': route,
                                            'ctn_pickface': req_line_value['ctn_line']
                                            }])

                            if gin_id.to_location_id.name in ('MDGCWH1-Sellable','MDGCWHA-Sellable'):
                                warehouse_ids = models.execute_kw(db, sd_uid, password, 'stock.warehouse', 'search',
                                                                [[('name', '=', 'MDGCentralWHA')]],
                                                                {'limit': 1})
                                # warehouse_id = models.execute_kw(db, sd_uid, password, 'product.product', 'read', [warehouse_ids])[0]
                                so_vals['warehouse_id']= warehouse_ids[0]

                            if gin_id.to_location_id.name in ('MDGCWH2-Sellable','MDGCWHB-Sellable'):
                                warehouse_ids = models.execute_kw(db, sd_uid, password, 'stock.warehouse', 'search',
                                                                  [[('name', '=', 'MDGCentralWHB')]],
                                                                  {'limit': 1})
                                # warehouse_id = models.execute_kw(db, sd_uid, password, 'product.product', 'read', [warehouse_ids])[0]
                                so_vals['warehouse_id'] = warehouse_ids[0]



                if so_create == True:
                    order_id = models.execute_kw(db, sd_uid, password, 'sale.order', 'create', [so_vals])
                    if order_id:
                        print
                        'order_id', order_id
                        models.execute_kw(db, sd_uid, password, 'sale.order', 'action_confirm', [order_id])
            return result
        except Exception , e:
            print "Exception",e
            # if order_id:
            #     models.execute_kw(db, sd_uid, password, 'sale.order', 'unlink', [[order_id]])
            raise e