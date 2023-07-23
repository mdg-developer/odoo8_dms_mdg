# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 NovaPoint Group LLC (<http://www.novapointgroup.com>)
#    Copyright (C) 2004-2010 OpenERP SA (<http://www.openerp.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################

{
    'name' : 'Connect With Ecommerce',
    'version' : '1.0',
    'author': 'seventh computing',
    'website': 'http://www.7thcomputing.com',
    'category' : 'Reporting',
    'depends' : [
                    "base",
                    "address_management_system",
                    "product",
                    "product_product","warehouse_application",
                    "woo_commerce_ept",'sale_group'
                ],
    'description': """
Connect With Ecommerce    
= = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
    Features:
    1. Show Delivery Team in City
    2. Show Delivery Team in State
    """,
    'data': [
        'views/credit_application_view.xml',
        'views/res_city_view.xml',
        'views/product_template_view.xml',
        'views/product_template_sequence.xml',
        'views/res_country_view.xml',
        'views/res_country_state_view.xml',
        'views/res_partner_view.xml',
        'views/res_township_view.xml',
        'views/product_pricelist_view.xml',
        'views/credit_application_approval.xml',
        'views/notified_days_view.xml',
        'views/weekly_noti_view.xml',
        'views/product_reorder_view.xml',
        'views/app_version_view.xml',
        'wizards/pricelist_multi_sync_woo_view.xml',
        'wizards/product_template_multi_delivery_view.xml',
        'views/stock_view.xml',
        'views/res_branch_view.xml',
        'views/noti_by_customer_view.xml',
        'views/sms_by_customer_view.xml',
        'views/woo_minimum_stock_view.xml',
        'wizards/mobile_sync_view.xml',
        'views/product_brand_view.xml',
        'views/product_group_view.xml',
        'views/product_tag_view.xml',
        'views/product_uom_view.xml',
        'views/product_supplier_view.xml',
        'views/product_department_view.xml',
        'views/product_approval_view.xml',
        'security/ir.model.access.csv',
                ],
    'installable': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: