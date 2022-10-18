import time
from openerp.osv import fields, osv
from openerp import _
from openerp import http
from openerp.http import request
from openerp.tools import html_escape as escape
import json
from openerp.osv.orm import except_orm
import requests
from requests.structures import CaseInsensitiveDict
import base64
import logging

class mobile_sync(osv.osv_memory):
    _name = 'mobile.sync'
    _description = 'Mobile Sync'

    _columns = {
        'sync': fields.boolean("Sync", required=True),
    }

    _defaults = {
        'sync': True,
    }

    def partner_mobile_sync_to_woo(self, cr, uid, ids, context=None):
        data = self.read(cr, uid, ids, context=context)[0]
        partner_obj = self.pool.get('res.partner')
        woo_instance_obj = self.pool.get('woo.instance.ept')
        instance = woo_instance_obj.search(cr, uid, [('state', '=', 'confirmed')], limit=1)
        if instance:
            instance_obj = woo_instance_obj.browse(cr, uid, instance)
            url = instance_obj.host + "/wp-json/auth-api/v1/odoo/users/phone_number_update"
            headers = CaseInsensitiveDict()
            login_info = instance_obj.admin_username + ":" + instance_obj.admin_password
            login_info_bytes = login_info.encode('ascii')
            base64_bytes = base64.b64encode(login_info_bytes)
            headers["Authorization"] = "Basic " + base64_bytes
            headers["Content-Type"] = "application/json"
        partner_lists = context.get('active_ids', [])
        for partner in self.pool.get('res.partner').browse(cr, uid, partner_lists, context=None):
            # woo_customer_id
            if partner.woo_customer_id:
                customer_data = {}
                if partner.mobile:
                    woo_customer_id = partner.woo_customer_id.split("_")[1]
                    customer_data = '''{"user_id":"%s","update_phone":"%s"}''' % (str(woo_customer_id), str(partner.mobile))
                    customer_response = requests.post(url, headers=headers, data=customer_data)
                    if customer_response.status_code not in [200, 201]:
                        raise except_orm(_('Error'),
                                         _("Error in syncing response mobile for woo customer id %s %s") % (
                                         partner.woo_customer_id, customer_response.content,))
                else:
                    raise except_orm(_('Error'),
                                     _("Woo customer id %s doesn't have mobile to sync to woo.") % (
                                         partner.woo_customer_id,))
        return True
