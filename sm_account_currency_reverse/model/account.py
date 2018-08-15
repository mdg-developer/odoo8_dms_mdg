
from openerp.exceptions import ValidationError, RedirectWarning, except_orm

from openerp import models, fields, api, _
import openerp.addons.decimal_precision as dp
from openerp.tools import float_compare
import logging
_log = logging.getLogger(__name__)

class res_currency(models.Model):
    _inherit = "res.currency"
  
    sm_reverse_rate = fields.Boolean(string='Reverse Rate')
    rate_new = fields.Float(compute='_compute_current_rate_new', string='Current Rate', digits=(12, 6),
                        help='The rate of the currency to the currency of rate 1.') 
    rate = fields.Float(compute='_compute_current_rate', string='Current Rate', digits=(12, 15),
                        help='The rate of the currency to the currency of rate 1.')
    
#     @api.multi
#     def _compute_current_rate(self):
#         date = self._context.get('date') or fields.Date.today()
#         company_id = self._context.get('company_id') or self.env['res.users']._get_company().id
#         # the subquery selects the last rate before 'date' for the given currency/company
#         query = """SELECT c.id, (SELECT r.rate FROM res_currency_rate r
#                                   WHERE r.currency_id = c.id AND r.name <= %s
#                                     AND (r.company_id IS NULL OR r.company_id = %s)
#                                ORDER BY r.company_id, r.name DESC
#                                   LIMIT 1) AS rate
#                    FROM res_currency c
#                    WHERE c.id IN %s"""
#         self._cr.execute(query, (date, company_id, tuple(self.ids)))
#         currency_rates = dict(self._cr.fetchall())
#         for currency in self:
#             currency.rate = currency_rates.get(currency.id) or 1.0
            
    @api.multi
    def _compute_current_rate_new(self):
        date = self._context.get('date') or fields.Date.today()
        company_id = self._context.get('company_id') or self.env['res.users']._get_company()
        # the subquery selects the last rate before 'date' for the given currency/company
#         query = """SELECT c.id, (SELECT r.rate_new FROM res_currency_rate r
#                                   WHERE r.currency_id = c.id AND r.name <= %s
#                                     AND (r.company_id IS NULL OR r.company_id = %s)
#                                ORDER BY r.company_id, r.name DESC
#                                   LIMIT 1) AS rate
#                    FROM res_currency c
#                    WHERE c.id IN %s"""
#         self._cr.execute(query, (date, company_id, tuple(self.ids)))
#         currency_rates = self._cr.fetchall()
#         if currency_rates:
        for currency in self:
            query = """SELECT c.id, (SELECT r.rate_new FROM res_currency_rate r
                                  WHERE r.currency_id = c.id AND r.name <= %s
                                    
                               ORDER BY r.name DESC
                                  LIMIT 1) AS rate
                   FROM res_currency c
                   WHERE c.id = %s"""
            self._cr.execute(query, (date,  currency.id))
            currency_rates = self._cr.fetchall()
            if currency_rates:
                
                
                currency.rate_new = currency_rates[0][1] or 1.0
                #currency.rate_new = currency_rates.get(currency.id) or 1.0
    @api.multi
    def _compute_current_rate(self):
        date = self._context.get('date') or fields.Date.today()
        company_id = self._context.get('company_id') or self.env['res.users']._get_company()#.id
        # the subquery selects the last rate before 'date' for the given currency/company
        query = """SELECT c.id, (SELECT r.rate FROM res_currency_rate r
                                  WHERE r.currency_id = c.id AND r.name <= %s                                   
                               ORDER BY r.name DESC
                                  LIMIT 1) AS rate
                   FROM res_currency c
                   WHERE c.id IN %s"""
        self._cr.execute(query, (date, tuple(self.ids)))
        currency_rates = dict(self._cr.fetchall())
        for currency in self:
            currency.rate = currency_rates.get(currency.id) or 1.0
            
#     def _get_conversion_rate(self,from_currency, to_currency):
#         _log.info ('currrrrrrrrrrrr')
#         if self._context is None:
#             context = {}
#         ctx = self._context.copy()
#         from_currency = self.browse(from_currency.id)
#         to_currency = self.browse(to_currency.id)
# 
#         if from_currency.rate == 0 or to_currency.rate == 0:
#             date = context.get('date', time.strftime('%Y-%m-%d'))
#             if from_currency.rate == 0:
#                 currency_symbol = from_currency.symbol
#             else:
#                 currency_symbol = to_currency.symbol
#             raise osv.except_osv(_('Error'), _('No rate found \n' \
#                     'for the currency: %s \n' \
#                     'at the date: %s') % (currency_symbol, date))
#         if to_currency and to_currency.sm_reverse_rate:
#             return from_currency.rate/to_currency.rate
#         else:
#             return to_currency.rate/from_currency.rate
