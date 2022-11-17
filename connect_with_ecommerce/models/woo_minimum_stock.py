from openerp.osv import fields, osv
import requests
import openerp.addons.decimal_precision as dp
import logging
from datetime import datetime
import datetime
from openerp.osv.orm import BaseModel, Model, MAGIC_COLUMNS, except_orm
from openerp.tools.translate import _
from requests.structures import CaseInsensitiveDict
import base64

class woo_minimum_stock(osv.osv):
    _name = "woo.minimum.stock"

    def _get_default_branch(self, cr, uid, context=None):
        branch_id = self.pool.get('res.users')._get_branch(cr, uid, context=context)
        if not branch_id:
            raise osv.except_osv(_('Error!'), _('There is no default branch for the current user!'))
        return branch_id

    _columns = {
        'branch_id': fields.many2one('res.branch', string="Branch", required=True),
        'township_id': fields.many2one('res.township',string="Township",  required=True),
        'stock_line': fields.one2many('woo.minimum.stock.line', 'stock_line_ids',
                                      string='Minimum Stock Line', copy=True),
        'retrive_date': fields.datetime('Last Retrived On', readonly=True),
        'retrive_uid': fields.many2one('res.users', 'Last Retrived By', readonly=True)

    }

    _defaults = {
        # 'date': fields.datetime.now,
        'branch_id': _get_default_branch,

    }

    def sync_to_woo_demo(self, cr, uid, ids, context=None):
        location_ids = []

    def sync_to_woo(self, cr, uid, ids, context=None):

        record = self.browse(cr, uid, ids)[0]

        data = None
        error_msg = None
        error_log = None

        woo_instance_obj = self.pool.get('woo.instance.ept')
        instance = woo_instance_obj.search(cr, uid, [('state', '=', 'confirmed')], limit=1)
        if instance:
            instance_obj = woo_instance_obj.browse(cr, uid, instance)
            url = instance_obj.host + "/wp-json/auth-api/v1/odoo/stocks/stock_data_update"
            headers = CaseInsensitiveDict()
            login_info = instance_obj.admin_username + ":" + instance_obj.admin_password
            login_info_bytes = login_info.encode('ascii')
            base64_bytes = base64.b64encode(login_info_bytes)
            headers["Authorization"] = "Basic " + base64_bytes
            headers["Content-Type"] = "application/json"
        if record:
            p_list = []
            for line in record.stock_line:
                stock_qty = line.qty
                min_qty = line.qty
                stock_status = 'no'
                if line.oos == True:
                    stock_status = 'yes'
                product_id = self.pool.get('product.product').browse(cr, uid, line.product_id.id, context=context)
                if product_id.uom_id and product_id.product_tmpl_id.ecommerce_uom_id:
                    if product_id.uom_id.factor > product_id.product_tmpl_id.ecommerce_uom_id.factor:
                        stock_qty = line.qty / (1/product_id.product_tmpl_id.ecommerce_uom_id.factor)
                    elif line.product_id.uom_id.factor < product_id.product_tmpl_id.ecommerce_uom_id.factor:
                        stock_qty = line.qty * (1 / product_id.product_tmpl_id.ecommerce_uom_id.factor)
                p_list.append({
                        "product_sku": product_id.name,
                        "stock_qty": stock_qty,
                        "stock_status": stock_status,
                        "min_stock": stock_qty,
                        "max_stock": 20
                    })

            data = {
                    'branch_code':record.branch_id.branch_code or '',
                    'city':record.township_id.city.name or '',
                    'township' : record.township_id.name or '',
                    'product_lists':p_list
                }
            error_msg = 'json data: %s' % ([data])
            logging.error(error_msg)
        response = requests.post(url, json=[data], headers=headers, timeout=60, verify=False)

        if response.status_code == 200:
            sms_status = 'success'
            raise except_orm(_('Info'), _("Minimum Stock sync to woo success") )
        else:
            raise except_orm(_('Error'), _("'%s'") % (response.content,))

        return True


    def retrieve_data(self, cr, uid, ids, context=None):
        location_ids = []
        if ids:
            min_id = ids[0]
            cr.execute("delete from woo_minimum_stock_line where stock_line_ids =%s",
                           (min_id,))
            min_stock = self.pool.get('woo.minimum.stock')
            min_stock_id = min_stock.browse(cr, uid, min_id, context=context)
            if min_stock_id.branch_id:
                cr.execute('''select lot_stock_id
                            from res_branch rb,stock_warehouse sw
                            where rb.id=sw.branch_id
                            and rb.active=true
                            and rb.id=%s
                            and main_location=true''', (min_stock_id.branch_id.id,))
                location_record = cr.fetchall()
                if location_record:
                    for loc in location_record:
                        location_ids.append(loc[0])
                    logging.warning("Check location for out of stock: %s", location_ids)
                    if location_ids:
                        cr.execute('''select A.id ,A.uom_id,B.qty,case when B.qty is null or B.qty = 0 then 'Out of Stock' ELSE 'Available Stock' end as label
                                    from
                                    (   select pp.id,pt.ecommerce_uom_id uom_id
                                        from product_product pp,product_template pt
                                        where pp.product_tmpl_id=pt.id
                                        and pp.active=true
                                        and pt.active=true
                                        and type!='service'
                                        and default_code is not null     
                                    )A
                                    left join
                                    (
                                        select COALESCE(sum(qty),0) qty,pp.id
                                        from stock_quant sq,product_product pp,product_template pt
                                        where sq.product_id=pp.id
                                        and pp.product_tmpl_id=pt.id
                                        and location_id in %s
                                        group by pp.id
                                    )B on (A.id=B.id)
                                    where qty is not null or qty <> 0 ''', (tuple(location_ids),))
                        product_record = cr.dictfetchall()
                        if product_record:
                            for product in product_record:
                                value = {
                                    'stock_line_ids': min_id,
                                    'product_id': product['id'],
                                    'uom_id': product['uom_id'],
                                    'qty': product['qty']

                                }
                                self.pool.get('woo.minimum.stock.line').create(cr, uid, value, context=context)
            self.write(cr, uid, ids, {'retrive_date': datetime.datetime.now(),'retrive_uid':uid}, context=context)

        return True

woo_minimum_stock()


class woo_minimum_stock_line(osv.osv):
    _name = 'woo.minimum.stock.line'

    _columns = {
        'stock_line_ids': fields.many2one('woo.minimum.stock', 'Minimum Stock'),
        'product_id': fields.many2one('product.product', "Product"),
        #'uom_id': fields.many2one('uom.uom', "UOM"),
        'uom_id': fields.related('product_id', 'ecommerce_uom_id', type='many2one', string='UOM',
                                           readonly=True, relation="product.uom"),
        'qty': fields.float('Quantity', digits_compute=dp.get_precision('Product Price')),
        'oos': fields.boolean('OOS', default=False)

    }




woo_minimum_stock_line()
