import datetime
from lxml import etree
import math
import pytz
import urlparse

import openerp
from openerp import tools, api
from openerp.osv import osv, fields
from openerp.osv.expression import get_unaccent_wrapper
from openerp.tools.translate import _





class sale_rental(osv.osv):
    
    _name = "sales.rental"
    _description = "Sales rental"
    _inherit = ['mail.thread', 'ir.needaction_mixin']    
 
    
    def _get_default_company(self, cr, uid, context=None):
        company_id = self.pool.get('res.users')._get_company(cr, uid, context=context)
        if not company_id:
            raise osv.except_osv(_('Error!'), _('There is no default company for the current user!'))
        return company_id    
    @api.depends('image')
    def _compute_images(self):
        for rec in self:
            rec.image_medium = tools.image_resize_image_medium(rec.image)
            rec.image_small = tools.image_resize_image_small(rec.image)

    def _inverse_image_medium(self):
        for rec in self:
            rec.image = tools.image_resize_image_big(rec.image_medium)

    def _inverse_image_small(self):
        for rec in self:
            rec.image = tools.image_resize_image_big(rec.image_small)   

         
    _columns = {
        'company_id':fields.many2one('res.company', 'Company'),
        'date':fields.date('Date'),
       'from_date':fields.date('From Date'),
        'to_date':fields.date('To Date'),
        'partner_id':fields.many2one('res.partner', 'Customer'  , required=True),  # 
        'name':fields.text('Description'),
        'address':fields.text('Address'),
        'month':fields.integer('Rental Month'),
        'unit':fields.selection({('day','Days'),('week','Weeks'),('month','Months'),('year','Years')},string='Unit'),
        'monthy_amt':fields.float('Monthly Cost'  , required=True),
        'total_amt':fields.float('Total Amount'  , required=True),
        'image': fields.binary("Location Photo"),
        'latitude':fields.float('Geo Latitude'),
        'longitude':fields.float('Geo Longitude'),                
  }
    _defaults = {
        'date': fields.datetime.now,
        'company_id': _get_default_company,
        'unit': 'day',
        }   
sale_rental()     
