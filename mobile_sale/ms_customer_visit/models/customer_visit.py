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
        'latitude':fields.float('Geo Latitude'),
        'longitude':fields.float('Geo Longitude'),
       'sale_team_id':fields.many2one('crm.case.section', 'Sale Team'),
       'date':fields.datetime('Date'),
        'visit_reason':fields.selection([
                ('no_shopkeeper', 'No Shopkeeper'),
                ('no_authorized_person', 'No Authorized Person'),
                ('products_already_existed', 'Products Already Existed'),
                 ('sold_other_people_products', 'Sold Other People Products'),
                 ('other_reason', 'Other Reasons')
            ], 'Reason'),
                'other_reason':fields.text('Remark'),
        'm_status':fields.selection([('pending', 'Pending'), ('approved', 'Approved'),
                                                      ('reject', 'Reject')], string='Status'),
    }
    _defaults = {        
        'm_status' : 'pending',
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
    @api.model
    def _get_default_image(self, is_company, colorize=False):
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

         
customer_visit()
