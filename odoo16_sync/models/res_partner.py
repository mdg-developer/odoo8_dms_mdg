from openerp.osv import fields, osv
from openerp import tools
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
import calendar
from datetime import datetime
import time
from datetime import date
from dateutil import relativedelta

class res_partner(osv.osv):

    _inherit = 'res.partner'    
    _columns = {  
                'sd_customer': fields.boolean('Sub D' , default=False),
            }    
    
    def on_change_sub_d_customer(self,cr,user,ids,sd_customer,context=None):
        
        res = {}
        if sd_customer == True:
            warning_msgs = _("Your customer will be Sub D customer ! ")
            if warning_msgs:
                warning = {
                           'title': _('Warning!'),
                           'message' : warning_msgs
                        }
            res.update({'warning': warning})
        return res