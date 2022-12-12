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
        'woo_user_id': fields.char('Woo User ID'),
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
        customer_point_obj = self.pool.get('woo.customer.point')
        woo_instance_obj = self.pool.get('woo.instance.ept')
        instance = woo_instance_obj.search(cr, uid, [('state', '=', 'confirmed')], limit=1)
        if instance:
            instance_obj = woo_instance_obj.browse(cr, uid, instance)
            url = instance_obj.host + "/wp-json/auth-api/v1/odoo/users/get-points-info"
            headers = CaseInsensitiveDict()
            login_info = instance_obj.admin_username + ":" + instance_obj.admin_password
            login_info_bytes = login_info.encode('ascii')
            base64_bytes = base64.b64encode(login_info_bytes)
            headers["Authorization"] = "Basic " + base64_bytes
            headers["Content-Type"] = "application/json"
            point_response = requests.get(url, headers=headers)
            if point_response.status_code in [200, 201]:
                point_data = point_response.json()
                cr.execute("delete from woo_customer_point;")
                for record in point_data:
                    user_id = record.get('user_id')
                    total_points = record.get('total_points')
                    point_history = record.get('point_history')
                    total_points_data = {
                        'woo_user_id': str(user_id),
                        'total_points': float(total_points),
                    }
                    customer_point_obj.create(cr, uid, total_points_data, context=context)
                    for item in point_history:
                        if item.get('expire_date') != '0000-00-00 00:00:00':
                            expire_date = item.get('expire_date')
                        else:
                            expire_date = None
                        existing_point_history = point_history_obj.search(cr, uid, [('woo_point_history_id', '=', item.get('id'))], context=context)
                        if not existing_point_history:
                            point_history_data = {
                                'woo_point_history_id': item.get('id'),
                                'woo_user_id': item.get('user_id'),
                                'expire_date': expire_date,
                                'action': item.get('action'),
                                'amount': item.get('amount'),
                                'date_earning': item.get('date_earning'),
                                'title': item.get('title'),
                                'custom_order_number': item.get('custom_order_number'),
                            }
                            point_history_obj.create(cr, uid, point_history_data, context=context)
                cr.execute("""update woo_point_history
                            set partner_id=rp.id,woo_customer_id=concat('1_',woo_point_history.woo_user_id)
                            from res_partner rp
                            where rp.woo_customer_id=concat('1_',woo_point_history.woo_user_id)
                            and woo_point_history.partner_id is null
                            and rp.parent_id is null;""")
                cr.execute("""update woo_point_history
                            set order_id=so.id
                            from sale_order so
                            where woo_point_history.custom_order_number=so.woo_order_number
                            and woo_point_history.order_id is null;""")
                cr.execute("update res_partner set total_points=cp.total_points from woo_customer_point cp where res_partner.woo_customer_id=concat('1_',cp.woo_user_id);")
