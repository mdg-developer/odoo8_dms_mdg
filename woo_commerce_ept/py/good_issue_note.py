import time

import os
from datetime import datetime
from datetime import timedelta  
from dateutil.relativedelta import relativedelta
from dateutil import parser
import time
from openerp.osv import fields , osv
from openerp.tools.translate import _
import datetime
import math

class good_issue_note(osv.osv):
    _inherit = "good.issue.note"
    
    def issue(self, cr, uid, ids, context=None):
        
        res = super(good_issue_note, self).issue(cr, uid, ids, context=context)
        for gin in self.browse(cr, uid, ids, context=context):
            requisition_obj = self.pool.get('stock.requisition').search(cr, uid, [('good_issue_id', '=', gin.id)])
            for req in self.pool.get('stock.requisition').browse(cr, uid, requisition_obj, context=context):
                for requisition in req.order_line:
                    sale_order_obj = self.pool.get('sale.order').search(cr, uid, [('name', '=', requisition.name)])
                    sale_order = self.pool.get('sale.order').browse(cr, uid, sale_order_obj, context=context)
                    if sale_order.woo_order_number:
                        one_signal_values = {
                                             'partner_id': sale_order.partner_id.id,
                                             'contents': "Your order " + sale_order.name + " is on the way.",
                                             'headings': "Burmart"
                                            }   
                        print 'one_signal_values',one_signal_values
                        self.pool.get('one.signal.notification.messages').create(cr, uid, one_signal_values, context=context)    
        return res
     
        