from openerp.osv import osv, fields, expression
from openerp import api, tools, SUPERUSER_ID
import openerp.addons.decimal_precision as dp
import logging
from datetime import datetime
import datetime

class price_change(osv.osv):
    _name = "price.change"
    
    _columns = {  
        'name': fields.char('Txn', size=64, readonly=True),
        'requested_date': fields.date('Requested Date', readonly=True),
        'requested_by': fields.many2one('res.users', 'Requested By', readonly=True),
        'confirmed_by': fields.many2one('res.users', 'Confirmed By', readonly=True),
        'confirmed_date': fields.date('Confirmed Date', readonly=True),
        'sale_pricelist_id': fields.many2one('product.pricelist', 'Sale Pricelist'),
        'description': fields.text('Description'),
        'approved_by': fields.many2one('res.users', 'Approved By', readonly=True),
        'approved_date': fields.date('Approved Date', readonly=True),
        'cost_pricelist_id': fields.many2one('product.pricelist', 'Cost Pricelist'),
        'line_ids': fields.one2many('price.change.line', 'price_change_id', 'Price Change Lines'),
        'state': fields.selection([('draft', 'Draft'), ('requested', 'Requested'), ('confirmed', 'Confirmed'), ('approved', 'Approved'), ('cancelled', 'Cancelled')], 'Status'),
    }

    _order = 'id desc'
    _defaults = {
        'requested_date': fields.datetime.now,
        'state': 'draft',
    }

    def request(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'requested_date': datetime.datetime.now(),'requested_by': uid, 'state': 'requested'})

    def confirm(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'confirmed_date': datetime.datetime.now(),'confirmed_by': uid, 'state': 'confirmed'})

    def approve(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'approved_date': datetime.datetime.now(), 'approved_by': uid, 'state': 'approved'})

    def cancel(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'cancelled'})

    def retrieve(self, cr, uid, ids, context=None):

        line_obj = self.pool.get('price.change.line')
        cr.execute("""delete from price_change_line where price_change_id=%s""", (ids[0],))
        result = {}
        price_change_obj = self.pool.get('price.change')
        datas = price_change_obj.read(cr, uid, ids, ['sale_pricelist_id', 'cost_pricelist_id'], context=None)
        for data in datas:
            sale_pricelist_id = data['sale_pricelist_id'][0]
            cost_pricelist_id = data['cost_pricelist_id'][0]
            cr.execute("""select product_id,default_code,uom_ratio,report_uom_id,new_price
                        from product_pricelist_item item,product_pricelist_version ppv,product_pricelist ppl,product_product pp,product_template pt
                        where item.price_version_id=ppv.id
                        and ppv.pricelist_id=ppl.id
                        and item.product_id=pp.id
                        and pp.product_tmpl_id=pt.id
                        and item.product_uom_id=pt.report_uom_id
                        and ppl.id=%s
                        and ppv.active=true;""",
                        (sale_pricelist_id,))
            pricelist_data = cr.fetchall()
            if pricelist_data:
                for val in pricelist_data:
                    cost_price = 0
                    cr.execute("""select new_price
                                from product_pricelist_item item,product_pricelist_version ppv,product_pricelist pp
                                where item.price_version_id=ppv.id
                                and ppv.pricelist_id=pp.id
                                and pp.id=%s
                                and product_id=%s
                                and product_uom_id=%s""",
                                (cost_pricelist_id, val[0], val[3],))
                    cost_price_data = cr.fetchall()
                    if cost_price_data:
                        cost_price = cost_price_data[0][0]
                    data_id = {'product_id': val[0],
                               'product_code': val[1],
                               'uom_ratio': val[2],
                               'uom_id': val[3],
                               'current_price': val[4],
                               'cost_price': cost_price,
                               'price_change_id': ids[0],
                               }
                    line_obj.create(cr, uid, data_id, context=context)
        return result

class price_change_line(osv.osv):
    _name = "price.change.line"
    _description = "Price Change Line"

    def _cal_current_margin(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        uom_ratio = 1
        if context is None:
            context = {}
        for data in self.browse(cr, uid, ids, context=context):
            val1 = 0.0
            if data.current_price and data.cost_price:
                val1 = ((data.current_price - data.cost_price) / data.current_price) * 100
            res[data.id] = val1
        return res

    def _cal_new_margin(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        uom_ratio = 1
        if context is None:
            context = {}
        for data in self.browse(cr, uid, ids, context=context):
            val1 = 0.0
            if data.new_price and data.cost_price:
                val1 = ((data.new_price - data.cost_price) / data.new_price) * 100
            res[data.id] = val1
        return res

    _columns = {
        'price_change_id': fields.many2one('price.change', 'Price Change'),
        'product_id':fields.many2one('product.product', 'Product'),
        'product_code':fields.char('Product Code'),
        'uom_ratio': fields.char('Packing Size'),
        'uom_id':fields.many2one('product.uom', 'UOM'),
        'cost_price': fields.float('Cost Price'),
        'current_price': fields.float('Current Price'),
        'new_price': fields.float('New Price'),
        'current_margin': fields.function(_cal_current_margin, string='Current Margin(%)', type='float'),
        'new_margin': fields.function(_cal_new_margin, string='New Margin(%)', type='float'),
    }

    def create(self, cursor, user, vals, context=None):
        if vals.get('product_id'):
            product_obj = self.pool.get('product.product')
            product_obj = product_obj.browse(cursor, user, vals.get('product_id'), context=context)
            product_code = product_obj.default_code
            uom_ratio = product_obj.uom_ratio
            uom_id = product_obj.report_uom_id.id if product_obj.report_uom_id else None
            vals['product_code'] = product_code
            vals['uom_ratio'] = uom_ratio
            vals['uom_id'] = uom_id
            logging.info("Check create price_change_id: %s", vals.get('price_change_id'))
            if vals.get('price_change_id'):
                price_change_obj = self.pool.get('price.change').browse(cursor, user, vals.get('price_change_id'), context=context)
                logging.info("Check create price_change_obj: %s", price_change_obj)
                if price_change_obj:
                    sale_pricelist_id = price_change_obj.sale_pricelist_id.id
                    cost_pricelist_id = price_change_obj.cost_pricelist_id.id
                    logging.info("Check create price_change_obj.sale_pricelist_id: %s", price_change_obj.sale_pricelist_id)
                    logging.info("Check create price_change_obj.cost_pricelist_id: %s", price_change_obj.cost_pricelist_id)
                    if sale_pricelist_id:
                        cursor.execute("""select new_price
                                        from product_pricelist_item item,product_pricelist_version ppv,product_pricelist pp
                                        where item.price_version_id=ppv.id
                                        and ppv.pricelist_id=pp.id
                                        and pp.id=%s
                                        and product_id=%s
                                        and product_uom_id=%s""",
                                       (sale_pricelist_id, product_obj.id, product_obj.report_uom_id.id,))
                        current_price_data = cursor.fetchall()
                        if current_price_data:
                            current_price = current_price_data[0][0]
                            vals['current_price'] = current_price
                    if cost_pricelist_id:
                        cursor.execute("""select new_price
                                        from product_pricelist_item item,product_pricelist_version ppv,product_pricelist pp
                                        where item.price_version_id=ppv.id
                                        and ppv.pricelist_id=pp.id
                                        and pp.id=%s
                                        and product_id=%s
                                        and product_uom_id=%s""",
                                       (cost_pricelist_id, product_obj.id, product_obj.report_uom_id.id,))
                        cost_price_data = cursor.fetchall()
                        if cost_price_data:
                            cost_price = cost_price_data[0][0]
                            vals['cost_price'] = cost_price
        return super(price_change_line, self).create(cursor, user, vals, context=context)

    def write(self, cursor, user, ids, vals, context=None):
        data = self.browse(cursor, user, ids, context)
        if data.product_id:
            product_obj = data.product_id
            product_code = product_obj.default_code
            uom_ratio = product_obj.uom_ratio
            uom_id = product_obj.report_uom_id.id if product_obj.report_uom_id else None
            vals.update({'product_code': product_code,
                         'uom_ratio': uom_ratio,
                         'uom_id': uom_id,
                        })
            if data.price_change_id.sale_pricelist_id:
                cursor.execute("""select new_price
                                from product_pricelist_item item,product_pricelist_version ppv,product_pricelist pp
                                where item.price_version_id=ppv.id
                                and ppv.pricelist_id=pp.id
                                and pp.id=%s
                                and product_id=%s
                                and product_uom_id=%s""",
                                (data.price_change_id.sale_pricelist_id.id, product_obj.id, product_obj.report_uom_id.id,))
                current_price_data = cursor.fetchall()
                if current_price_data:
                    current_price = current_price_data[0][0]
                    vals['current_price'] = current_price
            if data.price_change_id.cost_pricelist_id:
                cursor.execute("""select new_price
                                from product_pricelist_item item,product_pricelist_version ppv,product_pricelist pp
                                where item.price_version_id=ppv.id
                                and ppv.pricelist_id=pp.id
                                and pp.id=%s
                                and product_id=%s
                                and product_uom_id=%s""",
                                (data.price_change_id.cost_pricelist_id.id, product_obj.id, product_obj.report_uom_id.id,))
                cost_price_data = cursor.fetchall()
                if cost_price_data:
                    cost_price = cost_price_data[0][0]
                    vals['cost_price'] = cost_price
        res = super(price_change_line, self).write(cursor, user, ids, vals, context=context)
        return res

    def onchange_product_id(self, cr, uid, ids, product_id, sale_pricelist_id, cost_pricelist_id, context=None):
        product_obj = self.pool.get('product.product')
        product_code = None
        uom_ratio = None
        uom_id = None
        current_price = 0
        cost_price = 0
        logging.info("Check onchange_product_id sale_pricelist_id: %s", sale_pricelist_id)
        if product_id and sale_pricelist_id and cost_pricelist_id:
            product_obj = product_obj.browse(cr, uid, product_id, context=context)
            product_code = product_obj.default_code
            uom_ratio = product_obj.uom_ratio
            uom_id = product_obj.report_uom_id.id if product_obj.report_uom_id else None
            cr.execute("""select new_price
                        from product_pricelist_item item,product_pricelist_version ppv,product_pricelist pp
                        where item.price_version_id=ppv.id
                        and ppv.pricelist_id=pp.id
                        and pp.id=%s
                        and product_id=%s
                        and product_uom_id=%s""",
                       (sale_pricelist_id,product_obj.id,product_obj.report_uom_id.id,))
            current_price_data = cr.fetchall()
            if current_price_data:
                current_price = current_price_data[0][0]
            cr.execute("""select new_price
                        from product_pricelist_item item,product_pricelist_version ppv,product_pricelist pp
                        where item.price_version_id=ppv.id
                        and ppv.pricelist_id=pp.id
                        and pp.id=%s
                        and product_id=%s
                        and product_uom_id=%s""",
                       (cost_pricelist_id, product_obj.id, product_obj.report_uom_id.id,))
            cost_price_data = cr.fetchall()
            if cost_price_data:
                cost_price = cost_price_data[0][0]
        return {'value': {'product_code': product_code,
                          'uom_ratio': uom_ratio,
                          'uom_id': uom_id,
                          'current_price': current_price,
                          'cost_price': cost_price,
                          }}

    