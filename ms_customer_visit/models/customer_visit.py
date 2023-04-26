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
import requests
import logging

_logger = logging.getLogger(__name__)
baseUrlPrefix = "https://firebasestorage.googleapis.com/v0/b/odoo-8d694.appspot.com/o/finewine_customer_visit%2F"
baseUrlPostFix = ".png?alt=media"
class customer_visit(osv.osv):
    _name = "customer.visit"
    _description = "Customer Visit"

    _columns = {       
        'customer_id':fields.many2one('res.partner', 'Customer', domain="[('customer','=',True)]"),
        'customer_code':fields.char('Customer Code'),
        'user_id':fields.many2one('res.users', 'Salesman Name'),
        'sale_plan_day_id':fields.many2one('sale.plan.day', 'Sale Plan Day'),
        'sale_plan_trip_id':fields.many2one('sale.plan.trip', 'Sale Plan Trip'),
        'tablet_id':fields.many2one('tablets.information', 'Tablet ID'),
        'latitude':fields.float('Geo Latitude', digits=(16, 5), readonly=True),
        'longitude':fields.float('Geo Longitude', digits=(16, 5), readonly=True),
       'sale_team_id':fields.many2one('crm.case.section', 'Sale Team'),
       'date':fields.datetime('Date'),
        'visit_reason':fields.selection([
                ('no_authorized_person', 'No Authorized Person'),
                ('buyer_rejected', 'Buyer Rejected'),
                ('shop_closed', 'Shop Closed'),
                ('Sold', 'Sold'),
                ('has_sufficient_stock_holding_for_all_listed_skus', 'Has sufficient stock holding for ALL listed SKUs'),
                ('other_reason', 'Other Reasons'),
            ], 'Reason'),
                'other_reason':fields.text('Remark'),
        'm_status':fields.selection([('pending', 'Pending'), ('approved', 'Approved'),
                                                      ('reject', 'Reject')], string='Status'),
        'state': fields.selection([('pending', 'Pending'), ('approved', 'Validate'),
                                   ('reject', 'Reject')], string='Status'),
        'branch_id': fields.many2one('res.branch', 'Branch',required=True),
    'distance_status':fields.char('Distance Status', readonly=True),
        'township_id': fields.related(
                   'customer_id', 'township',
                   type='many2one',
                   relation='res.township',
                   string="Township",store=True),  
        'is_sync':fields.boolean('Is Sync', default=False),    
        'image1_reference':fields.char('Image1 Reference'),
        'image2_reference':fields.char('Image2 Reference'),
        'image3_reference':fields.char('Image3 Reference'),
        'image4_reference':fields.char('Image4 Reference'),
        'image5_reference':fields.char('Image5 Reference'),
        'visit_image_ids': fields.many2many('customer.visit.images', 'customer_visit_images_rel', 'customer_visit_id','visit_image_id', string="Customer Images Many2Many"),
        'is_image1':fields.boolean('Is Image1', default=False),   
        'is_image2':fields.boolean('Is Image2', default=False),    
        'is_image3':fields.boolean('Is Image3', default=False),    
        'is_image4':fields.boolean('Is Image4', default=False),    
        'is_image5':fields.boolean('Is Image5', default=False),
        'rejected_by': fields.many2one('res.users', "Rejected By"),
        'validated_by': fields.many2one('res.users', "Validated By"),
        'rejected_date': fields.datetime('Rejected Date'),
        'validated_date': fields.datetime('Validated Date'),
        'visit_reason_id': fields.many2one('visit.reason', 'Visit Reason', required=True),
 
    }
    _defaults = {        
        'm_status' : 'pending',
        'state': 'pending'
    } 
    # image: all image fields are base64 encoded and PIL-supported
    image = openerp.fields.Binary("Image", attachment=True,
        help="This field holds the image used as avatar for this contact, limited to 1024x1024px",
        default=lambda self: self._get_default_image(False, True))   
    image_medium = openerp.fields.Binary("Medium-sized image",
        compute='_compute_images', inverse='_inverse_image_medium', store=True, attachment=True,
        help="Medium-sized image of this contact. It is automatically "\
             "resized as a 128x128px image, with aspect ratio preserved. "\
             "Use this field in form views or some kanban views.")
    image_small = openerp.fields.Binary("Small-sized image",
        compute='_compute_images', inverse='_inverse_image_small', store=True, attachment=True,
        help="Small-sized image of this contact. It is automatically "\
             "resized as a 64x64px image, with aspect ratio preserved. "\
             "Use this field anywhere a small image is required.")
    # each image must have it's image_medium and image_small
    image1 = openerp.fields.Binary("Image", attachment=True,
        help="This field holds the image used as avatar for this contact, limited to 1024x1024px",
        default=lambda self: self._get_default_image1(False, True))   
    image_medium1 = openerp.fields.Binary("Medium-sized image",
        compute='_compute_images1', inverse='_inverse_image_medium1', store=True, attachment=True,
        help="Medium-sized image of this contact. It is automatically "\
             "resized as a 128x128px image, with aspect ratio preserved. "\
             "Use this field in form views or some kanban views.")
    image_small1 = openerp.fields.Binary("Small-sized image",
        compute='_compute_images1', inverse='_inverse_image_small1', store=True, attachment=True,
        help="Small-sized image of this contact. It is automatically "\
             "resized as a 64x64px image, with aspect ratio preserved. "\
             "Use this field anywhere a small image is required.")
    # each image must have it's image_medium and image_small
    image2 = openerp.fields.Binary("Image", attachment=True,
        help="This field holds the image used as avatar for this contact, limited to 1024x1024px",
        default=lambda self: self._get_default_image2(False, True))   
    image_medium2 = openerp.fields.Binary("Medium-sized image",
        compute='_compute_images2', inverse='_inverse_image_medium2', store=True, attachment=True,
        help="Medium-sized image of this contact. It is automatically "\
             "resized as a 128x128px image, with aspect ratio preserved. "\
             "Use this field in form views or some kanban views.")
    image_small2 = openerp.fields.Binary("Small-sized image",
        compute='_compute_images2', inverse='_inverse_image_small2', store=True, attachment=True,
        help="Small-sized image of this contact. It is automatically "\
             "resized as a 64x64px image, with aspect ratio preserved. "\
             "Use this field anywhere a small image is required.")
    # each image must have it's image_medium and image_small
    image3 = openerp.fields.Binary("Image", attachment=True,
        help="This field holds the image used as avatar for this contact, limited to 1024x1024px",
        default=lambda self: self._get_default_image3(False, True))   
    image_medium3 = openerp.fields.Binary("Medium-sized image",
        compute='_compute_images3', inverse='_inverse_image_medium3', store=True, attachment=True,
        help="Medium-sized image of this contact. It is automatically "\
             "resized as a 128x128px image, with aspect ratio preserved. "\
             "Use this field in form views or some kanban views.")
    image_small3 = openerp.fields.Binary("Small-sized image",
        compute='_compute_images3', inverse='_inverse_image_small3', store=True, attachment=True,
        help="Small-sized image of this contact. It is automatically "\
             "resized as a 64x64px image, with aspect ratio preserved. "\
             "Use this field anywhere a small image is required.")
    # each image must have it's image_medium and image_small
    image4 = openerp.fields.Binary("Image", attachment=True,
        help="This field holds the image used as avatar for this contact, limited to 1024x1024px",
        default=lambda self: self._get_default_image4(False, True))
    image_medium4 = openerp.fields.Binary("Medium-sized image",
        compute='_compute_images4', inverse='_inverse_image_medium4', store=True, attachment=True,
        help="Medium-sized image of this contact. It is automatically "\
             "resized as a 128x128px image, with aspect ratio preserved. "\
             "Use this field in form views or some kanban views.")
    image_small4 = openerp.fields.Binary("Small-sized image",
        compute='_compute_images4', inverse='_inverse_image_small4', store=True, attachment=True,
        help="Small-sized image of this contact. It is automatically "\
             "resized as a 64x64px image, with aspect ratio preserved. "\
             "Use this field anywhere a small image is required.")

    image5 = openerp.fields.Binary("Image", attachment=True,
        help="This field holds the image used as avatar for this contact, limited to 1024x1024px")
    image_medium5 = openerp.fields.Binary("Medium-sized image",
        compute='_compute_images5', inverse='_inverse_image_medium5', store=True, attachment=True,
        help="Medium-sized image of this contact. It is automatically "\
             "resized as a 128x128px image, with aspect ratio preserved. "\
             "Use this field in form views or some kanban views.")
    image_small5 = openerp.fields.Binary("Small-sized image",
        compute='_compute_images5', inverse='_inverse_image_small5', store=True, attachment=True,
        help="Small-sized image of this contact. It is automatically "\
             "resized as a 64x64px image, with aspect ratio preserved. "\
             "Use this field anywhere a small image is required.")

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
            
#     def main_val(self,cr,uid,ids,context=None):
#      if context is None:
#          context = {}
    # your logic will set over  hear
    
    # def method_name(self):
     #   print 'coming method name'
     #   view_id = self.env.ref('modul_name._id_of_form_view').id
     #   context = self._context.copy()

# image1
    @api.depends('image1')
    def _compute_images1(self):
        for rec in self:
            rec.image_medium1 = tools.image_resize_image_medium(rec.image1)
            rec.image_small1 = tools.image_resize_image_small(rec.image1)

    def _inverse_image_medium1(self):
        for rec in self:
            rec.image1 = tools.image_resize_image_big(rec.image_medium1)

    def _inverse_image_small1(self):
        for rec in self:
            rec.image1 = tools.image_resize_image_big(rec.image_small1)
            
# image2
    @api.depends('image2')
    def _compute_images2(self):
        for rec in self:
            rec.image_medium2 = tools.image_resize_image_medium(rec.image2)
            rec.image_small2 = tools.image_resize_image_small(rec.image2)

    def _inverse_image_medium2(self):
        for rec in self:
            rec.image2 = tools.image_resize_image_big(rec.image_medium2)

    def _inverse_image_small2(self):
        for rec in self:
            rec.image2 = tools.image_resize_image_big(rec.image_small2)
            
# image3
    @api.depends('image3')
    def _compute_images3(self):
        for rec in self:
            rec.image_medium3 = tools.image_resize_image_medium(rec.image3)
            rec.image_small3 = tools.image_resize_image_small(rec.image3)

    def _inverse_image_medium3(self):
        for rec in self:
            rec.image3 = tools.image_resize_image_big(rec.image_medium3)

    def _inverse_image_small3(self):
        for rec in self:
            rec.image3 = tools.image_resize_image_big(rec.image_small3)
            
# image4
    @api.depends('image4')
    def _compute_images4(self):
        for rec in self:
            rec.image_medium4 = tools.image_resize_image_medium(rec.image4)
            rec.image_small4 = tools.image_resize_image_small(rec.image4)

    def _inverse_image_medium4(self):
        for rec in self:
            rec.image4 = tools.image_resize_image_big(rec.image_medium4)

    def _inverse_image_small4(self):
        for rec in self:
            rec.image4 = tools.image_resize_image_big(rec.image_small4)

# image5
    @api.depends('image5')
    def _compute_images5(self):
        for rec in self:
            rec.image_medium5 = tools.image_resize_image_medium(rec.image5)
            rec.image_small5 = tools.image_resize_image_small(rec.image5)

    def _inverse_image_medium5(self):
        for rec in self:
            rec.image5 = tools.image_resize_image_big(rec.image_medium5)

    def _inverse_image_small5(self):
        for rec in self:
            rec.image5 = tools.image_resize_image_big(rec.image_small5)


    def go_image1(self, cr, uid, ids, context=None):
        result =  {
                  'name'     : 'Show Image1',
                  'res_model': 'ir.actions.act_url',
                  'type'     : 'ir.actions.act_url',
                  'target'   : 'new',
               }
        for record in self.browse(cr,uid,ids,context=context):
            result['url'] = baseUrlPrefix + record.image1_reference + baseUrlPostFix
            
        return result
    
    def go_image2(self, cr, uid, ids, context=None):
        result =  {
                  'name'     : 'Show Image2',
                  'res_model': 'ir.actions.act_url',
                  'type'     : 'ir.actions.act_url',
                  'target'   : 'new',
               }
        for record in self.browse(cr,uid,ids,context=context):
            result['url'] = baseUrlPrefix + record.image2_reference + baseUrlPostFix
            
        return result
    
    def go_image3(self, cr, uid, ids, context=None):
        result =  {
                  'name'     : 'Show Image3',
                  'res_model': 'ir.actions.act_url',
                  'type'     : 'ir.actions.act_url',
                  'target'   : 'new',
               }
        for record in self.browse(cr,uid,ids,context=context):
            result['url'] = baseUrlPrefix + record.image3_reference + baseUrlPostFix
            
        return result     
                   
    def go_image4(self, cr, uid, ids, context=None):
        result =  {
                  'name'     : 'Show Image4',
                  'res_model': 'ir.actions.act_url',
                  'type'     : 'ir.actions.act_url',
                  'target'   : 'new',
               }
        for record in self.browse(cr,uid,ids,context=context):
            result['url'] = baseUrlPrefix + record.image4_reference + baseUrlPostFix
            
        return result  
     
    def go_image5(self, cr, uid, ids, context=None):
        result =  {
                  'name'     : 'Show Image5',
                  'res_model': 'ir.actions.act_url',
                  'type'     : 'ir.actions.act_url',
                  'target'   : 'new',
               }
        for record in self.browse(cr,uid,ids,context=context):
            result['url'] = baseUrlPrefix + record.image5_reference + baseUrlPostFix
            
        return result               
    @api.model
    def _get_default_image(self, is_company, colorize=False):
#         img_path = openerp.modules.get_module_resource(
#             'base', 'static/src/img', 'company_image.png' if is_company else 'avatar.png')
        img_path = openerp.modules.get_module_resource(
            'base', 'static/src/img', 'company_image.png' if is_company else 'avatar.png')
        with open(img_path, 'rb') as f:
            image = f.read()

        # colorize user avatars
        if not is_company:
            image = tools.image_colorize(image)

        return tools.image_resize_image_big(image.encode('base64'))
    @api.model
    def _get_default_image1(self, is_company, colorize=False):
        img_path = openerp.modules.get_module_resource(
            'base', 'static/src/img', 'company_image.png' if is_company else 'avatar.png')
        with open(img_path, 'rb') as f:
            image = f.read()

        # colorize user avatars
        if not is_company:
            image = tools.image_colorize(image)

        return tools.image_resize_image_big(image.encode('base64'))
    @api.model
    def _get_default_image2(self, is_company, colorize=False):
        img_path = openerp.modules.get_module_resource(
            'base', 'static/src/img', 'company_image.png' if is_company else 'avatar.png')
        with open(img_path, 'rb') as f:
            image = f.read()

        # colorize user avatars
        if not is_company:
            image = tools.image_colorize(image)

        return tools.image_resize_image_big(image.encode('base64'))
    @api.model
    def _get_default_image3(self, is_company, colorize=False):
        img_path = openerp.modules.get_module_resource(
            'base', 'static/src/img', 'company_image.png' if is_company else 'avatar.png')
        with open(img_path, 'rb') as f:
            image = f.read()

        # colorize user avatars
        if not is_company:
            image = tools.image_colorize(image)

        return tools.image_resize_image_big(image.encode('base64'))
    @api.model
    def _get_default_image4(self, is_company, colorize=False):
        img_path = openerp.modules.get_module_resource(
            'base', 'static/src/img', 'company_image.png' if is_company else 'avatar.png')
        with open(img_path, 'rb') as f:
            image = f.read()

        # colorize user avatars
        if not is_company:
            image = tools.image_colorize(image)

        return tools.image_resize_image_big(image.encode('base64'))

    @api.model
    def _get_default_image5(self, is_company, colorize=False):
        img_path = openerp.modules.get_module_resource(
            'base', 'static/src/img', 'company_image.png' if is_company else 'avatar.png')
        with open(img_path, 'rb') as f:
            image = f.read()

        # colorize user avatars
        if not is_company:
            image = tools.image_colorize(image)

        return tools.image_resize_image_big(image.encode('base64'))

    def generate_image_old(self, cr, uid, ids, context=None):
        if ids:
            visit_data = self.browse(cr, uid, ids[0], context=context)
            import base64
            image1 =False
            image2 =False
            image3 =False
            image4 =False
            image5 =False
            if visit_data.image1_reference:
                    url =baseUrlPrefix + visit_data.image1_reference + baseUrlPostFix
                    response = requests.get(url).content
                    image1 = base64.b64encode(response)
            if visit_data.image2_reference:
                    url =baseUrlPrefix + visit_data.image2_reference + baseUrlPostFix
                    response = requests.get(url).content
                    image2 = base64.b64encode(response)                                                      
            if visit_data.image3_reference:
                    url =baseUrlPrefix + visit_data.image3_reference + baseUrlPostFix
                    response = requests.get(url).content
                    image3 = base64.b64encode(response)                                                                
            if visit_data.image4_reference:
                    url =baseUrlPrefix + visit_data.image4_reference + baseUrlPostFix
                    response = requests.get(url).content
                    image4 = base64.b64encode(response)                                                                        
            if visit_data.image5_reference:
                    url =baseUrlPrefix + visit_data.image5_reference + baseUrlPostFix
                    response = requests.get(url).content
                    image5 = base64.b64encode(response)    
        return self.write(cr, uid, ids, {'image':image1,'image1':image2,'image2':image3,'image3':image4,'image4':image5})

    def generate_image(self, cr, uid, ids, context=None):
        customer_image = False
        if ids:
            visit_data = self.browse(cr, uid, ids[0], context=context)
            import base64
            if visit_data.visit_image_ids:
                for image_id in visit_data.visit_image_ids:
                    if image_id.name:
                        url = baseUrlPrefix + image_id.name + baseUrlPostFix
                        response= requests.get(url).content
                        image = base64.b64encode(response)
                        image_id.write({'image':image})
                        _logger.info('-----------image has been retrieved----------')
            if visit_data.customer_id.image:
                customer_image = (visit_data.customer_id.image)
        return self.write(cr, uid, ids, {'image5':customer_image})

    def is_approve(self, cr, uid, ids, context=None):

        return self.write(cr, uid, ids, {'state': 'approved', 'validated_by': uid, 'validated_date': datetime.now()})

    def is_reject(self, cr, uid, ids, context=None):

        return self.write(cr, uid, ids, {'state': 'reject', 'rejected_by': uid, 'rejected_date': datetime.now()})
                   
                                        
customer_visit()
