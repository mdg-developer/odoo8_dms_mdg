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

class field_audit(osv.Model):    
    
    _name = "field.audit"      
    
    _columns = {
        'name':fields.char('No'),
        'partner_id': fields.many2one('res.partner', 'Customer'),
        'customer_code': fields.char('Customer Code'),
        'outlet_type': fields.many2one('outlettype.outlettype', string="Outlet type"),
        'township_id': fields.many2one('res.township', string="Township"),
        'city_id': fields.many2one('res.city', string="City"),
        'address': fields.char(string='Address'),
        'auditor_team_id': fields.many2one('crm.case.section', string="Auditor Team Name"),
        'date': fields.datetime(string='Date'),       
        'auditor_image': fields.binary("Auditor Photo"), 
        'frequency_id':fields.many2one('plan.frequency','Frequency'),
        'class_id':fields.many2one('sale.class', 'Class'),
        'sales_channel':fields.many2one('sale.channel', 'Sale Channel'),
        'branch_id':fields.many2one('res.branch', 'Branch'),
        'sale_team_id':fields.many2one('crm.case.section', 'Sales Team'),
        'latitude':fields.float('Geo Latitude', digits=(16, 5)),
        'longitude':fields.float('Geo Longitude', digits=(16, 5)),
        'shop_image': fields.binary("Shop Font And Sales Rep"),
        'merchant_image1': fields.binary("Merchandising Photo1"), 
        'merchant_image2': fields.binary("Merchandising Photo2"), 
        'merchant_image3': fields.binary("Merchandising Photo3"), 
        'merchant_image4': fields.binary("Merchandising Photo4"), 
        'merchant_image5': fields.binary("Merchandising Photo5"), 
        'note': fields.text("Note"),         
        'line_ids': fields.one2many('field.audit.line', 'audit_id', 'Field Audit lines'),
        'total_score':fields.float('Total Score'),
        'total_missed':fields.float('Total Missed'),
        'transaction_id':fields.char(string='Transaction Id'),
    }  
    
    def create(self, cursor, user, vals, context=None):
        sequence = self.pool.get('ir.sequence').get(cursor, user,
            'field.audit.code') or '/'
        vals['name'] = sequence        
        return super(field_audit, self).create(cursor, user, vals, context=context)
    
class field_audit_line(osv.Model):

    _name = 'field.audit.line'
    
    _columns = {            
            'audit_id':fields.many2one('field.audit', 'Field Audit'),
            'sequence': fields.integer('No.'),            
            'question_id': fields.many2one('audit.question', 'In-Call Requirements'),
            'complete':fields.boolean('Complete'),
        }   
