'''
Created on Jun 12, 2015

@author: Administrator
'''

import re
import time
from openerp import netsvc
from openerp.osv import orm,fields, osv
import openerp.addons.decimal_precision as dp
from datetime import datetime
from openerp.tools import float_round, float_is_zero, float_compare
from dateutil.relativedelta import relativedelta
from operator import attrgetter
from openerp.osv import fields, osv
from decimal import *
from openerp.tools import config
from openerp.tools.translate import _
from openerp.osv.orm import except_orm,browse_record

CURRENCY_DISPLAY_PATTERN = re.compile(r'(\w+)\s*(?:\((.*)\))?')
class account_journal(osv.osv):
    _inherit = 'account.journal'
    _columns = {      
                'update_currency':fields.boolean('Enable Update Currency'),
              }
account_journal()

class res_currency(osv.osv):
    _inherit = 'res.currency'
    def rate_compute(self, cr, uid,to_currency, from_amount, rate, rouding=True, context=None):
        getcontext().prec = to_currency.accuracy
        result =  Decimal(1)/Decimal(rate) * Decimal(from_amount)
        if rouding:
            return round(result,to_currency.accuracy)
        return result
res_currency()
   
class res_currency_rate(osv.osv):
    _inherit = "res.currency.rate"
    _description = "Currency Rate"

    _columns = {
        'rate': fields.float('(/)Rate',
#digits=(12, 18), 
            digits_compute=dp.get_precision('Currency_Rate'),help='The rate of the currency to the currency of rate 1'),
        'multi_rate': fields.float('(*)Rate', digits=(12, 6), help='The rate of the currency to the currency of rate multiple'),
    }
    
    
    _defaults = {
        'name': lambda *a: time.strftime('%Y-%m-%d 00:00:00'),
    }
    
    def on_change_rate(self,cr,uid,ids,rate,context=None):
        if rate:
            return {'value': {'rate': 1/rate}}
        
    _order = "name desc"

res_currency_rate()
class account_move(osv.osv):
    _inherit = 'account.move'
    _columns = {      
                'update_currency_disable':fields.boolean('Currency Rate Update Disable'),
              }
    
class currency_rate_update(osv.osv):
    _name = "currency.rate.update"
    _description = "Currency Rate Update"
    # _order = "id desc"
    
    _columns = {
        'name': fields.char('Name', required=True),
        'from_date' : fields.date('From Date', required=True),
        'to_date' : fields.date('To Date', required=True),
        'state': fields.selection([
            ('draft', 'Draft'),
            ('done', 'Success'),
            ('fail', 'Failed'),
            ], 'Status', readonly=True, copy=False, help="Gives the status of the quotation or sales order.\
              \nThe exception status is automatically set when a cancel operation occurs \
              in the invoice validation (Invoice Exception) or in the picking list process (Shipping Exception).\nThe 'Waiting Schedule' status is set when the invoice is confirmed\
               but waiting for the scheduler to run on the order date.", select=True),
       'currency_id': fields.many2one('res.currency', 'Currency'),
        'rate':fields.integer('Rate', required=True),
    }
    _defaults = {
        'state': 'draft',
        }
    
    def currency_rate_update(self, cr, uid, ids, context=None):
        data = self.browse(cr, uid, ids)[0]
        from_date = data.from_date
        to_date = data.to_date
        account_journal_obj = self.pool.get('account.journal')
        account_move_obj = self.pool.get('account.move')
        currency_obj = self.pool.get('res.currency')
        account_move_line_obj = self.pool.get('account.move.line')
	account_move_ids=res =None
        account_journal_ids  = account_journal_obj.search(cr,uid,[('update_currency','=',True),('currency','=',data.currency_id.id)])
        print 'this is journal',account_journal_ids
        if account_journal_ids:
            account_move_ids  = account_move_obj.search(cr,uid,['&',('journal_id','in',account_journal_ids),
                                                                ('state','!=','posted'),
                                                                ('update_currency_disable','=',False),
                                                                ('date','>=',from_date),
                                                                ('date','<=',to_date),
                                                                ])
#             print 'account_move_ids',account_move_ids
        rate = data.rate
#         print 'this is rate',rate
        converted_currency = currency_obj.browse(cr,uid,data.currency_id.id,context)
        converted_cur=converted_currency.id
        con_cur=converted_cur*1.0
#         print 'con_cur',con_cur
#         print 'converted_currency',converted_currency.id
#         print 'account_move_ids',account_move_ids
        if account_move_ids:
            for account_move_id in account_move_ids:
                line_ids = account_move_line_obj.search(cr,uid,[('move_id','=',account_move_id)])
                for line_id in line_ids:
                    print 'line_id',line_id
                    line = account_move_line_obj.browse(cr,uid,line_id,context)
                    curr_amount = line.amount_currency
                    print 'this is curr_amount',curr_amount
                    if account_move_id:
                        if curr_amount is not None and curr_amount != 0 :
                            value = {}
                            #amount = con_cur.round((1/rate) * curr_amount)
                            #amount = round((1/rate) * curr_amount)
                            # def compute(self, cr, uid,to_currency, from_amount, rate, round=True, context=None):
                            amount =  currency_obj.rate_compute(cr,uid,converted_currency,curr_amount, rate, True,context)
                            print 'this is amount',amount
                            type = 'dr'
                            
                                
                            if curr_amount < 0:
                                type = 'cr'
            
                            if (type=='dr'):
                                value['debit'] = abs(amount)
                                print 'This is debit amount', line['debit']
                            if (type== 'cr'):
                                value['credit'] = abs(amount)
                                print 'This is credit amount', line['credit'] 
                            value['currency_rate'] = rate
                            print 'line',line
                            res=account_move_line_obj.write(cr,uid,[line_id],value)
                self.write(cr, uid, [ids[0]], {'state': 'done',})  
        else:
            raise except_orm(_('Alert!:'),_("There is no Journal Entry."))
        return res

    
    
