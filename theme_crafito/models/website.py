# -*- coding: utf-8 -*-
# Part of AppJetty. See LICENSE file for full copyright and licensing details.

import math
import werkzeug
import calendar
from datetime import datetime
import time
from openerp import SUPERUSER_ID
from openerp.http import request
from openerp import api, fields, models, _
from openerp.addons.website.models.website import slugify
from openerp.tools.translate import _


class WebsiteMenu(models.Model):
    _inherit = "website.menu"

    is_megamenu = fields.Boolean(string='Is megamenu...?')
    megamenu_view_type = fields.Selection([('cat_megamenu', 'Category Megamenu'),
                                           ('pages_megamenu', "Pages Megamenu")],
                                     # default='cat_megamenu',
                                     string="Megamenu View Type")
    megamenu_size = fields.Selection([('medium', 'Medium'),
                                      ('large', 'Large')],
                                     default='medium',
                                     string="Megamenu Size")

    megamenu_type = fields.Selection([('2_col', '2 Columns'),
                                      ('3_col', '3 Columns'),
                                      ('4_col', '4 Columns')],
                                     default='3_col',
                                     string="Megamenu type")
    megamenu_bg = fields.Boolean(
        string='Want to set megamenu background', default=False)
    megamenu_bg_img_color = fields.Selection([('bg_img', 'Background image'),
                                              ('bg_color', 'Background color')],
                                             default='bg_img',
                                             string="Megamenu background selection")
    megamenu_bg_image = fields.Binary(string="Background image for megamenu")
    megamenu_bg_color = fields.Char(string="Background color for megamenu",
                                    default='#ccc',
                                    help="Background color for megamenu, for setting background color you have to pass hexacode here.")
    category_slider = fields.Boolean(
        string='Want to display category slider', default=False)
    carousel_header_name = fields.Char(string="Slider label",
                                       default="Latest",
                                       help="Header name for carousel slider in megamenu")
    category_slider_position = fields.Selection([('left', 'Left'), ('right', 'Right')],
                                                default='left', string="Category Slider Position")
    menu_icon = fields.Boolean(
        string='Want to display menu icon', default=False)
    menu_icon_image = fields.Binary(
        string="Menu Icon", help="Menu icon for your menu")

    display_menu_footer = fields.Boolean(string="Display menu footer", default=False,
                                         help="For displaying footer in megamenu")
    menu_footer = fields.Html(string="Footer content",
                              help="Footer name for megamenu")
    customize_menu_colors = fields.Boolean(
        string='Want to customize menu colors', default=False)
    main_category_color = fields.Char(string='Main menu color',
                                      help="Set color for main menu in megamenu")
    sub_category_color = fields.Char(string='Submenu color',
                                     help="Set color for submenu in megamenu")


class website(models.Model):
    _inherit = 'website'

    display_category_menu = fields.Boolean(string="Display category menu in menubar", default=True,
                                           help="Enable this checkbox to display category menu on website in menu bar.")
    category_menu_name = fields.Char(string="Category menu name", default="All Departments",
                                     help="Category name which will be visible in website.")

    # For Multi image
    thumbnail_panel_position = fields.Selection([
        ('left', 'Left'),
        ('right', 'Right'),
        ('bottom', 'Bottom'),
    ], default='left',
        string='Thumbnails panel position',
        help="Select the position where you want to display the thumbnail panel in multi image.")
    interval_play = fields.Char(string='Play interval of slideshow', default='5000',
                                help='With this field you can set the interval play time between two images.')
    enable_disable_text = fields.Boolean(string='Enable the text panel',
                                         default=True,
                                         help='Enable/Disable text which is visible on the image in multi image.')
    color_opt_thumbnail = fields.Selection([
        ('default', 'Default'),
        ('b_n_w', 'B/W'),
        ('sepia', 'Sepia'),
        ('blur', 'Blur'), ],
        default='default',
        string="Thumbnail overlay effects")
    no_extra_options = fields.Boolean(string='Slider effects',
                                      default=False,
                                      help="Slider with all options for next, previous, play, pause, fullscreen, hide/show thumbnail panel.")
    change_thumbnail_size = fields.Boolean(
        string="Change thumbnail size", default=False)
    thumb_height = fields.Char(string='Thumb height', default=50)
    thumb_width = fields.Char(string='Thumb width', default=88)

    # For Sort By
    enable_sort_by = fields.Boolean(string='Enable product sorting option',
                                    help='For enabling product sorting feature in website.',
                                    default=True)

    # For category menu in topmenu
    def get_categories(self):
        categoriess = self.env['product.public.category'].search(
            [('parent_id', '=', False)])
        return categoriess

    # For category menu in topmenu
    def get_child_categories(self, child_id):
        child_categories = self.env['product.public.category'].search(
            [('parent_id', '=', child_id.id)], order="sequence asc")
        return child_categories

    # For category megamenu
    @api.multi
    def get_public_product_category(self, submenu):
        categories = self.env['product.public.category'].search([('parent_id', '=', False),
                                                                 ('include_in_megamenu',
                                                                  '!=', False),
                                                                 ('menu_id', '=', submenu.id)],
                                                                order="sequence")
        return categories

    # For child category megamenu
    def get_public_product_child_category(self, children):
        child_categories = []
        for child in children:
            categories = self.env['product.public.category'].search([
                ('id', '=', child.id),
                ('include_in_megamenu', '!=', False)], order="sequence")
            if categories:
                child_categories.append(categories)
        return child_categories

    # For pages megamenu
    def get_megamenu_pages(self, submenu):
        menus = self.env['website.menu'].sudo().search(
            [('parent_id', '=', submenu.id)])
        return menus

    # For multi image
    @api.multi
    def get_multiple_images(self, product_id=None):
        productsss = False
        if product_id:
            products = self.env['biztech.product.images'].search(
                [('biz_product_tmpl_id', '=', product_id), ('more_view_exclude', '=', False)], order='sequence')
            if products:
                return products
        return productsss

    def get_related_product_ids(self, product):
        rel_lst = []
        inner_lst = []
        for rel in product.related_product_ids:
            inner_lst.append(rel)
            if len(inner_lst) == 4:
                rel_lst.append(inner_lst)
                inner_lst = []
        else:
            if inner_lst:
                rel_lst.append(inner_lst)
        return rel_lst

    @api.multi
    def convert_date(self, date_given):
        date = date_given
        temp1 = datetime.strptime(date, '%Y-%m-%d %H:%M:%S').date()
        if temp1:
            new_date = str(calendar.month_name[temp1.month]) + \
                ' '+str(temp1.day)+'th, '+str(temp1.year)
            return new_date

    # Collection snippets
    def get_slider_product_ids(self, collection):
        rel_lst = []
        inner_lst = []
        for rel in collection:
            inner_lst.append(rel)
            if len(inner_lst) == 3:
                rel_lst.append(inner_lst)
                inner_lst = []
        else:
            if inner_lst:
                rel_lst.append(inner_lst)
        return rel_lst

    def get_feature_products_collections(self, product):
        list_of_products = self.get_slider_product_ids(
            product.feature_products_collections)
        return list_of_products

    def get_on_sale_collections(self, product):
        list_of_products = self.get_slider_product_ids(
            product.on_sale_collections)
        return list_of_products

    def get_random_products_collections(self, product):
        list_of_products = self.get_slider_product_ids(
            product.random_products_collections)
        return list_of_products

    def get_low_price_collections(self, product):
        list_of_products = self.get_slider_product_ids(
            product.low_price_collections)
        return list_of_products

    # For Sorting products
    def get_sort_by_data(self):
        request.session['product_sort_name'] = ''
        sort_by = self.env['biztech.product.sortby'].search([])
        return sort_by

    # For setting current sort list
    def set_current_sorting_data(self):
        sort_name = request.session.get('product_sort_name')
        return sort_name

    def new_page(self, cr, uid, name, template='website.default_page', ispage=True, context=None):
        res = super(website, self).new_page(
            cr, uid, name, template=template, ispage=ispage, context=context)
        page_name = slugify(name, max_length=50)
        ir_view = self.pool.get('ir.ui.view')
        view_id = ir_view.search(
            cr, SUPERUSER_ID, [('name', '=', page_name)], context=context)
        if view_id:
            view = ir_view.browse(cr, SUPERUSER_ID, view_id, context=context)
            arch = '<?xml version="1.0"?><t t-name="website.'+str(page_name)+'"><t t-call="website.layout"> <div id="wrap" class="oe_structure oe_empty"><section class="page-title"><div class="container"><h1>'+str(
                page_name.capitalize())+'</h1><ul class="breadcrumb"><li><a href="/page/homepage">Home</a></li><li class="active">'+str(page_name.capitalize())+'</li></ul></div></section></div></t></t>'
            ir_view.write(
                cr, SUPERUSER_ID, view_id, {'arch': arch}, context=context)
        return res

    def get_event_data(self, category_event):
        event_cat = category_event.id
        event_today = str(
            datetime.strptime(str(datetime.now()), "%Y-%m-%d %H:%M:%S.%f").date())
        domain = [('state', "in", ['confirm']), ('website_published', '=', 'True'),
                  ('type', '=', event_cat), ('date_begin', '>=', event_today)]
        event = request.env['event.event'].sudo().search(domain, limit=8)
        
        ev = {}
        ev['event'] = event
        ev['count'] = len(event)
        if event:
            return ev
        else:
            return False

    def set_event_tag(self, event_date):
        date = event_date
        today = datetime.now()
        newtoday = datetime.strptime(str(today), "%Y-%m-%d %H:%M:%S.%f").date()
        temp1 = datetime.strptime(date, '%Y-%m-%d %H:%M:%S').date()
        if temp1:
            if temp1.month == today.month and temp1.day == today.day:
                return _("Today")
            elif temp1.month == today.month and temp1.isocalendar()[1] == today.isocalendar()[1]:
                return _("This week")
            elif temp1.month == today.month and temp1.isocalendar()[1] == (today.isocalendar()[1] + 1):
                return _("Next week")
            elif temp1.month == today.month:
                return _("This month")
            elif temp1.month == (today.month + 1):
                return _("Next month")
            else:
                return _("Up Comming")

    def pager(self, cr, uid, ids, url, total, page=1, step=30, scope=5, url_args=None, context=None):
        res = super(website, self). pager(cr, uid, ids, url=url,
                                          total=total,
                                          page=page,
                                          step=step,
                                          scope=scope,
                                          url_args=url_args,
                                          context=context)
        # Compute Pager
        page_count = int(math.ceil(float(total) / step))

        page = max(1, min(int(page if str(page).isdigit() else 1), page_count))
        scope -= 1

        pmin = max(page - int(math.floor(scope/2)), 1)
        pmax = min(pmin + scope, page_count)

        if pmax - pmin < scope:
            pmin = pmax - scope if pmax - scope > 0 else 1

        def get_url(page):
            _url = "%s/page/%s" % (url, page) if page > 1 else url
            if url_args and not url_args.get('tag') and not url_args.get('range1') and not url_args.get('range2') and not url_args.get('max1') and not url_args.get('min1') and not url_args.get('sort_id'):
                _url = "%s?%s" % (_url, werkzeug.url_encode(url_args))
            return _url
        res.update({
            # Overrite existing
            "page_start": {
                'url': get_url(pmin),
                'num': pmin
            },
            "page_previous": {
                'url': get_url(max(pmin, page - 1)),
                'num': max(pmin, page - 1)
            },
            "page_next": {
                'url': get_url(min(pmax, page + 1)),
                'num': min(pmax, page + 1)
            },
            "page_end": {
                'url': get_url(pmax),
                'num': pmax
            },
            'page_first': {
                'url': get_url(1),
                'num': 1
            },
            'page_last': {
                'url': get_url(int(res['page_count'])),
                'num': int(res['page_count'])
            },
            'pages': [
                {'url': get_url(page), 'num': page}
                for page in xrange(pmin, pmax+1)
            ]
        })
        return res



class WebsiteConfigSettings(models.TransientModel):

    _inherit = 'website.config.settings'

    display_category_menu = fields.Boolean(string="Display category menu in menubar", default=True,
                                           related='website_id.display_category_menu',
                                           help="Enable this checkbox to display category menu on website in menu bar.")
    category_menu_name = fields.Char(string="Category menu name", default="All Departments",
                                     related='website_id.category_menu_name',
                                     help="Category name which will be visible in website.")

    # For multi image
    thumbnail_panel_position = fields.Selection([
        ('left', 'Left'),
        ('right', 'Right'),
        ('bottom', 'Bottom')],
        string='Thumbnails panel position',
        related='website_id.thumbnail_panel_position',
        help="Select the position where you want to display the thumbnail panel in multi image.")
    interval_play = fields.Char(string='Play interval of slideshow',
                                related='website_id.interval_play',
                                help='With this field you can set the interval play time between two images.')
    enable_disable_text = fields.Boolean(string='Enable the text panel',
                                         related='website_id.enable_disable_text',
                                         help='Enable/Disable text which is visible on the image in multi image.')
    color_opt_thumbnail = fields.Selection([
        ('default', 'Default'),
        ('b_n_w', 'B/W'),
        ('sepia', 'Sepia'),
        ('blur', 'Blur')],
        related='website_id.color_opt_thumbnail',
        string="Thumbnail overlay effects")
    no_extra_options = fields.Boolean(string='Slider effects',
                                      related='website_id.no_extra_options',
                                      help="Slider with all options for next, previous, play, pause, fullscreen, hide/show thumbnail panel.")
    change_thumbnail_size = fields.Boolean(string="Change thumbnail size",
                                           related="website_id.change_thumbnail_size"
                                           )
    thumb_height = fields.Char(string='Thumb height',
                               related="website_id.thumb_height"
                               )
    thumb_width = fields.Char(string='Thumb width',
                              related="website_id.thumb_width"
                              )

    # For Sort By
    enable_sort_by = fields.Boolean(related="website_id.enable_sort_by", string='Enable product sorting option',
                                    help='For enabling product sorting feature in website.',
                                    default=True)