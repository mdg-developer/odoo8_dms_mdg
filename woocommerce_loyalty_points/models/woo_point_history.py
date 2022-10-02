from openerp.osv import fields, osv
import logging
import requests
from requests.structures import CaseInsensitiveDict
import base64
from openerp.osv.orm import except_orm
from openerp.tools.translate import _

class woo_point_history(osv.osv):
    _name = "woo.point.history"

    _columns = {
        'woo_point_history_id': fields.char('Woo Point History ID'),
        'woo_customer_id': fields.char('Woo Customer ID'),
        'partner_id': fields.many2one('res.partner', 'Customer'),
        'action': fields.char('Action'),
        'order_id': fields.many2one('sale.order', 'Sale Order'),
        'amount': fields.float('Amount'),
        'date_earning': fields.datetime('Date Earning'),
        'expire_date': fields.datetime('Expire Date'),
        'title': fields.char('Title'),
        'custom_order_number': fields.char('Custom Order Number'),
    }

    def get_woo_point_history(self, cr, uid, context=None):

        partner_obj = self.pool.get('res.partner')
        point_history_obj = self.pool.get('woo.point.history')
        partners = partner_obj.search(cr, uid, [('woo_customer_id', '!=', False),('parent_id', '=', False)])
        for data in partners:
            partner = partner_obj.browse(cr, uid, data)

            woo_instance_obj = self.pool.get('woo.instance.ept')
            instance = woo_instance_obj.search(cr, uid, [('state', '=', 'confirmed')], limit=1)
            if instance:
                instance_obj = woo_instance_obj.browse(cr, uid, instance)
                if partner.woo_customer_id:
                    woo_customer_id = partner.woo_customer_id.split("_")[1]
                    url = instance_obj.host + "/wp-json/auth-api/v1/odoo/users/get-points-info?user_id=" + woo_customer_id
                    headers = CaseInsensitiveDict()
                    login_info = instance_obj.admin_username + ":" + instance_obj.admin_password
                    login_info_bytes = login_info.encode('ascii')
                    base64_bytes = base64.b64encode(login_info_bytes)
                    headers["Authorization"] = "Basic " + base64_bytes
                    headers["Content-Type"] = "application/json"
                    point_response = requests.get(url, headers=headers)
                    if point_response.status_code in [200, 201]:
                        point_history = point_response.json()
                        total_points = point_history.get('total_points')
                        partner.write({"total_points": total_points})
                        point_history = point_history.get('point_history')
                        for item in point_history:
                            woo_point_history_id = item.get('id')
                            woo_point_history = point_history_obj.search(cr, uid, [('woo_point_history_id', '=', woo_point_history_id)])
                            if not woo_point_history:
                                if item.get('expire_date') != '0000-00-00 00:00:00':
                                    expire_date = item.get('expire_date')
                                else:
                                    expire_date = None
                                sale_order = self.pool.get('sale.order').search(cr, uid, [('woo_order_id', '=', int(item.get('order_id')))])
                                sale_order_obj = self.pool.get('sale.order').browse(cr, uid, sale_order)
                                values = {
                                    'woo_point_history_id': woo_point_history_id,
                                    'woo_customer_id': partner.woo_customer_id,
                                    'partner_id': partner.id,
                                    'action': item.get('action'),
                                    'order_id': sale_order_obj.id,
                                    'amount': float(item.get('amount')),
                                    'date_earning': item.get('date_earning'),
                                    'expire_date': expire_date,
                                    'title': item.get('title'),
                                    'custom_order_number': item.get('custom_order_number'),
                                }
                                point_history_obj.create(cr, uid, values, context=context)
