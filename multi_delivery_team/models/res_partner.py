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
                'delivery_team_id': fields.many2one('crm.case.section', 'Delivery Team'),
                    } 
    
class unassign_delivery_team(osv.osv_memory):
    _name = 'partner.unassign.delivery.team'
    _description = 'Unassign Delivery Team'
    _columns = {
        'confirm':fields.boolean('Confirm' ,readonly=True),
    }

    _defaults = {
         'confirm': True,                  
    }

    def print_report(self, cr, uid, ids, context=None):
        data = self.read(cr, uid, ids, context=context)[0]
        partner_obj = self.pool.get('res.partner')
        datas = {
             'ids': context.get('active_ids', []),
             'model': 'res.partner',
             'form': data
            }
        partner_id=datas['ids']
        confirm=data['confirm']
        for partner in partner_id: 
            if (confirm==True):
                cr.execute('update res_partner set delivery_team_id=null where id=%s',(partner,))      
        return True
    
class unassign_customer_tag(osv.osv_memory):
    _name = 'partner.unassign.customer.tag'
    _description = 'Unassign Delivery Team'
    _columns = {
        'confirm':fields.boolean('Confirm' ,readonly=True),
    }

    _defaults = {
         'confirm': True,                  
    }

    def print_report(self, cr, uid, ids, context=None):
        data = self.read(cr, uid, ids, context=context)[0]
        partner_obj = self.pool.get('res.partner')
        datas = {
             'ids': context.get('active_ids', []),
             'model': 'res.partner',
             'form': data
            }
        partner_id=datas['ids']
        confirm=data['confirm']
        for partner in partner_id: 
            if (confirm==True):
                cr.execute('delete from res_partner_res_partner_category_rel where  partner_id=%s',(partner,))      
        return True
                                                                                                     