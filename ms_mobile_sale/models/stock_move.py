from openerp.osv import fields, osv

class stock_move(osv.osv):
    _inherit = 'stock.move'
    _columns = {
                    'date': fields.datetime('Imported Date', required=True, select=True, help="Move date: scheduled date until move is done, then date of actual move processing", states={'done': [('readonly', True)]}),
                    'date_expected': fields.datetime('Transferred Date', states={'done': [('readonly', True)]}, required=True, select=True,
                                                     help="Scheduled date for the processing of this move"),
                    'issue':fields.char('Issue No'),
                }

stock_move()
