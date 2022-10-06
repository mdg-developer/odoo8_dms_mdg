from openerp.osv import fields, osv
from openerp.tools import float_compare
from datetime import datetime, timedelta
import datetime
import logging

class stock_opening(osv.osv):
    _name = 'stock.opening'

    _columns = {
                'product_id': fields.many2one('product.product', 'Product'),
                'location_id': fields.many2one('stock.location', 'Location'),
                'qty': fields.float('Qty'),
                'date': fields.date('Date'),
              }

    def insert_stock_opening_data(self, cr, uid, ids=None, context=None):

        current_date = datetime.datetime.now().date()
        cr.execute(
            """SELECT (date_trunc('month', (%s - interval '1 month')::date) + interval '1 month - 1 day')::date;""",
            (current_date,))
        last_month_end_date = cr.fetchall()
        logging.warning("Check last_month_end_date: %s", last_month_end_date)
        if last_month_end_date:
            cr.execute(
                """select * from get_stock_movement_balance(%s);""",
                (last_month_end_date[0][0],))
            stock_movement_data = cr.fetchall()
            if stock_movement_data:
                for sm in stock_movement_data:
                    location_id = sm[1]
                    product_id = sm[5]
                    qty = sm[6]
                    stock_opening = self.pool.get('stock.opening').search(cr, uid, [('product_id', '=', product_id),
                                                                                   ('location_id', '=', location_id),
                                                                                   ('qty', '=', qty),
                                                                                   ('date', '=', last_month_end_date[0][0])])
                    if not stock_opening:
                        opening_data = {
                            'product_id': product_id,
                            'location_id': location_id,
                            'qty': qty,
                            'date': last_month_end_date[0][0],
                        }
                        self.pool.get('stock.opening').create(cr, uid, opening_data, context=context)