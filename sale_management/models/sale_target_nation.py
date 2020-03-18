from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
from openerp import tools
import time
from dateutil.relativedelta import relativedelta
from datetime import datetime
import datetime
from openerp.exceptions import except_orm, Warning, RedirectWarning
from openerp.tools.translate import _


class sale_target_nation(osv.osv):
    _name = "sales.target.nation"
    _description = "Sales Target Nation"

    def on_change_pricelist(self, cr, uid, ids,  pricelist_id, context=None):
        values = {}
        data_line = []
        cr.execute("select pp.id from product_product pp ,product_template pt  where pp.product_tmpl_id=pt.id and pt.is_foc!=True and pt.type != 'service' and pt.active=True and pt.sale_ok=True ")
        product_line=cr.fetchall()
        print 'product_line ', product_line

        for line in product_line:
            product = self.pool.get('product.product').browse(cr, uid, line, context=context)
            if product.product_tmpl_id.type != 'service' and product.is_foc != True:
                cr.execute(
                    "select new_price from product_pricelist_item where price_version_id in ( select id from product_pricelist_version where pricelist_id=%s and active=True) and product_id=%s and product_uom_id=%s",
                    (pricelist_id, product.id, product.product_tmpl_id.report_uom_id.id,))
                product_price = cr.fetchone()
                if product_price:
                    product_price = product_price[0]
                else:
                    raise osv.except_osv(_('Warning'),
                                         _('Please Check Price List For (%s)') % (product.name_template,))
                sequence = product.sequence
                data_line.append({'product_id': line,
                                  'product_uom': product.product_tmpl_id.report_uom_id and product.product_tmpl_id.report_uom_id.id or False,
                                  'price_unit': product_price,
                                  'product_uom_qty': 0.0,
                                  'sequence': sequence,
                                  })
        values = {
            'target_line': data_line,
        }
        return {'value': values}

    def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
        res = dict.fromkeys(ids, 0.0)
        for order in self.browse(cr, uid, ids, context=context):
            val1 = 0.0
            for line in order.target_line:
                val1 += line.price_subtotal
            res[order.id] = val1
        return res

    def _default_date(self, cr, uid, ids, context=None):
        now = datetime.datetime.now()
        year = now.year
        month = now.month
        return time.strftime('%Y-%m-01')

    _columns = {
        'name': fields.char('Description'),
        'month': fields.selection([
            ('01', 'January'),
            ('02', 'February'),
            ('03', 'March'),
            ('04', 'April'),
            ('05', 'May'),
            ('06', 'June'),
            ('07', 'July'),
            ('08', 'August'),
            ('09', 'September'),
            ('10', 'October'),
            ('11', 'November'),
            ('12', 'December'),

        ], 'Month', copy=False, select=True),
        'target_line': fields.one2many('sales.target.nation.line', 'sale_ids', string='Sale Target Nation Line', copy=True),
        'description': fields.text('Description'),
        'date': fields.date('Target Date'),
        'year': fields.char('Year'),
        'amount_total': fields.function(_amount_all, string='Total Value',
                                        digits_compute=dp.get_precision('Product Price'), store=True),
        'company_id': fields.many2one('res.company', 'Company', required=True, readonly=True),
        'pricelist_id': fields.many2one('product.pricelist', 'Price list', required=True),

    }
    _defaults = {
        'date': _default_date,
        'month': lambda *a: str(time.strftime('%m')),
        'year': lambda *a: str(time.strftime('%Y')),
         'pricelist_id':1,  
        'company_id': lambda self, cr, uid, context: self.pool.get('res.company')._company_default_get(cr, uid,
                                                                                                       'sales.target',
                                                                                                       context=context),
    }


sale_target_nation()


class sale_target_nation_line(osv.osv):
    _name = 'sales.target.nation.line'

    def create(self, cr, uid, values, context=None):
        if values.get('sale_ids') and values.get('product_id'):
            order = self.pool['sales.target.nation'].read(cr, uid, values['sale_ids'], ['pricelist_id'], context=context)
            defaults = self.on_change_product_id(cr, uid, [], values['product_id'], order['pricelist_id'][0],
                                                 context=dict(context or {}))['value']
            values = dict(defaults, **values)

        return super(sale_target_nation_line, self).create(cr, uid, values, context=context)

    def _amount_line(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        if context is None:
            context = {}
        for line in self.browse(cr, uid, ids, context=context):
            price = line.price_unit * line.product_uom_qty
            res[line.id] = price
        return res

    def on_change_product_id(self, cr, uid, ids, product_id, pricelist_id, context=None):
        values = {}
        if not pricelist_id:
            raise except_orm(_('No PriceList!'), _('Please Insert PriceList.'))
        if product_id and pricelist_id:
            product = self.pool.get('product.product').browse(cr, uid, product_id, context=context)
            if product.product_tmpl_id.type != 'service' and product.is_foc != True:
                cr.execute(
                    "select new_price from product_pricelist_item where price_version_id in ( select id from product_pricelist_version where pricelist_id=%s and active=True) and product_id=%s and product_uom_id=%s",
                    (pricelist_id, product.id, product.product_tmpl_id.report_uom_id.id,))
                product_price = cr.fetchone()[0]
                sequence = product.sequence
                values = {
                    'product_uom': product.product_tmpl_id.report_uom_id and product.product_tmpl_id.report_uom_id.id or False,
                    'price_unit': product_price,
                    'sequence': sequence,

                }
        return {'value': values}

    def on_change_product_uom_qty(self, cr, uid, ids, product_id, product_uom_qty, pricelist_id, context=None):
        values = {}
        if product_uom_qty and pricelist_id:
            product = self.pool.get('product.product').browse(cr, uid, product_id, context=context)
            cr.execute(
                "select new_price from product_pricelist_item where price_version_id in ( select id from product_pricelist_version where pricelist_id=%s and active=True) and product_id=%s and product_uom_id=%s",
                (pricelist_id, product.id, product.product_tmpl_id.report_uom_id.id,))
            product_price = cr.fetchone()[0]
            if product.product_tmpl_id.type != 'service' and product.is_foc != True:
                values = {
                    'price_subtotal': product_uom_qty * product_price,
                }
        return {'value': values}

    _columns = {
        'sale_ids': fields.many2one('sales.target.nation', 'Sales Target Nation'),
        'sequence': fields.integer('Sequence'),
        'product_id': fields.many2one('product.product', 'Product SKU', required=True),
        'product_uom': fields.many2one('product.uom', 'UoM', readonly=True),
        'product_uom_qty': fields.float('QTY', required=True),
        'price_unit': fields.float('Unit Price', required=True, readonly=True,
                                   digits_compute=dp.get_precision('Product Price')),
        'price_subtotal': fields.function(_amount_line, string='Amount',
                                          digits_compute=dp.get_precision('Product Price'), type='float', ),
        'distribution_price': fields.integer('Distribution'),

    }


sale_target_nation()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:


