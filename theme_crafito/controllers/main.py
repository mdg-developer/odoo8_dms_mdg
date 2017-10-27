# -*- coding: utf-8 -*-
# Part of AppJetty. See LICENSE file for full copyright and licensing details.

import re
from openerp import http
from openerp.http import request
from openerp.addons.website.models.website import slug
from openerp.addons.website_sale.controllers import main
from openerp.addons.website_sale.controllers import main as main_shop
from openerp.addons.website_sale.controllers.main import QueryURL
from openerp.addons.website_sale.controllers.main import website_sale
from openerp.addons.website_sale.controllers.main import table_compute


class CrafitoSliderSettings(http.Controller):

    @http.route(['/theme_crafito/blog_get_options'], type='json', auth="public", website=True)
    def crafito_get_slider_options(self):
        slider_options = []
        option = request.env['blog.slider.config'].search(
            [('active', '=', True)], order="name asc")
        for record in option:
            slider_options.append({'id': record.id,
                                   'name': record.name})
        return slider_options

    @http.route(['/theme_crafito/blog_get_dynamic_slider'], type='http', auth='public', website=True)
    def crafito_get_dynamic_slider(self, **post):
        if post.get('slider-type'):
            slider_header = request.env['blog.slider.config'].sudo().search(
                [('id', '=', int(post.get('slider-type')))])
            values = {
                'slider_header': slider_header,
                'blog_slider_details': slider_header.collections_blog_post,
            }
            return request.website.render("theme_crafito.theme_crafito_blog_slider_view", values)

    @http.route(['/theme_crafito/blog_image_effect_config'], type='json', auth='public', website=True)
    def crafito_product_image_dynamic_slider(self, **post):
        slider_data = request.env['blog.slider.config'].search(
            [('id', '=', int(post.get('slider_type')))])
        values = {
            's_id': str(slider_data.no_of_counts) + '-' + str(slider_data.id),
            'counts': slider_data.no_of_counts,
            'auto_rotate': slider_data.auto_rotate,
            'auto_play_time': slider_data.sliding_speed,
        }
        return values

    # For Client slider
    @http.route(['/theme_crafito/get_clients_dynamically_slider'], type='http', auth='public', website=True)
    def get_clients_dynamically_slider(self, **post):
        client_data = request.env['res.partner'].sudo().search(
            [('add_to_slider', '=', True)])
        values = {
            'client_slider_details': client_data,
        }
        return request.website.render("theme_crafito.theme_crafito_client_slider_view", values)

    # For multi product slider
    @http.route(['/theme_crafito/product_multi_get_options'], type='json', auth="public", website=True)
    def crafito_product_multi_get_slider_options(self):
        slider_options = []
        option = request.env['multi.slider.config'].search(
            [('active', '=', True)], order="name asc")
        for record in option:
            slider_options.append({'id': record.id,
                                   'name': record.name})
        return slider_options

    @http.route(['/theme_crafito/product_multi_get_dynamic_slider'], type='http', auth='public', website=True)
    def crafito_product_multi_get_dynamic_slider(self, **post):
        if post.get('slider-type'):
            slider_header = request.env['multi.slider.config'].sudo().search(
                [('id', '=', int(post.get('slider-type')))])
            values = {
                'slider_details': slider_header,
                'slider_header': slider_header,
            }
            return request.website.render("theme_crafito.theme_crafito_multi_cat_slider_view", values)

    @http.route(['/theme_crafito/product_multi_image_effect_config'], type='json', auth='public', website=True)
    def crafito_product_multi_product_image_dynamic_slider(self, **post):
        slider_data = request.env['multi.slider.config'].search(
            [('id', '=', int(post.get('slider_type')))])
        values = {
            's_id': str(slider_data.no_of_collection) + '-' + str(slider_data.id),
            'counts': slider_data.no_of_collection,
            'auto_rotate': slider_data.auto_rotate,
            'auto_play_time': slider_data.sliding_speed,
        }
        return values

    @http.route(['/theme_crafito/newsone_get_dynamic_slider'], type='http', auth='public', website=True)
    def crafito_get_dynamic_newsone_slider(self, **post):
        if post.get('slider-type'):
            slider_header = request.env['blog.slider.config'].sudo().search(
                [('id', '=', int(post.get('slider-type')))])
            values = {
                'slider_header': slider_header,
                'blog_slider_details': slider_header.collections_blog_post,
            }

            return request.website.render("theme_crafito.theme_crafito_news1_view", values)

    @http.route(['/theme_crafito/newstwo_get_dynamic_slider'], type='http', auth='public', website=True)
    def crafito_get_dynamic_newstwo_slider(self, **post):
        if post.get('slider-type'):
            slider_header = request.env['blog.slider.config'].sudo().search(
                [('id', '=', int(post.get('slider-type')))])
            values = {
                'slider_header': slider_header,
                'blog_slider_details': slider_header.collections_blog_post,
            }
            return request.website.render("theme_crafito.theme_crafito_news2_view", values)

    @http.route(['/theme_crafito/theme_new_hardware_blog'], type='http', auth='public', website=True)
    def crafito_get_dynamic_hardwareblog_slider(self, **post):
        if post.get('slider-type'):
            slider_header = request.env['blog.slider.config'].sudo().search(
                [('id', '=', int(post.get('slider-type')))])
            values = {
                'slider_header': slider_header,
                'blog_slider_details': slider_header.collections_blog_post,
            }
            return request.website.render("theme_crafito.theme_crafito_hardware_blog_snippet_view", values)

    # Coming soon snippet
    @http.route(['/biztech_comming_soon/soon_data'], type="http", auth="public", website=True)
    def get_soon_data(self, **post):
        return request.website.render("theme_crafito.theme_crafito_coming_soon_mode_one_view")

    @http.route(['/biztech_comming_soon_two/two_soon_data'], type="http", auth="public", website=True)
    def get_soon_data_two(self, **post):
        return request.website.render("theme_crafito.theme_crafito_coming_soon_mode_two_view")

    def find_snippet_employee(self):
        emp = {}
        employee = request.env['hr.employee'].sudo().search(
            [('include_inourteam', '=', 'True')])
        emp['biztech_employees'] = employee
        return emp

    # For team snippet
    @http.route(['/biztech_emp_data_one/employee_data'], type="http", auth="public", website=True)
    def get_one_employee_details_custom(self, **post):
        emp = self.find_snippet_employee()
        return request.website.render("theme_crafito.theme_crafito_team_one", emp)

    @http.route(['/biztech_emp_data/employee_data'], type="http", auth="public", website=True)
    def get_employee_detail_custom(self, **post):
        emp = self.find_snippet_employee()
        return request.website.render("theme_crafito.theme_crafito_team_two", emp)

    @http.route(['/biztech_emp_data_three/employee_data'], type="http", auth="public", website=True)
    def get_employee_detail_custom_1(self, **post):
        emp = self.find_snippet_employee()
        return request.website.render("theme_crafito.theme_crafito_team_three", emp)

    # For Category slider
    @http.route(['/theme_crafito/category_get_options'], type='json', auth="public", website=True)
    def category_get_slider_options(self):
        slider_options = []
        option = request.env['category.slider.config'].search(
            [('active', '=', True)], order="name asc")
        for record in option:
            slider_options.append({'id': record.id,
                                   'name': record.name})
        return slider_options

    @http.route(['/theme_crafito/category_get_dynamic_slider'], type='http', auth='public', website=True)
    def category_get_dynamic_slider(self, **post):
        if post.get('slider-id'):
            slider_header = request.env['category.slider.config'].sudo().search(
                [('id', '=', int(post.get('slider-id')))])
            values = {
                'slider_header': slider_header
            }
            for category in slider_header.collections_category:
                query = """
                    SELECT
                        count(product_template_id)
                    FROM
                        product_public_category_product_template_rel
                    WHERE
                        product_public_category_id in %s
                """
                request.env.cr.execute(query, (tuple([category.id]),))
                product_details = request.env.cr.fetchone()
                category.linked_product_count = product_details[0]
            values.update({
                'slider_details': slider_header.collections_category,
            })
            return request.website.render("theme_crafito.theme_crafito_cat_slider_view", values)

    @http.route(['/theme_crafito/category_image_effect_config'], type='json', auth='public', website=True)
    def category_image_dynamic_slider(self, **post):
        slider_data = request.env['category.slider.config'].search(
            [('id', '=', int(post.get('slider_id')))])
        values = {
            's_id': slider_data.name.lower().replace(' ', '-') + '-' + str(slider_data.id),
            'counts': slider_data.no_of_counts,
            'auto_rotate': slider_data.auto_rotate,
            'auto_play_time': slider_data.sliding_speed,
        }
        return values

    @http.route(['/biztech_fact_model_data/fact_data'], type="http", auth="public", website=True)
    def get_factsheet_data(self, **post):
        return request.website.render("theme_crafito.theme_crafito_facts_sheet_view")

    @http.route(['/biztech_skill_model_data/skill_data'], type="http", auth="public", website="True")
    def get_skill_data(self, **post):
        return request.website.render("theme_crafito.theme_crafito_skills_view")

    # Multi image gallery
    @http.route(['/theme_crafito/crafito_multi_image_effect_config'], type='json', auth="public", website=True)
    def get_multi_image_effect_config(self):

        cur_website = request.website
        values = {
            'no_extra_options': cur_website.no_extra_options,
            'theme_panel_position': cur_website.thumbnail_panel_position,
            'interval_play': cur_website.interval_play,
            'enable_disable_text': cur_website.enable_disable_text,
            'color_opt_thumbnail': cur_website.color_opt_thumbnail,
            'change_thumbnail_size': cur_website.change_thumbnail_size,
            'thumb_height': cur_website.thumb_height,
            'thumb_width': cur_website.thumb_width,
        }
        return values

    # For Product slider
    @http.route(['/theme_crafito/product_get_options'], type='json', auth="public", website=True)
    def product_get_slider_options(self):
        slider_options = []
        option = request.env['product.slider.config'].search(
            [('active', '=', True)], order="name asc")
        for record in option:
            slider_options.append({'id': record.id,
                                   'name': record.name})
        return slider_options

    @http.route(['/theme_crafito/product_get_dynamic_slider'], type='http', auth='public', website=True)
    def product_get_dynamic_slider(self, **post):
        if post.get('slider-id'):
            slider_header = request.env['product.slider.config'].sudo().search(
                [('id', '=', int(post.get('slider-id')))])
            values = {
                'slider_header': slider_header
            }
            values.update({
                'slider_details': slider_header.collections_products,
            })
            return request.website.render("theme_crafito.theme_crafito_product_slider_view", values)

    @http.route(['/theme_crafito/product_image_effect_config'], type='json', auth='public', website=True)
    def product_image_dynamic_slider(self, **post):
        slider_data = request.env['product.slider.config'].search(
            [('id', '=', int(post.get('slider_id')))])
        values = {
            's_id': slider_data.name.lower().replace(' ', '-') + '-' + str(slider_data.id),
            'counts': slider_data.no_of_counts,
            'auto_rotate': slider_data.auto_rotate,
            'auto_play_time': slider_data.sliding_speed,
        }
        return values

    # For Featured Product slider
    @http.route(['/theme_crafito/featured_product_get_options'], type='json', auth="public", website=True)
    def featured_product_get_slider_options(self):
        slider_options = []
        option = request.env['feature.product.slider.config'].search(
            [('active', '=', True)], order="name asc")
        for record in option:
            slider_options.append({'id': record.id,
                                   'name': record.name})
        return slider_options

    @http.route(['/theme_crafito/featured_product_get_dynamic_slider'], type='http', auth='public', website=True)
    def featured_product_get_dynamic_slider(self, **post):
        if post.get('slider-id'):
            slider_header = request.env['feature.product.slider.config'].sudo().search(
                [('id', '=', int(post.get('slider-id')))])
            values = {
                'slider_header': slider_header
            }
            return request.website.render("theme_crafito.theme_crafito_featured_product_slider_view", values)

    @http.route(['/theme_crafito/featured_product_image_effect_config'], type='json', auth='public', website=True)
    def featured_product_image_dynamic_slider(self, **post):
        slider_data = request.env['feature.product.slider.config'].search(
            [('id', '=', int(post.get('slider_id')))])
        values = {
            's_id': slider_data.name.lower().replace(' ', '-') + '-' + str(slider_data.id),
            'counts': slider_data.no_of_counts,
            'auto_rotate': slider_data.auto_rotate,
            'auto_play_time': slider_data.sliding_speed,
        }
        return values

    @http.route(['/theme_crafito/event_slider/get_data'], type="http", auth="public", website=True)
    def get_event_data(self, **post):
        events = request.env['event.type'].sudo().search([])
        values = {'main_events_category': events}
        return request.website.render("theme_crafito.theme_crafito_events_view", values)


class CrafitoEcommerceShop(website_sale):

    @http.route()
    def cart_update_json(self, product_id, line_id=None, add_qty=None, set_qty=None, display=True):
        result = super(CrafitoEcommerceShop, self).cart_update_json(
            product_id=product_id, line_id=line_id, add_qty=add_qty, set_qty=set_qty, display=display)
        result.update({'theme_crafito.hover_total': request.website._render("theme_crafito.hover_total", {
            'website_sale_order': request.website.sale_get_order()
        })
        })
        return result

    @http.route()
    def shop(self, page=0, category=None, search='', ppg=False, **post):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        result = super(CrafitoEcommerceShop, self).shop(
            page=page, category=category, search=search, **post)
        sort_order = ""
        cat_id = []
        ppg = 18
        product = []
        newproduct = []

        # product template object
        product_obj = pool['product.template']

        attrib_list = request.httprequest.args.getlist('attrib')
        attrib_values = [map(int, v.split("-")) for v in attrib_list if v]
        attributes_ids = set([v[0] for v in attrib_values])
        attrib_set = set([v[1] for v in attrib_values])
        domain = request.website.sale_product_domain()
        domain += self._get_search_domain(search, category, attrib_values)
        url = "/shop"

        if post:
            request.session.update(post)

        prevurl = request.httprequest.referrer
        if prevurl:
            if not re.search('/shop', prevurl, re.IGNORECASE):
                request.session['sort_id'] = ""
                request.session['pricerange'] = ""
                request.session['min1'] = ""
                request.session['max1'] = ""

        session = request.session
        # for category filter
        if category:
            category = pool['product.public.category'].browse(
                cr, uid, int(category), context=context)
            url = "/shop/category/%s" % slug(category)

        if category != None:
            for ids in category:
                cat_id.append(ids.id)
            domain += ['|', ('public_categ_ids.id', 'in', cat_id),
                       ('public_categ_ids.parent_id', 'in', cat_id)]

        # For Product Sorting
        if session.get('sort_id'):
            session_sort = session.get('sort_id')
            sort = session_sort
            sorts_obj = pool['biztech.product.sortby']
            sorts_ids = sorts_obj.search(cr, uid, [], context=context)
            sorts = sorts_obj.browse(cr, uid, sorts_ids, context=context)
            sort_field = pool['biztech.product.sortby'].browse(
                cr, uid, int(sort), context=context)
            request.session['product_sort_name'] = sort_field.name
            order_field = sort_field.sort_on.name
            order_type = sort_field.sort_type
            sort_order = '%s %s' % (order_field, order_type)
            if post.get("sort_id"):
                request.session["sortid"] = [
                    sort, sort_order, sort_field.name, order_type]

        # For Price slider
        product_slider_ids = []
        asc_product_slider_ids = product_obj.search(
            cr, uid, [], limit=1, order='list_price', context=context)
        asc_products_slider = product_obj.browse(cr, uid, asc_product_slider_ids, context=context)
        desc_product_slider_ids = product_obj.search(
            cr, uid, [], limit=1, order='list_price desc', context=context)
        desc_products_slider = product_obj.browse(
            cr, uid, desc_product_slider_ids, context=context)

        if asc_products_slider and asc_products_slider.list_price:
            product_slider_ids.append(asc_products_slider.list_price)
        if desc_products_slider and desc_products_slider.list_price:
            product_slider_ids.append(desc_products_slider.list_price)

        if product_slider_ids:
            if post.get("range1") or post.get("range2") or not post.get("range1") or not post.get("range2"):
                range1 = min(product_slider_ids)
                range2 = max(product_slider_ids)
                result.qcontext['range1'] = range1
                result.qcontext['range2'] = range2

            if session.get("min1") and session["min1"]:
                post["min1"] = session["min1"]
            if session.get("max1") and session["max1"]:
                post["max1"] = session["max1"]
            if range1:
                post["range1"] = range1
            if range2:
                post["range2"] = range2
            if range1 == range2:
                post["range1"] = 0.0

            if request.session.get('min1') or request.session.get('max1'):
                if request.session.get('min1'):
                    if request.session['min1'] != None:
                        slid_product_ids = product_obj.search(cr, uid, [('list_price', '>=', request.session.get(
                            'min1')), ('list_price', '<=', request.session.get('max1'))], context=context)
                        slid_products = product_obj.browse(
                            cr, uid, slid_product_ids, context=context)
                        for prod_id in slid_products:
                            if prod_id.list_price >= float(request.session['min1']) and prod_id.list_price <= float(request.session['max1']):
                                product.append(prod_id.id)
                        request.session["pricerange"] = str(
                            request.session['min1'])+"-To-"+str(request.session['max1'])
                newproduct = product
                domain += [('id', 'in', newproduct)]

            if session.get('min1') and session['min1']:
                result.qcontext['min1'] = session["min1"]
                result.qcontext['max1'] = session["max1"]

        product_count = product_obj.search_count(
            cr, uid, domain, context=context)
        pager = request.website.pager(
            url=url, total=product_count, page=page, step=ppg, scope=7, url_args=post)
        product_ids = product_obj.search(
            cr, uid, domain, limit=ppg, offset=pager['offset'], order=sort_order, context=context)
        products = product_obj.browse(cr, uid, product_ids, context=context)

        # For Collascpe category
        parent_category_ids = []
        if category:
            parent_category_ids = [category.id]
            current_category = category
            while current_category.parent_id:
                parent_category_ids.append(current_category.parent_id.id)
                current_category = current_category.parent_id
        result.qcontext['parent_category_ids'] = parent_category_ids

        result.qcontext.update({'product_count': product_count,
                                'products': products,
                                'category': category,
                                'pager': pager,
                                'bins': table_compute().process(products)})

        return result

    @http.route(['/theme_carfito/removeattribute'], type='json', auth='public', website=True)
    def remove_selected_attribute(self, **post):
        if post.get("attr_remove"):
            remove = post.get("attr_remove")
            if remove == "pricerange":
                if request.session.get('min1'):
                    del request.session['min1']
                if request.session.get('max1'):
                    del request.session['max1']
                request.session[remove] = ''
                return True
            elif remove == "sortid":
                request.session[remove] = ''
                request.session["sort_id"] = ''
                return True
