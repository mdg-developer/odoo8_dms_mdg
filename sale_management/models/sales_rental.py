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
    
    def create(self, cr, uid, vals, context=None):
        if vals.get('partner_id'):
            defaults = self.on_change_partner_id(cr, uid, [], vals['partner_id'], context=context)['value']
            vals = dict(defaults, **vals)            
        ctx = dict(context or {}, mail_create_nolog=True)
        new_id = super(sale_rental, self).create(cr, uid, vals, context=ctx)
        self.message_post(cr, uid, [new_id], context=ctx)
        return new_id
    

    def on_change_partner_id(self, cr, uid, ids, partner_id, context=None):
        values = {}
        if partner_id:
            partner = self.pool.get('res.partner').browse(cr, uid, partner_id, context=context)
            values = {
                 'code': partner.customer_code,
                'street': partner.street,
                'street2': partner.street2,
                'city': partner.city and partner.city.id or False,
                'state_id': partner.state_id and partner.state_id.id or False,
                'country_id': partner.country_id and partner.country_id.id or False,
                'township': partner.township and partner.township.id or False,
            }
        return {'value': values}
        
    def _get_default_company(self, cr, uid, context=None):
        company_id = self.pool.get('res.users')._get_company(cr, uid, context=context)
        if not company_id:
            raise osv.except_osv(_('Error!'), _('There is no default company for the current user!'))
        return company_id    

         
    _columns = {
        'company_id':fields.many2one('res.company', 'Company'),
        'date':fields.date('Txn Date'),
       'from_date':fields.date('Contract Start Date'),
        'to_date':fields.date('Contract End Date'),
        'partner_id':fields.many2one('res.partner', 'Customer'  , required=True),  # 
         'code':fields.char('Customer ID',readonly=True),
        'note':fields.text('Note'),
        'name':fields.char('Description'),
        'street': fields.char('Street',readonly=True),
        'street2': fields.char('Street2',readonly=True),
        'city': fields.many2one('res.city', 'City', ondelete='restrict',readonly=True),
        'state_id': fields.many2one("res.country.state", 'State', ondelete='restrict',readonly=True),
        'country_id': fields.many2one('res.country', 'Country', ondelete='restrict',readonly=True),
        'township': fields.many2one('res.township', 'Township', ondelete='restrict',readonly=True),
        'total_amt':fields.float('Total Amount'  , required=True),
     #   'image': fields.binary("Location Photo"),
        'latitude':fields.float('Geo Latitude', digits=(14,15)),
        'longitude':fields.float('Geo Longitude', digits=(14,15)),
        'distance_status':fields.char('Distance Status'),

        'month_cost':fields.char("Monthly Cost"),
        'rental_month':fields.integer('Rental Month'),
#     'image' :fields.binary("Image", attachment=True,
#         help="This field holds the image used as avatar for this contact, limited to 1024x1024px",
#         default=lambda self: self._get_default_image(False, True)),   
#     'image_medium':fields.binary("Medium-sized image",
#         compute='_compute_images', inverse='_inverse_image_medium', store=True, attachment=True,
#         help="Medium-sized image of this contact. It is automatically "\
#              "resized as a 128x128px image, with aspect ratio preserved. "\
#              "Use this field in form views or some kanban views."),
#     'image_small' :fields.binary("Small-sized image",
#         compute='_compute_images', inverse='_inverse_image_small', store=True, attachment=True,
#         help="Small-sized image of this contact. It is automatically "\
#              "resized as a 64x64px image, with aspect ratio preserved. "\
#              "Use this field anywhere a small image is required."),
#     # each image must have it's image_medium and image_small
#     'image1':fields.binary("Image", attachment=True,
#         help="This field holds the image used as avatar for this contact, limited to 1024x1024px",
#         default=lambda self: self._get_default_image1(False, True))   ,
#     'image_medium1' :fields.binary("Medium-sized image",
#         compute='_compute_images1', inverse='_inverse_image_medium1', store=True, attachment=True,
#         help="Medium-sized image of this contact. It is automatically "\
#              "resized as a 128x128px image, with aspect ratio preserved. "\
#              "Use this field in form views or some kanban views."),
#     'image_small1' :fields.binary("Small-sized image",
#         compute='_compute_images1', inverse='_inverse_image_small1', store=True, attachment=True,
#         help="Small-sized image of this contact. It is automatically "\
#              "resized as a 64x64px image, with aspect ratio preserved. "\
#              "Use this field anywhere a small image is required."),
#     # each image must have it's image_medium and image_small
#     'image2' :fields.binary("Image", attachment=True,
#         help="This field holds the image used as avatar for this contact, limited to 1024x1024px",
#         default=lambda self: self._get_default_image2(False, True)),   
#     'image_medium2' :fields.binary("Medium-sized image",
#         compute='_compute_images2', inverse='_inverse_image_medium2', store=True, attachment=True,
#         help="Medium-sized image of this contact. It is automatically "\
#              "resized as a 128x128px image, with aspect ratio preserved. "\
#              "Use this field in form views or some kanban views."),
#     'image_small2' :fields.binary("Small-sized image",
#         compute='_compute_images2', inverse='_inverse_image_small2', store=True, attachment=True,
#         help="Small-sized image of this contact. It is automatically "\
#              "resized as a 64x64px image, with aspect ratio preserved. "\
#              "Use this field anywhere a small image is required."),
#     # each image must have it's image_medium and image_small
#     'image3' :fields.binary("Image", attachment=True,
#         help="This field holds the image used as avatar for this contact, limited to 1024x1024px",
#         default=lambda self: self._get_default_image3(False, True)),   
#     'image_medium3':fields.binary("Medium-sized image",
#         compute='_compute_images3', inverse='_inverse_image_medium3', store=True, attachment=True,
#         help="Medium-sized image of this contact. It is automatically "\
#              "resized as a 128x128px image, with aspect ratio preserved. "\
#              "Use this field in form views or some kanban views."),
#     'image_small3': fields.binary("Small-sized image",
#         compute='_compute_images3', inverse='_inverse_image_small3', store=True, attachment=True,
#         help="Small-sized image of this contact. It is automatically "\
#              "resized as a 64x64px image, with aspect ratio preserved. "\
#              "Use this field anywhere a small image is required."),
#     # each image must have it's image_medium and image_small
#     'image4' : fields.binary("Image", attachment=True,
#         help="This field holds the image used as avatar for this contact, limited to 1024x1024px",
#         default=lambda self: self._get_default_image4(False, True)),
#     'image_medium4': fields.binary("Medium-sized image",
#         compute='_compute_images4', inverse='_inverse_image_medium4', store=True, attachment=True,
#         help="Medium-sized image of this contact. It is automatically "\
#              "resized as a 128x128px image, with aspect ratio preserved. "\
#              "Use this field in form views or some kanban views."),
#     'image_small4' : fields.binary("Small-sized image",
#         compute='_compute_images4', inverse='_inverse_image_small4', store=True, attachment=True,
#         help="Small-sized image of this contact. It is automatically "\
#              "resized as a 64x64px image, with aspect ratio preserved. "\
#              "Use this field anywhere a small image is required."),          
  }
    
    _defaults = {
        'date': fields.datetime.now,
        'company_id': _get_default_company,
        'unit': 'day',
        }   
    
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

             
sale_rental()     
