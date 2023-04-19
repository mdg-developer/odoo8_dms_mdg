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
import base64



_logger = logging.getLogger(__name__)

baseUrlPrefix = "https://firebasestorage.googleapis.com/v0/b/odoo-8d694.appspot.com/o/finewine_customer_visit%2F"
baseUrlPostFix = ".png?alt=media"

class customer_visit_images(osv.osv):
    _name = "customer.visit.images"
    _description = "Customer Visit Images"

    _columns = {
        'name': fields.char('Image Reference'),
        'image':fields.binary('Image',attachment=True,default=lambda self: self._get_default_image(False, True)),
        'image_small':fields.binary('Small Image',attachment=True,compute='_compute_images', inverse='_inverse_image_small', store=True),
        'image_medium':fields.binary('Medium Image',attachment=True,compute='_compute_images', inverse='_inverse_image_medium', store=True),
        'customer_visit_id': fields.many2one('customer.visit', 'Customer Visit ID'),
        'is_image': fields.boolean('Is Image', default=False),
    }

    # This is that person picture
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

    # resize that image
    @api.depends('image')
    def _compute_images(self):
        for rec in self:
            rec.image_medium = tools.image_resize_image_medium(rec.image)
            rec.image_small = tools.image_resize_image_small(rec.image)
            _logger.info('-----------image has been resized to medium and small---------')
            return rec.image

    def _inverse_image_small(self):
        for rec in self:
            rec.image = tools.image_resize_image_big(rec.image_small)

    def _inverse_image_medium(self):
        for rec in self:
            rec.image = tools.image_resize_image_big(rec.image_medium)

    def go_image(self, cr, uid, ids, context=None):
        result = {
            'name': 'Show Image1',
            'res_model': 'ir.actions.act_url',
            'type': 'ir.actions.act_url',
            'target': 'new',
        }
        for record in self.browse(cr, uid, ids, context=context):
            result['url'] = baseUrlPrefix + record.image1_reference + baseUrlPostFix

        return result

    def generate_image(self, cr, uid, ids, context=None):
        if ids:
            visit_data = self.browse(cr, uid, ids[0], context=context)
            import base64
            image1 = False
            image2 = False
            image3 = False
            image4 = False
            image5 = False
            if visit_data.image1_reference:
                url = baseUrlPrefix + visit_data.image1_reference + baseUrlPostFix
                response = requests.get(url).content
                image1 = base64.b64encode(response)
            if visit_data.image2_reference:
                url = baseUrlPrefix + visit_data.image2_reference + baseUrlPostFix
                response = requests.get(url).content
                image2 = base64.b64encode(response)
            if visit_data.image3_reference:
                url = baseUrlPrefix + visit_data.image3_reference + baseUrlPostFix
                response = requests.get(url).content
                image3 = base64.b64encode(response)
            if visit_data.image4_reference:
                url = baseUrlPrefix + visit_data.image4_reference + baseUrlPostFix
                response = requests.get(url).content
                image4 = base64.b64encode(response)
            if visit_data.image5_reference:
                url = baseUrlPrefix + visit_data.image5_reference + baseUrlPostFix
                response = requests.get(url).content
                image5 = base64.b64encode(response)
        return self.write(cr, uid, ids,
                          {'image': image1, 'image1': image2, 'image2': image3, 'image3': image4, 'image4': image5})






